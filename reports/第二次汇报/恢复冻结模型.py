"""Reinstall the captured manifest, not a possibly updated mutable registry tag."""
from pathlib import Path
import importlib.util,hashlib
ROOT=Path(__file__).resolve().parents[2]
PIN='56671c2ab9385f9cfcb404638e32cd62d88e3501d44822208363c010179a3c90'
p=ROOT/'research/runs/qualification-20261027/qwen35-install/official-manifest.json'
raw=p.read_bytes()
if hashlib.sha256(raw).hexdigest()!=PIN:raise RuntimeError('Captured official manifest hash mismatch')
spec=importlib.util.spec_from_file_location('installer',ROOT/'research/scripts/install_candidate_model.py')
installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
original_fetch=installer.fetch_small
manifest_url=installer.BASE+'/manifests/'+installer.TAG
installer.fetch_small=lambda url:raw if url==manifest_url else original_fetch(url)
if __name__=='__main__':installer.main()