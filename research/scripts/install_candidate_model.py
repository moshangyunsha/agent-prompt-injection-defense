"""Verified official OCI blobs, copied without cross-volume rename on this Windows host."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import subprocess,os,json,hashlib,urllib.request,time,shutil
ROOT=Path(os.environ['LOCALAPPDATA'])/'BankingDefenseRuntime/models'
BASE='https://registry.ollama.ai/v2/library/qwen3.5'
TAG='9b-q4_K_M'
EVIDENCE=Path('research/runs/qualification-20261027/qwen35-install')
EVIDENCE.mkdir(parents=True,exist_ok=True)
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def fetch_small(url):
    with opener.open(url,timeout=30) as response:return response.read()
def sha_file(path):
    with path.open('rb') as stream:return 'sha256:'+hashlib.file_digest(stream,'sha256').hexdigest()
def download(layer):
    target=ROOT/'blobs'/layer['digest'].replace(':','-')
    if target.exists() and target.stat().st_size==layer['size'] and sha_file(target)==layer['digest']:return
    url=BASE+'/blobs/'+layer['digest']
    if layer['size']<1024*1024:
        data=fetch_small(url)
        if 'sha256:'+hashlib.sha256(data).hexdigest()!=layer['digest']:raise RuntimeError('Metadata digest mismatch')
        target.write_bytes(data);return
    pieces=ROOT/'candidate-download'/layer['digest'].replace(':','-');pieces.mkdir(parents=True,exist_ok=True)
    chunk=16*1024*1024
    def piece(offset):
        end=min(layer['size'],offset+chunk)-1
        path=pieces/str(offset)
        if path.exists() and path.stat().st_size==end-offset+1:return path
        result=subprocess.run(['C:/Windows/System32/curl.exe','--noproxy','*','--location','--fail','--silent','--show-error',
            '--retry','4','--retry-all-errors','--max-time','120','--range',f'{offset}-{end}',
            '--output',str(path),url+'?piece='+str(offset)],capture_output=True,text=True,creationflags=0x08000000)
        if result.returncode or not path.exists() or path.stat().st_size!=end-offset+1:
            raise RuntimeError(f'Download failed at {offset}: {result.stderr[:120]}')
        return path
    total=0;last=0
    with ThreadPoolExecutor(max_workers=16) as pool:
        for future in as_completed([pool.submit(piece,offset) for offset in range(0,layer['size'],chunk)]):
            total+=future.result().stat().st_size
            if time.monotonic()-last>10:
                print(json.dumps({'blob':layer['mediaType'].rsplit('.',1)[-1],'mib':round(total/2**20),'total_mib':round(layer['size']/2**20)}),flush=True);last=time.monotonic()
    with target.open('wb') as output:
        for offset in range(0,layer['size'],chunk):
            with (pieces/str(offset)).open('rb') as stream:shutil.copyfileobj(stream,output)
    if sha_file(target)!=layer['digest']:raise RuntimeError('Model weight digest mismatch')
    print(json.dumps({'verified':layer['digest'],'bytes':target.stat().st_size}),flush=True)
def put(data,kind):
    digest='sha256:'+hashlib.sha256(data).hexdigest();(ROOT/'blobs'/digest.replace(':','-')).write_bytes(data)
    return {'mediaType':kind,'digest':digest,'size':len(data)}
def main():
    raw=fetch_small(BASE+'/manifests/'+TAG);manifest=json.loads(raw)
    (EVIDENCE/'official-manifest.json').write_bytes(raw)
    for layer in [manifest['config'],*manifest['layers']]:download(layer)
    original=ROOT/'manifests/registry.ollama.ai/library/qwen3.5'/TAG
    original.parent.mkdir(parents=True,exist_ok=True);original.write_bytes(raw)
    params={'num_ctx':8192,'num_predict':1024,'temperature':0.7,'top_p':0.8,'top_k':20,'min_p':0,
            'repeat_penalty':1.0,'presence_penalty':1.5,'seed':42}
    layers=[l for l in manifest['layers'] if not l['mediaType'].endswith('.params')]
    layers.append(put(json.dumps(params,sort_keys=True).encode(),'application/vnd.ollama.image.params'))
    config=json.loads((ROOT/'blobs'/manifest['config']['digest'].replace(':','-')).read_text())
    if 'rootfs' in config:config['rootfs']['diff_ids']=[l['digest'] for l in layers]
    frozen={**manifest,'layers':layers,'config':put(json.dumps(config,sort_keys=True).encode(),manifest['config']['mediaType'])}
    target=ROOT/'manifests/registry.ollama.ai/library/banking-qwen35-9b/latest'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(frozen,sort_keys=True),encoding='utf-8')
    (EVIDENCE/'parameters.json').write_text(json.dumps(params,indent=2),encoding='utf-8')
    print(json.dumps({'installed':'banking-qwen35-9b:latest','all_blobs_verified':True,'params':params}),flush=True)
if __name__=='__main__':main()
