# Deep Research Skill for Claude Code / OpenCode / Codex / Autohand Code

[English](README.md) | [中文](README.zh.md)

> 如果喜欢就请 star 一下吧！:star:

> 灵感来源：[RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context](https://arxiv.org/abs/2511.18743)

适用于 Claude Code、OpenCode、Codex 和 Autohand Code 的结构化调研工作流技能，支持两阶段调研：outline生成（可扩展）和深度调查。人在回路设计确保每个阶段的精确控制。

![Deep Research Skills 工作流](workflow.png)

## 使用场景

- **学术研究**：论文综述、benchmark评测、文献分析
- **技术研究**：技术对比、框架评估、工具选型
- **市场研究**：竞品分析、行业趋势、产品比较
- **尽职调查**：公司研究、投资分析、风险评估

## 安装

```bash
git clone https://github.com/Weizhena/deep-research-skills.git
cd deep-research-skills
```

### Claude Code
```bash
# 中文版
cp -r skills/research-zh/* ~/.claude/skills/

# 英文版
cp -r skills/research-en/* ~/.claude/skills/

# 必需：安装agent和模块
cp agents/web-search-agent.md ~/.claude/agents/
cp -r agents/web-search-modules ~/.claude/agents/

# 必需：安装Python依赖
pip install pyyaml
```

### OpenCode (默认: gpt-5.4)
```bash
# Skills (同 Claude Code)
cp -r skills/research-zh/* ~/.claude/skills/   # 或 research-en 英文版

# 必需：为当前 shell 启用 web search
export OPENCODE_ENABLE_EXA=1

# 可选：写入 ~/.bashrc，永久生效
echo 'export OPENCODE_ENABLE_EXA=1' >> ~/.bashrc
source ~/.bashrc

# 必需：安装agent和模块
cp agents/web-search-opencode.md ~/.config/opencode/agents/web-search.md
cp -r agents/web-search-modules ~/.config/opencode/agents/

# 必需：安装Python依赖
pip install pyyaml
```

> **重要**：在 OpenCode 中，任何模型要想使用 `websearch`，需要设置 `OPENCODE_ENABLE_EXA=1`。单纯 `export` 只对当前 shell 生效；写入 `~/.bashrc` 后才是永久生效。不设置时，只有 `web fetch`，对深度调研阶段会弱很多。

### Autohand Code

从 Autohand Community Skills registry 安装：

```text
$skill-installer deep-research-skills
```

这个 registry 条目会把本项目的 deep research 工作流适配到 Autohand Code，用户无需 clone 本仓库即可按名称安装。

### Codex
```bash
# 英文版
mkdir -p ~/.codex/skills ~/.codex/agents
cp -r skills/research-codex-en/* ~/.codex/skills/

# 中文版
mkdir -p ~/.codex/skills ~/.codex/agents
cp -r skills/research-codex-zh/* ~/.codex/skills/

# 必需：安装 web researcher agent 和模块
cp agents-codex/web-researcher.toml ~/.codex/agents/
cp -r agents-codex/web-search-modules ~/.codex/agents/

# 必需：安装 Python 依赖
pip install pyyaml
```

使用以下两种方式之一更新 `~/.codex/config.toml`：

**方式 A：自动脚本**

```bash
cd deep-research-skills
bash scripts/install-codex.sh
```

**方式 B：手动编辑**

```toml
suppress_unstable_features_warning = true

[features]
multi_agent = true
default_mode_request_user_input = true

[agents.web_researcher]
description = "Use this agent when you need to research information on the internet, particularly for debugging issues, finding solutions to technical problems, or gathering comprehensive information from multiple sources. This agent excels at finding relevant discussions. Use when you need creative search strategies, thorough investigation, or compilation of findings from multiple sources."
config_file = "agents/web-researcher.toml"
```

## 命令

> **Claude Code 2.1.0+**：现已支持直接 `/skill-name` 触发！
>
> **旧版本**：请使用 `run /skill-name` 格式。
>
> **Autohand Code**：使用 `$skill-installer deep-research-skills` 安装后，可以用自然语言要求生成 deep research outline、补充 items/fields、执行 deep research 或生成最终报告。
>
> **Codex**：可以通过 `/skills` -> `List Skills` 选择这些 skills，也可以用自然语言触发，例如 `Use the research skill to build an outline for AI Agent Demo 2025`。

| 命令 (2.1.0+) | 描述 |
|---------------|------|
| `/research` | 生成包含items和fields的调研outline |
| `/research-add-items` | 向现有outline添加更多调研对象 |
| `/research-add-fields` | 向现有outline添加更多字段定义 |
| `/research-deep` | 使用并行agents对每个item进行深度调研 |
| `/research-report` | 从JSON结果生成markdown报告 |

## 工作流 & 示例

> **示例**：调研 "AI Agent Demo 2025"

### 阶段1：生成Outline
```
/research AI Agent Demo 2025
```
💡 **会发生什么**：告诉它你要研究什么 → 它帮你列出调研清单

对于 Codex，可以这样说：
```
Use the research skill to build an outline for AI Agent Demo 2025
```

**你会得到**：17个待调研的AI Agent清单（ChatGPT Agent、Claude Computer Use、Cursor等）+ 每个要收集哪些信息

### （可选）不满意？继续添加
```
/research-add-items
/research-add-fields
```
💡 **会发生什么**：补充更多调研对象或字段定义

### 阶段2：深度调研
```
/research-deep
```
💡 **会发生什么**：AI自动上网搜索每个item的详细信息，逐个完成

**你会得到**：每个Agent的详细资料（公司、发布日期、定价、技术规格、用户评价...）

### 阶段3：生成报告
```
/research-report
```
💡 **会发生什么**：所有数据 → 一份整理好的报告

**你会得到**：`report.md` - 带目录的完整Markdown报告，可直接阅读或分享

## 遇到问题？

如果过程中有什么不懂的，可以让 Claude Code、OpenCode 或 Codex 帮你理解这个项目：
```
帮我理解这个项目: https://github.com/Weizhena/deep-research-skills
```

## 参考文献

- RhinoInsight: Improving Deep Research through Control Mechanisms for Model Behavior and Context

## 许可证

MIT
