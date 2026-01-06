# Deep Research Skill for Claude Code

[English](#english) | [中文](#中文)

---

## English

> Inspired by [RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

A structured research workflow skill for Claude Code, supporting two-phase research: outline generation (extensible) and deep investigation. Human-in-the-loop design ensures precise control at every stage.

### Use Cases

- **Academic Research**: Paper surveys, benchmark reviews, literature analysis
- **Technical Research**: Technology comparison, framework evaluation, tool selection
- **Market Research**: Competitor analysis, industry trends, product comparison
- **Due Diligence**: Company research, investment analysis, risk assessment


### Installation

Choose your language version:

```bash
# English version
cp -r skills/research-en ~/.claude/skills/research

# Chinese version
cp -r skills/research-zh ~/.claude/commands/research

# Required: Install agent
cp agents/web-search-agent.md ~/.claude/agents/
```
### Commands

> **Note**: Use `run /research` instead of `/research` directly, as slash commands conflict with built-in commands.

### Workflow

#### Phase 1: Generate Outline
```
run /research <topic>
```
- Model knowledge generates initial items and field framework
- Web search supplements latest items
- User confirms and adjusts
- Outputs: `outline.yaml` (items + config) + `fields.yaml` (field definitions)

#### Phase 2: Deep Research
```
run /research/deep
```
- Parallel agents research each item (batch_size configurable)
- Each agent reads fields.yaml and outputs structured JSON
- Supports checkpoint resume
- Outputs: `results/*.json`

#### Optional: Expand Outline
```
run /research/add-items    # Add research targets via user input or web search
run /research/add-fields   # Add field definitions
```

#### Phase 3: Generate Report
```
run /research/report
```
- Generates Python script to convert JSON to markdown
- User selects summary fields for TOC
- Skips uncertain values automatically
- Outputs: `report.md`

---

## 中文

> 灵感来源：[RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

Claude Code 的结构化调研工作流技能，支持两阶段调研：outline生成（可扩展）和深度调查。人在回路设计确保每个阶段的精确控制。

### 使用场景

- **学术研究**：论文综述、benchmark评测、文献分析
- **技术研究**：技术对比、框架评估、工具选型
- **市场研究**：竞品分析、行业趋势、产品比较
- **尽职调查**：公司研究、投资分析、风险评估



### 安装

选择语言版本：

```bash
# 英文版
cp -r skills/research-en ~/.claude/skills/research

# 中文版
cp -r skills/research-zh ~/.claude/skills/research

# 必需：安装agent
cp agents/web-search-agent.md ~/.claude/agents/
```
### 命令

> **注意**：使用 `run /research` 而非直接 `/research`，因为斜杠命令与内置命令冲突。

### 工作流

#### 阶段1：生成Outline
```
run /research <topic>
```
- 模型知识生成初始items和字段框架
- 网络搜索补充最新items
- 用户确认并调整
- 输出：`outline.yaml`（items + 配置）+ `fields.yaml`（字段定义）

#### 阶段2：深度调研
```
run /research/deep
```
- 并行agents调研每个item（batch_size可配置）
- 每个agent读取fields.yaml并输出结构化JSON
- 支持断点续传
- 输出：`results/*.json`

#### 可选：扩展Outline
```
run /research/add-items    # 通过用户输入或网络搜索添加调研对象
run /research/add-fields   # 添加字段定义
```

#### 阶段3：生成报告
```
run /research/report
```
- 生成Python脚本将JSON转换为markdown
- 用户选择目录中显示的摘要字段
- 自动跳过不确定值
- 输出：`report.md`

---

## References / 参考文献

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## License / 许可证

MIT
