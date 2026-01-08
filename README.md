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
cp -r skills/research-en/* ~/.claude/skills/

# Chinese version
cp -r skills/research-zh/* ~/.claude/skills/

# Required: Install agent
cp agents/web-search-agent.md ~/.claude/agents/

# Required: Install Python dependency
pip install pyyaml
```

## Commands

> **Claude Code 2.1.0+**: Direct `/skill-name` trigger is now supported!
>
> **Older versions**: Use `run /skill-name` format instead.

| Command (2.1.0+) | Description |
|------------------|-------------|
| `/research` | Generate research outline with items and fields |
| `/research-add-items` | Add more items to existing outline |
| `/research-add-fields` | Add more fields to existing outline |
| `/research-deep` | Deep research each item with parallel agents |
| `/research-report` | Generate markdown report from JSON results |

## Workflow & Example

> **Example**: Researching "AI Agent Demo 2025"

### Phase 1: Generate Outline
```
/research AI Agent Demo 2025
```
💡 **What happens**: Tell it your topic → It creates a research list for you

**You get**: A list of 17 AI Agents to research (ChatGPT Agent, Claude Computer Use, Cursor, etc.) + what info to collect for each

### Phase 2: Deep Research
```
/research-deep
```
💡 **What happens**: AI automatically searches the web for each item, one by one

**You get**: Detailed info for each Agent (company, release date, pricing, tech specs, reviews...)

### Phase 3: Generate Report
```
/research-report
```
💡 **What happens**: All data → One organized report

**You get**: `report.md` - A complete markdown report with table of contents, ready to read or share

## Need Help?

If you have questions, ask Claude Code to explain this project:
```
Help me understand this project: https://github.com/Weizhena/deep-research-skills
```

## References

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## License

MIT
