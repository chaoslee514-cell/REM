# REM — 经验回放与技能蒸馏模块（中文说明）

**一句话：** 把 AI Agent 的真实执行轨迹，自动变成可复用的 Skills 和干净记忆。

---

## 它解决什么问题？

1. Agent 经常在不同会话里重复犯同样的错误  
2. 成功经验无法沉淀成可安装的 Skill  
3. 长任务轨迹噪声大，上下文越来越脏、token 越来越贵  
4. 现有 Memory 工具大多只能「存和找」，很少能从真实运行中蒸馏出可执行知识

---

## 快速体验

```bash
pip install -e .
rem demo
```

运行后会自动生成 `skills/` 目录下的 Skill 文件，并输出效果指标。

---

## 使用前后对比（简版）

**使用前：**  
Agent 修认证相关 bug 时，反复遇到 CI 权限错误，多次重试，浪费 token，且经验无法复用。

**使用后：**  
通过 REM 巩固和蒸馏，自动得到：
- 成功路径 Skill
- 失败规避 Skill
- 会话总结 Skill

下次遇到类似任务，可直接减少重复踩坑。

完整案例请看：[case-study.md](case-study.md)

---

## 基本命令

```bash
rem record <文件.jsonl> --session 任务名
rem consolidate --session 任务名
rem distill --session 任务名
rem stats --session 任务名
rem demo
```

---

## 适合谁用？

- 使用 Claude Code、Cursor 等 Coding Agent 的开发者
- 关注 Agent 稳定性与 token 成本的工程师
- 想把个人/团队成功经验沉淀成 Skill 的人

---

## 项目地址

https://github.com/chaoslee514-cell/REM

---

## 关键词（便于搜索）

AI Agent、智能体、经验回放、技能蒸馏、Agent Memory、失败模式、Claude Code、Cursor、MCP、本地优先、Skill 自动生成
