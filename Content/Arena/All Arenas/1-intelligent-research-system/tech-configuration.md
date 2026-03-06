# 技术配置（原始提取）

## 步骤 1：资源准备与环境配置

### 步骤定义
检查 Node、npm、python是否完成安装，为下一步安装 Claude Code 做准备

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：安装 Node
- 输入介绍：通过命令行安装 Node、npm、python。
- 输入示例：
相关命令如下：
```bash
node -v
注：输出可能类似"v22.21.1"

npm -v
注：输出可能类似"10.9.4"

python -V
注：输出可能类似"Python 3.11.13"
```

### 本步产出
- 输出名称：环境配置所需资源就绪
- 输出介绍：服务器已配置Python 环境、Node 环境，满足模型部署的要求

### 预估时间
1-2 日

## 步骤 2：Claude Code 安装和配置

### 步骤定义
通过 Node 安装和配置 Claude Code

### 参与人员
- 角色名称：算法工程师（前端工程师/后端工程师）
- 技能要求：熟悉 node 即可
- 角色数量：1

### 本步输入
- 输入名称：安装和配置 Claude Code
- 输入介绍：基于 Node 环境来安装和配置 Claude Code
- 输入示例：
相关命令如下：
```bash
# 安装 Claude Code
npm install -g @anthropic-ai/claude-code

# 配置环境变量（以 ~/.bashrc 为例，其他如 ~/.zshrc 等同理）
echo 'export ANTHROPIC_BASE_URL="YOUR_BASE_URL"' >> ~/.bashrc
echo 'export ANTHROPIC_AUTH_TOKEN="YOUR_AUTH_TOKEN"' >> ~/.bashrc

# 配置模型
vim ~/.claude/settings.json
{
  "env": {
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "YOUR_HAIKU_MODEL",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "YOUR_SONNET_MODEL",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "YOUR_OPUS_MODEL"
  }
}

# 启动成功确认命令，claude 进入命令行，输入任意文字后有收到对应回复且无报错则配置完成
claude
> your_input
```
- 资源链接：
1. Claude Code GitHub：https://github.com/anthropics/claude-code

### 本步产出
- 输出名称：可用的 Claude Code 服务
- 输出介绍：通过 Claude Code 来生成目标网站的 PRD 文件

### 预估时间
0.5-1 日

## 步骤 3：tavily-mcp 服务构建、启动（可选）

### 步骤定义
构建 tavily-mcp 服务，支持网络搜索、内容读取和智能问答能力

### 参与人员
- 角色名称：算法/后端工程师
- 技能要求：熟悉 linux 常用命令和python
- 角色数量：1

### 本步输入
- 输入名称：tavily-mcp 服务构建、启动
- 输入介绍：使用远程MCP服务器URL来安装和启动相关 mcp 服务
- 输入示例：
使用远程MCP服务器URL与Tavily API密钥：
```text
https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>
```
- 将以下内容添加到.claude.json文件
```json
{
  "mcpServers": {
    "tavily-remote-mcp": {
      "command": "npx -y mcp-remote https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>",
      "env": {}
    }
  }
}
```
运行以下代码查看是否连接成功：
```bash
claude mcp list

# 注：看到类似"tavily-remote-mcp：https://mcp.tavily.com/mcp（HTTP） - ✓ Connected"则成功
```
- 资源链接：
1. Claude Code GitHub：https://github.com/anthropics/claude-code

### 本步产出
- 输出名称：可用的 tavily 网络搜索 mcp 服务
- 输出介绍：构建和启动 tavily-mcp 服务

### 预估时间
0.5-1 日

## 步骤 4：metaso-mcp 服务构建、启动

### 步骤定义
构建 metaso-mcp 服务，支持网络搜索、内容读取和智能问答能力

### 参与人员
- 角色名称：算法/后端工程师
- 技能要求：熟悉 linux 常用命令
- 角色数量：1

### 本步输入
- 输入名称：metaso-mcp 服务构建、启动
- 输入介绍：使用远程MCP服务器URL来安装和启动相关 mcp 服务
- 输入示例：
通过命令行安装metaso-mcp：
```bash
claude mcp add -s user -t http search-metaso https://metaso.cn/api/mcp --header "Authorization: Bearer xxx" #将xxx换为API密钥
```
运行以下代码查看是否连接成功：
```bash
claude mcp list

# 注：看到类似"search-metaso: https://metaso.cn/api/mcp (HTTP) - ✓ Connected"则成功
```
- 资源链接：
1. Claude Code GitHub：https://github.com/anthropics/claude-code

### 本步产出
- 输出名称：可用的 metaso 网络搜索 mcp 服务
- 输出介绍：构建和启动 metaso-mcp 服务

### 预估时间
0.5-1 日

## 步骤 5：github、huggingface、arxiv-mcp 服务构建、启动（可选）

### 步骤定义
构建 github-mcp 服务，支持搜索github网站、内容读取能力
构建 huggingface-mcp 服务，支持搜索huggingface网站、内容读取能力
构建 arxiv-mcp 服务，支持搜索arxiv网站、内容读取能力

### 参与人员
- 角色名称：算法/后端工程师
- 技能要求：熟悉 linux 常用命令、python
- 角色数量：1

### 本步输入
- 输入名称：github、huggingface、arxiv-mcp 服务构建、启动（可选）
- 输入介绍：通过安装相关 python 依赖来安装和启动相关 mcp 服务
- 输入示例：
- 创建 requirements.txt 文件：
```bash
# 建议 python 3.10 及以上版本，如 python 3.11

loguru>=0.7.0
python-dotenv>=1.0.0
mcp>=1.0.0
```
- 创建相关服务 python 文件：
[github_server.py]
[hf_server.py]
[arxiv_server.py]
安装依赖并启动：
```bash
pip install -r requirements.txt
python github_server.py
python hf_server.py
python arxiv_server.py

# 注：看到类似"Uvicorn running on http://0.0.0.0:PORT (Press CTRL+C to quit)"则启动成功
```
注册 MCP 服务：
```bash
# arxiv
claude mcp add -s user -t sse paper-arxiv http://127.0.0.1:4002/sse
# github
claude mcp add -s user -t sse code-github http://127.0.0.1:4001/sse
# huggingface
claude mcp add -s user -t sse model-huggingface http://127.0.0.1:4003/sse
```
- 资源链接：
1. mcp-python-sdk GitHub：https://github.com/modelcontextprotocol/python-sdk

### 本步产出
- 输出名称：可用的针对 github、huggingface、arxiv网站的 mcp 服务
- 输出介绍：构建和启动 github、huggingface、arxiv-mcp 服务

### 预估时间
0.5-1 日

## 步骤 6：使用 Claude Code 生成调研报告

### 步骤定义
使用 Claude Code 自动调用前面的几个 MCP 服务来生成调研报告

### 参与人员
- 角色名称：算法工程师
- 技能要求：
1. 熟练使用多种思维链策略，对前沿与流行的开/闭源大模型资源较熟悉，有自己的使用经验、使用总结与心得
2. 熟练掌握NLP经典深度学习模型（如Transformer系、LLaMA系、GLM系等）及相关资源（网站、库、博客等）；掌握至少一种常用深度学习开发框架，如PyTorch等；对GPT-3.5之后的大规模生成式语言模型（大模型）的工作原理和最新消息保持持续关注与兴趣
3. 熟练掌握Python语言，会使用基本的正则表达式和命令行脚本；熟知NLP基础概念及经典任务（分类、匹配、序列标注、生成等）；能熟练运用常见NLP开源库（HanLP、LTP、Jieba等）
4. 态度积极主动，沟通有条理，有好奇心与自驱力
- 角色数量：1 人

### 本步输入
- 输入名称：使用 Claude Code 生成调研报告
- 输入介绍：和 Claude Code 交互确认输入信息来生成调研视频
- 输入示例：
传入已有调研报告模板.md、调研报告生成流程文档 skill.md 和 流程图.md
```python
# 素材要求如下
项目根目录/
├── files/ # 原始素材文件夹
│ └── 调研报告模板.md # 调研报告模板 (必须)
└── skill.md # 调研报告生成流程文档 (必须)
└── 深度研究报告生成全流程.md # 生成调研文档的流程图 (必须)
```
深度研究报告生成全流程.md 文件如下
[深度研究报告生成全流程.md]
skill.md 文件如下
[SKILL.md]
在项目根目录启动 Claude Code 来生成调研报告
```bash
# 启动 claude，请确保项目根目录下除了 files、skill.md、流程图外无其他文件
claude
> 根据 skill.md 生成 Deerflow 的调研报告

# 注：过程中会有研究方向等需要用户确认的选项，后面会自动生成最终调研报告
```

### 本步产出
- 输出名称：调研报告
- 输出介绍：Claude Code 自动生成最终调研报告

### 预估时间
0.5-1 日
