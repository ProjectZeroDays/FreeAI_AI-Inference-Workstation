"""Config backup system for FreeAI workstation.

Backs up all JSON config files to config/backups/ with timestamps.
Retains the last 30 backups per file and compresses older ones.
"""
import json
import gzip
import shutil
import tarfile
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
BACKUP_DIR = CONFIG_DIR / "backups"
MAX_BACKUPS = 30
COMPRESS_AFTER = 5  # compress backups older than this count per file


def _ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _human_size(bytes_: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


def backup_all() -> dict:
    """Create a timestamped backup of all config JSON files."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = _ts()
    backed_up = []
    errors = []

    for fpath in sorted(CONFIG_DIR.glob("*.json")):
        if fpath.name.startswith("."):
            continue
        try:
            content = fpath.read_text(encoding="utf-8")
            backup_name = f"{fpath.stem}__{ts}.json"
            backup_path = BACKUP_DIR / backup_name
            backup_path.write_text(content, encoding="utf-8")
            backed_up.append({
                "original": fpath.name,
                "backup": backup_name,
                "size": _human_size(fpath.stat().st_size),
            })
            _prune_backups(fpath.stem)
        except Exception as e:
            errors.append({"file": fpath.name, "error": str(e)})

    return {
        "ok": True,
        "timestamp": ts,
        "backed_up": backed_up,
        "errors": errors,
        "count": len(backed_up),
    }


def _prune_backups(stem: str) -> None:
    """Keep only the last MAX_BACKUPS backups for a given file stem."""
    backups = sorted(BACKUP_DIR.glob(f"{stem}_*.json"))
    if len(backups) <= MAX_BACKUPS:
        return
    to_delete = backups[: len(backups) - MAX_BACKUPS]
    for b in to_delete:
        try:
            b.unlink()
        except OSError:
            pass
    # Compress any remaining beyond COMPRESS_AFTER
    remaining = sorted(BACKUP_DIR.glob(f"{stem}_*.json"))
    if len(remaining) > COMPRESS_AFTER:
        for b in remaining[: len(remaining) - COMPRESS_AFTER]:
            _compress_backup(b)


def _compress_backup(path: Path) -> None:
    """Gzip a backup file and remove the uncompressed copy."""
    try:
        with open(path, "rb") as f_in:
            comp = path.with_suffix(".json.gz")
            with gzip.open(comp, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        path.unlink()
    except OSError:
        pass


def list_backups(filename: str) -> list:
    """List all backups for a specific config file, newest first."""
    stem = Path(filename).stem
    backups = sorted(
        list(BACKUP_DIR.glob(f"{stem}_*.json")) + list(BACKUP_DIR.glob(f"{stem}_*.json.gz")),
        reverse=True,
    )
    result = []
    for b in backups:
        size_bytes = b.stat().st_size
        mtime = datetime.fromtimestamp(b.stat().st_mtime)
        result.append({
            "filename": b.name,
            "timestamp": mtime.strftime("%Y-%m-%d %H:%M:%S"),
            "size": _human_size(size_bytes),
            "compressed": b.suffix == ".gz",
        })
    return result


def restore_backup(filename: str, backup_name: str) -> dict:
    """Restore a config file from a backup."""
    stem = Path(filename).stem
    backup_path = BACKUP_DIR / backup_name
    if not backup_path.exists():
        return {"ok": False, "error": "Backup not found"}
    try:
        if backup_name.endswith(".gz"):
            with gzip.open(backup_path, "rt", encoding="utf-8") as f:
                content = f.read()
        else:
            content = backup_path.read_text(encoding="utf-8")
        # Validate it's JSON
        json.loads(content)
        target = CONFIG_DIR / filename
        target.write_text(content, encoding="utf-8")
        return {"ok": True, "content": content}
    except Exception as e:
        return {"ok": False, "error": "An error occurred"}


def export_all_as_tar() -> Path:
    """Create a tar.gz archive of all current config files."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = BACKUP_DIR / f"configs_export_{_ts()}.tar.gz"
    with tarfile.open(archive_path, "w:gz") as tar:
        for fpath in sorted(CONFIG_DIR.glob("*.json")):
            if fpath.name.startswith("."):
                continue
            tar.add(fpath, arcname=fpath.name)
    return archive_path


if __name__ == "__main__":
    result = backup_all()
    print(json.dumps(result, indent=2))
