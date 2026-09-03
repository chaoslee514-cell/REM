# REM — Replay Experience Module

**From agent runs to production-ready Skills.**  
**把 Agent 真实执行轨迹，自动蒸馏成可复用的 Skills 和干净记忆。**

REM turns real agent execution trajectories into reusable Skills and clean memory.  
It filters noise, extracts critical paths, mines failure patterns, and distills them into installable Markdown skills.

> Not another vector memory.  
> An offline experience-replay engine that makes agents stop repeating the same mistakes.

> 不是又一个向量记忆库。  
> 而是一个离线经验回放引擎，让 Agent 不再重复犯同样的错误。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.1-green.svg)](https://github.com/chaoslee514-cell/REM)

**关键词 / Keywords:** `AI Agent` `Agent Memory` `Skill Distillation` `Experience Replay` `MCP` `Claude Code` `Cursor` `Agent Skills` `经验回放` `技能蒸馏` `智能体记忆` `失败模式挖掘`

---

## Quick Demo / 快速体验（30 秒）

```bash
pip install -e .
rem demo
```

This single command will:

1. Load sample trajectories  
2. Run consolidation (noise removal + critical path)  
3. Mine failure patterns  
4. Generate Skills into `./skills/`  
5. Print a clear metrics report

一条命令完成：加载示例 → 巩固 → 挖掘失败模式 → 生成 Skill → 输出指标报告。

```bash
ls skills/
cat skills/successful-path.md
cat skills/session-lessons.md
```

---

## Before vs After / 使用前后对比（真实场景）

### 场景：用 Agent 修复「认证 Token 过期时间」相关问题

#### Before（未使用 REM）

| 次数 | 发生了什么 | 结果 |
|------|------------|------|
| 第 1 次 | Agent 直接改 `src/auth.py` | 失败：CI 环境文件只读（Permission denied） |
| 第 2 次 | 几乎相同的操作再次尝试 | 再次失败：同样的 Permission denied |
| 第 3 次 | 继续重试 + 跑测试 | 失败：AuthenticationError + 浪费 token |
| 后续任务 | 没有沉淀任何经验 | 换一个 session 后继续重复踩坑 |

**典型代价：**
- 重复失败 2～3 次
- 额外消耗约 3000～5000 tokens
- 没有形成可复用的规避知识

#### After（使用 REM）

1. 把上述失败 + 成功轨迹导入 REM  
2. 运行 `rem consolidate` + `rem distill`  
3. 自动得到：

- `successful-path.md`：一条最短成功工具序列  
- `fail-*.md`：明确记录「CI 下 edit_file 会 Permission denied」并给出规避建议  
- `session-lessons.md`：会话级总结

**之后再做类似任务时：**
- Agent 可直接参考成功路径，减少无效重试
- 提前避开已知失败模式
- 上下文更干净，token 消耗下降

> 完整案例见：[docs/case-study.md](docs/case-study.md)

---

## The Problem / 解决什么问题

When you run coding agents seriously, you keep seeing the same issues:

- The agent retries the same failing tool call across sessions  
- Successful sequences are never captured as reusable knowledge  
- Long trajectories are full of dead-ends → context gets dirty and expensive  
- Most memory tools only store & retrieve; almost none **distill executable Skills** from real runs

实际使用 Agent 时常见痛点：

- 跨 session 重复犯同样错误  
- 成功经验无法沉淀成可安装的 Skill  
- 长轨迹充满重试和死胡同，上下文越来越脏、越来越贵  
- 现有 Memory 工具大多只负责「存和找」，很少能从真实运行中**蒸馏出可执行知识**

---

## What REM Does / 核心能力

| Step | English | 中文 |
|------|---------|------|
| **Capture** | Ingest structured trajectories | 采集结构化执行轨迹 |
| **Consolidate** | Filter noise, keep critical path, mine patterns | 过滤噪声、提取关键路径、挖掘失败模式 |
| **Distill** | Generate practical Markdown Skills | 蒸馏成可使用的 Markdown Skill |
| **Measure** | Report reduction & token savings | 输出可量化的效果指标 |

---

## Installation / 安装

```bash
git clone https://github.com/chaoslee514-cell/REM.git
cd REM
pip install -e .
```

Requirements: Python 3.10+

---

## Usage / 使用方法

### One-command demo
```bash
rem demo
```

### Manual workflow / 手动流程
```bash
# 1. 导入轨迹
rem record examples/sample_trajectory.jsonl --session my-task

# 2. 巩固
rem consolidate --session my-task

# 3. 蒸馏成 Skill
rem distill --session my-task --out ./skills

# 4. 查看统计
rem stats --session my-task
rem list
```

### Other commands
```bash
rem export --session my-task --out cleaned.jsonl
rem install skills/successful-path.md
```

---

## Architecture / 架构

```
JSONL / Agent Runtime
         │
         ▼
+----------------------+
|  Experience Buffer   |   SQLite (local-first)
+----------│-----------+
           │ consolidate
           ▼
+----------------------+
| Consolidation Engine |
| • Filter & score     |
| • Critical path      |
| • Failure patterns   |
+----------│-----------+
           │ distill
     ┌-----┴-----┐
     ▼           ▼
 Skill Files    Metrics
```

---

## Design Principles / 设计原则

1. **Local-first** — 数据默认留在本地  
2. **Measurable** — 每次运行都有具体数字  
3. **Skill-native** — 输出可直接被 Agent 使用  
4. **Engineer-centric** — CLI 优先，少魔法  
5. **Honest** — 明确写出当前局限

---

## Current Limitations / 当前局限

- Trajectory capture is still manual (JSONL). Automatic hooks for Claude Code / Cursor are planned.  
  轨迹采集目前仍需手动导入，后续会支持主流 Agent Runtime 自动采集。

- Skill generation is rule-based. Higher quality will come from better algorithms + optional LLM refinement.  
  Skill 生成目前以规则为主，后续会增强关键路径算法并支持可选 LLM 精炼。

- Failure clustering is signature-based, not full semantic clustering.  
  失败聚类目前基于错误签名，尚未做完整语义聚类。

---

## Roadmap / 路线图

- [x] Core buffer + consolidation + distillation  
- [x] One-command demo  
- [x] Before/After case study  
- [x] Chinese documentation for discoverability  
- [ ] Automatic trajectory capture from popular agent runtimes  
- [ ] Better critical-path & importance scoring  
- [ ] Optional LLM-assisted distillation  
- [ ] Semantic failure clustering  
- [ ] Public benchmark on repeated-error tasks

---

## Contributing / 贡献

Issues and PRs are welcome.  
欢迎提交 Issue 和 PR。

High-impact areas:
1. Runtime adapters (Claude Code, Cursor, etc.)
2. Better scoring / critical-path logic
3. Higher-quality skill templates
4. Real-world usage reports

---

## License

MIT
