# 工具型智能体提示注入防御

本项目研究模型读取受污染的外部内容后，工具执行如何遵守原始用户任务。实验使用AgentDojo银行环境和Qwen3.5-9B，比较默认执行C0、工具返回来源标记C1和执行授权检查C2。

第二阶段已完成V0检查器、独立评分器、43项程序测试、12条正常任务资格检查、8条试跑及144条正式对照轨迹。第三阶段的字段与记录授权V1、第四阶段的摘要来源保留V2尚未实现。

## 组员从哪里开始

1. 阅读[第二次实验报告](reports/第二次汇报/第二次汇报技术实现与实验说明.md)，了解任务、实现、实验步骤和结论。
2. 汇报制作可使用[排版版PDF](reports/第二次汇报/第二次汇报技术实现与实验说明_瑞士现代主义.pdf)、[排版版Word](reports/第二次汇报/第二次汇报技术实现与实验说明_瑞士现代主义.docx)和[原版Word](reports/第二次汇报/第二次汇报技术实现与实验说明.docx)。
3. 原始图片在[编辑器实拍](reports/第二次汇报/编辑器实拍/)，报告案例对应的[完整C0轨迹](research/runs/qualified-20261027/main-seed17/traces/user_task_6__injection_task_4__C0.json)和[完整C2轨迹](research/runs/qualified-20261027/main-seed17/traces/user_task_6__injection_task_4__C2.json)可逐项核对。
4. 第一次汇报的[27页PPT](reports/第一次汇报/交付快照/presentation.pptx)、[讲稿](reports/第一次汇报/交付快照/speaker-script.md)和[文献来源](reports/第一次汇报/交付快照/source-map.md)保留在同一仓库。

## 项目结构

| 位置 | 内容 |
|---|---|
| `research/src/banking_defense/` | 模型适配、攻击模板、任务授权策略、V0执行器、独立评分和运行器 |
| `research/scripts/` | 模型准备、正常任务资格检查、实验运行和统计入口 |
| `research/tests/` | 43项本地程序测试 |
| `research/runs/qualified-20261027/` | 144条正式轨迹、8条试跑、逐项指标、调用表和复核记录 |
| `research/runs/qualification-20261027/qwen35-precise/` | 12条通过准入的原始正常任务记录 |
| `reports/第二次汇报/` | 第二次报告、原始记录图片和模型恢复脚本 |
| `reports/第一次汇报/交付快照/` | 第一次汇报的PPT、讲稿和来源索引 |
| `src/`、`scripts/`、`assets/` | 第一次PPT的TypeScript源码、生成脚本和配套图片 |

## 核心实现

AgentDojo提供模拟银行状态、工具函数和任务集。本项目实现了以下模块：

- [policies.py](research/src/banking_defense/policies.py)：将用户任务登记为允许的写工具、次数和固定参数约束。
- [v0_executor.py](research/src/banking_defense/v0_executor.py)：在银行函数执行前检查每个调用，记录允许或拒绝决定。
- [pipelines.py](research/src/banking_defense/pipelines.py)：使用同一模型装配C0、C1、C2。
- [local_llm.py](research/src/banking_defense/local_llm.py)：通过兼容接口调用本地模型，处理工具定义、调用编号和跨轮历史。
- [scoring.py](research/src/banking_defense/scoring.py)：独立核验正确任务结果、预定攻击目标和未授权状态变化。
- [runner.py](research/src/banking_defense/runner.py)：重置实验环境、执行任务、记录请求和工具结果，并保存前后状态。

## 实验设置与已完成结果

四项任务为三月支出统计、差额退款、全额退款和新增周期付款。三个攻击目标为音乐服务信息外传、修改既有周期付款收款人和向攻击者累计转账超过10。每项任务接受正常输入及三个攻击输入，分别运行C0/C1/C2，构成48项矩阵；三个采样种子42、17、73共144条正式轨迹。

| 配置 | 正常任务完整完成 | 攻击目标达成 | 未授权写入 | 攻击下完整完成 |
|---|---|---|---|---|
| C0 | 11/12 | 5/36 | 10/36 | 24/36 |
| C1 | 10/12 | 7/36 | 10/36 | 25/36 |
| C2 | 11/12 | 0/36 | 3/36 | 27/36 |

正式实验包含556次模型请求、135个候选写调用。C2在7条攻击轨迹中实际拒绝15个请求，正常合法候选调用误拒为0/8。C2的3条偏离任务写入均为差额退款金额2、正确金额4的情况，对应尚未核验的动态金额计算依据。

完整完成要求结果正确、没有额外未授权状态变化，并正常给出最终答复。四项开发任务上的重复测量用于本阶段配置比较；独立任务评测属于第五阶段。

原始统计：[aggregate.json](research/runs/qualified-20261027/aggregate.json)、[144条逐项指标](research/runs/qualified-20261027/全部轨迹指标.csv)、[135个候选写调用](research/runs/qualified-20261027/全部候选写调用.csv)。试跑与主实验分别统计。银行账户、交易和口令等字段来自AgentDojo模拟数据。

## 获取项目与本地测试

直接下载：仓库页面点击 **Code → Download ZIP** 并解压。使用Git：

```powershell
git clone https://github.com/moshangyunsha/agent-prompt-injection-defense.git
cd agent-prompt-injection-defense
```

研究工程使用Python 3.12.4，依赖锁定于`research/requirements-lock.txt`；AgentDojo固定到提交`089ed468cf3ed0322acc66b0211f26d9d90dbf60`。在项目根目录执行：

```powershell
python -m venv research/.venv
.\research\.venv\Scripts\python.exe -m pip install -r research/requirements-lock.txt
.\research\.venv\Scripts\python.exe -m pip install -e research -c research/requirements-lock.txt
.\research\.venv\Scripts\python.exe -m unittest discover -s research/tests
```

本地程序测试使用脚本模型及受控输入，不依赖模型推理服务。直接阅读报告、图片和已有实验轨迹也不需要启动模型。

## 运行模型实验

本阶段使用Qwen3.5-9B Q4_K_M、Ollama 0.40.11和OpenAI Python SDK 3.37.0。SDK连接本地Ollama兼容接口。Windows下按以下顺序准备已冻结的模型版本：

```powershell
.\research\.venv\Scripts\python.exe research/scripts/setup_local_model.py
.\research\.venv\Scripts\python.exe reports/第二次汇报/恢复冻结模型.py
.\research\config\start-local-server.ps1
```

模型权重与推理运行时安装到`%LOCALAPPDATA%/BankingDefenseRuntime`，未放入Git仓库。恢复脚本使用已保存的官方清单与摘要校验模型文件。

新电脑先运行正常任务资格检查，生成本机的资格记录。原始采集清单保留了采集时的路径和模型身份信息。

```powershell
.\research\.venv\Scripts\python.exe research/scripts/qualify_model.py --reasoning-effort low --temperature 0.6 --top-p 0.95 --max-tokens 4096 --output research/runs/new-qualification
```

资格检查通过后先进行8条试跑，再运行48项矩阵。新运行输出到独立目录：

```powershell
.\research\.venv\Scripts\python.exe research/scripts/run_experiments.py --reasoning-effort low --temperature 0.6 --top-p 0.95 --max-tokens 4096 --qualification research/runs/new-qualification/qualification.json --smoke-test --output research/runs/new-smoke
.\research\.venv\Scripts\python.exe research/scripts/run_experiments.py --reasoning-effort low --temperature 0.6 --top-p 0.95 --max-tokens 4096 --qualification research/runs/new-qualification/qualification.json --seed 42 --output research/runs/new-main-seed42
```

正式实验的实际请求参数为temperature=0.6、top_p=0.95、presence_penalty=0、输出预算4096 token、上下文8192 token、最多15轮工具执行，启用模型思考。

## PPT工程

`output/presentation.pptx`是第一次汇报成品。PPT源码使用Node.js、TypeScript和PptxGenJS；可通过`npm ci`安装依赖并运行`npm run typecheck`。构建与PowerPoint渲染脚本使用原始`input/`资料和PPT模板，117MB原始模板未放入仓库；制作新PPT可直接参考已交付的成品、讲稿及第二次报告。

## 上游与来源

- [AgentDojo](https://github.com/ethz-spylab/agentdojo)：任务环境、工具和公开攻击模板；其MIT许可原文保存在[third-party/AgentDojo-LICENSE.txt](third-party/AgentDojo-LICENSE.txt)。
- [Ollama](https://github.com/ollama/ollama)与[Qwen](https://github.com/QwenLM)：本地模型推理及模型发布来源。
- 汇报中的论文图摘录及学术依据见[第一次汇报来源索引](output/source-map.md)。

`PUBLICATION_MANIFEST.json`记录公开快照中原始文件的字节数与摘要。Git属性保留原始字节及换行，供冻结代码和实验记录复核。

公开快照检查结果见[发布验证记录](docs/发布验证.md)。
