"""Preserve assistant text AND calls as in the Qwen tokenizer template."""
import hashlib, json, os, urllib.request
from pathlib import Path
root=Path(os.environ['LOCALAPPDATA'])/'BankingDefenseRuntime/models'
evidence=Path('research/runs/qualification-20261027/template-evidence')
evidence.mkdir(parents=True,exist_ok=True)
base=json.loads((root/'manifests/registry.ollama.ai/library/qwen2.5/7b-instruct-q4_K_M').read_text())
opener=urllib.request.build_opener()
for name in ['tokenizer_config.json','generation_config.json']:
    url='https://huggingface.co/Qwen/Qwen2.5-7B-Instruct/raw/main/'+name
    with opener.open(url,timeout=30) as response:(evidence/name).write_bytes(response.read())
def read(layer):return (root/'blobs'/layer['digest'].replace(':','-')).read_bytes()
def put(data,kind):
    digest='sha256:'+hashlib.sha256(data).hexdigest()
    (root/'blobs'/digest.replace(':','-')).write_bytes(data)
    return {'mediaType':kind,'digest':digest,'size':len(data)}
template_layer=next(l for l in base['layers'] if l['mediaType'].endswith('.template'))
old=read(template_layer).decode()
start=old.index('{{ if .Content }}')
end=old.index('{{ if not $last }}',start)
replacement='''{{ if .Content }}{{ .Content }}{{ end }}
{{- range .ToolCalls }}
<tool_call>
{"name": "{{ .Function.Name }}", "arguments": {{ .Function.Arguments }}}
</tool_call>
{{- end }}'''
new=old[:start]+replacement+old[end:]
assert '{{- else if .ToolCalls }}' not in new
(evidence/'original-ollama.tmpl').write_text(old,encoding='utf-8')
(evidence/'compatible-ollama.tmpl').write_text(new,encoding='utf-8')
generation=json.loads((evidence/'generation_config.json').read_text())
params={'num_ctx':8192,'num_predict':1024,'temperature':generation['temperature'],
        'top_p':generation['top_p'],'top_k':generation['top_k'],
        'repeat_penalty':generation['repetition_penalty'],'seed':42}
layers=[l for l in base['layers'] if not l['mediaType'].endswith(('.template','.params'))]
layers += [put(new.encode(),'application/vnd.ollama.image.template'),
           put(json.dumps(params,sort_keys=True).encode(),'application/vnd.ollama.image.params')]
config=json.loads(read(base['config']))
config['rootfs']['diff_ids']=[l['digest'] for l in layers]
manifest={**base,'layers':layers,'config':put(json.dumps(config,sort_keys=True).encode(),base['config']['mediaType'])}
target=root/'manifests/registry.ollama.ai/library/banking-qwen25-compatible/latest'
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(manifest,sort_keys=True),encoding='utf-8')
Path('research/config/qwen25-compatible.tmpl').write_text(new,encoding='utf-8')
(evidence/'parameters.json').write_text(json.dumps(params,indent=2),encoding='utf-8')
print(json.dumps({'model':'banking-qwen25-compatible:latest','parameters':params,'template_fix':'preserve text and every tool call in the same assistant message'}))
