# 新种子候选：不靠长材料、主要考金融知识的 benchmark

日期：2026-11-21　｜　范围：2024-11 以后发布　｜　来源：arXiv 摘要、ACL Anthology、数据集页面（只看了摘要和目录页，标"待核实"的要打开原文确认）

## 结论

首选 **XFinBench**，备选 **FinanceReasoning（Hard 子集）**；**FinChain** 适合拿来做"GT 构造即正确"的对照。

挑选标准：
- 题目自带所需数字，或只附一小段材料，可以在不检索的条件下作答；
- 难点在金融概念、公式和推理，不在找数；
- 数据公开，有标准答案；
- 没被刷满，强模型之间还有差距。

## 第一档：建议优先看

### XFinBench（ACL 2025 Findings，arXiv 2508.15861）
- 4,235 题，取自研究生金融教材。考查：术语理解、时间推理、预测、情景规划、数值建模。
- 最好的纯文本模型 o1 总正确率 67.3%，在时间推理和情景规划上落后人类专家最多，说明还没被刷满。
- 部分题带图（曲线图等），用作种子时只取纯文本题。
- 附 3,032 个金融术语的知识库。作者发现补充知识只对小模型有稳定提升，可见它考的不只是"背没背过"。
- 公开：GitHub 和 Hugging Face（`Zhihan/XFinBench`），MIT 许可。
- 待核实：题型分布（判断、选择、计算各占多少）。

### FinanceReasoning（ACL 2025，arXiv 2506.05828）
- 2,238 题，分 Easy、Medium、Hard。其中 Hard 238 题，平均约 8 步推理，要组合多个公式。
- 作者修订了 4 个公开数据集里 15.6% 的题，新标注 908 题，每题附 Python 解法，所以 GT 可以执行复核。
- 判分严格：允许 0.2% 误差，单位、符号、小数位都要对。o1 用代码解题（PoT），在 Hard 上达到 89.1%。
- 附 3,133 个金融函数（公式库）。
- 注意：部分题来自 FinQA、TAT-QA 系的数据集，带报表片段，要先筛掉，只留题干自带数字的题。
- 公开：Hugging Face `BUPT-Reasoning-Lab/FinanceReasoning`。许可待核实。

### FinChain（ACL 2026，arXiv 2506.02515）
- 12 个金融领域、58 个主题。每个主题 5 个参数化模板：2 个简单、2 个中等、1 个难。每个模板附可执行的 Python 代码，生成题目、逐步推理和答案。
- GT 构造即正确，还能逐步检查推理（ChainEval）。作者测了 26 个模型，难模板上前沿模型也吃力。
- 对我们的用处：它本身就能生成新数值的题，用它当种子做"换数字"意义不大。更适合两种用法：
  - 当对照：比较我们的改题方法和它的模板生成，哪种做出的题更有区分度；
  - 借它的代码，给我们改过的题快速算 GT。
- 公开：GitHub `mbzuai-nlp/finchain`。

### QuantEval（arXiv 2601.08689，2026-01）
- 1,575 题：知识问答 660、量化数学推理 855、量化策略编程 60。策略编程题会被放进回测框架实际运行。
- 偏量化金融，不是公司财务。如果论文想覆盖公司财务以外的领域，可以作为第二个种子。
- 作者称数据、评测脚本和回测配置都已公开，待核实。

## 第二档：有用，但有明显限制

| 名称 | 是什么 | 限制 |
|---|---|---|
| FINESSE-Bench（arXiv 2605.15482，2026-05） | 8 个子集共 3,993 题，仿 CFA 一至三级、CMT、CFTe 考试，另有交易任务和一套俄语竞赛题 | 多为考试式题目，题型和许可待核实 |
| FinEval-KR（arXiv 2506.21591） | 中文，22 个子领域，把"知识分"和"推理分"分开算 | 中文题；它的拆分方法对我们"到底考到什么能力"的问题很有参考价值 |
| BankMathBench（LREC 2026，arXiv 2602.17072） | 存款、贷款等银行产品的计算题，分三级难度，自动流水线生成 | 场景窄；语言待核实（作者来自 KakaoBank） |
| FinanceQA（AfterQuery，arXiv 2501.18062） | 模仿投资分析工作的计算题，其中一类要求模型自己补合理假设 | 部分任务依赖 10-K 原文；排行榜最好成绩约 54% |
| RiskReason（arXiv 2611.01236，2026-11） | 金融风险推理，每题附形式化规格、可验证答案和依赖关系图 | 刚发布，细节未核实 |

## 不建议

- **CFA 三级评测（arXiv 2507.02954）**：用的是商业模拟题，不公开，没法当种子。
- **FinanceMath、BizBench**：2023 年 11 月发布，超出两年范围。FinanceReasoning 已经修订并吸收了同类题目。

## 换成知识型种子要注意的两件事

1. **评测设置简单了，但污染风险更大。**不用给材料，"给多少材料"的问题自然消失，不给材料就是合理设置。但这类题考的是记忆里的知识，教材和考试题很可能出现在训练数据里。这正好是 AutoFinBench 改题的动机，改题时要换数字和情景，不能只换说法。
2. **GT 复核换了一种做法。**原来是回到 SEC 原文核对取数；换成知识题后，没有原文可查。可以用两种办法：
   - 用代码重算：FinanceReasoning 有 Python 解法，FinChain 有模板代码；
   - 让多个强模型独立求解，答案不一致的交人裁决。

## 来源

- XFinBench: https://arxiv.org/abs/2508.15861 ，https://aclanthology.org/2025.findings-acl.457
- FinanceReasoning: https://arxiv.org/abs/2506.05828v2 ，https://aclanthology.org/2025.acl-long.766
- FinChain: https://arxiv.org/abs/2506.02515v3 ，https://aclanthology.org/2026.acl-long.662/
- QuantEval: https://arxiv.org/abs/2601.08689
- FINESSE-Bench: https://arxiv.org/abs/2605.15482
- FinEval-KR: https://arxiv.org/abs/2506.21591
- BankMathBench: https://arxiv.org/abs/2602.17072
- FinanceQA: https://arxiv.org/abs/2501.18062
- RiskReason: https://arxiv.org/pdf/2611.01236
- CFA Level III: https://arxiv.org/abs/2507.02954
