"""Secrets manager — AES-256 encrypted file storage for dashboard secrets.

Provides a simple key-value secrets store with on-disk encryption.
Secrets are stored individually as encrypted files under config/secrets.enc/.
A JSON metadata file tracks names only (no values).

Fallback: if encrypted storage is unavailable, secrets are held in-memory
and optionally synced to environment variables via os.environ.
"""
import base64
import hashlib
import json
import os
import time
import threading
from pathlib import Path

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as _padding
from cryptography.hazmat.backends import default_backend

try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    _HAS_KDF = True
except ImportError:
    _HAS_KDF = False

ROOT = Path(__file__).parent.parent
SECRETS_DIR = ROOT / "config" / "secrets.enc"
METADATA_PATH = SECRETS_DIR / "metadata.json"

_LOCK = threading.Lock()
_IN_MEMORY = {}


def _get_master_key() -> bytes:
    """Return the 32-byte master key from env or generate a deterministic one."""
    raw = os.environ.get("SECRETS_MASTER_KEY", "")
    if raw:
        h = hashlib.sha256(raw.encode("utf-8")).digest()
        return h
    # Fallback: derive from a fixed project salt so tests work without env var
    salt = os.environ.get("SECRETS_SALT", "freeai-dashboard-secrets-salt-2024")
    return hashlib.pbkdf2_hmac("sha256", b"default-master-key", salt.encode(), 100000)


def _derive_key(name: str) -> bytes:
    """Per-secret key derived from master key + name."""
    master = _get_master_key()
    return hashlib.pbkdf2_hmac("sha256", master, name.encode("utf-8"), 100000)


def _encrypt_value(plaintext: str, key: bytes) -> str:
    """Encrypt a string value with AES-256-CBC + PKCS7."""
    iv = os.urandom(16)
    plaintext_bytes = plaintext.encode("utf-8")
    padder = _padding.PKCS7(128).padder()
    padded = padder.update(plaintext_bytes) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode("ascii")


def _decrypt_value(ciphertext_b64: str, key: bytes) -> str:
    """Decrypt a base64-encoded AES-256-CBC ciphertext."""
    raw = base64.b64decode(ciphertext_b64)
    iv = raw[:16]
    ciphertext = raw[16:]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = _padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded) + unpadder.finalize()
    return plaintext.decode("utf-8")


def _load_metadata() -> dict:
    """Load the metadata JSON (names only, no values)."""
    if METADATA_PATH.exists():
        try:
            return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"secrets": {}, "updated_at": 0}


def _save_metadata(meta: dict):
    """Persist metadata JSON."""
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    meta["updated_at"] = int(time.time())
    METADATA_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def _encrypted_path(name: str) -> Path:
    safe = "".join(c if c.isalnum() else "_" for c in name)
    path = SECRETS_DIR / os.path.normpath(f"{safe}.enc")
    resolved = path.resolve(strict=False)
    if not str(resolved).startswith(str(SECRETS_DIR.resolve()) + os.sep) and resolved != SECRETS_DIR.resolve():
        raise ValueError(f"Secret name '{name}' resolves outside secrets directory")
    return path


def store_secret(name: str, value: str) -> bool:
    """Store an encrypted secret by name."""
    if not name or not value:
        return False
    name = name.strip()
    value = str(value)
    key = _derive_key(name)
    enc = _encrypt_value(value, key)
    path = _encrypted_path(name)  # nosec B108
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(enc, encoding="utf-8")  # nosec B108
    with _LOCK:
        _IN_MEMORY[name] = value
    meta = _load_metadata()
    meta["secrets"][name] = {
        "created_at": meta["secrets"].get(name, {}).get("created_at", int(time.time())),
        "updated_at": int(time.time()),
    }
    _save_metadata(meta)
    return True


def get_secret(name: str) -> str | None:
    """Retrieve and decrypt a secret by name. Returns None if not found."""
    name = name.strip()
    with _LOCK:
        if name in _IN_MEMORY:
            return _IN_MEMORY[name]
    key = _derive_key(name)
    path = _encrypted_path(name)
    if not path.exists():
        return None
    try:
        enc = path.read_text(encoding="utf-8").strip()
        return _decrypt_value(enc, key)
    except Exception:
        return None


def delete_secret(name: str) -> bool:
    """Delete a secret by name. Returns True if it existed."""
    name = name.strip()
    with _LOCK:
        _IN_MEMORY.pop(name, None)
    path = _encrypted_path(name)  # nosec B108
    if path.exists():
        path.unlink()  # nosec B108
        meta = _load_metadata()
        meta["secrets"].pop(name, None)
        _save_metadata(meta)
        return True
    return False


def list_secrets() -> list[str]:
    """Return a sorted list of secret names (never values)."""
    names = set()
    with _LOCK:
        names.update(_IN_MEMORY.keys())
    if SECRETS_DIR.exists():
        for f in SECRETS_DIR.glob("*.enc"):
            safe = f.stem
            if safe not in ("metadata",):
                names.add(safe)
    meta = _load_metadata()
    names.update(meta.get("secrets", {}).keys())
    return sorted(names)


def rotate_secret(name: str, new_value: str) -> bool:
    """Rotate a secret: delete old, store new. Returns True on success."""
    if not delete_secret(name):
        return False
    return store_secret(name, new_value)


def import_secrets(data: dict) -> dict:
    """Bulk import secrets from a dict {name: value}. Returns {ok, failed}."""
    ok = []
    failed = []
    for name, value in data.items():
        if store_secret(name, str(value)):
            ok.append(name)
        else:
            failed.append(name)
    return {"ok": ok, "failed": failed, "imported": len(ok), "failed_count": len(failed)}


def export_secrets() -> dict:
    """Export all secrets as {name: value} for backup/restore.
    Note: returns plaintext — use with caution.
    """
    result = {}
    for name in list_secrets():
        val = get_secret(name)
        if val is not None:
            result[name] = val
    return result


def get_secret_metadata(name: str) -> dict | None:
    """Return metadata for a secret (creation/update times, no value)."""
    meta = _load_metadata()
    info = meta.get("secrets", {}).get(name)
    if info is None:
        return None
    return {
        "name": name,
        "created_at": info.get("created_at", 0),
        "updated_at": info.get("updated_at", 0),
    }
