# Claude Code Skill Pack

这是一套给 Claude Code 用的本地 Logseq 配置包。它不是 MCP，也不是 server，而是基于 Claude Code 官方支持的两种机制:

- `~/.claude/CLAUDE.md`
- `~/.claude/commands/*.md`

它的目标是让 Claude Code 在需要你的历史知识时，优先通过 `logseq-cli` 检索本地 Logseq graph，而不是直接猜测或粗暴扫描整个笔记目录。

## 包含内容

- 用户级 memory 片段:
  - [integrations/claude/CLAUDE.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/CLAUDE.md)
- 用户级 slash commands:
  - [logseq-status.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-status.md)
  - [logseq-kb.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-kb.md)
  - [logseq-daily.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-daily.md)
  - [logseq-project.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-project.md)
  - [logseq-topic.md](/Users/yiyi/program/llm/logseq-cli/integrations/claude/commands/logseq-topic.md)
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

## 可用命令

- `/logseq-status`
  - 检查默认 graph 是否可用
- `/logseq-kb <topic>`
  - 拉取某个主题或项目的定向上下文
- `/logseq-daily [YYYY-MM-DD]`
  - 生成日报和当前重点
- `/logseq-project <project>`
  - 生成项目简报
- `/logseq-topic <topic>`
  - 汇总某个主题、tag 或 recurring pattern
- `/logseq-capture <note>`
  - 把结论或任务保守地写回 Logseq
- `/logseq-next [YYYY-MM-DD]`
  - 从 journal 和 tasks 推出下一步行动

## 设计原则

- 默认走 `logseq-cli --json`
- 默认只做小范围检索
- 默认不直接扫描整个 Logseq graph
- 默认不直接写入，除非你显式要求 capture
- 回答时区分“来自 Logseq 的事实”和“模型的推断”

