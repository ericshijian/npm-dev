# 技术配置（原始提取）

## 步骤 1：Claude Code 安装和配置

### 步骤定义
通过 Node 安装和配置 Claude Code

### 参与人员
- 角色名称：前端工程师/后端/算法工程师
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

## 步骤 2：PRD 生成

### 步骤定义
通过 Claude Code 生成网站 PRD

### 参与人员
- 角色名称：产品经理
- 技能要求：具备产品、建站相关知识，熟悉 markdown 格式
- 角色数量：1

### 本步输入
- 输入名称：通过 Claude Code 生成网站 PRD
- 输入介绍：和 Claude Code 进行一次或多次交互来生成 markdown 格式的 PRD 文件
- 输入示例：
相关命令如下：
```bash
# 把已有材料放到项目根目录，然后启动 Claude Code
claude
> 根据已有材料生成网站的prd，保存为md文件

# 对生成的prd不满意可以继续对话，对应md文件大模型修改后会实时更新，直到符合要求
```
- 资源链接：
1. Claude Code GitHub：https://github.com/anthropics/claude-code

### 本步产出
- 输出名称：PRD 文件
- 输出介绍：符合要求的 markdown 格式的 PRD 文件

### 预估时间
0.5-1 日

## 步骤 3：网站生成

### 步骤定义
通过 Lovable 生成最终网站

### 参与人员
- 角色名称：产品经理
- 技能要求：具备产品、建站相关知识
- 角色数量：1

### 本步输入
- 输入名称：通过 Lovable 生成最终网站
- 输入介绍：基于 Claude Code 生成的 PRD，和 Lovable 交互生成最终网站
- 输入示例：
相关操作如下：访问 https://lovable.dev/，点击左下角的 Attach 上传 PRD 文件，简单描述建站需求，如"根据当前 PRD 来建站实现 XXX 网站的全部功能（含交互）"，对细节等地方不满意，也可以对话继续优化
- 资源链接：
1. Lovable：https://lovable.dev/

### 本步产出
- 输出名称：网站原型链接
- 输出介绍：可互联网公开访问的网站原型链接

### 预估时间
0.5-1 日
