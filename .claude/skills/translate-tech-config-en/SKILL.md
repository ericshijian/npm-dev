---
name: translate-tech-config-en
description: 读取 tech-configuration.zh.json，翻译得到 tech-configuration.en.json。保持 JSON 结构一致。每次处理一条数据。
---

# Translate Tech Config En

翻译技术配置 JSON 从中文到英文。

## 数据源

- 目录: `Content/Arena/All Arenas/{arena-folder}/`
- 源文件: `tech-configuration.zh.json`
- 目标文件: `tech-configuration.en.json`（同目录）

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. 遍历 `Content/Arena/All Arenas/` 下的 arena 目录
2. 找到下一条待处理的记录：
   - 有 `tech-configuration.zh.json` 但没有 `tech-configuration.en.json`，或者
   - `tech-configuration.zh.json` 的修改时间晚于 `tech-configuration.en.json`（中文版已更新）
3. 读取 `tech-configuration.zh.json` 内容
4. 翻译 JSON 中的中文文本值为英文（保持 JSON 结构不变）
5. 校验翻译后的 JSON 结构与源结构一致
6. 写入 `tech-configuration.en.json` 文件
7. 输出处理结果

## 增量更新

通过比较文件修改时间判断是否需要更新：
- 使用 `stat -f %m` (macOS) 或 `stat -c %Y` (Linux) 获取文件修改时间戳
- 如果 `tech-configuration.zh.json` 时间戳 > `tech-configuration.en.json` 时间戳，则需要更新

## 保证

- 只翻译值，不改变 JSON 结构
- 保持 steps 数组和 subsections 数组结构
- 每次只处理一条数据

## 用法

```bash
# 调用 skill 翻译下一条
$translate-tech-config-en

# 指定 arena-folder
$translate-tech-config-en --folder 1-intelligent-research-system
```
