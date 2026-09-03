# 真实使用前后对比案例 / Before vs After Case Study

本文用一个简化但真实的开发场景，说明 REM 的实际价值。

## 场景

任务：修复项目中认证 Token 过期时间过短的问题（`src/auth.py`）。

开发者使用 Coding Agent（如 Claude Code / Cursor）多次尝试完成该任务。

---

## 使用前：没有 REM

### 实际发生的过程

**第 1 次尝试**
- Agent 读取 `src/auth.py`
- 直接尝试修改文件
- 结果：CI 环境报错  
  `Permission denied: file is read-only in CI environment`

**第 2 次尝试**
- 换了一种修改方式再次调用 `edit_file`
- 结果：同样 Permission denied
- 上下文中已经堆积了失败信息

**第 3 次尝试**
- 继续重试 + 跑测试
- 额外出现：`AuthenticationError: invalid token signature`
- Token 消耗上升，对话越来越长，有效信号被噪声淹没

### 使用前的核心问题

1. **重复错误没有被沉淀**  
   同一类 Permission denied 反复出现，Agent 没有「记住」。

2. **成功路径没有固化**  
   即使某次成功了，经验也只留在当次对话里，下次类似任务难以复用。

3. **上下文质量下降**  
   重试、失败、无效步骤不断累积，导致后续推理更贵、更不稳定。

4. **知识无法跨 session 迁移**  
   新开一个会话，几乎又从零开始试错。

---

## 使用后：接入 REM

把上述几次运行的轨迹（成功 + 失败）导出为 JSONL，导入 REM：

```bash
rem record auth_trajectories.jsonl --session auth-fix
rem consolidate --session auth-fix
rem distill --session auth-fix --out ./skills
```

### REM 自动完成的事情

1. **过滤噪声**  
   去掉纯重试、低价值步骤，保留关键路径和必要失败上下文。

2. **提取成功路径**  
   生成 `successful-path.md`，例如：
   - `read_file`
   - `grep`
   - `edit_file`（正确参数）
   - `run_tests`

3. **挖掘失败模式**  
   识别高频错误：
   - 工具：`edit_file`
   - 典型错误：`Permission denied: file is read-only in CI environment`
   - 给出预防建议（先检查环境是否可写、或改用其他流程）

4. **输出会话级总结**  
   `session-lessons.md` 汇总「什么有效、什么反复失败、下次怎么做」。

### 使用后的变化

| 维度 | 使用前 | 使用后 |
|------|--------|--------|
| 重复踩坑 | 多次撞上同一 Permission denied | 有专门的失败规避 Skill，可提前拦截 |
| 成功经验 | 留在聊天记录里，难复用 | 固化为 `successful-path` Skill |
| Token / 上下文 | 重试多，噪声大 | 关键路径保留，噪声明显下降 |
| 跨会话能力 | 新 session 基本从零开始 | 可直接加载已蒸馏 Skills |
| 知识形态 | 临时、分散 | 可版本管理、可分享、可安装 |

---

## 量化直觉（示例）

在示例数据上运行 `rem demo` 时，通常可以看到：

- 原始步骤被压缩（memory reduction）
- 预估 token 节省（根据减少的步骤估算）
- 明确的失败模式数量
- 直接可读的 Skill 文件

这些数字会随真实轨迹变化，但方向一致：**把「试错成本」转成「可积累资产」**。

---

## 适合什么人

- 经常用 Claude Code / Cursor / 其他 Agent 写代码、改 bug 的个人开发者
- 希望团队减少重复踩坑、沉淀内部 Skill 的小团队
- 做 Agent 产品、需要从真实运行中持续产出领域技能的人

---

## 如何复现本案例

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

## 总结

**使用前：** Agent 会重复犯错，成功经验难以沉淀，上下文越用越脏。  
**使用后：** 失败被归纳成规避技能，成功被蒸馏成可复用路径，下次同类任务有据可依。

这就是 REM 最直接的实用价值。
