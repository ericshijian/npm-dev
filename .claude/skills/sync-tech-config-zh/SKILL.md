---
name: sync-tech-config-zh
description: 从 Original Documents/implementation-details.md 读取技术步骤部分，生成 tech-configuration.zh.json 文件到对应 arena 目录。每次处理一条数据。
---

# Sync Tech Config Zh

从 Original Documents/implementation-details.md 提取技术步骤，生成中文 JSON 配置文件。

## 数据源

- 目录: `Content/Arena/All Arenas/{arena-folder}/`
- 文件: `Original Documents/implementation-details.md`
- 目标: `tech-configuration.zh.json`（同目录）

## JSON 结构

```json
{
  "steps": [
    {
      "number": 1,
      "title": "步骤名称",
      "subsections": [
        {"title": "步骤定义", "content": ["..."]},
        {"title": "参与人员", "content": ["..."]},
        {"title": "本步输入", "content": ["..."]},
        {"title": "本步产出", "content": ["..."]},
        {"title": "预估时间", "content": ["..."]}
      ]
    }
  ]
}
```

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. 遍历 `Content/Arena/All Arenas/` 下的 arena 目录
2. 找到下一条待处理的记录：
   - 没有 `tech-configuration.zh.json` 文件，或者
   - `Original Documents/implementation-details.md` 的修改时间晚于 `tech-configuration.zh.json`（源文件已更新）
3. 读取 `Original Documents/implementation-details.md` 文件
4. 定位 "3\. **技术步骤**" 部分
5. 解析每个技术步骤表格，提取：
   - 步骤序号
   - 步骤名称
   - 步骤定义
   - 参与人员
   - 本步输入
   - 本步产出
   - 预估时间
6. 构建 JSON 结构
7. 写入 `tech-configuration.zh.json` 文件
8. 输出处理结果

## 增量更新

通过比较文件修改时间判断是否需要更新：
- 使用 `stat -f %m` (macOS) 或 `stat -c %Y` (Linux) 获取文件修改时间戳
- 如果 `Original Documents/implementation-details.md` 时间戳 > `tech-configuration.zh.json` 时间戳，则需要更新

## 用法

```bash
# 调用 skill 处理下一条
$sync-tech-config-zh

# 指定 arena-folder
$sync-tech-config-zh --folder 1-intelligent-research-system
```
