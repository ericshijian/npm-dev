# 技术配置（原始提取）

## 步骤 1：安装 docker

### 步骤定义
docker（含docker-compose）的安装

### 参与人员
- 角色名称：后端工程师
- 技能要求：熟悉 docker 安装、使用
- 角色数量：1

### 本步输入
- 输入名称：在 Ubuntu 系列操作系统（Ubuntu-22.04 等）中安装 docker
- 输入介绍：首先确保开通一台云服务器，确保服务器资源满足“CPU ≥8 核、内存 ≥ 32GB”，操作系统选择Ubuntu。在服务器正常运行的情况下，通过命令行操作完成docker的安装
- 输入示例：
命令行安装语句如下：
```bash
# 安装相关命令
sudo apt update
sudo apt install docker.io
sudo apt install docker-compose -y

# 安装是否成功确认相关命令，两个命令都输出版本号则安装成功
docker -v
docker-compose --version
```
- 资源链接：
1. docker Docs：https://docs.docker.com/

### 本步产出
- 输出名称：可运行的 docker 服务
- 输出介绍：通过docker能够便捷安装本方案所需的毕昇框架及相关服务，因此首先确保正确安装了docker

### 预估时间
0.25-0.5 日

## 步骤 2：部署毕昇平台

### 步骤定义
通过docker部署毕昇平台

### 参与人员
- 角色名称：后端/算法工程师
- 技能要求：熟悉 docker，掌握常见智能体平台（如毕昇、Dify 等）的私有化部署
- 角色数量：1

### 本步输入
- 输入名称：通过docker拉取毕昇镜像
- 输入介绍：先从Github网站下载毕昇的项目文件，里面包含 docker的配置文件，运行该项目文件后，会从毕昇的docker仓库拉取本方案的docker镜像并启动服务
- 输入示例：
命令行下载项目文件并启动服务的语句如下：
```bash
# 下载代码
git clone https://github.com/dataelement/bisheng.git

# 启动服务
cd bisheng/docker
docker compose -f docker-compose.yml -p bisheng up -d

# 启动成功确认命令，确认是否 10 个相关服务都都是 Up 状态
docker ps | grep bisheng

# 启动后，在浏览器中访问 http://IP:3001 ，出现登录页，进行用户注册，默认第一个注册的用户会成为系统 admin
```
- 资源链接：
1. 毕昇（Bisheng）项目文件 Github：https://github.com/dataelement/bisheng

### 本步产出
- 输出名称：可用的毕昇平台服务
- 输出介绍：运行毕昇平台服务后，可通过该平台构建生产级别的智能体工作流

### 预估时间
1-2.5 日

## 步骤 3：导入本方案工作流

### 步骤定义
下载本方案在毕昇平台构建的现成的工作流 json文件，导入到已运行的毕昇平台

### 参与人员
- 角色名称：产品经理/后端/算法工程师
- 技能要求：能熟练使用常见的低代码（“拖拉拽”方式）构建智能体工作流平台（如毕昇、Dify等）
- 角色数量：1

### 本步输入
- 输入名称：毕昇工作流json文件
- 输入介绍：在毕昇平台新建一个空白工作流，并在其中导入准备好的 json 文件
- 输入示例：
以下是该json文件的样例：
[01-脑筋急转弯互动版.json]
- 资源链接：
毕昇社区-工作流精选（最后一行，作者为zh）：手搓100个Workflow【活动】

### 本步产出
- 输出名称：一个待运行的脑筋急转弯应用（智能体工作流）
- 输出介绍：该应用即满足本方案的目标，并支持版本管理、发布、 API调用等功能

### 预估时间
1 小时

## 步骤 4：配置大模型

### 步骤定义
在毕昇平台配置常见大模型，来支持平台上各个应用（工作流、智能体等）的调用

### 参与人员
- 角色名称：后端/算法工程师
- 技能要求：掌握常见智能体平台（如毕昇、Dify 等）的大模型配置
- 角色数量：1

### 本步输入
- 输入名称：所用大模型API的key和base url
- 输入介绍：在“毕昇平台模型→模型管理界面”配置大模型API相关信息，并设置默认的系统模型，该步骤推荐基于硅基流动平台的大模型API
- 输入示例：
key：通常格式为sk-xxxxxx
base url：格式实例如https://api.openai.com/v1
- 资源链接：
1. 硅基流动官网大模型页面：https://cloud.siliconflow.cn/me/models

### 本步产出
- 输出名称：配置好的大模型
- 输出介绍：整个毕昇平台各应用都可用的配置好的大模型，后续应用使用已有模型无需重复配置

### 预估时间
2 小时

## 步骤 5：通过页面试用工作流

### 步骤定义
大模型配置完成后，在毕昇平台找到之前配置的应用，点击运行即可试用工作流。作为拓展尝试，也推荐阅读毕昇官方的工作流搭建教程，这样可以自己调整/搭建工作流，方便进行个性化改造

### 参与人员
- 角色名称：产品经理/后端/算法工程师
- 技能要求：熟悉常见智能体平台（如毕昇、Dify 等）的使用
- 角色数量：1

### 本步输入
- 输入名称：工作流使用选项和交互
- 输入介绍：选择脑筋急转弯类型，开始作答等使用交互
- 输入示例：如选择“反常规思维类”并开始作答，输入答案后将返回正确性，并支持继续作答/质疑问题/要答案等
- 资源链接：
毕昇官方搭建工作流教程：BISHENG workflow

### 本步产出
- 输出名称：一个可运行的脑筋急转弯应用
- 输出介绍：试用通过后，可以直接发布上线

### 预估时间
0.5 - 1.5 日

## 步骤 6：通过API调用工作流

### 步骤定义
结合具体业务场景，将脑筋急转弯工作流通过毕昇的API接入原有流程

### 参与人员
- 角色名称：后端/算法工程师
- 技能要求：掌握至少一门后端语言（如 Python、Java、Go 等），熟悉基于HTTP的API服务的封装
- 角色数量：1

### 本步输入
- 输入名称：工作流发布后的url和workflow_id
- 输入介绍：一般在对外发布-API 访问页面也会直接给出，然后通过python/java等发起 http 请求来调用工作流
- 输入示例：
python版本的API 代码调用示例如下：
```python
# -*- coding: utf-8 -*-
import json

import requests

url = "http://IP:3001/api/v2/workflow/invoke"
# 从应用的地址栏获取
workflow_id = "xxxxxx"


def get_workflow_output_message(query: str) -> str:
"""
调用工作流，自动完成两次请求，并返回最终的输出内容（message 字段）
:param query: 用户输入
:return: 模型返回的文本内容（message 字段）
"""
headers = {'Content-Type': 'application/json'}

# 第一次请求，初始化工作流
init_payload = json.dumps({
"workflow_id": workflow_id,
"stream": False,
})
init_response = requests.post(url, headers=headers, data=init_payload)
init_data = init_response.json()

if init_response.status_code != 200 or init_data.get("status_code") != 200:
raise Exception("初始化请求失败:\n" + json.dumps(init_data, indent=2, ensure_ascii=False))

session_id = init_data["data"]["session_id"]

input_node_id = None
message_id = None
for event in init_data["data"]["events"]:
if event["event"] == "input":
input_node_id = event["node_id"]
message_id = event["message_id"]
break

if not input_node_id or not message_id:
raise Exception("未能找到 input 节点或 message_id")

# 第二次请求，传入 query
second_payload = json.dumps({
"workflow_id": workflow_id,
"stream": False,
"input": {
input_node_id: {
"user_input": query
}
},
"message_id": message_id,
"session_id": session_id
})
second_response = requests.post(url, headers=headers, data=second_payload)
second_data = second_response.json()

print(f'second_data: \n{second_data}')

if second_response.status_code != 200 or second_data.get("status_code") != 200:
raise Exception("传入 query 请求失败:\n" + json.dumps(second_data, indent=2, ensure_ascii=False))

# 提取最终输出 message 内容
for event in second_data["data"]["events"]:
if event["event"] == "output_msg" and "output_schema" in event:
return event["output_schema"].get("message", "")

raise Exception("未找到 output_msg 类型的事件")


def run():
query = "xxxxxx"
print(f"query: {query}\n")
result = get_workflow_output_message(query)
print(f"result: \n{result}")


# 示例调用
if __name__ == "__main__":
run()
```
- 资源链接：
毕昇官方对外发布工作流的API教程：工作流对外发布 API

### 本步产出
- 输出名称：基于本方案工作流的独立的API 服务
- 输出介绍：可以灵活地嵌入相关业务系统

### 预估时间
0.25-0.5 日
