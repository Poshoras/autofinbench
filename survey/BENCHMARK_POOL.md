# 用其他 benchmark 改进 seed（SecQue Ratio）：调研

更新：2026-11-20　｜　机器可读版：`benchmark_pool.csv`

**做法**：从金融 benchmark 的论文里，找出每个 benchmark 声称测出的能力缺陷。把这个缺陷当作一种"改题方向"，套到 SecQue 的种子题上。再从三方面判断能不能用：

- **数据可用性**：新题需要的数据能不能从公开渠道（SEC XBRL、年报正文）拿到。
- **GT 可信性**：新答案能不能用代码，从核实过的数据算出来。
- **评估可信性**：能不能用代码或简单判断打分，而不是依赖开放式的裁判模型。

> 说明：规模、许可证、结论尽量取自论文摘要或官方页面。只在二手来源看到、还没核对原文的，标注"待核"。

---

## 0. 结论

- **最适合直接用的 6 个方向**（数据来自 XBRL，GT 由代码构造，打分可以自动化）：
  1. 多期追踪
  2. 跨公司比较
  3. 缺前提识别
  4. 计算核验（找错）
  5. 干扰上下文
  6. 数字扰动

  前 4 个确实改变了"考什么"；后 2 个考的能力基本不变，适合作为对照或污染检测。
- **建议先试 3 个**：多期追踪、缺前提识别、计算核验。三者分别对应三类不同缺陷：跨期整合、信息不全时是否诚实、能否核查别人的计算。我们现有的数据和代码可以直接支撑。
- **需要在论文里正面区分的相关工作**：
  - SEC-QA（Kensho）：从 SEC 数据生成、可随新文件刷新的题库。
  - FinForge：半合成金融 benchmark 生成。
  - Benchmark Self-Evolving / SEB：在种子 benchmark 上演化新题。

  这几篇和 AutoFinBench 的定位最接近。

---

## 1. Benchmark 池

### A. 基于 SEC 文件的问答（与 seed 同类）

| Benchmark | 出处 | 规模 | 数据是否公开 | 评测方式 |
|---|---|---|---|---|
| **SecQue**（seed） | GEM 2025，arXiv 2504.04596 | 565 题（Ratio 188） | 公开，MIT，**仅限评测，禁止训练** | GPT-4o 裁判 0/1/2 分 × 5 次 |
| FinanceBench | arXiv 2311.11944 | 10,231 题，40 家公司 | **只公开 150 题样本**，CC-BY-NC-4.0 | 人工判对 / 错 / 拒答 |
| DocFinQA | ACL 2024 short，arXiv 2401.06915 | 约 7k 题（版本间不同） | 公开（HF） | 执行准确率（附 Python 程序） |
| SEC-QA | FinNLP 2025，arXiv 2406.14394 | 待核 | 待核（是生成框架） | 程序化答案 |
| FinDER | ICLR 2025 workshop，arXiv 2504.15800 | 5,703 题，S&P 500 10-K | 公开（HF） | 检索 + 生成 |
| Fin-RATE | arXiv 2602.07294 | 7,500 条，3 类任务 | 公开（HF GGLabYale/Fin-RATE） | 分任务准确率，含错误归因 |
| FinAgentBench | NeurIPS 2025，arXiv 2508.14052 | 约 26K | 待核 | 文档级和段落级排序 |
| Finance Agent Benchmark（Vals） | arXiv 2508.00828 | 537 题，9 类 | **只公开约 50 题**，其余私有 | 带工具的 agent，按评分细则判分 |
| FinSearchComp | ICLR 2026，arXiv 2509.13160 | 635 题 | 公开，CC-BY-4.0 | 准确率，有人类基线 |
| FrontierFinance（Samaya） | arXiv 2608.11683 | 220 题，11,543 条评分细则 | 公开（数据 + 判分代码） | 长答案按细则判分 |

### B. 数值推理（带可执行程序 / 公式的标准答案）

| Benchmark | 出处 | 规模 | 数据是否公开 | 评测方式 |
|---|---|---|---|---|
| FinQA | EMNLP 2021，arXiv 2109.00122 | 8,281 题，财报数据 1999–2019 | 公开（GitHub，许可证待核） | 执行准确率 / 程序准确率 |
| ConvFinQA | EMNLP 2022，arXiv 2210.03849 | 3,892 段对话，14,115 题 | 公开（GitHub） | 执行准确率 / 程序准确率 |
| TAT-QA | ACL 2021，arXiv 2105.07624 | 16,552 题 | 公开；许可证说法不一（仓库写 CC BY 4.0，论文写非商用） | EM / F1（含单位与数量级） |
| MultiHiertt | ACL 2022，arXiv 2206.01347 | 10,440 题 | 公开（GitHub） | EM / F1 |
| BizBench | ACL 2024，arXiv 2311.06602 | 8 个任务 | 公开（HF kensho/bizbench） | 生成代码，执行判分 |
| FinanceMath | ACL 2024，arXiv 2311.09797 | 1,200 题 | 公开（GitHub yale-nlp） | 准确率（附 Python 解答） |
| FinanceReasoning | ACL 2025，arXiv 2506.05828 | 2,238 题（1,420 题由公开数据集修订而来） | 公开 | 准确率 |
| FinChain | ACL 2026，arXiv 2506.02515 | 58 个主题，参数化模板 | 公开（GitHub mbzuai-nlp/finchain） | 步骤级 + 最终答案（ChainEval） |
| V-FiLLM | arXiv 2608.11047 | 由合成表格生成 | 待核 | 构造即正确，可控难度 |

### C. 鲁棒性、信息缺失、核验

| Benchmark | 出处 | 规模 | 数据是否公开 | 评测方式 |
|---|---|---|---|---|
| FinanceQA（AfterQuery） | arXiv 2501.18062 | 待核 | 公开（HF AfterQuery） | 精确匹配，不给部分分 |
| RealFin | ACL 2026 Findings，arXiv 2602.07096 | 2,020 题（中英，含"条件缺失"版本） | 公开（GitHub） | 作答 / 识别缺失 / 拒绝错误选项 |
| FailSafeQA（Writer） | arXiv 2502.06329 | 220 条，上下文是 10-K | 公开，MIT | 裁判模型打分：鲁棒性、上下文依据、合规 |
| FinDVer | EMNLP 2024，arXiv 2411.05764 | 2,400 或 4,000（版本间不同） | 公开（GitHub） | 支持 / 反驳 + 解释 |
| FinVerBench | arXiv 2605.29586（单作者，未同行评审） | 1,985 条，基于 43 家公司 10-K 的 XBRL | 作者称公开 | 注入错误后检测：召回率 / 假阳性率 |
| FinED-Bench | ACL 2026 Findings，arXiv 2608.12342 | 973 篇文档，4,123 处错误 | 待核 | 错误检测准确率 |
| FinTrust | EMNLP 2025，arXiv 2510.15232 | 7 个维度 | 公开（GitHub） | 分维度 |
| FinTagging | arXiv 2505.20650 | 对齐全部 US-GAAP 概念 | 公开（GitHub / HF） | macro-F1 |

### D. 方法论（如何在种子上演化新题）

| 工作 | 出处 | 要点 |
|---|---|---|
| Benchmark Self-Evolving | COLING 2025，arXiv 2402.11443 | 6 种改写操作，如上下文改写、加噪、反转、换问法、加复杂度、子能力拆解；多 agent 生成并双重验证 |
| SEB（Make Benchmarks Live Again） | ICML 2026 | 保留种子 benchmark 的领域和技能分类，再找出模型的失败模式和偏差 |
| GSM-Symbolic | arXiv 2410.05229 | 把题目模板化后换数字，或加入无关条件（NoOp），模型表现明显下降 |
| FinForge | arXiv 2601.06747 | 半合成金融题生成；FinForge-5k，经人工核验 |
| Beyond the Reported Cutoff | arXiv 2504.00042 | 模型对新近年份、大公司的财务数据记得更好；数据来自 Compustat（不公开） |

---

## 2. 这些论文说模型 / 智能体缺什么能力

按能力归类。每条是论文自己的结论；"待核"的来自二手摘要。

| 能力 | 缺陷 | 出处 |
|---|---|---|
| **检索定位** | GPT-4-Turbo 加检索系统时，81% 的题答错或拒答 | FinanceBench |
| | 先选对文件类型、再找到段落的多步检索仍是难点；模型对文件结构的先验较强 | FinAgentBench |
| **长文档** | 平均上下文从 FinQA 的不到 700 词增至 12.3 万词，最长的文档上表现最差 | DocFinQA |
| **多文档整合** | 标准 RAG 在多文档问题上普遍失败 | SEC-QA |
| | 需要汇总多份文件的"复杂检索"比单点取数更难 | Finance Agent Benchmark |
| **时间对齐 / 跨期追踪** | 跨期追踪、跨公司比较时表现下降，出现时间错配、实体错配、比较幻觉 | Fin-RATE |
| | 不能搜索的模型在时效性任务上得 0 分；最难任务多数模型低于 30%，人类为 51.4–76.7% | FinSearchComp |
| **口径与会计惯例** | 模型约 60% 的真实分析任务失败；难在手工整理指标、遵循会计和估值惯例、在信息不全时做假设 | FinanceQA |
| | GAAP 与非 GAAP 的调整是单独的一类难题 | Finance Agent Benchmark |
| **领域知识** | GPT-4o 用 CoT 只有 60.9%，人类专家约 92% | FinanceMath |
| | 非专家人类的执行准确率约 51%，专家约 91%：题目需要领域知识 | FinQA |
| **数值计算 / 多步推理** | 错误分 4 类：误解题意、公式用错、取数错、算错；后两类随难度上升 | FinanceReasoning |
| | 推理深度增加时准确率最多降 51%；数字扰动下最多降 47 个百分点 | V-FiLLM |
| | 高级模板（多步）上，前沿模型也明显吃力 | FinChain |
| **信息缺失时的诚实** | 通用模型倾向于猜答案，不指出缺了什么；多数金融专用模型认不出缺失的前提 | RealFin |
| | 上下文缺失或无关时，最鲁棒的模型（o3-mini）41% 的情况下编造信息 | FailSafeQA |
| **核验 / 找错** | 核验含表格和文字的声明时，GPT-4o 明显落后于人类专家 | FinDVer |
| | 原始提示下，14 次完整运行中有 9 次对**无错**报表给出 95–100% 的假阳性；数字是否四舍五入会改变召回率（100% vs 79%） | FinVerBench |
| | 越难的错误越难查：一般知识类 52.33%，金融推理类 38.00% | FinED-Bench |
| **鲁棒性** | 语义不变的扰动（错别字、问法不完整等）会改变答案 | FailSafeQA |
| | 换数字或加无关条件就掉分，说明部分能力是模式匹配 | GSM-Symbolic |
| **记忆 / 污染** | 对新近年份、大公司的记忆更好，幻觉也随公司规模上升 | Beyond the Reported Cutoff |
| **工具使用与成本** | 准确率随花费呈对数增长，每题超过约 1 美元后收益很小；领先模型不超过 50%（论文版本） | Finance Agent Benchmark |

---

## 3. 哪些能用于 seed：逐项评估

seed 的特点：开卷计算比率，题目附原文片段，答案可以由 XBRL 数据算出。我们已有的工具：
- 从 XBRL 和正文取数，并与原文核对。
- 回测原题 GT。
- 处理口径问题。
- 成对出题。

### 第一档：建议采用（三方面都高）

| # | 改题方向（来源） | 在 seed 上怎么改（用现有题举例） | 数据可用性 | GT 可信性 | 评估可信性 | 主要风险 |
|---|---|---|---|---|---|---|
| 1 | **多期追踪**（Fin-RATE 跨期题、FAB Trends） | 024 P&G ROA：FY2025 vs FY2026 改为 FY2022–FY2026 每年的 ROA，问哪年最高、是否连续下降 | 高：companyfacts 有多年数据，需要 2–3 份 10-K | 高：代码计算 | 高：逐年数值（容差）+ 趋势判断 | **重述**：不同年份的 10-K 对同一年报的数可能不同（我们已遇到 P&G 员工数 107k 和 108k），题干须写明"用各年自己年报的数"或"用最新年报" |
| 2 | **跨公司比较**（Fin-RATE 跨公司题、FAB Market Analysis） | 005 JPM 杠杆率 → JPM vs GS 同一季度；SecQue 自带多家同行业公司 | 高：XBRL | 中高：两家公司的科目名可能不同，要做映射 | 高：两个数值 + 谁更高 | 财年截止日不同（P&G 6 月、多数公司 12 月）；只选两家科目口径相同的指标 |
| 3 | **缺前提识别**（RealFin、FinanceQA 假设题、FailSafeQA 缺失上下文） | 027 CCC 要求平均余额 → 给模型的原文片段里**删掉上一年存货**；正确做法是指出缺什么，或明确写出改用的假设 | 高：我们控制给什么原文 | **高：答案由构造决定**（删了哪项就是哪项） | 中高：判断"是否指出缺失项、是否编造数字"，可以用简单二分类裁判 | 只适用于附原文的设置；要确认删掉后真的无法从别处推出 |
| 4 | **计算核验 / 找错**（FinDVer、FinVerBench、FinED-Bench） | 001 Apple：给出"利息保障倍数 = EBIT ÷ 2,687"，问对不对、错在哪（2,687 实为支付的利息）。回测找到的 5 处真实错误可直接用，另外可人为注入：科目用错、两年口径混用、算术错、舍入错 | 高 | 高：错误由回测确认或人为注入 | 高：对 / 错 + 错误类型 + 改正后的数值 | **必须混入同样多的无错题做对照**（FinVerBench 发现模型大量误报）；舍入要统一 |
| 5 | **干扰上下文**（FailSafeQA 无关上下文、GSM-NoOp） | 006 Nike：同时给 NIKE Brand 收入和 NIKE Inc. 总收入；001 类：同时给利润表利息费用和现金流量表支付的利息 | 高 | 高：答案不变 | 高：与原题相同 | 干扰项要来自同一份文件，且确实容易混淆；我们回测发现的混淆点正好可以用 |
| 6 | **数字扰动**（GSM-Symbolic、V-FiLLM） | 按比例改动原文里的数字（生成"反事实年报"），答案用代码重算 | 高 | 中高：要保证报表恒等式仍成立（资产 = 负债 + 权益、小计） | 高 | 考查点和原题一样，**只适合作为污染对照**，不算"改变考什么" |

### 第二档：可以做，但要额外工作或换实验设置

| 改题方向（来源） | 为什么放第二档 |
|---|---|
| GAAP / 非 GAAP 调整（FAB Adjustments、FinanceQA） | 非 GAAP 数字不在 XBRL 里，要从正文取数，只有一个来源（我们做过 P&G 调整后 FCF，靠组成项互相核对） |
| 长文档（DocFinQA） | 把原文片段换成整份 10-K，题不变、GT 不变。变的是输入，考的是检索 |
| agent 检索（FinSearchComp、FAB、FinAgentBench） | 让模型自己用 EDGAR 工具找数据。GT 可以沿用，但要搭一套带工具的评测环境 |
| 子能力拆解（Benchmark Self-Evolving、ConvFinQA 多轮、FinanceReasoning 错误分类） | 把一道题拆成"找数 → 选公式 → 计算"几问。本身不是新题，而是**诊断工具**：能说清模型错在哪一步，正好回应"难度提升来自哪里"的质疑 |

### 第三档：不建议用于这个 seed

| 方向 | 原因 |
|---|---|
| 业绩是否超预期（FAB Beat or Miss） | 需要分析师一致预期，数据不公开 |
| 股价 / 市场数据 | Nike 新年报已删掉股价表；行情数据不在 SEC 文件里 |
| 新闻反事实（FIN-FORCE） | 答案是开放叙述，GT 无法验证 |
| 长篇分析按细则判分（FrontierFinance） | 评分依赖细则和裁判模型；与"答案可验证"的目标相反 |
| 简写、模糊的提问（FinDER） | 和我们"题目自足、答案唯一"的规则冲突 |
| 纯知识或公式题（FinanceMath、FinChain、CFA 类） | 不基于具体文件，只能借鉴公式库 |
| 公平性、安全性（FinTrust） | 与 Ratio 题无关 |
| XBRL 打标签（FinTagging） | 是另一种任务；但它的"科目对齐"思路可以帮我们自动诊断原题用错科目 |
| 合成文档（FinanceComplexQA、V-FiLLM 表格） | 不是真实文件，与 seed 的设置不同 |

---

## 4. 从池子里得到的质量控制经验

1. **公开数据集的 GT 本身就有不少错**。FinanceReasoning 修订了 4 个公开数据集的测试 / 验证集，需要更新的比例在 9.72%–30.00% 之间。我们回测的 17 道 seed 中有 5 道（约 29%）有实质性错误，比例相当。这说明"回测原题 GT"这一步本身就有价值，可以作为贡献点。
2. **舍入和呈现方式会改变测量结果**（FinVerBench）。我们已有"靠近舍入分界"的标记，找错题要统一舍入规则。
3. **找错题必须配无错对照**。否则一个"什么都说有错"的模型也能得高分。
4. **多种正确算法**。SecQue 原文承认存在这个问题但没有处理。我们在题干里写明口径，比事后接受多种答案更干净。
5. **能用代码打分就不用裁判模型**。
   - FinQA 用执行准确率，FinanceQA 用精确匹配（"金融里没有部分分"）。
   - SecQue、FailSafeQA、FAB 依赖裁判模型，需要多次打分或人工校准。
   - 建议新题的答案用结构化字段（数值、方向、缺失项、错误类型），代码判分；裁判模型只用于评解释文字。
6. **闭卷测试要控制公司规模和年份**（Beyond the Reported Cutoff）。我们的公司全是超大市值公司，闭卷下"记住旧答案"的效应会偏大。

---

## 5. 建议的下一步

1. 在现有 15 道题上试点 **多期追踪、缺前提识别、计算核验** 三个方向，每个方向生成 10–15 道。
2. 每道新题记录：来源方向、依据的论文缺陷、GT 的构造方式、打分方式。
3. 同一受测模型分别答原题和新题，按方向报告准确率变化；用"子能力拆解"说明掉分发生在哪一步。

---

## 参考链接

- SecQue: https://arxiv.org/abs/2504.04596 ・ 数据 https://huggingface.co/datasets/nogabenyoash/SecQue
- FinanceBench: https://arxiv.org/abs/2311.11944
- DocFinQA: https://arxiv.org/abs/2401.06915
- SEC-QA: https://arxiv.org/abs/2406.14394
- FinDER: https://arxiv.org/abs/2504.15800
- Fin-RATE: https://arxiv.org/abs/2602.07294
- FinAgentBench: https://arxiv.org/abs/2508.14052
- Finance Agent Benchmark: https://arxiv.org/abs/2508.00828 ・ https://vals.ai/benchmarks/finance_agent
- FinSearchComp: https://arxiv.org/abs/2509.13160
- FrontierFinance: https://arxiv.org/abs/2608.11683
- FinQA: https://arxiv.org/abs/2109.00122
- ConvFinQA: https://arxiv.org/abs/2210.03849
- TAT-QA: https://arxiv.org/abs/2105.07624 ・ https://github.com/NExTplusplus/tat-qa
- MultiHiertt: https://arxiv.org/abs/2206.01347
- BizBench: https://arxiv.org/abs/2311.06602
- FinanceMath: https://arxiv.org/abs/2311.09797
- FinanceReasoning: https://arxiv.org/abs/2506.05828
- FinChain: https://arxiv.org/abs/2506.02515
- V-FiLLM: https://arxiv.org/abs/2608.11047
- FinanceQA: https://arxiv.org/abs/2501.18062
- RealFin: https://arxiv.org/abs/2602.07096
- FailSafeQA: https://arxiv.org/abs/2502.06329 ・ https://huggingface.co/datasets/Writer/FailSafeQA
- FinDVer: https://arxiv.org/abs/2411.05764
- FinVerBench: https://arxiv.org/abs/2605.29586
- FinED-Bench: https://arxiv.org/abs/2608.12342
- FinTrust: https://arxiv.org/abs/2510.15232
- FinTagging: https://arxiv.org/abs/2505.20650
- Benchmark Self-Evolving: https://arxiv.org/abs/2402.11443
- SEB（ICML 2026）: https://icml.cc/virtual/2026/77935
- GSM-Symbolic: https://arxiv.org/abs/2410.05229
- FinForge: https://arxiv.org/abs/2601.06747
- Beyond the Reported Cutoff: https://arxiv.org/abs/2504.00042
- FIN-FORCE: https://arxiv.org/abs/2505.19430
