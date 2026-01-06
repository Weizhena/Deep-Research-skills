# Deep Research Skill for Claude Code

[English](README.md) | [中文](README.zh.md)

> 灵感来源：[RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

Claude Code 的结构化调研工作流技能，支持两阶段调研：outline生成（可扩展）和深度调查。人在回路设计确保每个阶段的精确控制。

## 使用场景

- **学术研究**：论文综述、benchmark评测、文献分析
- **技术研究**：技术对比、框架评估、工具选型
- **市场研究**：竞品分析、行业趋势、产品比较
- **尽职调查**：公司研究、投资分析、风险评估

## 安装

```bash
# 中文版
cp -r skills/research-zh ~/.claude/skills/research

# 必需：安装agent
cp agents/web-search-agent.md ~/.claude/agents/
```

## 命令

> **注意**：使用 `run /research` 而非直接 `/research`，因为斜杠命令与内置命令冲突。

| 命令 | 描述 |
|------|------|
| `run /research` | 生成包含items和fields的调研outline |
| `run /research/add-items` | 向现有outline添加更多items |
| `run /research/add-fields` | 向现有outline添加更多fields |
| `run /research/deep` | 使用并行agents对每个item进行深度调研 |
| `run /research/report` | 从JSON结果生成markdown报告 |

## 工作流

### 阶段1：生成Outline
```
run /research <topic>
```
- 模型知识生成初始items和字段框架
- 网络搜索补充最新items
- 用户确认并调整
- 输出：`outline.yaml`（items + 配置）+ `fields.yaml`（字段定义）

### 阶段2：深度调研
```
run /research/deep
```
- 并行agents调研每个item（batch_size可配置）
- 每个agent读取fields.yaml并输出结构化JSON
- 支持断点续传
- 输出：`results/*.json`

### 可选：扩展Outline
```
run /research/add-items    # 通过用户输入或网络搜索添加调研对象
run /research/add-fields   # 添加字段定义
```

### 阶段3：生成报告
```
run /research/report
```
- 生成Python脚本将JSON转换为markdown
- 用户选择目录中显示的摘要字段
- 自动跳过不确定值
- 输出：`report.md`

## 参考文献

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## 许可证

MIT
