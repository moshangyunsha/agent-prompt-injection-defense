"""Restore verified OCI model blobs by copy; works on hosts that reject same-directory rename."""
from __future__ import annotations
import hashlib,json,os,urllib.request
from pathlib import Path

ROOT=Path(os.environ["LOCALAPPDATA"])/"BankingDefenseRuntime/models"
REGISTRY="https://registry.ollama.ai/v2/library/qwen2.5"
TAG="7b-instruct-q4_K_M"
PARAMETERS={"num_ctx":8192,"temperature":0,"seed":42,"num_predict":768}
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def fetch(url):
    with opener.open(urllib.request.Request(url,headers={"User-Agent":"ollama"}),timeout=90) as response:return response.read()
def sha(data):return "sha256:"+hashlib.sha256(data).hexdigest()
def blob(item):
    path=ROOT/"blobs"/item["digest"].replace(":","-")
    if path.exists():
        with path.open("rb") as stream:actual="sha256:"+hashlib.file_digest(stream,"sha256").hexdigest()
        if actual==item["digest"]:return path.read_bytes() if item["size"]<1024*1024 else None
        raise RuntimeError("Existing blob SHA256 mismatch")
    partial=path.with_name(path.name+"-partial")
    if partial.exists() and partial.stat().st_size==item["size"]:
        data=partial.read_bytes()
        if sha(data)==item["digest"]:path.write_bytes(data);return data
    if item["size"]>1024*1024:raise RuntimeError("Missing verified main model blob")
    data=fetch(REGISTRY+"/blobs/"+item["digest"])
    if sha(data)!=item["digest"]:raise RuntimeError("Registry metadata hash mismatch")
    path.write_bytes(data);return data
def put_blob(data,kind):
    digest=sha(data);path=ROOT/"blobs"/digest.replace(":","-");path.write_bytes(data)
    return {"mediaType":kind,"digest":digest,"size":len(data)}
def main():
    raw=fetch(REGISTRY+"/manifests/"+TAG);manifest=json.loads(raw)
    config=json.loads(blob(manifest["config"]))
    params={}
    for layer in manifest["layers"]:
        data=blob(layer)
        if layer["mediaType"].endswith(".params") and data:params=json.loads(data)
    base=ROOT/"manifests/registry.ollama.ai/library/qwen2.5"/TAG
    base.parent.mkdir(parents=True,exist_ok=True);base.write_bytes(raw)
    params.update(PARAMETERS)
    layers=[row for row in manifest["layers"] if not row["mediaType"].endswith(".params")]
    layers.append(put_blob(json.dumps(params,sort_keys=True).encode(),"application/vnd.ollama.image.params"))
    if isinstance(config.get("rootfs"),dict):config["rootfs"]["diff_ids"]=[row["digest"] for row in layers]
    config_blob=put_blob(json.dumps(config,sort_keys=True).encode(),manifest["config"]["mediaType"])
    frozen={**manifest,"config":config_blob,"layers":layers}
    target=ROOT/"manifests/registry.ollama.ai/library/banking-qwen25-7b-v0/latest"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(frozen,sort_keys=True),encoding="utf-8")
    print(json.dumps({"base_tag":TAG,"local_tag":"banking-qwen25-7b-v0:latest","parameters":params,"layers":len(layers),"all_blobs_verified":True}),flush=True)
if __name__=="__main__":main()
