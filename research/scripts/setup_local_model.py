"""Install a pinned portable Ollama runtime. No administrator, PATH edits, or cloud inference."""
from __future__ import annotations
import hashlib
import json
import os
import shutil
import time
import urllib.request
import zipfile
from pathlib import Path

VERSION = "0.40.11"
URL = f"https://github.com/ollama/ollama/releases/download/v{VERSION}/ollama-windows-amd64.zip"
SHA256 = "bda4a493ba8a7c24d57263cd843cd68cee84f44aed4299eeed532acad7eda12a"
RUNTIME_ROOT = Path(os.environ["LOCALAPPDATA"]) / "BankingDefenseRuntime"


def main():
    RUNTIME_ROOT.mkdir(parents=True, exist_ok=True)
    archive = RUNTIME_ROOT / f"ollama-{VERSION}.zip"
    partial = archive.with_suffix(".zip.part")
    if not archive.exists() and partial.exists() and partial.stat().st_size == 1586356606:
        with partial.open("rb") as stream:
            if hashlib.file_digest(stream, "sha256").hexdigest() == SHA256:
                shutil.copyfile(partial, archive)
    if not archive.exists():
        request = urllib.request.Request(URL, headers={"User-Agent": "banking-defense-research"})
        started = time.monotonic()
        with urllib.request.urlopen(request, timeout=120) as response, partial.open("wb") as output:
            size = int(response.headers.get("Content-Length", 0)); received = 0; previous = 0
            while chunk := response.read(4 * 1024 * 1024):
                output.write(chunk); received += len(chunk)
                if received - previous >= 64 * 1024 * 1024:
                    print(json.dumps({"downloaded_mib": round(received / 2**20), "total_mib": round(size / 2**20), "seconds": round(time.monotonic()-started)}), flush=True)
                    previous = received
        shutil.copyfile(partial, archive)
    digest = hashlib.file_digest(archive.open("rb"), "sha256").hexdigest()
    if digest != SHA256:
        raise RuntimeError("Ollama archive hash mismatch; do not execute it.")
    target = RUNTIME_ROOT / f"ollama-{VERSION}"
    if not (target / "ollama.exe").exists():
        with zipfile.ZipFile(archive) as source:
            for name in source.namelist():
                if not (target / name).resolve().is_relative_to(target.resolve()):
                    raise RuntimeError("Unexpected archive path")
            source.extractall(target)
    print(json.dumps({"runtime_root": str(RUNTIME_ROOT), "executable": str(target / "ollama.exe"), "archive_sha256": digest}), flush=True)


if __name__ == "__main__":
    main()
