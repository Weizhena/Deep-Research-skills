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

### Commands

| Command | Description |
|---------|-------------|
| `/research` | Generate research outline with items and fields |
| `/research/add-items` | Add more items to existing outline |
| `/research/add-fields` | Add more fields to existing outline |
| `/research/deep` | Deep research each item with parallel agents |
| `/research/report` | Generate markdown report from JSON results |

### Installation

Choose your language version:

```bash
# English version
cp -r skills/research-en ~/.claude/skills/research

# Chinese version
cp -r skills/research-zh ~/.claude/commands/research
```

### Workflow

#### Phase 1: Generate Outline
```
/research <topic>
```

#### Phase 2: Deep Research
```
/research/deep
```

#### Optional: Expand Outline
```
/research/add-items
/research/add-fields
```

#### Phase 3: Generate Report
```
/research/report
```

---

## 中文

> 灵感来源：[RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

Claude Code 的结构化调研工作流技能，支持两阶段调研：outline生成（可扩展）和深度调查。人在回路设计确保每个阶段的精确控制。

### 使用场景

- **学术研究**：论文综述、benchmark评测、文献分析
- **技术研究**：技术对比、框架评估、工具选型
- **市场研究**：竞品分析、行业趋势、产品比较
- **尽职调查**：公司研究、投资分析、风险评估

### 命令

| 命令 | 描述 |
|------|------|
| `/research` | 生成包含items和fields的调研outline |
| `/research/add-items` | 向现有outline添加更多items |
| `/research/add-fields` | 向现有outline添加更多fields |
| `/research/deep` | 使用并行agents对每个item进行深度调研 |
| `/research/report` | 从JSON结果生成markdown报告 |

### 安装

选择语言版本：

```bash
# 英文版
cp -r skills/research-en ~/.claude/skills/research

# 中文版
cp -r skills/research-zh ~/.claude/commands/research
```

### 工作流

#### 阶段1：生成Outline
```
/research <topic>
```

#### 阶段2：深度调研
```
/research/deep
```

#### 可选：扩展Outline
```
/research/add-items
/research/add-fields
```

#### 阶段3：生成报告
```
/research/report
```

---

## References / 参考文献

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## License / 许可证

MIT
