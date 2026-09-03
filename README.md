# REM — Replay Experience Module

**From agent runs to production-ready Skills.**  
**把 Agent 真实执行轨迹，自动蒸馏成可复用的 Skills 和干净记忆。**

REM turns real agent execution trajectories into reusable Skills and clean memory.  
It filters noise, extracts critical paths, mines failure patterns, and distills them into installable Markdown skills.

> Not another vector memory.  
> An offline experience-replay engine that makes agents stop repeating the same mistakes.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.3.0-green.svg)](https://github.com/chaoslee514-cell/REM)

**关键词 / Keywords:** AI Agent、Agent Memory、Skill 蒸馏、经验回放、Experience Replay、MCP、Claude Code、Cursor、本地优先、失败模式挖掘、Agent 技能自动生成

---

## Quick Demo（30 秒上手）

```bash
pip install -e .
rem demo
```

一键完成：加载示例轨迹 → 巩固（去噪 + 关键路径）→ 挖掘失败模式 → 生成 Skills → 输出指标报告。

```bash
ls skills/
cat skills/successful-path.md
cat skills/session-lessons.md
```

---

## 真实使用前后对比（Case Study）

下面是一个简化但真实的场景：**用 Agent 修复认证 Token 过期问题**。

### 使用前（没有 REM）

开发者让 Agent 多次尝试修复 `src/auth.py` 中的 token 过期逻辑：

| 轮次 | 发生了什么 | 结果 |
|------|------------|------|
| 第 1 次 | Agent 直接改文件 | CI 报错：`Permission denied: file is read-only` |
| 第 2 次 | 换个参数再改 | 同样 Permission denied |
| 第 3 次 | 继续重试 + 跑测试 | 又出现 `AuthenticationError: invalid token signature` |
| 结果 | 重复踩坑，上下文越来越脏 | 浪费 token，问题解决慢 |

典型问题：
- 同样的失败没有被记住
- 成功路径没有沉淀成可复用技能
- 下次类似任务还是从零开始试错

### 使用后（有 REM）

把这几次运行的轨迹导入 REM：

```bash
rem record examples/sample_trajectory.jsonl --session auth-fix
rem consolidate --session auth-fix
rem distill --session auth-fix
```

REM 自动产出：

1. **`successful-path.md`**  
   提炼出最短成功路径：`read_file → grep → edit_file → run_tests`

2. **失败规避 Skill**  
   明确记录：`edit_file` 在 CI 只读环境下会 Permission denied，并给出预防建议

3. **`session-lessons.md`**  
   总结本会话的成功经验与高频失败点

### 对比效果

| 维度 | 使用前 | 使用后 |
|------|--------|--------|
| 重复错误 | 多次踩同一 Permission denied | 有明确规避 Skill，可提前拦截 |
| 成功经验 | 散落在对话里，下次难复用 | 固化为可安装的 successful-path |
| 上下文质量 | 重试噪声多，token 消耗高 | 关键路径保留，噪声下降 |
| 下次同类任务 | 几乎从零开始 | 可直接加载已蒸馏 Skill |

**一句话价值：**  
让 Agent 的「试错成本」变成「可积累的资产」。

更完整的案例说明见：[docs/case-study.md](docs/case-study.md)

---

## 解决什么问题 / The Problem

当你认真用 Coding Agent（Claude Code、Cursor、OpenClaw 等）时，经常遇到：

- Agent 在不同 session 里重复犯同样的错误
- 成功的工具调用序列无法沉淀成可复用 Skill
- 长轨迹充满重试和死胡同 → 上下文污染、费用上升
- 多数 Memory 工具只负责「存和找」，几乎不负责「从真实运行中蒸馏可执行知识」

REM 把每次运行当作 Experience Replay Buffer 中的经验，做可量化的离线巩固与技能蒸馏。

---

## 核心能力 / What REM Does

| 步骤 | 作用 |
|------|------|
| **Capture 采集** | 结构化记录工具调用、结果、错误、耗时、token |
| **Consolidate 巩固** | 过滤噪声、提取关键路径、挖掘失败模式 |
| **Distill 蒸馏** | 生成实用的 Markdown Skills |
| **Measure 度量** | 输出记忆压缩比、预估 token 节省、模式数量 |

---

## 安装 / Installation

```bash
git clone https://github.com/chaoslee514-cell/REM.git
cd REM
pip install -e .
```

需要：Python 3.10+

---

## 使用方法 / Usage

### 一键演示
```bash
rem demo
```

### 手动流程
```bash
rem record examples/sample_trajectory.jsonl --session my-task
rem consolidate --session my-task
rem distill --session my-task --out ./skills
rem stats --session my-task
```

### 其他命令
```bash
rem list
rem export --session my-task --out cleaned.jsonl
rem install skills/successful-path.md
```

---

## 架构 / Architecture

```
JSONL / Agent Runtime
         │
         ▼
+----------------------+
|  Experience Buffer   |   SQLite（本地优先）
+----------│-----------+
           │ consolidate
           ▼
+----------------------+
| Consolidation Engine |
| • 过滤与评分         |
| • 关键路径           |
| • 失败模式挖掘       |
+----------│-----------+
           │ distill
     ┌-----┴-----┐
     ▼           ▼
 Skill 文件      指标报告
```

---

## 设计原则

1. **本地优先** — 数据默认不出机器  
2. **可度量** — 每次运行都有具体数字  
3. **Skill 原生** — 输出可直接给 Agent 使用  
4. **工程师友好** — CLI 优先，少魔法  
5. **诚实** — 明确写出当前局限  

---

## 当前局限 / Current Limitations

- 轨迹采集目前仍是手动 JSONL，主流 Runtime 自动挂钩仍在规划中
- Skill 生成以规则为主，更高质量需要更好的关键路径算法 + 可选 LLM 精炼
- 失败聚类目前基于错误签名，尚未做完整语义聚类
- 还缺少大规模公开 benchmark

这些都是已知并持续改进的方向。

---

## 项目结构

```
REM/
├── rem/
│   ├── cli.py
│   ├── buffer.py
│   ├── consolidator.py
│   ├── distill.py
│   ├── models.py
│   └── ...
├── examples/
├── docs/
│   └── case-study.md
├── tests/
└── README.md
```

---

## Roadmap

- [x] 核心 Buffer + 巩固 + 蒸馏
- [x] 一键 demo
- [x] 前后对比案例
- [x] 中英文 README
- [ ] 主流 Agent Runtime 自动采集
- [ ] 更强的关键路径与重要性评分
- [ ] 可选 LLM 辅助蒸馏
- [ ] 语义级失败聚类
- [ ] 公开 benchmark

---

## 贡献 / Contributing

欢迎 Issue 和 PR。当前高价值方向：

1. Runtime 适配（Claude Code、Cursor 等）
2. 更好的评分 / 关键路径逻辑
3. 更高质量的 Skill 模板
4. 真实使用反馈与 benchmark

---

## License

MIT
