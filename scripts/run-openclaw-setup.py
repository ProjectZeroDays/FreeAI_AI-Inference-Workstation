#!/usr/bin/env python3
"""SSH into Kali VPS and run the OpenClaw setup script."""
import paramiko
import sys
import os

HOST = "93.188.162.144"
USER = "root"
PASSWORD = "1Tr3y@113nSm1th"
SCRIPT_PATH = "scripts/openclaw-kali-setup.sh"

def main():
    # Read the setup script (force UTF-8)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    script_path = os.path.join(project_root, SCRIPT_PATH)
    with open(script_path, "r", encoding="utf-8", errors="replace") as f:
        script_content = f.read()

    print(f"[*] Connecting to {USER}@{HOST}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        print("[*] Connected! Running OpenClaw setup...")
        print("[*] This will take several minutes. Be patient.\n")

        # Upload script to remote
        sftp = client.open_sftp()
        remote_script = "/tmp/openclaw-setup.sh"
        with open(os.path.join(project_root, SCRIPT_PATH), "rb") as f:
            sftp.putfo(f, remote_script)
        sftp.chmod(remote_script, 0o755)
        print(f"[*] Uploaded script to {remote_script}")

        # Run the script
        stdin, stdout, stderr = client.exec_command(
            f"bash {remote_script} 2>&1",
            timeout=600
        )

        # Stream output
        output_lines = []
        while True:
            line = stdout.readline()
            if not line and stdout.channel.recv_exit_status() is not None:
                break
            if line:
                line = line.rstrip()
                output_lines.append(line)
                print(line)

        # Get any remaining stderr
        stderr_text = stderr.read().decode("utf-8", errors="replace").strip()
        if stderr_text:
            print(f"\n[STDERR]\n{stderr_text}")

        exit_status = stdout.channel.recv_exit_status()
        print(f"\n[*] Script exited with code {exit_status}")

        # Cleanup
        client.exec_command(f"rm -f {remote_script}")

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()
