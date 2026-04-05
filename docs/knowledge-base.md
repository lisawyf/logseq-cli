# 用本地 Logseq 作为大模型知识库

这份文档说明如何把你的本地 Logseq graph 作为个人知识库，接给 Claude Code 或其他能调用本地命令的大模型工具，同时保持当前项目的约束:

- 只走本地文件
- 不增加 MCP
- 不增加 HTTP server
- 不增加 daemon
- 不暴露任何网络接口

核心思路不是“把整个 Logseq 都塞给模型”，而是把 `logseq-cli` 当成一个本地、可审计、可复用的检索和写入边界。模型需要上下文时，先调用 CLI，再基于返回结果工作。

## 推荐架构

推荐你按下面的优先级落地。

### 方案 A: 最实用, 先把 `logseq-cli` 作为本地检索层

这是当前最稳妥的做法。

流程:

1. 大模型收到你的任务。
2. 它先用 `logseq-cli` 检索与你问题相关的 pages, journals, tasks, summaries。
3. 它只把命中的少量结果放进当前上下文。
4. 它完成分析、计划、总结或写作。
5. 需要落回 Logseq 时，再显式调用 `capture` / `journal append` / `page append`。

优点:

- 不需要改 Logseq 本体
- 不需要维护常驻服务
- 输出是稳定 JSON，适合 agent 消费
- 读写边界清晰，风险低
- 能在任何目录工作，只要先 `graph use`

### 方案 B: 给 Claude Code 增加固定工作流

这一步是在方案 A 的基础上，加上 Claude Code 的记忆和 slash commands，让它更稳定地“先查知识库，再回答”。

适用场景:

- 你经常问“我之前做过什么”
- 你希望 Claude Code 在做计划、写周报、分析项目时，优先参考 Logseq
- 你希望它把会议结论、任务和 project note 回写到 Logseq

### 方案 C: 给其他模型或你自己的脚本做一个本地适配层

如果目标工具不能像 Claude Code 一样直接跑本地命令，就用一个很薄的适配层:

- 你的脚本调用 `logseq-cli ... --json`
- 脚本把 JSON 结果裁剪成摘要
- 再把裁剪后的内容送给模型

这样仍然不需要 MCP 或服务端。

## 为什么不要直接把整个 Logseq 丢给模型

不建议默认把整个 graph 作为上下文，原因很直接:

- token 成本高
- 噪音很大，模型容易抓错重点
- 隐私暴露面更大
- journals 天生包含大量低信号内容
- 你很难控制“本次任务到底参考了哪些知识”

更好的做法是按任务类型选择命令:

- 找事实: `page read`, `journal read`
- 找线索: `search text`, `search links`, `search tags`
- 找行动项: `tasks list`
- 找聚合结论: `summarize daily`, `summarize weekly`, `summarize project`, `summarize topic`
- 写回结果: `capture quick`, `capture task`, `capture project`

## 先完成的基础配置

先在你的机器上安装 CLI，然后设置默认 graph。

```bash
python3 -m pip install dist/logseq_cli-0.2.0-py3-none-any.whl
logseq-cli graph use --graph ~/Documents/Logseq
```

设置后，默认 graph 会写入:

```text
~/.config/logseq-cli/config.toml
```

例如:

```toml
default_graph = "/Users/you/Documents/Logseq"
```

之后你不在 Logseq 目录里，也可以直接运行:

```bash
logseq-cli search text "OpenClaw" --json
logseq-cli summarize project "OpenClaw" --json
logseq-cli tasks list --state todo,doing --json
```

## Claude Code 的推荐接法

Claude Code 最适合的接法，不是让它直接读整个 Logseq 目录，而是让它在需要时调用 `logseq-cli`。

### 第一步: 给 Claude Code 一条稳定规则

在:

```text
~/.claude/CLAUDE.md
```

加入类似下面的个人规则:

```md
# Personal Knowledge Base

- My Logseq knowledge base is available through `logseq-cli`.
- Before answering questions about my past work, projects, journals, tasks, plans, decisions, or notes, query Logseq first instead of guessing.
- Prefer structured commands with `--json`.
- Prefer small targeted retrieval:
  - `search text`
  - `search links`
  - `search tags`
  - `tasks list`
  - `summarize daily`
  - `summarize weekly`
  - `summarize project`
  - `summarize topic`
  - `page read`
  - `journal read`
- For writes, ask before using:
  - `capture quick`
  - `capture task`
  - `capture project`
  - `journal append`
  - `page append`
```

这条规则的作用是:

- 让 Claude Code 把 Logseq 当成“先查再说”的知识源
- 避免它凭空脑补你的历史上下文
- 避免一次性把太多无关笔记塞进当前会话

### 第二步: 给 Claude Code 几个高频 slash commands

Anthropic 官方文档支持把自定义 slash commands 放在:

```text
~/.claude/commands/
```

推荐你至少建 3 个。

如果你只想让 Claude Code 通过 `logseq-cli` 间接访问知识库，这一步已经够了，不需要把 Logseq 目录本身暴露给 Claude Code。

#### 1. `/kb`

文件:

```text
~/.claude/commands/kb.md
```

内容示例:

```md
---
description: Pull targeted context from my local Logseq knowledge base
argument-hint: [topic or project]
---

先用我的本地 Logseq 知识库查询与 "$ARGUMENTS" 相关的上下文。

请优先运行这些命令并阅读结果:
- `logseq-cli search text "$ARGUMENTS" --json`
- `logseq-cli search links "$ARGUMENTS" --json`
- `logseq-cli search tags "$ARGUMENTS" --json`
- `logseq-cli summarize topic "$ARGUMENTS" --json`

如果它明显是一个项目名，再额外运行:
- `logseq-cli summarize project "$ARGUMENTS" --json`

然后输出:
1. 与该主题最相关的历史事实
2. 相关 pages / journals
3. 仍然打开的 tasks
4. 对当前问题真正有用的 5 条以内上下文
```

用途:

- 问某个主题前先拉上下文
- 做方案、写代码、写周报前先回忆历史

#### 2. `/daily-brief`

文件:

```text
~/.claude/commands/daily-brief.md
```

内容示例:

```md
---
description: Build a daily work brief from my Logseq journal
argument-hint: [date: optional]
---

如果没有参数，默认今天。

请先查询:
- `logseq-cli summarize daily --today --json`
- `logseq-cli tasks list --state todo,doing,now,later,waiting --json`

如果提供了日期参数，就改用:
- `logseq-cli summarize daily --date "$ARGUMENTS" --json`

然后输出:
1. 今天做过的事
2. 仍在推进中的事
3. 需要我现在处理的 3 个优先项
4. 一段适合发给同事的简短日报
```

用途:

- 开工前看上下文
- 下班前写日报
- 快速恢复中断中的工作

#### 3. `/capture-result`

文件:

```text
~/.claude/commands/capture-result.md
```

内容示例:

```md
---
description: Capture a finished result back into Logseq
argument-hint: [project and result]
---

先把 "$ARGUMENTS" 解析为项目名和结果内容。

默认执行:
- `logseq-cli capture project "<project>" --text "<result>" --json`

如果结果明显是任务完成或待跟进项，再建议附加:
- `logseq-cli capture task --today --text "<result>" --project "<project>" --json`

执行前先用一句话确认你将写入什么。
```

用途:

- 把工作结果沉淀回 Logseq
- 让“用知识库”不只是读取，也包含回写

### 第三步: 把日常工作切成固定模式

推荐你真的按模式使用，而不是每次临时想命令。

#### 开工前

```bash
logseq-cli summarize daily --today --json
logseq-cli tasks list --state todo,doing,now,waiting --json
```

让模型基于这些结果回答:

```text
根据今天 journal 和未完成任务，帮我排一个 3 项优先级列表，并说明为什么。
```

#### 做项目时

```bash
logseq-cli summarize project "Project Alpha" --json
logseq-cli search text "Project Alpha" --json
logseq-cli links backlinks "Project Alpha" --json
```

让模型回答:

```text
结合这些历史记录，帮我总结这个项目当前状态、已知风险和下一步。
```

#### 碰到某个主题时

```bash
logseq-cli summarize topic "ops" --json
logseq-cli search tags "ops" --json
```

让模型回答:

```text
根据我过去关于 ops 的记录，帮我整理出常见问题、重复动作和可标准化流程。
```

#### 收工时

```bash
logseq-cli summarize daily --today --json
```

如果模型总结没问题，再显式回写:

```bash
logseq-cli capture quick --today --text "今天完成了 X，下一步是 Y" --json
```

## 其他大模型的通用接法

这里按能力分三类。

### 类型 1: 能运行本地 shell 命令的 agent

例如任何带 shell tool / terminal tool 的本地 agent。

最佳做法和 Claude Code 一样:

- 给它一条“先查 Logseq，再回答”的系统规则
- 优先调用 `logseq-cli ... --json`
- 只取和当前问题相关的少量结果
- 写入动作单独确认

这类工具和 `logseq-cli` 的契合度最高。

## Claude Code 什么时候需要直接读 Logseq 目录

默认不需要。

如果你的目标只是:

- 回忆历史上下文
- 总结某个 topic / project
- 找 tasks
- 回写少量 capture

那么只让 Claude Code 调 `logseq-cli` 就够了，噪音最小。

只有在下面这些情况，才建议让 Claude Code 直接读取 Logseq 目录:

- 你要它检查某个原始 Markdown / Org 文件的具体写法
- 你要它批量整理多个页面
- 你要它做较复杂的本地重构或格式清理

这时再考虑用 Claude Code 的附加目录能力，把 graph 作为额外目录加入，而不是默认每次都加。

思路是:

- 日常问答和总结: 走 `logseq-cli`
- 需要直接改原始文件: 再给 Claude Code 直接目录访问

这样更稳，也更省上下文。

### 类型 2: 不能跑本地命令, 但你能写一个小脚本

做一个很薄的 Python 包装层就够了。

示例:

```python
import json
import subprocess


def kb(command: list[str]) -> dict:
    result = subprocess.run(
        ["logseq-cli", *command, "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


project = kb(["summarize", "project", "OpenClaw"])
tasks = kb(["tasks", "list", "--state", "todo,doing"])

context = {
    "project": project["data"],
    "tasks": tasks["data"],
}
```

然后把 `context` 送给你自己的模型调用层。

适合:

- OpenAI Responses API
- Anthropic API
- 你自己的桌面脚本
- 内部自动化工具

### 类型 3: 纯聊天界面, 不能调本地命令

这种情况下不要硬做“自动接入”。

更实用的是先在终端跑:

```bash
logseq-cli summarize project "OpenClaw" --json
logseq-cli tasks list --state todo,doing --json
```

再把结果贴给模型，让它基于真实上下文工作。

虽然不是全自动，但准确性通常比“让模型猜你的历史知识”高很多。

## 命令映射: 任务类型对应什么命令

### 1. 回忆过去做过什么

优先:

- `summarize daily`
- `summarize weekly`
- `journal read`
- `search text`

### 2. 搞清某个项目的全貌

优先:

- `summarize project`
- `page read`
- `links backlinks`
- `links outgoing`
- `tasks list`

### 3. 查某个主题是否反复出现

优先:

- `summarize topic`
- `search tags`
- `search text`

### 4. 从历史记录中找待办

优先:

- `tasks list`
- `journal summarize`
- `summarize weekly`

### 5. 产出日报 / 周报 / 复盘

优先:

- `summarize daily`
- `summarize weekly`
- `journal read`
- `search text`

### 6. 记录结论和下一步

优先:

- `capture quick`
- `capture task`
- `capture project`
- `journal append`
- `page append`

## 你应该给模型什么约束

无论 Claude Code 还是其他模型，都建议加下面这几条约束:

1. 遇到“我的历史上下文”“以前做过什么”“上次决定是什么”这类问题时，先查 Logseq，不要猜。
2. 默认优先结构化命令和 JSON，而不是直接扫整个目录。
3. 每次只取最相关的 3 到 10 条结果，不要一次展开整本笔记。
4. 写入 Logseq 前先确认。
5. 回答时区分“来自知识库的事实”和“基于事实的推断”。

这是提高可信度的关键。

## 不建议一开始就做的事

下面这些方向不是不能做，而是不建议作为第一步:

- 自动把整个月 journals 注入每次对话
- 给每个 prompt 都挂一个大而全的 hook
- 直接做 semantic search, embeddings, vector DB
- 自动写回大量页面
- 为了给模型用而重构你的整个 Logseq 目录

这些做法容易在准确性提升之前，先把复杂度和噪音拉高。

## 什么时候再考虑本地语义搜索

当你出现下面这些情况时，再考虑做“完全本地”的语义层:

- graph 已经很大，关键词搜索经常漏掉同义表达
- 同一个概念在不同页面里叫法不一致
- 你经常问“意思相近但词不一样”的问题

届时可以考虑新增一个离线索引流程，但仍然保持这个边界:

- 索引是本地生成
- 检索是本地执行
- 对外仍然只暴露 `logseq-cli` 风格的命令

也就是说，将来可以有 `search semantic`，但仍然不需要 HTTP server 或 MCP。

## 隐私和安全建议

即使你的 Logseq 在本地，模型工具本身未必是“完全不出网”的。

你至少要注意三件事:

1. 只把命中的少量结果发给模型，不要把整个 graph 发出去。
2. 如果日志、日记、会议记录很敏感，优先做 topic/project 级摘要，而不是直接发送原文。
3. 区分“本地文件访问”与“模型请求是否仍然发往云端”。

对 Claude Code，官方文档明确说明:

- Claude Code 本地运行，但为了与模型交互，会把 prompts 和 outputs 通过网络发送到 Anthropic。
- 自定义 slash commands 可放在 `~/.claude/commands/` 或项目下 `.claude/commands/`。
- 个人或项目级记忆文件可放在 `~/.claude/CLAUDE.md` 或项目内 `CLAUDE.md`。

所以最佳实践是:

- 检索留在本地
- 发送给模型的上下文保持最小化
- 敏感内容先做本地摘要再发

## 一套足够好的起步方案

如果你希望今天就开始用，建议直接这么做:

1. 安装 `logseq-cli`
2. 运行 `logseq-cli graph use --graph ~/Documents/Logseq`
3. 在 `~/.claude/CLAUDE.md` 写入“先查 Logseq 再回答”的规则
4. 创建 `/kb` 和 `/daily-brief` 两个自定义 slash commands
5. 工作时用 `summarize project`, `summarize topic`, `tasks list`
6. 收工时用 `capture quick` 或 `capture task`

这套组合已经足够把 Logseq 变成一个真正可用的个人知识库，而不是一个只能手工翻的笔记堆。

## 参考链接

- Anthropic Claude Code 概览: https://docs.anthropic.com/en/docs/claude-code/overview
- Anthropic Claude Code Memory: https://docs.anthropic.com/en/docs/claude-code/memory
- Anthropic Claude Code Slash Commands: https://docs.anthropic.com/en/docs/claude-code/slash-commands
- Anthropic Claude Code Hooks Guide: https://docs.anthropic.com/en/docs/claude-code/hooks-guide
- Anthropic Claude Code Data Usage: https://docs.anthropic.com/en/docs/claude-code/data-usage
- Anthropic Claude Code Security: https://docs.anthropic.com/en/docs/claude-code/security
