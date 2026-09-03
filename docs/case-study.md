# Case Study / 使用前后对比案例

## 场景说明

任务：使用 AI Coding Agent 修复项目中的「认证 Token 过期时间」问题。

这是一个非常常见的真实开发场景：Agent 需要读文件、搜索关键词、修改代码、跑测试。

---

## Before：未使用 REM

### 第 1 次尝试
- Agent 读取 `src/auth.py`
- 直接尝试 `edit_file`
- **结果**：失败  
  `Permission denied: file is read-only in CI environment`

### 第 2 次尝试（新 session）
- Agent 几乎重复相同操作
- 再次命中同一个权限错误
- **结果**：再次失败，额外消耗 tokens

### 第 3 次尝试
- 继续修改 + 跑测试
- 出现连锁错误：`AuthenticationError: invalid token signature`
- **结果**：任务未完成，经验没有沉淀

### 总结（Before）

| 指标 | 表现 |
|------|------|
| 重复失败次数 | 2～3 次 |
| 额外 token 消耗 | 约 3000～5000 |
| 是否形成可复用知识 | 否 |
| 换 session 后是否还踩坑 | 是 |

**核心问题：** 成功和失败的经验都只存在于当次上下文中，无法跨 session 复用。

---

## After：使用 REM

### 操作步骤

```bash
# 1. 把包含成功与失败的轨迹导入
rem record examples/sample_trajectory.jsonl --session auth-fix

# 2. 巩固（过滤噪声 + 提取关键路径 + 挖掘失败模式）
rem consolidate --session auth-fix

# 3. 蒸馏成 Skill
rem distill --session auth-fix --out ./skills
```

### 自动得到的产物

1. **`successful-path.md`**  
   一条最短、可复用的成功工具序列（读文件 → 搜索 → 修改 → 测试）

2. **`fail-*.md`**  
   明确记录：
   - 在 CI 环境下对 `edit_file` 会触发 Permission denied
   - 给出规避建议（先检查权限/环境，再决定是否直接编辑）

3. **`session-lessons.md`**  
   会话级总结：什么有效、什么反复失败、下次该怎么做

### 之后再做类似任务时

- 可直接把生成的 Skill 提供给 Agent
- Agent 优先走成功路径，减少盲目重试
- 提前避开已知失败模式
- 上下文更干净，整体 token 更省

### 总结（After）

| 指标 | 表现 |
|------|------|
| 重复失败 | 明显减少 |
| 经验是否沉淀 | 是（生成可安装 Skill） |
| 跨 session 是否可复用 | 是 |
| 可量化收益 | 有 memory reduction 与预估 token 节省报告 |

---

## 一句话对比

**Before：** 每次都像第一次做这个任务，重复踩坑。  
**After：** 把真实踩坑和成功路径变成可复用的 Skill，让 Agent 越用越稳。

---

## 如何复现这个案例

```bash
git clone https://github.com/chaoslee514-cell/REM.git
cd REM
pip install -e .
rem demo
```

然后查看：

```bash
cat skills/successful-path.md
cat skills/session-lessons.md
ls skills/
```

---

## 适用人群

- 经常使用 Claude Code / Cursor / 其他 Coding Agent 的开发者
- 希望减少 Agent 重复犯错的人
- 想把成功经验沉淀成团队可复用 Skill 的人
- 关注 token 成本与上下文质量的工程师

---

## 中文搜索关键词

AI Agent 经验回放、Agent Skill 自动生成、智能体失败模式、Agent 记忆巩固、Claude Code 技能蒸馏、Cursor Agent 经验复用、Agent 不再重复犯错
