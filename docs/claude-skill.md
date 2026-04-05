# Claude Code Skill Pack

这是一套给 Claude Code 用的本地 Logseq 配置包。它不是 MCP，也不是 server，而是基于 Claude Code 官方支持的三种机制:

- `~/.claude/skills/<skill-name>/SKILL.md`
- `~/.claude/CLAUDE.md`
- `~/.claude/commands/*.md`

它的目标是让 Claude Code 在需要你的历史知识时，优先通过 `logseq-cli` 检索本地 Logseq graph，而不是直接猜测或粗暴扫描整个笔记目录。

## 包含内容

- Claude Skill:
  - [SKILL.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/skills/logseq-kb/SKILL.md)
  - [commands.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/skills/logseq-kb/references/commands.md)
- 用户级 memory 片段:
  - [integrations/claude/CLAUDE.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/CLAUDE.md)
- 用户级 slash commands:
  - [logseq-status.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-status.md)
  - [logseq-kb.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-kb.md)
  - [logseq-daily.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-daily.md)
  - [logseq-weekly.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-weekly.md)
  - [logseq-project.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-project.md)
  - [logseq-topic.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-topic.md)
  - [logseq-decisions.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-decisions.md)
  - [logseq-lessons.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-lessons.md)
  - [logseq-capture.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-capture.md)
  - [logseq-next.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-next.md)
- 安装脚本:
  - [install_claude_skill.sh](/Users/yiyi/program/llm/logseq-cli/scripts/install_claude_skill.sh)

## 安装

先保证 `logseq-cli` 已经安装，并且命令可用。

然后执行:

```bash
chmod +x scripts/install_claude_skill.sh
./scripts/install_claude_skill.sh
```

再设置默认 graph:

```bash
logseq-cli graph use --graph ~/Documents/Logseq
```

完成后，重启 Claude Code 或开一个新会话。

你可以在 Claude Code 里直接确认 Skill 是否已加载:

```text
What Skills are available?
```

## 可用命令

- `/logseq-status`
  - 检查默认 graph 是否可用
- `/logseq-kb <topic>`
  - 拉取某个主题或项目的定向上下文
- `/logseq-daily [YYYY-MM-DD]`
  - 生成日报和当前重点
- `/logseq-weekly [YYYY-MM-DD]`
  - 生成周视角卡片和 weekly brief
- `/logseq-project <project>`
  - 生成项目简报
- `/logseq-topic <topic>`
  - 汇总某个主题、tag 或 recurring pattern
- `/logseq-decisions <topic>`
  - 提取决策和原因
- `/logseq-lessons <topic>`
  - 提取经验、踩坑和最佳实践
- `/logseq-capture <note>`
  - 把结论或任务保守地写回 Logseq
- `/logseq-next [YYYY-MM-DD]`
  - 从 journal 和 tasks 推出下一步行动

## 设计原则

- 官方 Skill 负责自动触发
- 默认走 `logseq-cli --json`
- 默认只做小范围检索
- 默认不直接扫描整个 Logseq graph
- 默认不直接写入，除非你显式要求 capture
- 回答时区分“来自 Logseq 的事实”和“模型的推断”

## 官方参考

- Claude Code Agent Skills: [docs.claude.com/en/docs/claude-code/skills](https://docs.claude.com/en/docs/claude-code/skills)
- Claude Code Slash Commands: [docs.claude.com/en/docs/claude-code/slash-commands](https://docs.claude.com/en/docs/claude-code/slash-commands)
- Claude Code Memory: [code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)
