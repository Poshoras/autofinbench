# 金融 Agent Benchmark 调研报告：你的 22 个名单

日期：2026-11-26 · 作者：Claude（为 AutoFinBench 准备）

**名单状态**：一共 22 个，**找到并读了 21 个**，`FAAB` 没找到（见 #19）。

- P298 "Evaluating Frontier Agents on End-to-End Investment Banking Workflows" 是 **ICLR 2026 的 workshop 论文**，和 arXiv 上的 BankerToolBench 是同一条工作线，但数字不同。我把两篇放在一起写（#14）。
- 信息来源是论文全文、GitHub 和 HF 页面。长论文的后半部分有时只拿到工具生成的摘要，凡是来自摘要的数字都标了 ⚠️。"我的判断"是我的观点，不是论文的结论。
- 更早一版的 27 个 benchmark（含名单以外的）见 [AGENT_BENCH_SURVEY.md](AGENT_BENCH_SURVEY.md)。

**缩写说明**：
- Q=题目，GT=标准答案，R=rubric；✅ 公开，◐ 部分公开，❌ 不公开，? 未说明。
- PIT（point-in-time）= 时点约束：只能使用提问时点之前已经公开的信息。

## 总览表

| # | ID | Benchmark | 任务形态 | 评估方式 | 当前最好 | 数据 |
|---|---|---|---|---|---|---|
| 1 | P? | DataClawBench | 在约 200 万条记录里探索并算出答案 | LLM judge 判单一答案 + 里程碑 | Opus 4.6 63.4% | Q/GT ✅ MIT |
| 2 | P016 | FinanceGym / FinanceHarness | 带截止日的研究报告（PIT 语料） | 0–4 rubric，LLM judge | ⚠️ 约 34–45% | Q ✅，R ❌ |
| 3 | P021 | FinDeepForecast | 实时预测 | 容差判对，确定性 | 39.5% | ? |
| 4 | P024 | FinFIRST | 搜索、作答并给出可追溯的来源 | 原子 rubric，judge κ=0.82 | Opus 5 87.6% | Q/GT/R ✅ |
| 5 | P028 | FinRetrieval | 从结构化库检索数值 | LLM judge 二值 | 有 API 时 90.8%，只用网页 19.8% | Q/GT/轨迹 ✅ |
| 6 | P041 | IPO Finance Agent | S-1 尽调 | 模型共识生成的 rubric | 79.8% | ◐ 70 条 |
| 7 | P046 | ProFinR / ProFinAgent | L1 检索 → L3 研究，配 53 个工具 | 1% 容差 + 工具 Jaccard + 双 judge | 原生 41.5%，用其框架 83.3% | Q/GT ✅ |
| 8 | P053 | Finance Agent Benchmark (Vals) | 工具研究题 | rubric，3 个 judge 评审团 | v2.1 69.47% | ◐ |
| 9 | P056 | FinSearchComp | 搜索短答案 | judge + 容差，与人工一致 95% | 68.9%（人类 75） | Q/GT ✅ |
| 10 | P283 | FinDeepResearch | 公司研报 | rubric judge | 37.9 | ? |
| 11 | P285 | ICBCBench | 中英双语深度研究：客观题 + 研报 | GPT-5.4 / Gemini judge + 专家 rubric | 58.7（EN）/ 63.4（ZH） | Q/GT/R ✅ |
| 12 | P286 | FinRpt | 生成个股研报 | 买卖评级准确率 + GPT-4o 两两比较 | 胜率 0.69 ⚠️ | ✅ |
| 13 | P293 | GAUGE | Agent 搭建估值模型 | 代码检查 + judge + 专业实践区间 | Fable 5 53.4（资深分析师 88.3） | ❌（待放出） |
| 14 | P298 | IB Workflows（≈ BankerToolBench） | 投行交付物 | rubric / agent-as-judge | 33.8% 成功率（workshop）/ 16% 通过率（arXiv） | arXiv 版 ✅ |
| 15 | P? | FinForesight | 无前视的预测回测 | 完全确定性 | 0.71 | ✅ CC-BY |
| 16 | P? | CryptoAnalystBench | 加密资产长报告 + 引用 | 1–10 分 judge，κ 只有 0.35–0.42 | 约 9 分（已饱和） | Q ✅ |
| 17 | P? | AgenticFinBench | 真实请求长答案 | 无参考 rubric + claim 审计 | Q=89.2 | Q/R ✅ |
| 18 | P? | BuySideFlow | SQL/Python 流程 + 时点合规 | 表格比对 + 专家 PIT 审计 | 36.8%；**答对的里有 50.8% 违反 PIT** | ◐（授权库） |
| 19 | P? | FAAB | 多 agent 流程的失败归因 | — | — | **未找到** |
| 20 | P? | Investor's Last Exam | 截断时点的买方研究 | rubric + 实际结果 | 68.1 | ◐ |
| 21 | P? | DealTrace | PE 交易 memo 与模型的逐阶段复核 | 逐阶段对照来源 + 4 个 judge | 未给总分 | ? |
| 22 | P? | DeepFinance | PE/IB 长程尽调（人类约 27 小时/题） | 专家 rubric | 57.6% | ❌ |

---

## 一、名单以外、值得补进来的

前 8 个我已经读过，详情见 [AGENT_BENCH_SURVEY.md](AGENT_BENCH_SURVEY.md)：

| 名称 | 为什么值得补 |
|---|---|
| **BankerToolBench arXiv 正式版**（[2604.11304](https://arxiv.org/abs/2604.11304)） | P298 只是 workshop 版。正式版有 100 题，约 150 条 rubric/题，任务、rubric 和数据 CC-BY 公开；agent-as-judge 与人工一致 88.2%，高于人与人之间的 84.6% |
| **FrontierFinance (Samaya)**（[2608.11683](https://arxiv.org/abs/2608.11683)） | 公开 220 题和 11,543 条 rubric；拿 FAB v2 的 harness 做过对比 |
| **FrontierFinance (Kensho/S&P)**（[2604.05912](https://arxiv.org/abs/2604.05912)） | 给出了 **judge 高估的直接证据**：judge 给 87.5，人工只有 70.9，人类专家 77.2 |
| **MBABench**（[2605.22664](https://arxiv.org/abs/2605.22664)） | 101 个建模任务带 golden 工作簿，公开，正好和 GAUGE 互补 |
| **LiveSearch**（[2610.37166](https://arxiv.org/abs/2610.37166)） | "题目即程序、GT 由执行得到"，每天刷新，**和 AutoFinBench 思路最接近** |
| **Fin-RATE**（[2602.07294](https://arxiv.org/abs/2602.07294)，KDD'26） | 7,500 道跨公司、跨年的题，连同语料一起公开（MIT） |
| **Bank-World**（[2610.39733](https://arxiv.org/abs/2610.39733)）/ **CFAgentBench**（[2606.22000](https://arxiv.org/abs/2606.22000)） | 用状态检查判对错，是金融版的 τ-bench |
| **FinToolBench / FinMCP-Bench / FinTrace** | 在工具调用轨迹这一层做评测 |
| 见到但还没读：**ATLAS-Finance**（[2611.22085](https://arxiv.org/abs/2611.22085)，13 家模拟机构共 100 个投行任务）、**BigFinanceBench**（[2606.03829](https://arxiv.org/abs/2606.03829)，按工作流给部分分并定位失败）、**FinHopper**（[2610.26036](https://arxiv.org/abs/2610.26036)，多跳逐步评分）、**CausalLoss-Fin**（[2609.25960](https://arxiv.org/abs/2609.25960)，把金融 agent 的损失归因到决策或基础设施故障，可能与 FAAB 相近） | |

---

## 二、逐篇调研（按你的名单顺序）

每篇固定 6 项。"我的判断"给两个打分：**评估可自动化程度**和 **GT 自动化后的可信度**。

### 1. DataClawBench（[2605.02503](https://arxiv.org/abs/2605.02503)，2026-05）
- **Task**：agent（OpenClaw 框架，Docker 内可用 Python、文件和网页工具）拿到问题时**没有任何数据源或表结构提示**，要自己在约 206 万条企业、行业、政策记录里找证据，给出唯一答案。共 492 题（易 131 / 中 286 / 难 75）。
  - 例 [原文，HF easy001]："In which province is the enterprise with the highest R&D investment ratio nationwide in 2022 located?" → "Jiangsu Province"
  - 例 [原文]："In 2022, is the operating revenue of Company X higher than the total operating revenue of its industry in its province?"
- **Capability**：没有先验时找证据、实体对齐、单位统一、跨源关联、按政策筛选、聚合、多步推理、处理脏数据。
- **Evaluation**：准确率由 LLM judge（GLM-5）判定；过程指标（GPR/TPE）由 LLM 对照里程碑判定。没有报告与人工的一致率。
  - 我的判断：**自动化程度高**，答案唯一。
- **Performance**：Claude Opus 4.6 63.4%（易 76.8 / 中 62.2 / 难 44.8），其余 7 个模型都低于 50%。
  - 主要问题：带着错答案就停了；实体查不到就放弃；上下文或超时后无声中止；政策分母筛错；单位不一致；正负号错误。
- **GT Construction**：简单题来自知识图谱和模板流水线 ⚠️；中等和难题由专家从 400+ 候选中整理。每题由专家设计，再由第二位专家和多个 agent 分别求解，达成共识后保留。数据来自作者所在智库的咨询数据，已匿名。
  - 我的判断：答案本质是数据库上的聚合，可以写成 SQL 由程序计算，**可信度高**。
- **Data**：HF `GTML-LAB/DataClaw`（MIT），492 题附 gold 答案和 ⚠️ 里程碑；部分表来自天池（CC BY-NC-SA）。没有找到代码。

### 2. FinanceGym / FinanceHarness（[2607.27853](https://arxiv.org/abs/2607.27853)，2026-07）
二者是同一篇论文：FinanceGym 是 benchmark，FinanceHarness 是在同一个 PIT 环境里运行 agent 的框架。
- **Task**：针对带截止日的问题写一份带引用的分析师式报告，检索只能用截止日及之前发布的文档。
  - 例 [原文，leaderboard]："How does Air France-KLM's accelerated transition toward a 60.5% majority stake in SAS impact its strategic bandwidth…"
  - ⚠️ 案例："Build an auditable five-year unlevered DCF for Microsoft (MSFT) from its latest fiscal-year results."
- **Capability**：取证、跨源验证、综合成报告、预测截止日之后的结果。
- **Evaluation**：每条 rubric 按 0–4 分打分后换算成百分比，judge 为 Gemini-3.5-Flash（leaderboard 已改成 3 个 judge）。专家参与验证，没有报告一致率。
- **Performance**：Qwen3.6-27B 不用框架 25.3%，用框架 32.4%；⚠️ 表中最好的是 Opus 4.7，34.1%；摘要说 Opus 5 "低于 45%"（正文写 44.9%）。
  - ⚠️ **截止日之前的题约 46%，截止日之后的题只有约 12%**。
- **GT Construction**：LLM 根据实体图生成问题、论点和两层 rubric；专家验证了 500 题中的 411 题（82%），约 1.2 专家小时/题。公开 400 题、2,464 条 rubric。
  - 我的判断：LLM 生成、专家验证，**可信度中**。
- **Data**：HF `Rujun/FinanceGym`（400 题，CC BY-NC 4.0）；**rubric 和语料不公开**；代码在 GitHub `Yijia-Xiao/FinanceHarness`。

### 3. FinDeepForecastBench（[2601.05039](https://arxiv.org/abs/2601.05039)，2026-01）
- **Task**：实时预测，分两种：周期性数值（96 个宏观指标、121 个公司指标）和非周期性二元事件。10 周共 1,394 题，覆盖 8 个经济体、1,314 家公司。论文没有给完整例题，只列了 ROA、EPS 这类指标名。
- **Capability**："extensive information gathering and multi-step reasoning"，以及对派生比率的算术推理。
- **Evaluation**：确定性评分，按相对误差阈值判对（百万级 5%、比率 1%、利率/汇率 0.1%），事件题完全匹配。专家核验全部非周期性 GT，标注员一致率 95%。
- **Performance**：o3-deep-research 39.5%；周期性数值题最好只有 25.5%；只推理不联网低于 10%；去掉搜索掉 11–14 分。
- **GT Construction**：周期性题从官方来源自动解析；事件题由 LLM 汇总证据、专家确认；每周解析一次。
  - 我的判断：数值部分**可信度高**，事件部分**中**。
- **Data**：论文称在 OpenFinArena 平台公开，未核实。

### 4. FinFIRST（[2609.25192](https://arxiv.org/abs/2609.25192)，2026-09，inclusionAI）
- **Task**：agent 用网页搜索、页面访问和 Python 回答金融问题，并给出来源。
  - 例 [原文节选]："Using the latest official and industry data available as of June 30, 2026, and Meta's official disclosures…" → 参考答案 72.45%
- **Capability**：在有效时点内检索、选权威来源、对齐实体和期间、统一单位、计算、**证据可追溯**。
- **Evaluation**：GLM-5.1 judge 对每条原子标准判二值，只看最终回答；指标有 Atomic、加权 rubric 分、Strict Pass。8 位专家核查 50 例，**κ=0.816**。
  - 我的判断：**自动化程度高**。
- **Performance**：Claude-Opus-5 原子分 87.59%，GPT-5.6-Sol 严格通过率 71.54%。
  - 主要问题：检索做对了，计算和作答却跟不上；⚠️ 17.5% 的答案对了但没有证据支撑；漏答。
- **GT Construction**：50+ 位金融专家写题和参考材料包，并整理了 138 个来源的权威来源地图；6 阶段质检（重做、仲裁、LLM 只负责标出问题）。约 1,258 个候选**只录用 123 题（9.78%）**。
  - 我的判断：**可信度高，但很贵**。
- **Data**：HF `inclusionAI/FinFIRST`（Apache-2.0），123 题附参考答案和 701 条原子标准；来源地图没有单独公开。

### 5. FinRetrieval（[2603.04403](https://arxiv.org/abs/2603.04403)，2026-01，Daloopa）
- **Task**：500 道从结构化数据库检索具体数值的题，比较两种设置：有结构化数据 MCP 工具（Daloopa API）和只能网页搜索；共 14 种配置。
  - 例 [原文]："What was Stryker Corporation's amortization of intangible assets within operating expenses for the full fiscal year 2020, in USD millions?" → $472 million
- **Capability**：结构化库数值检索、工具使用、期间口径处理。
- **Evaluation**：GPT-5.2 judge（温度 0）判二值对错，带归一化规则。人工复查所有失败案例，发现 13 个是 judge 判错（占失败的 2.5%）。
  - 我的判断：**自动化程度高**。
- **Performance**：Claude Opus + 推理 + MCP **90.8%，只用网页 19.8%，差 71 个点**；所有 MCP 配置都在 80–91%。
  - 主要问题在**期间口径**：在 26 个"按期间筛选失败"的案例里，财年与日历季度错位、起止年份标注不一致占 46%，粒度不匹配占 27%，业绩指引的存储约定占 23%。美国与非美国之间 5.6 个点的差距也来自这个原因。
- **GT Construction**：数据库值经三阶段生成题目：
  1. 分层抽样（美国与非美国各半，6 个类别）；
  2. 补充上下文（上下各 10 行，加上**源文件截图并高亮对应单元格**）；
  3. GPT-5.1 把它写成问答。
  - 只保留人工核验过的值，自动生成值和推算值都剔除（约 9%）。覆盖 4,649 家公司、41 个国家。
  - 我的判断：**可信度高**。这就是"数据库到 LLM 转写"的标准流水线，和 AutoFinBench 的 XBRL 思路几乎一样。
- **Data**：HF `daloopa/finretrieval`，含题目、7,000 条回答、评分和**完整工具轨迹**；许可未写明。注意作者是 Daloopa 员工，工具是他们的商业 API。

### 6. IPO Finance Agent（[2606.23032](https://arxiv.org/abs/2606.23032)，单一作者）
- **Task**：围绕 SpaceX 的 S-1 做 IPO 尽调问答，可用网页、EDGAR 和检索；共 1,000 题，公开 70 题。论文正文没有文字例题。
- **Capability**：7 个领域：分部经济、KPI 质量、治理、同一控制下重述会计、资本强度、执行风险、估值与承销。
- **Evaluation**：每题按 rubric 给部分分，grader 为 GLM-5.1，**和得分最高的 GLM-5.2 同属一个家族，有自我偏好风险**；每条最终 rubric 由人工专家审核。
- **Performance**：GLM-5.2 79.8%，Qwen 3.7 Max 78.9%，Kimi K2.6 68.0%，Nemotron 3 Ultra 45.5%。估值与承销最弱；FAB v2 的 harness 因为 S-1 太长基本跑不通。
- **GT Construction**：从 5 个模型的回答里抽取事实，跨厂商有 2 家以上一致才保留，再经过归纳、修复、去重，最后人工审核。
  - 我的判断：模型共识不等于事实（它们可能犯同样的错），**可信度中低**。
- **Data**：GitHub `benstaf/ipoagent`（MIT），公开 70 题，附 facts 和 rubric；另外 930 题私有。

### 7. ProFinR / ProFinAgent（ICML 2026，[PMLR](https://proceedings.mlr.press/v306/huang26ap.html)，清华 FIB 实验室）
- **Task**：528 道专家设计的题，覆盖 4 个金融领域，分三级：L1 数据检索、L2 数据分析、L3 端到端研究。配套的"金融工具宇宙"有 53 个工具，分 13 类。
  - 例 [原文 Table 2]：
    - L1 "What was the closing price of Meta Platforms (META) on Dec. 29, 2023?"
    - L2 "Calculate the 14-day RSI for Coinbase (COIN) from 2023-01-01 to 2023-06-30."
    - L3 "Produce a risk assessment report for Boeing (BA) covering supply chain disruptions and safety incidents (2024–2025)."
- **Capability**：工具使用、多源计算、跨文档对齐、长程规划与写报告。
- **Evaluation**：三个维度：
  - 数值精度：相对误差小于 1% 判对；
  - 工具对齐：与专家轨迹的工具类别算 Jaccard；
  - L3 合理性：两个 judge 都判通过，再乘以关键信息覆盖率。
  - 另有两阶段核验：LLM 查格式，领域专家审事实。一致率未写。
- **Performance**：
  - 原生模型：Claude Sonnet 4.6 总分 41.5%；GPT-5.2 29.7%，**L1 只有 16.8%**（简单检索反而差，因为它凭记忆答）；
  - 换成作者的 ProFinAgent 框架（DAG 规划 + 案例记忆）：Sonnet 4.6 83.3%，GPT-5.2 79.5%。
  - 主要问题：时间错位、编造数据、编造工具。
- **GT Construction**：作者只写了"expert-designed"，人数未写；参考答案在 execution_result 字段里，工具对齐用专家轨迹。
  - 我的判断：L1/L2 可以用行情 API 加 TA-Lib 程序化复算，**可信度高**；L3 **中**。
- **Data**：HF `huangchenglaile/ProFinR`（528 题，Apache-2.0），字段为 query、difficulty、expected_tool_types、execution_result；GitHub `tsinghua-fib-lab/ProFinAgent` 有工具实现。HF 例：「Who is the current CFO of Amazon in 2025?」→「Brian T. Olsavsky」。

### 8. Finance Agent Benchmark — Vals（[2508.00828](https://arxiv.org/abs/2508.00828)）
- **Task**：agent 用 Tavily 网页搜索、EDGAR 检索、HTML 解析等工具回答研究题，分 9 类，从检索到建模。
  - 例 [原文]："What was the quarterly revenue of Salesforce (NYSE:CRM) for the quarter ended December 31, 2024?"
- **Capability**："tasks from information retrieval to complex financial modeling"
- **Evaluation**：v1 把专家答案拆成要点 rubric，加一条"矛盾" rubric，由 LLM judge 打分；v2 改为"dealbreaker 门槛的部分分"，由 3 个 judge 组成评审团。没有报告与人工的一致率。
- **Performance**：论文 v1 o3 46.8%；**官网 v2.1（2026-11-19）Claude Fable 5.2 69.47%**；v2 时 Gemini 4 Argon 65.40%。专家做一题平均 16.8 分钟、$25.66。
- **GT Construction**：7 位来自投行、对冲基金、PE 的专家出题，每题由另一位专家复核。v2 共 927 题，v2.1 修了一批题并换了 judge，官网写明分数与 v2 不可比。
  - 我的判断：短答案部分**可信度高**，建模部分**中**。
- **Data**：v1 公开 50 题（CC BY 4.0）；v2/v2.1 公开 27 题，私有验证 450、测试约 450。**专业团队也要靠持续人工修题来维护**。

### 9. FinSearchComp（[2509.13160](https://arxiv.org/abs/2509.13160)，ICLR 2026，字节 Seed 等）
- **Task**：635 题，分三类：T1 时效数据获取、T2 简单历史查询、T3 复杂历史调查；分全球和大中华两个子集。
  - 例 [原文]："What was the total assets of Starbucks as of September 27, 2020?" → $29,374.5 million
- **Capability**："search proficiency and knowledge-grounded reasoning"
- **Evaluation**：LLM judge 加容差带（论文没写 judge 模型）；每个子集约 400 条人工核验，一致率 95%。
- **Performance**：Grok 4（联网）全球子集 68.9%，豆包（联网）大中华子集 54.2%；人类专家分别为 75.0 和 88.3。不联网时 T1 接近 0。
  - 主要问题：时间戳过期、单位/币种错误、财年日历错位、开盘价和收盘价混淆。
- **GT Construction**：50 位专家加 20 位资深评审，约 240 小时；每题由 1–2 人盲做复核，资深专家仲裁。
  - 我的判断：T2/T3 可以由 XBRL 生成，**可信度高**。
- **Data**：HF `ByteSeedXpert/FinSearchComp`（CC-BY-4.0），含题目、答案和解题 trace。

### 10. FinDeepResearch（[2510.13936](https://arxiv.org/abs/2510.13936)）
- **Task**：给定公司、市场和财年，写一份 6 节的研报。覆盖 64 家公司、8 个市场、4 种语言，共 15,808 个评分点。
- **Capability**：识别、计算、抽象、解释四层。
- **Evaluation**：LLM judge 加 rubric：识别和计算按 0/1，抽象按 claim 覆盖，解释按 10 分制；另有规则评的结构分。
- **Performance**：o3-deep-research 37.9；⚠️ 解释层最好只有约 20；中国内地和香港市场最难。
- **GT Construction**：先让多个 LLM 生成参考报告，再由 30+ 位专家两轮核验，每个事实至少两个来源交叉验证。
  - 我的判断：**可信度中**。
- **Data**：论文称在 OpenFinArena 公开，未核实。

### 11. ICBCBench（[2606.17458](https://arxiv.org/abs/2606.17458)，2026-06，行业联盟）
- **Task**：中英双语深度研究，分两个 track：客观题（短答案、选择、数值）和主观题（写长报告，按专家 rubric 评）。工具有 Search、Visit、多模态、Coding。
  - 例 ⚠️ [意译]："宣布推荐收购 Allfunds 的交易所运营商是谁？" → "Deutsche Börse; 1.7"（1.7 为 Allfunds 的管理资产，万亿欧元）
- **Capability**：检索与推理的准确性、多跳、图表等多模态材料、工具使用、引用有据、来源质量、**置信度校准**。
- **Evaluation**：
  - 客观题：GPT-5.4 judge，另算校准误差 RMSCE；
  - 主观题：Gemini-3.1-Pro 按 100 分 rubric 打分；
  - 最终分 = 0.8×专家 rubric 分 + 0.1×引用 + 0.1×来源；
  - 人工：25 位专家评了 36 个样本，经 ICC 过滤后保留 15 题；⚠️ 专家与 LLM 的 Spearman 只有 0.643。
  - 我的判断：主观题 judge 的可信度**中**。
- **Performance**：英文总分最好 DeerFlow（+GPT-5.5）58.67；中文最好 OpenClaw（+GPT-5.5）63.38；英文主观题 o3-deep-research 71.84；英文客观题最好 52.50。
  - ⚠️ 主要问题：校准差、遇到多模态掉分、报告流畅但有事实错误。
- **GT Construction**：
  - 客观题：从 2 万+ 份报告里经 5 个阶段产生，由多个 LLM 初筛，至少 3 名学生做题并交叉复核（共 15 名学生）；
  - 主观题：218 个候选选出 40 个，专家起草 rubric、GPT-5.4 润色、至少 3 位专家审核。
- **Data**：HF `DeepFin-Intelligence/ICBCBench`（数据 Apache-2.0，代码 MIT）：公开客观题 80、主观题 40（含答案和 rubric），另有 60 题私有。原始报告不分发，只给 URL。

### 12. FinRpt（[2511.07322](https://arxiv.org/abs/2511.07322)，AAAI 2026）
- **Task**：给定股票代码和日期，生成一份 6 节的个股研报，包括买入/卖出评级。输入有 6 类数据：公司信息、财务指标、公告、新闻、价格、指数。论文同时提出了 9 个 agent 组成的 FinRpt-Gen 框架。
  - 例 ⚠️：贵州茅台的风险分析输出为 "Public opinion risks, Policy fluctuation risks, Counterfeit product risks…"
- **Capability**：读财报、判断新闻影响、识别风险、根据价格走势给评级。
- **Evaluation**：
  - 评级准确率（与事后实际涨跌比对）、ROUGE-L、BERTScore、NumberRate；
  - 6 项指标由 GPT-4o 做两两比较，正反两种顺序各判一次，结论翻转就记为平局；
  - 3 位分析师各评了 30+30 份报告，⚠️ Fleiss κ 0.84–0.89；GPT-4o 与人工多数意见 50 对里一致 45 对。
- **Performance**：⚠️ 调整后胜率最高的是 Qwen2.5-7B-SFT-RL，0.69；人工评分专家研报 4.30，FinRpt 生成的 4.20。
- **GT Construction**：**参考研报是 GPT-4o 用 FinRpt-Gen 生成的**；评级标签被强制对齐到事后实际涨跌，再用东方财富的专家研报做润色。共 6,825 篇，覆盖中证 800，时间是 2024-09 到 2024-11。
  - 我的判断：参考报告是模型写的，**作为 GT 可信度低**；评级用两个月窗口的涨跌，**噪声大**。它更像一个训练集。
- **Data**：HF `jinsong8/FinRpt`（train 5,556 / val 617 / test 652），代码在 GitHub；许可未写明。

### 13. GAUGE（[2607.24889](https://arxiv.org/abs/2607.24889)，v2 改名为 "One Analyst Is Not Ground Truth"）
- **Task**：扮演初级卖方研究员。给 3 年经审计的历史数据和一个基准日期（不给一致预期），要求交出：
  - 一个 11 个 sheet、全部由公式驱动的工作簿（三表、收入拆分、债务表、WACC、DCF、敏感性、自检）；
  - 一份 3–5 条结论的 memo；
  - 一份假设文件。
  - 只能用 Python，不能联网，最多 50 轮或 1,800 秒。共 196 题，例如 Accenture（ACN）。
- **Capability**：分两部分：**机械构建**（配平、活公式、无硬编码）和**金融判断**（驱动因素、WACC、利润率、估值），共 56 个细项、5 大支柱。
- **Evaluation**：
  - 56 个细项中，29 个由**确定性代码检查**，23 个由 LLM judge 判（Claude Opus 4.8，投 5 次取多数），4 个用"区间"检查；另有 8 道有效性门槛。
  - judge 与 3 位专家在 460 例上一致 86.7%，κ 0.81；**专家之间是 89.4%，κ 0.85**，两者接近。
  - 我的判断：**自动化程度高**。
- **Performance**：最好的是 Claude Fable 5，53.4；Opus 4.8 49.6；GPT-OSS-120B 9.3。
  - **人类基线**：资深分析师 88.3，初级 66.0，学生 43.2。
  - 构建分和判断分的差距，中位数 26 分。
  - ⚠️ 细项举例：FCF 定义通过率 98%，但区分维护性与扩张性资本开支只有 2%，针对经营驱动因素做敏感性分析只有 9%，WACC 很粗（40% 是 50bp 的整数倍）。
- **GT Construction**：**没有标准答案**，而是用"**专业实践区间**"打分。区间来自 1,001 份授权的分析师估值工作簿（922 个标的、25 个 GICS 行业组），分三层：
  - **方法层**：该标的参考工作簿自己的 WACC ±374bp，隐含倍数 ±20%；
  - **行业层**：同一 GICS 组所有工作簿的 p10–p90；
  - **公司层**：只用来校准区间宽度，不参与打分。
  - WACC 取方法层和行业层的交集。落在严格区间得 2 分，落在放宽区间得 1 分，区间外 0 分。
  - 留出验证：行业层 WACC 覆盖率 82.4%，**能识别 85.4% 的伪造值**（在真值上偏移 ±3 个单位）。
  - 我的判断：**这是名单里最值得借鉴的 GT 思路**——判断类题目不设唯一答案，用专业实践的分布做区间，机械部分交给程序检查。
- **Data**：**尚未公开**（论文写"future version"）。方法层面（rubric、门槛、评分器、judge prompt）称会公开；工作簿需要签研究使用协议。

### 14. P298「Evaluating Frontier Agents on End-to-End Investment Banking Workflows」≈ BankerToolBench
- **P298 本身**：ICLR 2026 的两场 workshop poster（[DATA-FM](https://iclr.cc/virtual/2026/10019766) 和 [Advances in Financial AI](https://iclr.cc/virtual/2026/10016536)）。
  - 摘要：175 位投行人员，VP/MD 级别的真实需求，可用 FactSet 和 SEC EDGAR，产出多文件交付物，单题最多 8 个银行家小时，测了 8 个前沿模型，**最好的 Claude Opus 4.5 成功率 33.8%**。
  - OpenReview 有人机验证，正文读不到。
- **arXiv 正式版 BankerToolBench**（[2604.11304](https://arxiv.org/abs/2604.11304)，Handshake AI，NeurIPS 2026）：主题相同、数字不同，可以看作 P298 的扩展版。
  - **Task**：100 题，在沙箱里（data room、行情 MCP、EDGAR）产出 Excel、PPT、PDF、Word。人类平均每题 5 小时，最长 21 小时。
    - 例 [原文]："You are an analyst in the M&A group at a bulge-bracket bank. … The final deliverable should be an Excel file with the accretion-dilution model for this potential transaction."
  - **Capability**：建模与公式完整性、取数、判断、跨交付物一致性、可直接给客户的格式。
  - **Evaluation**：每题约 150 条加权二值 rubric，由 agent-as-judge "Gandalf"（Gemini 3 Flash Preview）实际打开文件检查；与人工一致 88.2%（κ 0.76），**高于人与人之间的 84.6%**。
  - **Performance**：GPT-5.4 任务通过率 16%，3 次全过 13%；**银行家认为可直接交客户的比例是 0%**。失败原因：公式/代码 41%、推理 27%、检索 18%、编造 13%。
  - **GT Construction**：502 是合作银行家总数，其中 172 人直接参与造题，累计 5,700+ 小时；只有部分题目有 golden 交付物。
    - 我的判断：**无法自动化**。
  - **Data**：HF（CC-BY-4.0）公开任务、rubric、部分 golden 交付物和约 5.5 GB 数据。

### 15. FinForesight（[2611.01621](https://arxiv.org/abs/2611.01621)，2026-11，OpenFinMind）
- **Task**：根据检索到的证据做预测，覆盖 A 股、美股、港股，分 4 类：估值区间 VAL、排序 RANK、事件 EVT、基本面 FUND；另有两类诊断题：反事实 CF 和计算 CALC。
  - 例 [原文]：五粮液（000858）"Using public information available before 2026-01-30, estimate bear, base, and bull price targets." 2026-02-27 的实际参考价为 104.05 元；GPT-4.1-mini（配 GPT-Researcher）给出 95/110/125。
- **Capability**：时点约束下的预测、反事实推理、多步计算；对改写提示和数值扰动的稳健性。
- **Evaluation**：**完全确定性，不用 LLM judge**：VAL/FUND 看相对误差，RANK 看 Spearman 和 top-K，EVT 用 Brier 技能分，CF 看方向是否一致，CALC 按容差判对。
- **Performance**：最好 0.7099（GPT-Researcher + Gemini 3.1 Flash-Lite），22 种配置在 0.56–0.71 之间。
  - ⚠️ **27 组对比里有 25 组，模型在训练数据时期内的题（T1）得分高于知识截止之后的题（T2）**；
  - 改写提示会改变 16.8–23.7% 的预测。
- **GT Construction**：GT 来自实际行情（Yahoo）和交易所、EDGAR、统计局等的正式发布；题目由模板生成。
  - **防泄漏**：三种检索策略对比——只用搜索、PIT 控制、PIT 加 LLM 过滤；对网页逐页审计时间戳；按每个模型各自的知识截止日生成实例。
  - ⚠️ 美股"T2 与实时的差距"：只用搜索 0.120，加 PIT 0.062，再加过滤 0.029。
  - 我的判断：GT 完全程序化，**可信度高**；**量化泄漏的方法可以直接借用**。
- **Data**：HF `OpenFinMind/FinForesight`（CC-BY-4.0，约 1,100–1,300 条，与论文数字不一致）；代码 Apache-2.0。

### 16. CryptoAnalystBench（[2602.11304](https://arxiv.org/abs/2602.11304)，2026-02，Sentient）
- **Task**：用行情、搜索、链上数据和代码工具，针对加密货币或 DeFi 问题写长篇分析，**没有参考答案**。
  - 例 [原文]："Which altcoins are breaking all-time highs this week?" 某个代币的历史高点，一个工具给 $0.195、另一个给 $0.1812，回答没有核对这一冲突。
- **Capability**：工具编排、综合大量工具输出、时效、引用归属、对账冲突来源、风险提示。
- **Evaluation**：LLM judge 按 1–10 分评相关性、时效、深度、数据一致性（默认 DeepSeek-V3.1）；另有 claim 级流水线，把每条 claim 判为精确、推导或编造。**专家与 judge 的 κ 只有 0.35–0.42**。
  - 我的判断：整体打分的自动化**可信度低**；claim 级的编造检测更可靠。
- **Performance**：GPT-5.2、Kimi K2.5 各项得分都在 8.8–9.6 之间，**已经饱和**；所有模型编造的 claim 都低于 6%。
  - 主要问题：信息过期或没标时间范围、缺少风险提示、综合太浅、没有对账来源冲突。
- **GT Construction**：198 题来自生产流量：约 2,000 条聚类 → 去重后约 650 → 按难度过滤到约 350 → 专家精选 198。rubric 参考了加密分析师的意见。
- **Data**：GitHub `sentient-agi/CryptoAnalystBench`（Apache-2.0），含 198 题、judge 脚本和错误分类。

### 17. AgenticFinBench（[2611.04813](https://arxiv.org/abs/2611.04813)）
- **Task**：230 个真实请求（中文 189、英文 41），8 类，L1–L4 四级，**没有参考答案**。
  - 例 [原文]："Can you compare stocks wdc and stx"
- **Capability**：任务完成度、推理、证据与准确性、适用范围；另外检查 claim 能否在轨迹里找到出处、会不会被外部事实推翻。
- **Evaluation**：无参考 rubric 加两阶段 claim 审计，合成 Q（0–100），judge 为 DeepSeek V4.1 Flash。与专家一致 84.8–92.3%（κ 0.70–0.82），**与专家之间相当**。
- **Performance**：GPT-5.6 Sol（Codex CLI）Q=89.2。**18 个配置全都出现过幻觉 claim**，有幻觉的回答占 0.9–47%；L1 到 L4 下降约 10 分；投资规划类最弱。
- **GT Construction**：从生产日志过滤出题，专家匿名化并审核；rubric 由 LLM 只看题面起草，再审核。
  - 我的判断：rubric 部分可信度**中**，审计部分**高**。
- **Data**：公开题目和 rubric（5,817 条正向 + 1,780 条负向）；许可未写明。

### 18. BuySideFlow（[2611.12966](https://arxiv.org/abs/2611.12966)，2026-11）
- **Task**：在一个授权中国金融数据库的固定快照（110 张表、4,547 列）上写 SQL 或 SQL+Python 流程，回答买方研究问题；结果要和参考一致，**并且遵守时点约束**。共 408 题（股票 166、基金 125、固收 93、宏观 24）。
  - 例 [原文]："Task stock_069 asks which three Shenwan level-1 industries account for the largest total weight in the CSI 300 index."
- **Capability**：数据检索与选择、金融计算、SQL/Python 流程；**处理披露日截断、历史状态和记录版本的时间推理**。
- **Evaluation**：
  - 结果按表格程序化比对（统一列名、声明精度、行序）；
  - 图和文字由 LLM 按清单打分；
  - **专家审计实际执行的流程，用 20 类代码标注 PIT 违规**：先由 GPT-6.1 SOL 提出标签，再由专家确认；⚠️ 与独立标注员一致 91%，κ 0.818。
  - 人工参与很重。
- **Performance**：结果准确率 16.2–36.8%。**在 380 个结果正确、经过审计的运行中，193 个（50.8%）有确认的 PIT 违规**——一半"答对的题"用了当时还拿不到的信息。
  - 主要违规类型：用了后来才披露的报告；拿当前状态代替历史状态（比如当前的上市状态）；没剔除已过期的版本。
- **GT Construction**：
  - 券商资产配置部的 2 位研究员收集问题，1 位配置专家筛选，3 位基金经理审核；
  - 数据工程师和量化研究员写参考流程；
  - 共 4 轮审核，**51% 的题在审核中至少被记过一次问题**。
  - 我的判断：GT 由参考程序执行得到，**可信度高**；PIT 审计可以用"披露日"字段做规则自动化一大部分。
- **Data**：⚠️ 题目、参考程序和答案都有提供；数据库样本在阿里云上，需申请只读账号，受原授权约束。许可和链接未写明。

### 19. FAAB —— **未找到**
- 试过的办法：arXiv 搜 "FAAB"；arXiv 按关键词搜 "failure detection blame attribution financial multi-agent"；网页搜 FAAB 的三种可能全称。都没有找到对应论文。
- 相近的工作：
  - **CausalLoss-Fin**（[2609.25960](https://arxiv.org/abs/2609.25960)）：把金融 agent 的损失归因到决策或基础设施故障；
  - **Who&When**（[2505.00212](https://arxiv.org/abs/2505.00212)）：通用的多 agent 失败归因；
  - **BLAME/POIROT**（[2606.02282](https://arxiv.org/abs/2606.02282)）：环境里包含 TradingAgents 交易系统。
- **麻烦把 FAAB 的链接或全称发我**，我按同样的模板补上。

### 20. Investor's Last Exam（[2610.38342](https://arxiv.org/abs/2610.38342)）
- **Task**：86 个买方研究任务（公司研究 78、市场预测 8），在一个**按版本存储、严格截断时点的语料库**（343 万个文档版本）里完成。
  - 例 [原文]："Task O80 asks for Tesla's Q2 2026 deliveries, GAAP revenue, and GAAP automotive gross margin"
- **Capability**："coordinate evidence retrieval, computation, and financial reasoning across multi-step workflows"
- **Evaluation**：7 个维度的加权 rubric；预测题按实际结果用 interval score 评分。judge 是 GPT-6 Astra，**它同时也是被测模型**；没有报告一致率。
- **Performance**：GPT-6 Astra 总分 68.1，"预测与建模"维度约 52.5。⚠️ **放开公开网页时，Astra 有 57% 的轨迹引用了截止日之后的来源**。
- **GT Construction**：专家编写，AI 辅助；预测题 GT 用实际结果。
- **Data**：HF `HenryJ12/InvestorLastExam` 上有 86 题、1,472 条 rubric 和 ground truth，但 GitHub 写的是"不分发"，两边矛盾。都没有写许可。

### 21. DealTrace（NeurIPS 2026 workshop，Agentic AI Benchmark for Enterprise Tasks，[页面](https://neurips.cc/virtual/2026/160081)）
- **Task**：复核一笔 PE 交易：把叙述性 memo 和背后的 Excel 模型对照着读，重建估值所依赖的预测，再写出投资建议。流程分多个阶段（你写的是 5 个阶段），**每个阶段都对照它所引用的来源评分**。论文正文读不到，没有例题。
- **Capability**：带出处的多阶段金融推理。
- **Evaluation**：逐阶段对照来源评分，最终写作由 4 个 judge 组成的评审团打分。具体模型和一致率未知。
- **Performance**：摘要里唯一的数字："**把预测阶段替换成真值，每个模型都比上一级提升 20 分以上；把抽取或对账阶段替换成真值，只提升几分**"——预测是瓶颈。
  - 方法是**干预式失败定位**：修复或移除某个阶段，看最终结论依赖的是哪里。
- **GT Construction**：真实 memo 配真实模型；标注者是谁未写。
  - 我的判断：干预式定位**可以自动化**，前提是每个阶段都有可程序化的真值。
- **Data**：未知（OpenReview 页面打不开）。

### 22. DeepFinance（[2611.10926](https://arxiv.org/abs/2611.10926)，2026-11，Julius Research）
- **Task**：超长程的 PE/IB 任务（估值、尽调、承销、建模）。每题是一个需求加一个 data room（平均 19 个文件：xlsx、docx、eml、PDF、CSV），**人类平均每题约 27.1 小时**，共 21 题。
  - 例 [原文节选]："The IC is meeting this afternoon on Corliss."
  - 参考答案 [意译]：全现金报价 5,080.3 万美元，不向 Quarrie 付款，2026-04-01 交割。
  - 一条 rubric [原文]："The workbook reports reconciled FY2025 revenue of 42.880."
- **Capability**：分三类：Output（计算和交付物）、Workflow（找到并用上证据）、Judgment（证据是否支撑假设和决策）；另外考察对账冲突来源、保持可审计。
- **Evaluation**：通过的 rubric 条目占比，每题跑 10 次取平均；grader 同时看交付物和轨迹，judge 模型未写，一致率未写。
- **Performance**：GPT-6 Astra（max）57.6%（置信区间 49.5–66.2），Opus 5.5 54.8，Sonnet 5.5 54.6，**前 4 名在统计上分不开**。
  - 主要问题：**输入错了但计算是对的**；**找到了关键证据却没有据此行动**；上游错误层层传递；几乎不质疑给定的假设。
- **GT Construction**：21 题由 PE/IB 从业者（摩根大通、瑞银、Evercore 背景）编写，使用脱敏后的真实数据；专家 rubric 平均 84 条；参考解是工作簿；由 agent 验证器加人工同行评审。
  - 我的判断：只有 21 题，置信区间宽约 17 个点；GT **无法自动化**。
- **Data**：未公开，只有 [leaderboard 和样例](https://www.juliusresearch.ai/blog/deep-finance)。

---

## 三、重新分类

### 主分类：按 GT 的获得方式（推荐）

| 类别 | 数量 | 成员 | 特点 |
|---|---|---|---|
| **G1 专家手写的确定答案** | 5 | FAB、FinSearchComp、FinFIRST、ProFinR、DataClawBench | 质量高但贵（FinFIRST 录用率 9.8%）、规模小；**最适合做种子** |
| **G2 由数据库、程序或事后真实数据给出答案** | 4 | FinRetrieval（数据库值）、BuySideFlow（参考 SQL）、FinForesight（实际行情）、FinDeepForecast（官方发布） | 可以自动化、可以刷新；**这就是 AutoFinBench 的路线** |
| **G3 LLM 生成 + 人工验证** | 4 | FinanceGym（LLM 写 rubric，专家验证 82%）、FinDeepResearch（LLM 写参考报告）、ICBCBench（LLM 初筛 + 学生和专家复核）、FinRpt（LLM 写报告，基本没有核验） | 可信度取决于人审的深度，FinRpt 最弱 |
| **G4 没有参考答案，只有 rubric 或审计** | 4 | AgenticFinBench、IPO Agent（模型共识）、CryptoAnalystBench、Investor's Last Exam（rubric + 实际结果） | 可信度由 rubric 质量和 judge 偏差决定；CryptoAnalyst 的 κ 只有 0.4 |
| **G5 专业交付物 + 专家 rubric、参考解或实践区间** | 4 | P298/BankerToolBench、DeepFinance、DealTrace、GAUGE | 最接近真实工作、成本最高；**GAUGE 用实践区间替代唯一答案** |
| 未知 | 1 | FAAB | — |

### 副分类：按底层材料

| 材料 | 数量 | 成员 |
|---|---|---|
| **M1 公司披露和研究语料**（SEC 文件、招股书、带版本的语料库） | 5 | FAB、FinDeepResearch、IPO Agent、Investor's Last Exam、FinanceGym |
| **M2 开放网页和多源新闻** | 5 | FinSearchComp、FinFIRST、ICBCBench、FinDeepForecast、FinRpt |
| **M3 结构化数据库或金融 API** | 5 | FinRetrieval、BuySideFlow、DataClawBench、ProFinR、FinForesight |
| **M4 真实用户请求日志** | 2 | AgenticFinBench、CryptoAnalystBench |
| **M5 交易 data room 或 Excel 模型** | 4 | P298/BTB、DeepFinance、DealTrace、GAUGE |

### 另外两个视角
- **评结果还是评过程**：评过程的有 7 个——FAAB、DealTrace（逐阶段）、BuySideFlow（PIT 审计）、FinFIRST（证据链）、DataClawBench（里程碑）、ProFinR（工具对齐）、CryptoAnalystBench（claim 级）。**这类正在快速增加**。
- **是否有时点约束**：FinanceGym、FinForesight、BuySideFlow、Investor's Last Exam、FinDeepForecast、FinFIRST（题面写明"as of"日期），一共 6 个，都是 2026 年的工作。**时点约束已经成了主流方向**。

### 能不能当种子（题目和 GT 都公开）
- **可以**：FinFIRST（123 题）、FinRetrieval（500 题 + 轨迹）、DataClawBench（492 题）、ProFinR（528 题）、FinSearchComp（635 题）、ICBCBench（120 题）、FinForesight、FinRpt（6,825 篇）；
- **只有题目或 rubric**：FinanceGym、AgenticFinBench、IPO Agent、CryptoAnalystBench、Investor's Last Exam；
- **不可以**：GAUGE（待放出）、DeepFinance、DealTrace、P298、BuySideFlow（数据库需授权）、FAB（大部分私有）、FinDeepResearch 和 FinDeepForecast（平台上，未核实）。

---

## 四、可以往哪些方向挖（结合这 22 个和其他领域 agent 的进展）

### 先看这批 benchmark 揭示的 5 个事实
1. **"答对"被严重高估**：
   - BuySideFlow：答对的里有 50.8% 违反时点约束；
   - Investor's Last Exam：57% 的轨迹引用了截止日之后的来源；
   - FinForesight：27 组里有 25 组，训练期内的题得分更高；
   - FinanceGym：截止日前约 46%，截止日后约 12%。
2. **工具和 harness 的影响大于模型本身**：FinRetrieval 有结构化 API 时 90.8%，只用网页 19.8%；ProFinR 原生 41%，用作者的框架后 83%。
3. **会构建，不会判断**：
   - GAUGE：构建与判断的差距中位数 26 分；
   - DeepFinance：找到证据却不行动，也不质疑假设；
   - BTB：可直接交客户的比例 0%；
   - DealTrace：预测阶段是瓶颈。
4. **judge 的可靠性差别很大**：原子化、二值化的标准一致性高（FinFIRST κ 0.82、GAUGE 0.81）；整体打 Likert 分的一致性低（CryptoAnalyst 0.35–0.42、ICBCBench ρ 0.64）。
5. **高质量 GT 极贵，样本因此很小**：DeepFinance 21 题，Investor's Last Exam 86 题，FinFIRST 123 题；BTB 花了 5,700 小时。

### 方向（按对 AutoFinBench 的价值排序）

**① 程序化 GT + 换期，并且自动做 PIT 审计（主线）**
- FinRetrieval 的"数据库值 + 源文件截图 → LLM 写题"和 LiveSearch 的"题目即程序"都证明了这条路可行。
- 用 FinFIRST、FinSearchComp T2/T3、ProFinR L1/L2、FinRetrieval 做种子，把题目改写成 XBRL companyfacts 或行情数据上的程序，然后换报告期、换公司。
- **新机会**：XBRL companyfacts 的每条事实都带 `filed`（披露日期）字段。拿它和 agent 的工具调用轨迹对照，就能**自动检测 PIT 违规**。BuySideFlow 目前靠专家人工审计，这一步可以用程序完成，而且能直接量化"答对的里有多少是偷看的"。

**② 判断类题目用"实践区间"做 GT（借鉴 GAUGE）**
- 涉及判断的题（WACC、增长假设、估值倍数）不设唯一答案，而是用同行业、同期的公开数据（XBRL、可比公司）构造 p10–p90 区间；机械部分交给程序检查。
- GAUGE 的区间来自授权的分析师工作簿；我们可以试着**只用公开数据**来构造区间。这本身就是一个研究问题，可以接到 `step1/GT_CREDIBILITY.md`。

**③ 干预式失败定位（借鉴 DealTrace，回应 FAAB 这一类）**
- 程序化的题天然可以拆成"取数 → 对齐 → 计算 → 判断"几个阶段，每一步都有程序算出的真值。依次把某一步替换成真值，看最终得分提升多少，就能**自动定位瓶颈**。
- 这样不需要人工标注失败，也比 FAAB 式的事后归因更客观。

**④ 按能力缺口设计算子，由 solver 反馈驱动演化（AutoSciBench 的闭环）**
- 每个缺口对应一个算子：
  - **期间口径**（FinRetrieval 中占 46%）：财年与日历、起止年份；
  - **历史状态与当前状态**（BuySideFlow 的 A2 类违规）；
  - **来源冲突对账**（CryptoAnalyst、DeepFinance）；
  - **不给答案、只给假设**（GAUGE 的判断部分）；
  - **给出带错误的前提**（DeepFinance：模型几乎不质疑；我们 step2 的 D 组也全错）。
- solver 在哪里失败，就沿哪个方向继续加难度；每一步都要通过程序化 GT 和 grader 变异测试，避免"变难其实是题变坏了"。

**⑤ grader 的可信度：原子化标准 + 变异测试**
- 证据表明原子二值标准明显比整体 Likert 打分可靠。把 rubric 拆成原子标准，再往正确答案里注入已知错误（换口径、错一期、编一个数），看 grader 能不能抓出来。
- GAUGE 用 ±3 单位的伪造值测出 85.4% 的识别率，就是这个思路，可以直接照着做。

**⑥ 固定 harness，把模型能力和工具能力分开报告**
- FinRetrieval 和 ProFinR 都说明工具和框架带来的差距在 40–70 分。AutoFinBench 至少要报告三种设置：闭卷、标准工具、给定证据，并说明每道题在哪种设置下测的是什么能力（这和我们 step1 的"算子 × 设置"矩阵是同一件事）。

**⑦ 用自动生成解决样本太小的问题**
- 21 题的置信区间宽约 17 个点，前几名在统计上分不开。程序化生成可以以几乎零的边际成本扩到几千题，**这是对 DeepFinance、FinFIRST 这类高成本 benchmark 最直接的补充**。

**对 AutoFinBench 的建议优先级**：
1. 方向 ① + ⑥：马上可以做，已有 `xbrl_series.py`；
2. 方向 ③ + ④ + ⑤：这是论文的方法贡献；
3. 方向 ②：独立的研究点，可以放在第二篇。
