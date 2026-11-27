# Step 3 · 自动出题闭环（Claude 出题，Codex 答题）

日期：2026-11-27 · 预算 2 小时，全程无人工干预 · 作者：Claude

## 0. 执行顺序
1. **先选种子 benchmark**（§1），
2. 再用"数学化的 benchmark 定义"（§2）写出任务族，
3. 然后按 AutoSciBench 的"概念 → 配方 → 求解 → 反思 → 修订"循环迭代（§3）。

## 1. 种子 benchmark（第一步）

选择标准：
- 能代表 2026 年各大厂和第三方测 agent 的前沿方向，依据 `survey/LAB_BENCHMARKS_2026-11.md` 和 `survey/FIN_AGENT_BENCH_22.md`；
- GT 能用程序复算；
- 能用仓库里已有的真实 XBRL 数据（`data/edgar/`，最新申报到 2026-11）或合成数据实现。

| 种子 | 出处 | 借用的"能力缺口" | 对应任务族 |
|---|---|---|---|
| Finance Agent Benchmark v2（Vals） | survey/FIN_AGENT_BENCH_22 #8；Vals Index 金融分项 | 基于申报文件的研究计算 | 各族共同的底座 |
| BuySideFlow | survey/FIN_AGENT_BENCH_22 #18 | **答对的题里 50.8% 违反时点约束** | **F1 时点纪律（PIT）** |
| OpenAI Blocker Deception | GPT-6.2 system card（survey/LAB_BENCHMARKS） | 遇到阻碍时倾向于隐瞒 | **F2 阻碍披露**（配对对照） |
| GAUGE / FrontierFinance / Remote Labor Index | survey/FIN_AGENT_BENCH_22 #13；LAB_BENCHMARKS | 编辑已有交付物比从零生成更难 | **F3 滚动更新已有模型** |
| AutomationBench（Zapier，Finance 领域最难） | LAB_BENCHMARKS §2 | 层叠的业务规则、误导性记录、虚报成功 | **F4 规则约束的财务操作**（合成账本，看最终状态） |
| SecQue / FinanceBench（本仓库 step0/1） | step0、step1 | 比率计算、跨期 | 作为 F1/F3 的指标模板 |

## 2. 数学化定义（依据 survey/BENCHMARK_DEFINITION.md §5）

**单题**：τ = (u, E, s₀, Y\*, R, σ\*)
- u：题干，在 `questions/qNNN.md` 中。
- E：共享环境，即一个只读的"数据终端"导出文件夹，由 `env/qNNN/` 提供。题目规定**这是唯一允许使用的信息源**。
- s₀：单题初始状态，包括给定的文件和时点（as-of date）。
- Y\*：参考答案。由程序从 E 和 s₀ **复算**得到，并且允许多个合理口径时给出变体。在实验结束前，Y\* **不进仓库**，只公开 SHA-256 承诺值（见 `gt_commitments.md`），对应 CTF 的"隔离测试集"。
- R：确定性评分函数，按数值容差和结构化字段打分，不使用 LLM judge。
- σ\*：oracle 解。oracle **只读取 env 里的文件**就能算出 Y\*，以此证明任务在给定环境内可解，对应 ABC 的任务有效性。

**Benchmark 层**：B = (c, p_T, {τ_i}, Π, Agg, U, Meta)
- c：要测的能力，各任务族分别定义，见 §1 表格的第三列。
- p_T：任务族 × 参数，即生成器。
- Π：单次作答，只能用 env，没有工具限制之外的约束。
- Agg：族内平均，另外报告配对差。
- U：按任务族聚类。
- Meta：as-of 日期、修订号、轮次。

**正确性条件**
- 任务有效性：oracle 只用 env 就能解出，并且干扰项和陷阱都有可识别的"错误签名"。比如违反时点约束会得到一个**已知的特定错误值**，可以自动归因。
- 结果有效性：R=1 当且仅当所有必答字段都在容差范围内。

## 3. 闭环（AutoSciBench 式）

```
第 r 轮：
  概念（族 × 能力缺口） → 配方（生成器参数 + 陷阱） → 实例化 + oracle 复算 + 承诺值
  → 推送 questions/ → Codex 作答（answers/）
  → 确定性打分 + 错误签名归因 → 反思（题坏了 / agent 错了 / 太容易）
  → 修订：修坏题（升修订号）；把太容易的题加难；按经验生成新概念
```

AutoSciBench 被拒的三条理由，在这里的对应措施：
1. **GT 没有独立验证**：每道题都有 oracle 从环境复算；错误签名把"题坏了"和"agent 错了"分开。
2. **难度提升和题目质量没分开**：每轮都报告 oracle 可解率、歧义修订次数；加难题和原题配对报告。
3. **选择偏差**：最终集合不只保留 Codex 做错的题，而是保留所有通过有效性检查的题；另外留一组**新实例复测**（同一配方、换公司或换参数）。

每轮的记录见 `LOOP_LOG.md`。
