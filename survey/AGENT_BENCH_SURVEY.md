# 金融 Agent Benchmark 调研报告（27 个）

> **用户的 22 个名单对应的主报告见 [FIN_AGENT_BENCH_22.md](FIN_AGENT_BENCH_22.md)**。本文是更早的一版，写的时候还没收到名单，可以作为补充材料。

日期：2026-11-26 · 用时约 40 分钟 · 作者：Claude（为 AutoFinBench 准备）

> **⚠️ 先说明名单问题**：你的消息里写了"这是我要调研的名单"，但名单没有一起发过来。我检查了仓库和这台机器上最近新增的文件，都没有找到。你说过不能问你，所以我按下面的办法定了名单：
> - **核心 18 个**：仓库 `survey/benchmark_pool.csv` 中属于 **agent / 金融文件研究** 类的条目，加上我们之前检索到的主流金融 agent benchmark；
> - **补充 6 个**：这次新检索到的（见第一部分）；
> - **追加 3 个**：Investor's Last Exam、CFAgentBench、FinTrace（第二部分 E 组）。
>
> 如果你原本的名单里有别的条目，发给我就能按同一模板补上。
> 纯 QA / 数值推理类数据集（FinQA、TAT-QA 等）不在本次范围内，见 [BENCHMARK_POOL.md](BENCHMARK_POOL.md)。
>
> **可靠性**：信息来自论文 arXiv HTML 全文和 GitHub / HF 页面。长论文的后半部分有时只拿到工具生成的摘要，凡是来自摘要的数字都标了 ⚠️。"我的判断"是我的观点，不是论文的结论。

---

## 总览表

缩写说明：**Q**=题目，**GT**=标准答案，**R**=rubric，**Src**=原始材料。✅ 公开，◐ 部分公开，❌ 不公开，? 未说明。

| # | Benchmark | 任务形态 | 评估方式 | 当前最好成绩 | 数据公开 |
|---|---|---|---|---|---|
| 1 | FinanceBench | 文件短答案 QA | 人工判对错 | GPT-4-Turbo 长上下文 79%（2023） | Q/GT/Src ◐（150 条） |
| 2 | Vals Finance Agent (FAB) | 工具研究题 | rubric + LLM judge（v2 起改为 3 个 judge 评审团） | 论文 o3 46.8%；官网 v2.1 Claude Fable 5.2 69.47% | ◐（v1 50 条 / v2.1 27 条公开） |
| 3 | FinSearchComp | 搜索短答案 | LLM judge + 容差 | Grok 4 68.9%（人类 75.0） | Q/GT ✅ |
| 4 | FinAgentBench | 文档/段落排序 | nDCG | 段落 nDCG@5 0.42 | ? |
| 5 | Fin-RATE | 文件 QA（跨公司/跨年） | 3 个 LLM judge 集成 | 跨年 43.5%（人类 85.9） | Q/GT/Src ✅ |
| 6 | FrontierFinance (Samaya) | 投研长答案 | rubric，3 个 judge 投票 | 56.0%（自家 harness） | Q/R ✅（gated） |
| 7 | AgenticFinBench | 真实请求长答案 | 无参考 rubric + claim 审计 | Q=89.2 | Q/R ✅ |
| 8 | FinToolBench | 工具调用 QA | judge + 轨迹合规 | Soft 0.82 | Q/工具 ◐ |
| 9 | MBABench | Excel 建模 | judge 对照 golden 逐项 | L4 72.6/100 | Q/GT ✅ |
| 10 | FrontierFinance-CU (Kensho) | Excel+PPT 建模（computer use） | rubric judge + 人工 | 人工评分：GPT-5.4 70.9%（人类 77.2%） | ❌（forthcoming） |
| 11 | FORCE-Bench (Microsoft) | ERP + 公开数据研究 | 8 维 rubric judge | 0.80（自家 agent） | Q ✅ |
| 12 | IPO Finance Agent | S-1 尽调 | 模型共识生成的 rubric | GLM-5.2 79.8% | ◐（70 条） |
| 13 | FinDeepForecast | 实时预测 | 确定性容差 | 39.5% | ?（平台） |
| 14 | FutureX-Finance | 股价预测 | 误差公式 | 46.4 | ❌（尚未放出） |
| 15 | LiveSearch | 实时行情搜索 | 执行程序得出 GT | 76.7 | ◐（元组） |
| 16 | SecQue | 文件分析长答案 | 5×GPT-4o judge | GPT-4o 0.69 / 0.79 | Q/GT/Src ✅ |
| 17 | BizFinBench | 中文多任务（含工具使用） | EM + GPT-4o judge | o3 73.9 | ✅（NC） |
| 18 | AI-Trader | 实盘模拟交易 | 收益率/夏普等 | 美股 CR 9.56% | 代码 ✅ |
| 19 | **BankerToolBench** 🆕 | 投行交付物 | agent-as-judge rubric | 0% 被评为 client-ready | Q/R/Src ✅，GT ◐ |
| 20 | **FinDeepResearch** 🆕 | 公司研报 | rubric judge | 37.9 | ?（平台） |
| 21 | **Deep FinResearch Bench** 🆕 | 业绩前瞻研报 | judge + 预测误差 | 2.31（分析师 2.84） | ❌ |
| 22 | **FinGAIA** 🆕 | 中文 GAIA 式任务 | 人工为主 | 48.9（专家 84.7） | ◐（13 条） |
| 23 | **FinMCP-Bench** 🆕 | MCP 工具链 | 工具 P/R/F1 | 多轮 EMR ≤4.1 | Q/GT ✅ |
| 24 | **Bank-World** 🆕 | 银行状态变更工作流 | 状态检查 + rubric | 单轮 full-pass 55% | ❌ |
| 25 | Investor's Last Exam ➕ | 时点截断的买方研究 | rubric + 实际结果 | GPT-6 Astra 68.1 | ◐（HF 有任务和 rubric，与 GitHub 说法矛盾） |
| 26 | CFAgentBench ➕ | 建筑金融 ERP 操作 | 状态差异 oracle | pass^1 0.67 / pass^5 0.38 | ◐ |
| 27 | FinTrace ➕ | 多轮 MCP 工具轨迹 | 3 项算法指标 + 6 项 judge 指标 | Opus 4.6 0.788 | Q ✅（MIT） |

---

## 一、建议补充的高质量 benchmark（检索约 4 分钟）

| 名称 | 为什么值得放进来 |
|---|---|
| [BankerToolBench](https://arxiv.org/abs/2604.11304)（Handshake AI，NeurIPS 2026） | 目前规模最大、最"真"的投行交付物 benchmark：Excel/PPT、约 150 条 rubric/题、人类平均 5 小时一题；数据和 rubric 完全公开（CC-BY-4.0） |
| [FinDeepResearch](https://arxiv.org/abs/2510.13936) | 8 个市场、4 种语言的公司研报，15,808 个评分点；按能力分为识别、计算、抽象、解释四层 |
| [Deep FinResearch Bench](https://arxiv.org/abs/2604.21006) | 唯一用**真实卖方分析师报告**做对照的 benchmark，同时考察预测和估值精度 |
| [FinGAIA](https://arxiv.org/abs/2507.17186) | 中文金融版 GAIA，有专家人类基线（84.7 对 48.9） |
| [FinMCP-Bench](https://arxiv.org/abs/2603.24943)（ICASSP 2026） | 真实 App 日志 + MCP 工具，GT 是工具调用轨迹，覆盖多轮场景 |
| [Bank-World](https://arxiv.org/abs/2610.39733) | 金融里少见的 **τ-bench 式状态环境**（审批、权限、记账），用确定性状态检查评分 |

另外追加读了 3 个（第二部分 E 组）：Investor's Last Exam、CFAgentBench、FinTrace。还看到但没读的：FinNextAssist、FinanceHarness（是系统，不是 benchmark）。

---

## 二、逐篇调研

每篇固定 6 项。"我的判断"给出两个打分：**评估可自动化程度**和 **GT 自动化后的可信度**，各分高/中/低。

### A 组：文件与搜索型研究题

#### 1. FinanceBench（[2311.11944](https://arxiv.org/abs/2311.11944)，2023-11，Patronus AI）
- **Task**：给定 SEC 文件（10-K/10-Q/8-K/业绩材料），回答开卷问题，共 10,231 题。例 [原文]："What is Boeing's FY2022 cost of goods sold (in USD millions)?" → "$63,078 million"
- **Capability**：信息抽取、数值推理、逻辑推理，以及在长文件中检索。
- **Evaluation**：由研究团队成员人工标注"正确 / 错误 / 拒答"，允许单位和四舍五入的小偏差。人工占 100%。
  - 我的判断：**自动化程度高**。短答案加单位，用规则加容差再加 LLM 抽取就能评（SecQue 的 judge 与人工 F1 达到 0.85）。
- **Performance**：GPT-4-Turbo 长上下文 79%，oracle 证据 85%，共享向量库仅 19%（68% 拒答），闭卷 9%。
  - 主要问题：编造的错误答案多于拒答；顺序效应很大（上下文放前面 78%，放后面 25%）。
  - 这是 2023 年的结果，现在的 agent 应该高很多，但论文没有新数据。
- **GT Construction**：招募 20 名标注员，淘汰 5 名，其中 13 人写题、2 人抽取指标，最后由一名资深分析师审核，周抽检 10–20%。材料是 40 家公司 2015–2023 年的 361 份文件。
  - 我的判断：7,983 道"指标生成题"来自结构化数据，用 XBRL 重算后**可信度高**；领域题和开放题**可信度中**。
- **Data**：GitHub 公开 150 条，含 question、answer、evidence 原文、justification、推理类型和 PDF。全集需邮件申请。数据许可未写明。

#### 2. Vals Finance Agent Benchmark（[2508.00828](https://arxiv.org/abs/2508.00828)，2025-05，Vals AI）
- **Task**：agent 用工具（Tavily 网页搜索、EDGAR 检索、HTML 解析、信息提取）回答 537 道研究题，分 9 类，从检索到建模。例 [原文]："What was the quarterly revenue of Salesforce (NYSE:CRM) for the quarter ended December 31, 2024?"（论文没给答案）
- **Capability**："tasks from information retrieval to complex financial modeling"，即多步工具研究。
- **Evaluation**：把专家答案拆成要点 rubric，另加一条"矛盾" rubric；rubric 由 GPT-4o 起草、作者人工审，再用 LLM judge 打分。指标是 class-balanced accuracy。人工只参与 rubric 审核，论文没有报告 judge 与人工的一致率。
  - 我的判断：**自动化程度中高**，短答案题可以直接用规则评。
- **Performance**：o3 46.8%，每题成本 $3.79，没有模型超过 50%。专家做一题平均 16.8 分钟、$25.66。
  - 主要问题：工具误用（Llama 4 编造文档）、反复失败的调用、表格数据处理差 ⚠️。
- **GT Construction**：7 位来自投行、对冲基金、PE 的专家出题，每题由另一位专家复核。
  - 我的判断：短答案部分**可信度高**（可从 XBRL 复算）；建模和判断类题**可信度中**。
- **Data**：公开验证集 50 条（CC BY 4.0），私有验证集 150 条需申请，测试集 337 条不公开；harness 为 MIT。
- **版本演进（arXiv 只有 v1 论文，下面的信息来自 [vals.ai](https://www.vals.ai/benchmarks/fabv2-1) 官网，已核实）**：
  - **v1.1**：537 题，Claude Opus 4.7 最高 64.37%；
  - **v2**（已归档）：927 题（公开 27 / 私有验证 450 / 测试 450）。评分改为"dealbreaker 门槛的部分分"为主、All-Pass 为辅，由 GPT-5.4、Gemini-3.1-Pro、Sonnet 4.6 三个 judge 组成评审团。最高是 Gemini 4 Argon，65.40%；
  - **v2.1**（2026-11-19 更新）：换了评审团（GPT-6.1 Sol、Gemini 3.8 Flash、Sonnet 5.5），修了一批题，官网写明分数与 v2 不可比。Claude Fable 5.2 第一，69.47%。
  - 启示：**专业团队也要靠持续人工修题和换 judge 来维护**，这正好说明了自动更新的需求。

#### 3. FinSearchComp（[2509.13160](https://arxiv.org/abs/2509.13160)，ICLR 2026，字节 Seed 等）
- **Task**：635 题，分三类：T1 时效数据获取、T2 简单历史查询、T3 复杂历史调查；分全球和大中华两个子集。例 [原文]："What was the total assets of Starbucks as of September 27, 2020?" → $29,374.5 million（允许舍入误差）
- **Capability**："search proficiency and knowledge-grounded reasoning"，即新鲜度、时点准确性、多期综合。
- **Evaluation**：LLM judge 加容差带（论文没写是哪个 judge 模型），由专家抽检。每个子集用 4–5 个模型约 400 条做人工核验，一致率 95%（T1 约 91.5%，T3 最高 99.8%）。T1 用实时 API 结果核对。
  - 我的判断：**自动化程度高**。
- **Performance**：Grok 4（联网）全球子集 68.9%；豆包（联网）大中华子集 54.2%；人类专家分别为 75.0 和 88.3。不联网时 T1 接近 0。
  - 主要问题：搜索太浅、时间戳过期、单位/币种错误、财年日历错位、开盘价和收盘价混淆。
- **GT Construction**：50 位专家加 20 位资深评审，共约 180 + 60 小时。每题由 1–2 人盲做复核，分歧由资深专家仲裁。
  - 我的判断：T2/T3 可以由 XBRL 或数据库自动生成，**可信度高**。
- **Data**：已核实。HF `ByteSeedXpert/FinSearchComp` 有 635 行，**CC-BY-4.0**，字段为 id/tier/question/tool_template/answer/trace，**题目、GT 和解题 trace 都公开**；judge prompt 在附录 C。没有 GitHub repo。

#### 4. FinAgentBench（[2508.14052](https://arxiv.org/abs/2508.14052)，NeurIPS 2025）
- **Task**：两阶段 agentic 检索。先给 5 种文件（10-K、10-Q、8-K、电话会、DEF 14A）排序，再给文件内的段落排序，共约 26K 例。论文正文没有给出文字例题，只在图里有。
- **Capability**："agentic retrieval with multi-step reasoning"，即选文件类型和段落级检索。
- **Evaluation**：nDCG@5、MAP@5、MRR@5，本身就是全自动；人工只参与标注。
- **Performance**：文件排序 nDCG 0.78（Claude Sonnet 4），**段落排序只有 0.42**。o4-mini 做强化微调后从 0.345 提到 0.371。
- **GT Construction**：2 位专家写 query，金融从业者标注相关性，每条 2 人标注、有分歧再裁决。材料是 EDGAR 2023–24 年约 3,000 家公司的文件。
  - 我的判断：相关性本身带主观性，用 LLM 自动标注**可信度中**。
- **Data**：论文没有给出数据链接，**可能不公开**。

#### 5. Fin-RATE（[2602.07294](https://arxiv.org/abs/2602.07294)，KDD 2026，Yale）
- **Task**：7,500 题，分三类：DR-QA（单段细节）、EC-QA（同行业同年跨公司比较）、LT-QA（单公司多年追踪）。例题只在图里。
- **Capability**："precise extraction and localized reasoning"、"multi-entity integration and comparison"、"temporal alignment and trend reasoning"。
- **Evaluation**：4 档标签，加 5 个 Likert 维度，加 13 类错误分类。用 GPT-5 + DeepSeek-V3.2 + Qwen3-235B 三个 judge 集成，与人工一致率 88.8–90.5%；单用 GPT-5 只有 79.6%。
  - 我的判断：已经自动化，**集成 judge 明显比单个 judge 好**。
- **Performance**：给定正确上下文时，DR 57.5%，EC 43.6%，LT 43.5%；人类分别为 92.4、82.7、85.9。RAG（top-5）各项都低于 27%。
  - 主要问题：实体混淆、时间错配、趋势幻觉；EC 的检索错误中 75% 是证据缺失。
- **GT Construction**：DeepSeek-V3.2 以"先摘要再出题"的方式生成，两个 LLM 过滤，再人工复核（核对段落、重算数字）。材料是 43 家公司 2020–2025 年的 2,472 份文件。
  - 我的判断：这是典型的"LLM 生成 + 人审"，**可信度中**。
- **Data**：HF `GGLabYale/Fin-RATE`（MIT），含语料和 3 个 QA json，**题目、语料、答案都公开**。提交历史里删掉过一个 key_points 文件，所以拆解要点可能没有公开。

#### 6. FrontierFinance — Samaya（[2608.11683](https://arxiv.org/abs/2608.11683)）
- **Task**：220 道带"提问日期"的开放式投研题，分 6 个场景。例 [原文，作者标注为简化版]："What EPS guidance did Delta provide in its latest earnings call?"（该题有 37 条 rubric）
- **Capability**：定性综合 45%、穷尽检索（跨时间/实体/主题）、数值推理 26.8%、多跳 24.1%、因果 6.4%。
- **Evaluation**：二值 rubric 共 11,543 条（7,487 条 must-have），由 Sonnet 4.6、Gemini 3.1 Pro、GPT-5.4 三个 judge 多数投票。**没有报告与人工的一致率**。
  - 我的判断：**自动化程度中**，rubric 可以自动判，但 rubric 本身需要专家写。
- **Performance**：Samaya 自家 harness 56.0%；Claude Fable 5（FAB v2 harness）49.2%；Kimi K3 46.4%；Opus 4.8（网页搜索 harness）33.0%。"筛选与发现"场景最好只有 33%。
  - 主要问题：凭记忆访问 URL 导致出错；可能记住了提问日期之后的信息。
- **GT Construction**：前买方、卖方、投行人员分 4 个阶段写题和 rubric，两轮审计。rubric 依据：SEC 文件 39%、公司材料 25%、专业知识 19%、市场数据 7%。共标注约 4,500 题，公开 220 题。
  - 我的判断：rubric 交给 LLM 自动写，**可信度中低**；其中依据 SEC 的那部分**可信度中高**。
- **Data**：HF `samaya-ai/FrontierFinance`（gated，CC-BY-4.0），公开题目和 rubric，**没有参考答案和原始材料**。评分代码 Apache-2.0。

#### 7. AgenticFinBench（[2611.04813](https://arxiv.org/abs/2611.04813)，2026-11）
- **Task**：230 个真实用户请求（中文 189、英文 41），8 类，L1–L4 四级，**没有参考答案**。例 [原文]："Can you compare stocks wdc and stx"
- **Capability**：任务完成度、解释推理、证据与准确性、适用范围；另外检查 claim 能否在 agent 轨迹里找到出处、会不会被外部事实推翻。
- **Evaluation**：无参考 rubric 加两阶段 claim 审计，合成 Q（0–100），judge 为 DeepSeek V4.1 Flash。在 1,800 条回答上与专家对比：一致率 84.8–92.3%，κ 0.70–0.82，**与专家之间的一致率相当**。
  - 我的判断：**自动化程度高**，这一套方法值得借鉴。
- **Performance**：最好的是 GPT-5.6 Sol（Codex CLI）Q=89.2，最低 65.4。L1 平均 89.4，L4 降到 79.2；投资规划类最弱。
  - **18 个配置全都出现幻觉 claim**，有幻觉的回答占 0.9–47%。
  - 没达到的推理要求里，最多的是"解释事件如何影响利润或价格"（45.8%）。
- **GT Construction**：从生产日志（14,697 + 23,731 条）过滤出题，专家匿名化并审核。rubric 由 LLM 只看题面起草，再单独审一遍，有专家审核。
  - 我的判断：**无参考 rubric 的可信度上限有限**，审计部分可信度高。
- **Data**：项目页可下载 questions.json、rubrics.json（5,817 条正向 + 1,780 条负向）和结果；GitHub `NashnovaResearch`。许可未写明。

### B 组：工具调用、建模与工作流

#### 8. FinToolBench（[2603.08262](https://arxiv.org/abs/2603.08262)）
- **Task**：295 道必须用工具才能答的题，配 760 个免费工具（261 个 RapidAPI 接口、499 个 AkShare 接口），对答案和每一步调用都评分。例 [意译]：financebench_9 案例，GT 为 "Performance is not measured through operating margin."
- **Capability**：能力指标（调用率 TIR、执行成功率 TESR、正确率 CER、Soft Score）加金融合规指标（时效 TMR、意图克制 IMR、领域对齐 DMR）。
- **Evaluation**：GPT-5.1 judge，重复 3 次取平均。3 位专家标注 60 题和 50 条轨迹：专家之间一致 85.3%，专家与流水线一致 83.8%。
- **Performance**：Gemini-3.1-Pro 的 Soft Score 最高（0.822），但 **TIR 只有 0.15**，也就是大多不调工具直接作答。Qwen3-8B 的 TIR 为 0.87。
  - 主要问题：调用保守的覆盖不够，调用激进的轨迹噪声大；接口报错、超时；用代理指标顶替所问指标。
- **GT Construction**：**题目和 GT 直接继承自 FinanceBench 和 OpenFinData**，由 Qwen3-8B 过滤；工具用检索加 LLM 投票来对齐，专家抽检。这是"从种子 benchmark 派生新 benchmark"的先例，和 AutoFinBench 直接相关。
  - 我的判断：GT 的可信度取决于种子本身，**中**。
- **Data**：GitHub `Double-wk/FinToolBench` 公开题目和工具清单，作者称是"minimal data"，许可不明，运行需要自备 RapidAPI 订阅。

#### 9. MBABench（[2605.22664](https://arxiv.org/abs/2605.22664)，Columbia namkoong-lab）
- **Task**：根据商业案例和起始工作簿，搭出完整的多 sheet Excel 模型，共 101 题。例 [原文]：ModelOff 2015 的 "Bread and Butter"，"Contestants are asked to build a financial model for the acquisition of Macrohard, a fictional company."，要求三表模型和 10 年 IRR。
- **Capability**：Accuracy（最终数、起始值、完成度）、Formula（逻辑、硬编码、范围、引用）、Format（结构、可读性、数字格式）。
- **Evaluation**：LLM judge 对照 golden solution 逐项判 pass/fail。论文用 Gemini-2.5-pro，repo 默认改成 gpt-5.6-sol。在 408 条标注上与专家对比：acc 0.92，F1 0.85。README 里另有 129 项 rubric 和 23 项确定性检查。
  - 我的判断：**自动化程度高**，有 golden 工作簿时尤其可靠。
- **Performance**：专有 harness 上的 GUI 或代码 agent 表现最好，结论里点名 Claude Cowork 最强。L2 最好 92.4（Claude Code），L4 最好 72.6（Codex）。
  - 主要问题：硬编码代替公式、范围差一位但数字碰巧对、正负号错误、空白 sheet、GUI 处理不了循环引用。
- **GT Construction**：题目来自 FMWC、ModelOff、Wall Street Prep 等建模竞赛和课程，**本身带官方答案**，由 2 位 MBA 和 3 位从业者花了 700+ 小时整理。
  - 我的判断：**可信度高**，因为是竞赛官方解。
- **Data**：GitHub（Apache-2.0）加 HF，101 题都带起始工作簿和 golden solution，**公开**。

#### 10. FrontierFinance — Kensho / S&P / MIT（[2604.05912](https://arxiv.org/abs/2604.05912)）
- **Task**：基于 SEC 文件做 25 个 Excel 模型（三表、LBO、DCF、并购、贷方模型），部分还要配 PPT memo；专家平均每题 18.3 小时。例 [原文节选]："We are evaluating a full buyout of a publicly traded business called Electronic Arts … Single-sheet LBO model (Excel) with all sections specified below."
- **Capability**：长程建模能力，包括取数、公式完整性、跨表链接、循环引用、债务瀑布、敏感性表、写 memo。
- **Evaluation**：先过 PASS/FAIL 门槛，再按最多 140 条 rubric 打分，judge 为 Sonnet 4.6（可调用 EDGAR 和计算工具）。judge 与人工的相关：**没有 rubric 时 r=0.204，有 rubric 时 0.627**；而且 judge 系统性高估 LLM。
  - 我的判断：**自动化程度中**，必须有 rubric，还要用人工校准 judge 的偏高。
- **Performance**：judge 评分 GPT-5.4 87.5；但在人工评分的 10 题子集上，**GPT-5.4 只有 70.9%，人类专家 77.2%**。
  - 主要问题：依赖结构断裂、硬编码、为配平编造数字、缺乏自检。
- **GT Construction**：一位前投行人员加一位 AI 数据专家，每种模型约 27.5 小时；rubric 由从业者写，参考模型经专家审核；人工评分花了 50+ 小时。
  - 我的判断：参考模型无法自动生成，**可信度低**。
- **Data**：**不公开**，论文写 "forthcoming"。

#### 11. FORCE-Bench（[2607.19409](https://arxiv.org/abs/2607.19409)，Microsoft）
- **Task**：251 题，分三类：ERP 应收应付查询 100 题、上市公司业绩研究 126 题、业务简报 25 题。例 [原文]："For our credit evaluation of Caterpillar, what is their long-term debt-to-equity ratio (3-year average) as of September 2025?" → "1.42 (or 142%)"
- **Capability**：8 个 rubric 维度（准确、引用、清晰、深度、有据、时效、相关、结构），并有延迟预算：一般 60 秒，简报 300 秒。
- **Evaluation**：GPT-5.2（通过 DSPy）对每条断言打 0–1 分。没有报告与人工的一致率；用 Opus 4.6 做交叉 judge，Spearman 0.944。
- **Performance**：作者自家的 Finance Agent（M365 Copilot）0.80，GPT-5.5 0.67，Opus 4.7 0.63；超时设置下 Opus 的准确率只有 0.27。作者自己承认，benchmark 和自家 agent 是一起开发的，存在偏向。
- **GT Construction**：ERP 部分的答案来自合成的 Dynamics 365 数据，**是确定的**；公开数据部分随时间变化，**没有固定 GT**。
  - 我的判断：合成企业数据这条路**可信度高**，可以借鉴。
- **Data**：GitHub `microsoft/FinanceBenchmark`（MIT），含 dataset.yaml（README 写约 300 题）。复现 ERP 部分需要 D365 许可。

#### 12. IPO Finance Agent（[2606.23032](https://arxiv.org/abs/2606.23032)，单一作者）
- **Task**：围绕 SpaceX 的 S-1 做 IPO 尽调问答，可用网页、EDGAR 和检索；共 1,000 题，公开 70 题。论文正文没有文字例题。
- **Capability**：7 个领域：分部经济、KPI 质量、治理、同一控制下重述会计、资本强度、执行风险、估值与承销。
- **Evaluation**：每题按 rubric 给部分分，grader 为 GLM-5.1，**和得分最高的 GLM-5.2 同属一个家族，有自我偏好风险**。每条最终 rubric 都由人工专家审过。
- **Performance**：GLM-5.2 79.8%，Qwen 3.7 Max 78.9%（每题 $0.30），Kimi K2.6 68.0%，Nemotron 3 Ultra 45.5%。估值与承销最弱；FAB v2 的 harness 因为 S-1 太长基本跑不通。
- **GT Construction**：**rubric 自动生成**：从 5 个模型的回答里抽取事实，跨厂商有 2 家以上一致才保留，再经过归纳、评估、修复、去重，最后人工审核。
  - 我的判断：模型之间的共识不等于事实（它们可能犯同样的错），**可信度中低**；人审这一步是兜底。
- **Data**：GitHub `benstaf/ipoagent`（MIT），公开 70 题，附 facts 和 rubric；另外 930 题私有。

### C 组：实时、预测与交易

#### 13. FinDeepForecast（[2601.05039](https://arxiv.org/abs/2601.05039)）
- **Task**：实时预测，分两种：周期性数值（96 个宏观指标、121 个公司指标）和非周期性二元事件。10 周共 1,394 题，覆盖 8 个经济体、1,314 家公司。论文没有给出完整例题，只列了指标名，例如 ROA、EPS。
- **Capability**："extensive information gathering and multi-step reasoning"，以及对派生比率的算术推理。
- **Evaluation**：确定性评分，按相对误差阈值判对（百万级指标 5%、比率 1%、利率/汇率 0.1%），事件题完全匹配。专家核验全部非周期性题的 GT，标注员一致率 95%；周期性 GT 准确率 99.8%。
- **Performance**：o3-deep-research 39.5%，Perplexity 39.4%；周期性数值题最好只有 25.5%；只推理不联网的模型低于 10%；去掉搜索掉 11–14 分。
- **GT Construction**：周期性题从官方来源自动解析；事件题由 LLM 汇总证据、专家确认；每周解析一次，设"待定"和"作废"两种状态。
  - 我的判断：数值部分**可信度高**，事件部分**中**。
- **Data**：论文称在 OpenFinArena 平台公开，我没能核实（页面要靠 JS 渲染）。

#### 14. FutureX-Finance（FutureX-Pro，[2601.12259](https://arxiv.org/abs/2601.12259)，字节）
- **Task**：预测 150 个标的（美股 100、A 股 50）的点位、区间极值和方向。模板 [原文]："What will be the {Closing Price} of {Tesla, Inc. (ID: TSLA)} on {2025-12-25}?"
- **Capability**："function as a quantitative analyst, requiring precise numerical predictions"
- **Evaluation**：S = max(0, 1 − 20·|ŷ−y|/|y|)，全自动。
- **Performance**：Type 1 上 GPT-5-high 46.4，没有模型超过 50。
- **GT Construction**：到期后的行情数据，全自动。
  - 我的判断：GT 本身可信度高，但**股价里噪声占主导，题目效度存疑**。
- **Data**：金融题**尚未放出**。

#### 15. LiveSearch（[2610.37166](https://arxiv.org/abs/2610.37166)）
- **Task**：关于 A 股、港股、美股、基金、指数、宏观序列的中文单跳题，agent 只能用搜索和网页抓取。例 [意译]："腾盛博药-B（02137.HK）最近一个交易日的后复权涨跌额是多少港元？" 2026-09-16 的 gold 为 −0.015。
- **Capability**：能否靠网页搜索找回"由专业数据源确定的值"。
- **Evaluation**：逐题二值，judge 为 gemini-3.5-flash，gold 由执行验证程序得出，**全程没有人工参与**。
- **Performance**：DeepSeek V4.1 Flash 76.7，Claude Opus 5 76.2，GPT-6 Astra 74.5。
  - 主要问题集中在**口径**：港股复权方式、均线定义、美股成交额口径；还有把哪一天当"最新交易日"弄错，以及引用二手来源。
- **GT Construction**：**题目即程序**：对专业数据服务（MCP，96 个工具）的调用加上抽取器；LLM 只负责把程序转写成题面，并做 1% 的数值一致检查。题库 3,320 题，每天重跑，3 天内有 70% 的 gold 发生变化。
  - 我的判断：**可信度高**，前提是数据源本身可信。
- **Data**：可以共享（题目、时间戳、值）三元组和工具 schema；实时评测需要接入该数据服务；代码未写明是否开源。

#### 16. SecQue（[2504.04596](https://arxiv.org/abs/2504.04596)，GEM 2025）
- **Task**：基于 10-K/10-Q 片段的 565 道开放题，分四类：比较与趋势 220、比率 188、风险 85、分析师洞察 72。例 [原文]："How has NVIDIA's Interest Coverage Ratio changed from 2023 to 2024?" GT：EBIT/利息，FY2024 为 128.3，FY2023 为 16.1。
- **Capability**："reasoning over long unstructured data"，包括表格抽取、数值、风险、洞察。
- **Evaluation**：5 次 GPT-4o 调用，每次按 0/1/2 打分后聚合，与人工对比 F1(2)=0.85（124 条）。
- **Performance**：GPT-4o strict 0.69、normalized 0.79；分析师洞察这一类最低，作者也承认这类评分不太可靠。
- **GT Construction**：3 位 SME 写题，再由 2 位专家复审；材料是 29 家公司 2018–2024 年的 45 份文件。
  - 我们自己的发现：GT 有算术错误、口径混用、表格空格导致列错位（见 step0、step1）。所以**人工 GT 也不可靠**。
- **Data**：HF `nogabenyoash/SecQue`（MIT，限评测用），题目、GT、4 种格式的上下文**全部公开**。

#### 17. BizFinBench（[2505.19457](https://arxiv.org/abs/2505.19457)，HiThink；v2 进了 ICML 2026）
- **Task**：6,781 道中文题，5 个维度 9 个子任务（异动归因、数值计算、时序推理、数据描述、股价预测、实体识别、情绪识别、工具使用、知识问答）。例题只有图片。v1 已标为过时，v2 扩到 29,578 题。这是单轮 LLM 题，**不完全是 agent benchmark**。
- **Capability**：精度敏感的金融任务，包括计算、推理、抽取、预测、知识。
- **Evaluation**：客观题用 EM；开放题用 GPT-4o 的 IteraJudge，与人工的 Spearman 为 0.57（FDD）和 0.87（FTU）。
- **Performance**：o3 平均 73.9，DeepSeek-R1 73.1；情绪识别最好只有 47.7；时序推理弱。
- **GT Construction**：题目来自同花顺问财的用户日志，GPT-4o 清洗并合成，再由 GPT-4o 出候选答案，3 位资深专家全票通过才保留。
  - 我的判断：**可信度中**。
- **Data**：GitHub 公开，代码 Apache-2.0，数据 CC BY-NC 4.0。

#### 18. AI-Trader（[2512.10971](https://arxiv.org/abs/2512.10971)，港大 HKUDS）
- **Task**：实时模拟交易：纳斯达克 100（按小时）、上证 50（按日）、10 个加密货币对（按日），通过 MCP 调用行情、搜索、新闻、计算、下单工具。提示词 [原文]："Your long-term goal is to maximize returns through this portfolio."
- **Capability**："dynamic reasoning capabilities, tool utilization efficiency, and decision robustness"
- **Evaluation**：累计收益、Sortino、波动率、最大回撤，对比 QQQ、上证 50、CD5 基准；没有人工。
- **Performance**：美股 MiniMax-M2 收益 9.56%（QQQ 1.87%）；A 股没有 agent 跑赢上证 50；加密货币里 DeepSeek-v3.1 −12.18%（基准 −14.30%）。
  - 主要问题：暴跌中一路持有、目标权重死板、过拟合单一市场、根据未经核实的新闻下单。
  - 测试窗口只有约 5 周，**统计噪声很大**。
- **GT Construction**：没有 GT，由市场结果决定。
- **Data**：GitHub（MIT）；实时结果无法从 repo 复现。

### D 组：本次补充

#### 19. BankerToolBench（[2604.11304](https://arxiv.org/abs/2604.11304)，Handshake AI，NeurIPS 2026）
- **Task**：扮演初级投行分析师，在沙箱里（data room、MCP 行情、EDGAR）产出 Excel、PPT、PDF、Word 交付物，共 100 题。人类平均每题 5 小时，最长 21 小时。例 [原文]："You are an analyst in the M&A group at a bulge-bracket bank. … The final deliverable should be an Excel file with the accretion-dilution model for this potential transaction."
- **Capability**：建模与公式完整性、取数、判断、**跨交付物一致性**、可直接给客户的格式、透明度。
- **Evaluation**：每题约 150 条加权二值 rubric，由 agent-as-judge "Gandalf"（OpenHands + Gemini 3 Flash Preview）**实际打开文件检查**。与人工共识一致 88.2%（κ 0.756），**高于人与人之间的 84.6%**。
  - 我的判断：**自动化程度高**，交付物类任务可以借鉴这种做法。
- **Performance**：最好的 GPT-5.4 也有近一半 rubric 没通过，**银行家认为可直接交客户的比例是 0%**。
  - 任务通过率 16%，3 次全过（Pass^3）13%，所有关键项全过只有 2%。
  - 失败原因占比（GPT-5.4 轨迹）：公式/代码 41%、推理 27%、检索与坚持 18%、编造 13%。
- **GT Construction**：银行家写需求和 rubric，经多轮审核。502 是合作银行家的总人数，**直接参与造题的是 172 人，累计 5,700+ 小时**。只有部分题目有 golden 交付物。
  - 我的判断：**无法自动化**。
- **Data**：HF（CC-BY-4.0）公开 tasks.jsonl（需求 + rubric）、部分 golden 交付物、任务文件和约 5.5 GB SEC/行情数据。**目前公开程度最好的交付物类 benchmark**。

#### 20. FinDeepResearch（[2510.13936](https://arxiv.org/abs/2510.13936)）
- **Task**：给定公司、市场和财年，写一份 6 节的研报。覆盖 64 家公司、8 个市场、4 种语言，共 15,808 个评分点。⚠️ 提示词摘录："Assuming today's date is 2025-09-20, generate a research report on this company."
- **Capability**：识别、计算、抽象、解释四层，即"结构严谨"和"信息精确"。
- **Evaluation**：LLM judge 加 rubric：识别和计算按 0/1，抽象按 claim 覆盖，解释按 10 分制；另有规则评的结构分。我读到的部分没写 judge 模型和一致率。
- **Performance**：o3-deep-research 37.9，Grok-4 DeepSearch 37.3；⚠️ 解释层最好只有 20.3；中国内地和香港市场最难。
- **GT Construction**：先让多个 LLM 生成参考报告，再由 30+ 位专家两轮核验，每个事实至少两个来源交叉验证。
  - 我的判断：先 LLM 生成、再人工核验，**可信度中**。
- **Data**：论文称在 OpenFinArena 公开，未核实。

#### 21. Deep FinResearch Bench（[2604.21006](https://arxiv.org/abs/2604.21006)）
- **Task**：为 25 家标普 500 公司（IT、金融、医疗）写 FY2025 Q1–Q2 的业绩前瞻研报，与两家机构分析师的报告对照。例题为意译。
- **Capability**：定性严谨度、业绩预测（SMAPE）、估值（命中率、MAE）、评级准确、claim 真实性。
- **Evaluation**：GPT-5 按 1–4 分打分，与 8 位专家的两两一致率 80%（Gemini 2.5 Pro 53.8%，Sonnet 4 31.2%）。预测部分用实际财报确定性评分；claim 由 GPT-5 抽取、GPT-4.1 加联网核验。
- **Performance**：最好的 DR agent（Gemini）2.31，**分析师 2.84**；事实性 OpenAI 86.0%、Gemini 69.6%。
  - 主要问题：模板化、没有情景分析、目标价只给单点。
- **GT Construction**：参考是 100 份专业报告（专有，通过 Yahoo Finance 订阅获取），rubric 由 o3 抽取；预测题 GT 用实际财报。
  - 我的判断：预测部分**可信度高**，质量部分**中**。
- **Data**：**不公开**，原始报告仅限客户。

#### 22. FinGAIA（[2507.17186](https://arxiv.org/abs/2507.17186)，上财）
- **Task**：407 道中文题，7 个子领域、3 个层级，需要网页浏览、文件解析、多模态和 Python。例 [原文]："沧州营业部的负责人是谁？"——要先认出期货公司的 logo，再进官网查找。
- **Capability**：网页浏览 42.7%、文件 18.1%、多模态 15.2%、代码 12.2%、计算 10.1%。
- **Evaluation**：准确率，**以人工评审为主**，LLM judge 为辅。
  - 我的判断：短答案题，**可以完全自动化**。
- **Performance**：ChatGPT DeepResearch 48.9；**人类专家 84.7**，非专家 46.9。作者总结了 5 类错误，包括金融术语偏差、业务流程认知障碍、幻觉推理。
- **GT Construction**：4 位金融教授设计场景，6 位本科生标注（约 90 分钟/题），4 位业内人士全票通过才保留。
- **Data**：只公开一部分（HF 13 条）；计划公开 150 条 dev。

#### 23. FinMCP-Bench（[2603.24943](https://arxiv.org/abs/2603.24943)，阿里点金 / 且慢，ICASSP 2026）
- **Task**：用 65 个 MCP 工具回答理财用户的问题，共 613 例：单工具 145、多工具 249、多轮 219。论文正文没有文字例题。
- **Capability**：工具选择、依赖链、并行调用、多轮对话中的工具使用。
- **Evaluation**：只比工具集合，算 P/R/F1 和完全匹配率，**不评最终答案**（作者认为这类问题没有标准答案）。
- **Performance**：Qwen3-235B-Thinking 的工具 F1 为 64.3、完全匹配 25.9；**多轮完全匹配最好只有 4.1**。
- **GT Construction**：约 1 万条真实 App 日志匿名化后，6 位专家每例 2 人按 Likert 评审，所有维度 ≥4 才保留。
  - 我的判断：GT 是"一条合理的调用轨迹"，但**合理的轨迹不止一条**，所以完全匹配偏严。
- **Data**：GitHub 公开 json，含 GT 轨迹；调用工具需要且慢的 MCP 地址。

#### 24. Bank-World（[2610.39733](https://arxiv.org/abs/2610.39733)，Arcanum Labs）
- **Task**：两家模拟银行里的 50 个工作流：25 个单轮，25 个多轮（有一位模拟经理参与）。agent 要通过工具改变系统状态、走审批、汇报进度。例 [原文]：SQ-22 "Allocate assets and cash while preserving an unpaid receivable."
- **Capability**：计算与对账、遵循指令、审批与权限边界、保留记录、**如实汇报状态**、处理对话中途新到的信息。
- **Evaluation**：加权 rubric 加确定性状态检查，再加强制门槛（门槛不过即 0 分）。GPT-6.1 Sol 与 Opus 5.5 两个 judge 一致率 97%（κ 0.86），没有与人工对比。
- **Performance**：单轮 Sol 全部通过 55%，多轮 Opus 44%。
  - 主要问题：**判断对了但动作没做完**（800 次里有 173 次）、重复收费、未经批准就付款。
- **GT Construction**：由 1 位作者在 LLM 协助下构建，每题有参考解、"不应行动"对照组、141 个变异版本、25,952 条确定性检查可回放；记录全部是合成数据。
  - 我的判断：状态检查**可信度高**。
- **Data**：**不公开**，只公开方法和逐题结果。

### E 组：追加（论文后半部分只读到摘要，细节可信度略低）

#### 25. Investor's Last Exam（[2610.38342](https://arxiv.org/abs/2610.38342)）
- **Task**：86 个买方研究任务（公司研究 78、市场预测 8），在一个**按版本存储、严格截断信息时点的语料库**（3,430,336 个文档版本）里完成。例 [原文，来自 README]："Task O80 asks for Tesla's Q2 2026 deliveries, GAAP revenue, and GAAP automotive gross margin"
- **Capability**："coordinate evidence retrieval, computation, and financial reasoning across multi-step workflows"
- **Evaluation**：7 个维度的加权 rubric（0–100），预测题按实际结果用 interval score 评分。judge 是 GPT-6 Astra，**它同时也是被测模型**；另用 GPT-OSS-120B 做稳健性检查。没有报告一致率。
- **Performance**：GPT-6 Astra 总分 68.1，"预测与建模"维度约 52.5。
  - 主要问题：分析对了、预测却错；读错现金流；提交失败。
  - ⚠️ **Astra 走公开网页的轨迹里有 57% 引用了截止日之后的来源**——不加沙箱，泄漏非常普遍。
- **GT Construction**：专家编写，AI 辅助检索和审核；预测题 GT 用实际结果。
- **Data**：GitHub 写的是"不分发"，但 HF `HenryJ12/InvestorLastExam` 上有 86 个任务、1,472 条 rubric 和 ground_truth_json，两边说法矛盾。都没有写许可。

#### 26. CFAgentBench（[2606.22000](https://arxiv.org/abs/2606.22000)，建筑业金融）
- **Task**：1,014 个任务规格，8 个领域、77 个任务族，其中 40 个是可执行套件。agent 在 ERP 等系统里完成变更单、付款准备等操作，只"准备"资金流动，不实际执行。例 [意译]：判断一张变更单是否属于业主变更。
- **Capability**：agent 能否在企业软件栈里、在政策约束下**可靠地**完成工作。
- **Evaluation**：比对状态差异，加"禁止改动"硬门槛，再加输出的正则检查；报告 pass^1 和 pass^5。**所有报告的数字都不经过 LLM judge**。
- **Performance**：DeepSeek-V3.1 pass^1 0.67，但 pass^5 只有 0.38，**可靠性崩塌**；跨应用 ERP 同步接近 0。没有测闭源前沿模型。
- **GT Construction**：种子来自行业论坛帖子、计划文档、播客；oracle 是确定性的，只收录 oracle 打满分的任务。
  - 我的判断：**可信度高**。
- **Data**：⚠️ 论文称公开 jsonl、环境目录和应用接口（verified split 711 题）；Pro split 303 题私有。许可未写明。

#### 27. FinTrace（[2604.10015](https://arxiv.org/abs/2604.10015)）
- **Task**：800 个查询，在 FMP 的 MCP 工具上走多轮调用轨迹，覆盖 34 类。例 [原文]："What was the average of the total deductions for the years 2004, 2005, and 2006?"
- **Capability**：作者的结论原话是 "all models struggle with information utilization and final answer quality"
- **Evaluation**：9 个指标，分 4 条轴：3 个算法指标（工具 F1、步骤效率、冗余），6 个由 Claude-Sonnet-4.6 按 5 分 Likert 打分。与专家对比：排序 κ=0.89，逐项加权 κ 0.63–0.86。
- **Performance**：Claude-Opus-4.6 总分 0.788，但通过率只有 2.65/5；推理型 QA 最难。另外 SFT 后 32B 模型有 43.9% 的轨迹不给答案，DPO 后降到 5.8%。
- **GT Construction**：3 个前沿 LLM 生成候选，LLM judge 选出最佳，4 位专家审核全部 800 条。
  - 我的判断：**可信度中**。
- **Data**：HF `YupengCao/FinTrace`（MIT），测试集 800 条公开；轨迹和训练数据标为 "coming soon"。

---

## 三、重新分类

### 主分类：按 GT 的获得方式（我推荐用这个，和 AutoFinBench 关系最直接）

| 类别 | 数量 | 成员 | 特点 |
|---|---|---|---|
| **G1 专家手写的确定答案** | 6 | FinanceBench、Vals FAB、FinSearchComp、SecQue、FinGAIA、FinAgentBench（相关性标签） | 短答案、可以对答案；成本高、规模小、会过时；**最适合做种子** |
| **G2 LLM 生成 + 人工审核** | 6 | Fin-RATE、BizFinBench、FinToolBench（继承种子 GT）、FinMCP-Bench（日志 + 审核）、FinDeepResearch（LLM 写参考报告）、FinTrace（多个 LLM 出候选 + 专家审） | 规模大；可信度取决于人审的深度 |
| **G3 没有参考答案，只有 rubric** | 6 | FrontierFinance-Samaya（专家 rubric）、AgenticFinBench（LLM rubric）、IPO Agent（模型共识 rubric）、FORCE-Bench（公开数据部分）、Deep FinResearch（从分析师报告抽 rubric）、Investor's Last Exam（专家 rubric + 实际结果） | 开放式长答案；可信度由 rubric 质量和 judge 偏差决定 |
| **G4 参考交付物或状态 + 检查项** | 5 | MBABench（golden 工作簿）、FrontierFinance-CU（参考模型）、BankerToolBench（golden 交付物 + rubric）、Bank-World（参考解 + 状态检查）、CFAgentBench（状态差异 oracle） | 最接近真实工作；构造成本最高 |
| **G5 由世界或程序决定** | 4 | LiveSearch（执行程序）、FinDeepForecast、FutureX-Finance（事后解析）、AI-Trader（市场） | 天然不受污染、可持续刷新；能考察的能力较窄 |

### 副分类：按底层材料

| 材料 | 数量 | 成员 |
|---|---|---|
| **M1 SEC 文件、年报、招股书** | 9 | FinanceBench、SecQue、Fin-RATE、FinAgentBench、Vals FAB、IPO Agent、FinDeepResearch、Deep FinResearch、Investor's Last Exam（带版本的文档库） |
| **M2 网页和实时数据 API** | 9 | FinSearchComp、LiveSearch、FutureX-Finance、FinDeepForecast、AI-Trader、FinToolBench、FinGAIA、FrontierFinance-Samaya、FinTrace |
| **M3 真实用户请求日志** | 3 | AgenticFinBench、FinMCP-Bench、BizFinBench |
| **M4 工作环境和交付物（Excel/PPT/ERP/银行系统）** | 6 | MBABench、FrontierFinance-CU、BankerToolBench、FORCE-Bench、Bank-World、CFAgentBench |

（每个只归入主要材料。FrontierFinance-Samaya 和 BankerToolBench 也大量使用 SEC 文件。）

**两条轴交叉后的观察**：M1 × G1 最密集，也最接近饱和。M4 × G5 是空白：交付物任务目前**全部依赖 rubric 或参考解**，还没有"由程序确定 GT"的做法。

### 另外两个常用视角
- **输出形式**：短答案（1、2、3、13–16、22）；长报告（6、7、11、12、20、21、25）；文件交付物（9、10、19）；动作或状态（18、23、24、26、27）；排序（4）。
- **数据可用性**（决定能不能当种子）：
  - **完整公开**（题目 + GT + 原始材料）：SecQue、Fin-RATE、MBABench、BankerToolBench（GT 只有部分）、FinanceBench（150 条）、FinMCP-Bench、FinSearchComp（题目 + GT + 解题 trace，原始材料在网上）、FinTrace（800 条测试集）；
  - **只公开题目和 rubric**：FrontierFinance-Samaya、AgenticFinBench、IPO Agent（70 条）；
  - **基本不可用**：FrontierFinance-CU、Deep FinResearch、Bank-World、FinAgentBench、FutureX-Finance。

---

## 四、可以往哪些方向挖（我的初步思考）

先看现状。**检索和短答案已经接近饱和**：SecQue 0.79，LiveSearch 77，AgenticFinBench Q=89。**真正的短板在三处**：
- **建模交付物**：client-ready 比例 0%，judge 还系统性高估；
- **解释与因果**：FinDeepResearch 解释层约 20；AgenticFinBench 最常缺的是"事件如何影响利润"；
- **多轮与动作**：FinMCP 多轮完全匹配 ≤4%；Bank-World 判断对了但动作没做完。

对照其他领域 agent 评测的走向（SWE-bench 用测试判对、τ-bench 用状态判对、GAIA/BrowseComp 用短答案判对、AutoSciBench/TRACE 让题目自己演化），我认为有以下方向：

1. **把 G1 的题目改写成"可执行 GT"（最直接，也是 AutoFinBench 的主线）**
   - LiveSearch 证明了"题目 = 程序，GT = 执行结果"可行，而且可以每天刷新。
   - 种子可以用 FinanceBench 的指标题、SecQue 的比率题、FinSearchComp 的 T2/T3、Fin-RATE 的 LT/EC，把每道题改写成 XBRL companyfacts 上的一段程序（我们 step1 已有 `xbrl_series.py`）。
   - 这样一套程序同时支持：换报告期（越过模型知识截止）、换公司、改条件。GT 由代码算，还能**反过来审计种子 GT**：我们已经在 SecQue 里发现了算术错误和列错位。

2. **交付物任务也要有"程序判定"的 GT：用蜕变测试（metamorphic testing）**
   - MBABench、BTB、FrontierFinance-CU 都依赖 rubric 或参考解，成本高，judge 还偏高（r 只有 0.63）。
   - 软件测试里的做法是：**不知道正确答案时，检查输入和输出之间的关系**。比如改一个假设（增长率加 1%），模型的输出应该按可推导的方向和幅度变化；硬编码的模型改了输入输出不动，会直接暴露。
   - 这个检查可以完全自动化，**正好能抓住这几篇都列出的头号失败——硬编码和断链**。目前金融领域没人这样做。

3. **合成企业或银行环境 + 状态检查（金融版 τ-bench）**
   - FORCE-Bench 的 ERP 部分和 Bank-World 说明，合成账套能给出确定的 GT，还能考察审批、权限、对账、如实汇报这些能力。但 Bank-World 不公开，FORCE-Bench 要 D365 许可。
   - CFAgentBench 已经在建筑金融领域这么做了，但领域很窄，也没测闭源前沿模型；它还发现 pass^1 0.67 到 pass^5 只剩 0.38，**可靠性才是真正的短板**。
   - **通用、开源的合成公司账套环境**仍然是空白。可以从真实 10-K 反推一家"影子公司"的总账，让报表和 XBRL 对得上，这样可信度有保证。

4. **rubric 和 judge 的可信度本身就是研究点**
   - 现象：模型共识 rubric（IPO Agent）、只看题面写的 rubric（AgenticFinBench）、同家族 judge 自我偏好（IPO、Bank-World）、judge 偏高（FrontierFinance-CU）。
   - 方法：**对 grader 做变异测试**——向正确答案里注入已知错误（换口径、错一期、编一个数字），看 rubric 和 judge 能不能抓出来。Bank-World 的"不应行动"对照组和变异版本就是这个思路，你桌面上那篇 "Who Verifies the Verifier"（协同演化的可检查 grader）也属于这个方向。
   - 这一点可以直接接上我们的 `step1/GT_CREDIBILITY.md`。

5. **用"时点沙箱"解决污染，同时复用历史事件**
   - AI-Trader 把搜索限制在模拟时间之前，Samaya 给每题设提问日期，FinDeepForecast 则要等事件发生。
   - 改进办法：冻结截至 T 的 EDGAR 文件和新闻，在 T 时点提问，用 T 之后的真实数据当 GT。这样不用"等未来"就能批量造预测和判断题。和"换到截止日之后"配合起来，可以给企业私有 agent 做不受污染的评测。
   - **Investor's Last Exam 已经做了带版本的语料库**，并量化出：放开公开网页时，**57% 的轨迹引用了截止日之后的来源**。这说明不做沙箱，所谓"预测"大多是在偷看答案。
   - 我们可以在它的基础上补两点：一是让 GT 由程序计算，二是批量生成题目（它只有 86 题，全是人写的）。

6. **按能力缺口设计算子，让 solver 反馈驱动题目演化（AutoSciBench 那套闭环搬到金融）**
   - 每个已经暴露的缺口对应一个算子，作用在种子题上：
     - **口径切换**：复权方式、财年日历、GAAP 与非 GAAP（LiveSearch、FinSearchComp 最常见的错误）；
     - **跨实体或跨期对齐**（Fin-RATE EC/LT 只有约 43%）；
     - **缺失或错误前提**（我们 step2 的 D 组全错，FinanceQA/RealFin 也有类似发现）；
     - **对话中途追加信息**（Bank-World）；
     - **要求解释事件到利润的传导**（AgenticFinBench）。
   - 闭环：solver 在哪个算子上失败，就沿那个方向继续加难度，但每一步都要过可执行 GT 和 grader 变异测试这两道关，避免"变难其实是题变坏了"（这正是 AutoSciBench 被拒的理由之一）。

7. **评过程，不只评结果：证据链和溯源**
   - FinToolBench 发现 Gemini 的调用率只有 0.15，也就是靠记忆答题；AgenticFinBench 发现所有配置都出现过无法在轨迹中找到出处的 claim。
   - 可以要求答案里**每个数字都能追溯到某次工具返回**，再用程序检查。这完全能自动化，也能区分"记住的"和"查到的"，对评估私有金融 agent 特别有用。

8. **加上成本和延迟维度**
   - Vals 每题 $3.79，专家 $25.66；FORCE-Bench 设了 60 秒预算；IPO Agent 报了每题成本。可以报告"花多少钱或多少时间达到多少分"的曲线，企业用户更关心这个。

**对 AutoFinBench 的建议优先级**：
1. 方向 1（可执行 GT + 换期，G1 种子）——马上可以开始，已有代码基础；
2. 方向 6 和方向 4（按缺口设计的算子 + grader 变异测试）——这是论文的方法贡献；
3. 方向 2 或 3（交付物的蜕变测试 / 合成账套）——第二篇论文，或者扩展部分。

---

*相关文件*：[AUTO_UPDATE_RELATED_WORK.md](AUTO_UPDATE_RELATED_WORK.md)（自动更新 benchmark 的相关工作）、[BENCHMARK_POOL.md](BENCHMARK_POOL.md)（32 个金融 QA 数据集池）、[../step1/GT_CREDIBILITY.md](../step1/GT_CREDIBILITY.md)
