# 相关工作检索：自动更新 / 自我演化的 benchmark（侧重金融）

检索日期：2026-11-25。方法：Web 搜索加 arXiv 摘要页核对。**只读了摘要**，没有读全文；标 ⚠️ 的条目只见到标题或片段，未核实。

## 一句话结论

**目前没有找到完全对口的金融工作**，即同时满足以下五点：
1. 从种子 benchmark 出发；
2. agent 自己去做题、探查；
3. 根据失败反思改进方向；
4. 改写或更新题目；
5. 新 GT 可验证。

完整闭环只在**非金融**领域出现（AutoSciBench）。金融领域的工作各自只覆盖其中一两块。另外，没有检索到名为 "AutoFinBench" 的论文或项目。

---

## A. 通用领域：benchmark 自动生成 / 演化（必引，也是方法上的直接对手）

| 论文 | 时间 | 从种子出发 | 求解→反思→改题闭环 | GT 怎么保证 | 领域 |
|---|---|---|---|---|---|
| [AutoSciBench](https://arxiv.org/abs/2610.05140) (Kim et al., Genentech/KAIST) | 2026-10 | 是 | **是**：solver 轨迹加 judge 反馈，修改 recipe 或 concept；结束后把经验蒸馏给新 concept | recipe 中规定 GT 的构造和验证方式 | 计算生物、材料、临床影像 |
| [Benchmark Self-Evolving](https://arxiv.org/abs/2402.11443) (Wang et al., 复旦) | 2024-02 | 是 | 否：多 agent 用 6 种 reframing 操作改写 context 或问题，没有反馈循环 | 摘要只说 "high confidence" | 4 个通用任务；[代码](https://github.com/NanshineLoong/Self-Evolving-Benchmark) |
| [TRACE](https://arxiv.org/abs/2510.00415) (Guo et al.) | 2025-10 | 是 | 部分：agent 自由探索，把题演化得更难，分阶段流水线，不是迭代闭环 | validate-by-reproduce，要求轨迹可复现 | GAIA、AIME-2024 |
| [Benchmark Agent](https://arxiv.org/abs/2606.06462) (Xiong et al.) | 2026-06 | 否，从用户需求出发 | 否：端到端构建流水线加 QC | 人评、LLM judge、一致性检查 | 通用，含领域推理 |

**和我们的关系**：AutoSciBench 是模板，也是对标对象。Benchmark Self-Evolving 的"操作算子"思路和我们 step1/step2 的 operator 很像，需要说明差别。TRACE 的"可复现验证"可以对照我们的 GT 可信度问题。

## B. 金融：会自动刷新或生成题目的 benchmark（最接近的金融工作）

| 论文 | 时间 | 做了什么 | 缺什么（相对我们） |
|---|---|---|---|
| [SEC-QA](https://arxiv.org/abs/2406.14394) (Lai et al., Kensho) | 2024-06 | "continuous dataset generation"：用最新的、LLM 还没见过的 SEC 文件半自动生成 QA，可以反复刷新 | 没有 agent 反思闭环，不从种子题出发 |
| [LiveSearch](https://arxiv.org/abs/2610.37166) | 2026-10 | 每道题存成**可执行验证程序**（调用专业金融数据 API 加抽取器），题面固定，GT 每天重新执行得出；3 天内有 70% 的题 GT 发生变化 | 没有反思改题，题目由枚举加 LLM 转述生成；**GT 设计值得借鉴** |
| [Backtrader-Bench](https://arxiv.org/abs/2608.11232) (IJCAI'26 FinLLM WS) | 2026-07 | generator 写带验证代码的题；**不用工具的 solver 能答对的题丢掉**；独立 checker 重新推导答案。[代码](https://github.com/rzhao999/Backtrader-Bench) | 只做过滤，不反思生成策略；限于量化回测场景 |
| [FinForge](https://arxiv.org/abs/2601.06747) (Matlin et al., GT FinTech Lab) | 2026-01 | 从专家筛选的语料出发，LLM 生成并验证 QA，再经人工验证，得到 FinForge-5k。[代码](https://github.com/gtfintechlab/FinForge) | 是快照，没有闭环，也没有种子题 |
| [FinTradeBench](https://arxiv.org/abs/2603.19225) | 2026-03 | **150 道专家种子题，跨公司、跨时间扩展到 1400 道**（NASDAQ-100，十年） | 摘要没写怎么扩展，代码尚未发布；**和我们的 time-shift 思路最像，必须读全文** |
| [FinDeepForecast](https://arxiv.org/abs/2601.05039) | 2026-01 | live 多 agent 系统，每周生成金融预测题（1314 家公司），已连续运行 10 周 | 是预测题，GT 等事件发生后得到；没有改题闭环 |
| [FutureX-Pro / FutureX-Finance](https://arxiv.org/abs/2601.12259) (字节) | 2026-01 | 沿用 FutureX 的 live、无污染流水线，扩展到金融等垂直领域 | 同上，是预测类 |

## C. 容易混淆：自我演化的是 agent，不是 benchmark

写 related work 时要和下面这些划清界限，审稿人可能会拿来对比：

- [FinSkillOps](https://arxiv.org/abs/2609.19680)：SEC 文件 QA 系统，从失败诊断中提炼 skill 补丁并做回归验证。演化的是**系统**，不是题目。
- ⚠️ [FinEvolveBench](https://arxiv.org/pdf/2606.06960)、⚠️ [FinEvo-Bench](https://arxiv.org/pdf/2608.06144)：评测"会自我演化的 agent"的 benchmark，题目本身是固定的。
- ⚠️ [LiveMACE](https://arxiv.org/pdf/2610.09872)、⚠️ [Investor's Last Exam](https://arxiv.org/pdf/2610.38342)、⚠️ Stanford EDGAR 数据集中的 EDGAR-Forecast（[2606.18192](https://arxiv.org/html/2606.18192v2)，用 2026 年 10-Q 做截止日之后的预测）：只看到片段，未核实。
- 静态金融 benchmark（不更新，可作为种子来源）：[FinSearchComp](https://arxiv.org/abs/2509.13160)、Finance Agent Benchmark（[2508.00828](https://arxiv.org/pdf/2508.00828)，v2.1 靠专家人工修题）。

---

## 对 AutoFinBench 的含义（我的判断）

1. **空白点成立**：同时具备"金融 + 种子驱动 + solver 反馈的反思闭环 + 可验证 GT"的工作还没有。最好的说法是"把 AutoSciBench 式闭环搬到金融，并解决金融特有的 GT 可信问题"。
2. **最大威胁是 FinTradeBench**（种子跨公司、跨时间扩展）和 **SEC-QA**（用新文件刷新）。两者都要读全文，说明我们比它们多了什么：反思闭环、改变考察能力的算子、GT 验证。
3. **可以直接借的设计**：
   - LiveSearch 的"题目 = 可执行程序，GT 由执行得到"，可用来回答 GT 可信度问题；
   - Backtrader-Bench 的"不用工具的 solver 能答对就丢弃"，正好可以作为审稿人要的 rejection-sampling baseline 的一个版本。
4. **下一步建议**：读 FinTradeBench、SEC-QA、AutoSciBench、LiveSearch 的全文，补一张逐维对比表，放进 proposal 的 related work。
