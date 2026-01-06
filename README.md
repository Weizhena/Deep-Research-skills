# Deep Research Skill for Claude Code

[English](README.md) | [中文](README.zh.md)

> Inspired by [RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

A structured research workflow skill for Claude Code, supporting two-phase research: outline generation (extensible) and deep investigation. Human-in-the-loop design ensures precise control at every stage.

## Use Cases

- **Academic Research**: Paper surveys, benchmark reviews, literature analysis
- **Technical Research**: Technology comparison, framework evaluation, tool selection
- **Market Research**: Competitor analysis, industry trends, product comparison
- **Due Diligence**: Company research, investment analysis, risk assessment

## Installation

```bash
# English version
cp -r skills/research-en ~/.claude/skills/research

# Required: Install agent
cp agents/web-search-agent.md ~/.claude/agents/
```

## Commands

> **Note**: Use `run /research` instead of `/research` directly, as slash commands conflict with built-in commands.

| Command | Description |
|---------|-------------|
| `run /research` | Generate research outline with items and fields |
| `run /research/add-items` | Add more items to existing outline |
| `run /research/add-fields` | Add more fields to existing outline |
| `run /research/deep` | Deep research each item with parallel agents |
| `run /research/report` | Generate markdown report from JSON results |

## Workflow

### Phase 1: Generate Outline
```
run /research <topic>
```
- Model knowledge generates initial items and field framework
- Web search supplements latest items
- User confirms and adjusts
- Outputs: `outline.yaml` (items + config) + `fields.yaml` (field definitions)

### Phase 2: Deep Research
```
run /research/deep
```
- Parallel agents research each item (batch_size configurable)
- Each agent reads fields.yaml and outputs structured JSON
- Supports checkpoint resume
- Outputs: `results/*.json`

### Optional: Expand Outline
```
run /research/add-items    # Add research targets via user input or web search
run /research/add-fields   # Add field definitions
```

### Phase 3: Generate Report
```
run /research/report
```
- Generates Python script to convert JSON to markdown
- User selects summary fields for TOC
- Skips uncertain values automatically
- Outputs: `report.md`

## References

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## License

MIT
