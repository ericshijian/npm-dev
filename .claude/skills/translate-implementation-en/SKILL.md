---
name: translate-implementation-en
description: 读取 implementation.zh.json，翻译得到 implementation.en.json。保持 JSON 结构一致。每次处理一条数据。
---

# Translate Implementation En

翻译实施配置 JSON 从中文到英文。

## 数据源

- 目录: `Content/Arena/All Arenas/{arena-folder}/`
- 源文件: `implementation.zh.json`
- 目标文件: `implementation.en.json`（同目录）

## 翻译规则

1. **保持 JSON 结构一致**：phases、subsections 结构不变
2. **翻译所有中文内容**：
   - `phases` 中的 `title` 字段
   - `subsections` 中的 `title` 和 `content` 数组中的文本
3. **术语一致性**：
   - 需求识别与团队构建 -> Requirements Identification and Team Building
   - 价值确认与需求细化 -> Value Confirmation and Requirements Refinement
   - 初步验证与立项 -> Preliminary Verification and Project Initiation
   - 正式上线与优化迭代 -> Official Launch and Iterative Optimization
   - 团队构成 -> Team Composition
   - 实施内容 -> Implementation Content
   - 相关资源 -> Related Resources
   - 结果产出 -> Results/Deliverables
   - 实施周期 -> Implementation Cycle

## 执行步骤

用户调用此 skill 时，我执行以下步骤：

1. 遍历 `Content/Arena/All Arenas/` 下的 arena 目录
2. 找到下一条待处理的记录：
   - 有 `implementation.zh.json` 但没有 `implementation.en.json`，或者
   - `implementation.zh.json` 的修改时间晚于 `implementation.en.json`（中文版已更新）
3. 读取 `implementation.zh.json` 内容
4. 翻译 JSON 中的中文文本值为英文（保持 JSON 结构不变）
5. 校验翻译后的 JSON 结构与源结构一致
6. 写入 `implementation.en.json` 文件
7. 输出处理结果

## 增量更新

通过比较文件修改时间判断是否需要更新：
- 使用 `stat -f %m` (macOS) 或 `stat -c %Y` (Linux) 获取文件修改时间戳
- 如果 `implementation.zh.json` 时间戳 > `implementation.en.json` 时间戳，则需要更新

## 保证

- 只翻译值，不改变 JSON 结构
- 保持 phases 数组和 subsections 数组结构
- 每次只处理一条数据

## 用法

```bash
# 调用 skill 翻译下一条
$translate-implementation-en

# 指定 arena-folder
$translate-implementation-en --folder 1-intelligent-research-system
```
