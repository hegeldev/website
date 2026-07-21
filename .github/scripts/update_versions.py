import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True, cwd=ROOT)


def main():
    protocol_version = os.environ["PROTOCOL_VERSION"]
    new_version = os.environ["NEW_VERSION"]
    app_id = os.environ["HEGEL_RELEASE_APP_ID"]

    versions_path = ROOT / "public" / "api" / "versions.json"
    versions = json.loads(versions_path.read_text())

    if protocol_version in versions:
        print(f"Protocol version {protocol_version} already mapped, nothing to do")
        return

    versions[protocol_version] = new_version
    # Sort by protocol version (major.minor numeric comparison)
    def version_key(kv):
        parts = kv[0].split(".")
        return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)

    sorted_versions = dict(sorted(versions.items(), key=version_key))
    versions_path.write_text(json.dumps(sorted_versions, indent=2) + "\n")

    git("config", "user.name", "hegel-release[bot]")
    git("config", "user.email", f"{app_id}+hegel-release[bot]@users.noreply.github.com")

    git("add", "public/api/versions.json")
    git("commit", "-m", f"Add protocol version {protocol_version} mapping")

    # A hegel-core release can cascade into near-simultaneous releases of the
    # language libraries, all pushing to main at once. On a rejected push,
    # rebase onto origin/main and retry. The rebase is always clean since each
    # flow touches a distinct path.
    attempts = 5
    for attempt in range(attempts):
        if attempt:
            print(f"Push rejected, rebasing onto origin/main (attempt {attempt + 1}/{attempts})")
            time.sleep(2)
            git("fetch", "origin")
            git("rebase", "origin/main")
        result = subprocess.run(["git", "push", "origin", "main"], cwd=ROOT)
        if result.returncode == 0:
            return
    raise SystemExit(f"Failed to push after {attempts} attempts")


if __name__ == "__main__":
    main()
