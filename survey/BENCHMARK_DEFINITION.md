# Benchmark 与 Benchmark Task 的形式化定义：文献调研

日期：2026-11-27 · 作者：Claude（为 AutoBenchmark / AutoFinBench 研究准备）

## 阅读说明

**标记方式**
- **【原文】**：论文原句，保留英文，并注明章节。
- **【我的归纳】**：我自己的总结和判断，不是论文观点。

**核实方式**
- 每条【原文】都读过 arXiv HTML 或 PDF 全文。PDF 用 `pdftotext` 抽取，再在文本里定位原句。
- 读不到全文的文献集中列在 §6，正文不引用。
- 不预设你的三元组 `Task = (Question, Environment, Evaluation Rubrics)` 是对的，第 4 节专门评价它。

---

## 0. 结论速览

**Q1：有没有论文、综述或标准对 benchmark 或 task 做过明确的数学定义或结构化拆解？**

有，但分散在五类文献里。在我检索的范围内，**没有一个被广泛接受、统一的"benchmark"数学定义**。

| 类别 | 代表文献 | 形式化程度 |
|---|---|---|
| A. 概念定义（什么是 benchmark） | Raji 2021、Sim 2003、Kistowski 2015、Donoho 2017、Bean 2025 | 结构化文字，没有公式 |
| B. 单个任务的数学形式化 | MAML 2017、WebArena、OSWorld、τ-bench、SWE-bench、bsuite | **有公式**（MDP/POMDP 元组、奖励函数） |
| C. 工程标准（任务由哪些文件和函数组成） | Harbor、METR Task Standard、Inspect AI | 接口规范 |
| D. 测量学与统计 | VIM（JCGM 200:2012）、Wallach 2025、Miller 2024、tinyBenchmarks | **有公式**（测量模型、标准误、IRT） |
| E. benchmark 整体性质的定义 | AutoBencher、ABC、BetterBench、HELM | **有公式**（AutoBencher 的难度、区分度、新颖性） |

**Q2：用哪些变量描述 benchmark？有没有比三元组更全面的定义？**
- 我从文献里归纳出 **19 类变量**，见 §2。三元组覆盖了其中 3 类，另外部分覆盖 3 类。
- 有更全面的拆解：
  - **测量学视角**：Wallach 的四个层级和四个过程。
  - **RL 视角**：MAML 的任务四元组加任务分布 p(T)，bsuite 的"环境、交互、分析"。
  - **工程视角**：Harbor 和 METR 的任务结构，它们与你的三元组几乎一致，但多了参考解和资源配置。
- 第 5 节给出一个综合草案，属于我的归纳。

---

## 1. 逐篇文献

### A. 概念层：什么是 benchmark

#### A1. Raji et al. 2021, *AI and the Everything in the Whole Wide World Benchmark*
- 链接：https://arxiv.org/abs/2111.15366 （NeurIPS 2021 Datasets & Benchmarks track）
- **【原文】§2.2**：
  > "we describe a *benchmark* as a particular combination of a dataset or sets of datasets (at least test data, sometimes also training data), and a metric, conceptualized as representing one or more specific tasks or sets of abilities, picked up by a community of researchers as a shared framework for the comparison of methods."
  >
  > "The task is a particular specification of a problem, as represented in the dataset."
  >
  > "A metric is a way to summarize system performance over some set or sets of tasks as a single number or score. The metric provides a means of counting success and failure at the level of individual system outputs and summarizing those counts over the full dataset."
- **【我的归纳】与三元组的关系**：
  - 对应关系：dataset 大致对应 Question（含 GT），metric 对应 Evaluation。**这里没有 Environment**，因为这是静态数据集时代的定义。
  - Raji 多出两样东西：
    1. "conceptualized as representing … abilities"，也就是要测的能力，即构念。
    2. "picked up by a community"，强调社会接受这一层。
  - metric 被明确拆成两层：**单个输出的判对**和**整个数据集上的汇总**。三元组里的 Rubrics 把这两层合在了一起。

#### A2. Sim, Easterbrook & Holt 2003, *Using Benchmarking to Advance Research: A Challenge to Software Engineering*（ICSE 2003）
- 论文本身在 IEEE 付费墙后，没读到。下面引用的是 **Sim 本人的报告幻灯片**：*Benchmarking: The Way Forward for Software Evolution*，https://soft.vub.ac.be/FFSE/Workshops/ELISA-submissions/Sim-slides.pdf 。另外 Prechelt 的课程讲义（https://www.inf.fu-berlin.de/inst/ag-se/teaching/V-EMPIR-2023/15_benchmarking.pdf ）引用的是这篇 ICSE 2003 论文，列出的组成部分相同。
- **【原文】幻灯片 "What is a benchmark?" 和 "Benchmark Components" 两页**：
  > "A benchmark is a standard test or set of tests used to compare alternatives. It consists of a motivating comparison, a task sample, and a set of performance measures."
  >
  > "1. Motivating Comparison – Comparison to be made – Motivation for research area and benchmark"
  >
  > "2. Task Sample – Representative sample of problems from a problem domain – Most controversial part of benchmark design"
  >
  > "3. Performance Measures – Performance = fitness for purpose; a relationship between technology and task – Can be qualitative or quantitative, measured by human, machine, or both"
- **【我的归纳】**：
  - 这是一个和你的三元组**同级、但切法不同**的三元组：
    - **Motivating Comparison**：为什么比、比什么。三元组里没有。
    - **Task Sample**：强调"从问题域中**抽样**"，也就是代表性。三元组只描述单题，没有抽样这个概念。
    - **Performance Measures**：对应 Evaluation，但定义为"技术与任务之间的关系"。
  - 同样没有 Environment。

#### A3. von Kistowski et al. 2015, *How to Build a Benchmark*（ICPE 2015, SPEC/TPC 视角）
- 链接：https://research.spec.org/icpe_proceedings/2015/proceedings/p333.pdf （DOI 10.1145/2668930.2688819）
- **【原文】§2.1**：
  > "We define a benchmark as a 'Standard tool for the competitive evaluation and comparison of competing systems or components according to specific characteristics, such as performance, dependability, or security'."
- **【原文】§1 与 §2.2，三种类型**："specification-based, kit-based, and hybrid"。其中 "Specification-based benchmarks begin with a definition of a business problem to be simulated by the benchmark"，而 kit-based 提供 "near 'load and go' implementations"。
- **【原文】§3，五条质量标准**：
  > "Relevance: How closely the benchmark behavior correlates to behaviors that are of interest to consumers of the results"
  >
  > "Reproducibility: The ability to consistently produce similar results when the benchmark is run with the same test configuration"
  >
  > "Fairness: Allowing different test configurations to compete on their merits without artificial limitations"
  >
  > "Verifiability: Providing confidence that a benchmark result is accurate"
  >
  > "Usability: Avoiding roadblocks for users to run the benchmark in their test environments"
- **【我的归纳】**：
  - "specification-based 和 kit-based"的区分说明：**环境不一定由 benchmark 提供**。只给问题规格的 benchmark，环境由参赛方自己实现。三元组默认环境属于任务本身。
  - 五条标准是对 benchmark 的**性质约束**，不是组成部分。其中 Verifiability（结果是否准确）和 Reproducibility 与你关心的 GT 可信度直接相关。

#### A4. Donoho 2017, *50 Years of Data Science*（JCGS 2017；2015 年版本）
- 链接：https://courses.csail.mit.edu/18.337/2015/docs/50YearsDataScience.pdf
- **【原文】§6.1 "The Common Task Framework"**：
  > "An instance of the CTF has these ingredients:
  > (a) A publicly available training dataset involving, for each observation, a list of (possibly many) feature measurements, and a class label for that observation.
  > (b) A set of enrolled competitors whose common task is to infer a class prediction rule from the training data.
  > (c) A scoring referee, to which competitors can submit their prediction rule. The referee runs the prediction rule against a testing dataset which is sequestered behind a Chinese wall. The referee objectively and automatically reports the score (prediction accuracy) achieved by the submitted rule."
- 补充：Donoho 2023 年的 *Data Science at the Singularity*（https://arxiv.org/abs/2310.00865 ，§3 [FR-3]）改称 "Challenge Problems Paradigm"，列出 "a shared public dataset, a prescribed and quantified task performance metric, a set of enrolled competitors"，以及 public leaderboard。
- **【我的归纳】**：
  - CTF 是**制度层面**的定义，三元组是单题层面的定义。
  - CTF 多出三样东西：**参赛者**、**裁判**、**被隔离的测试集**。"隔离"正是防污染的制度设计。
  - 对 AutoFinBench 的意义：你要论证的"新 benchmark 不被污染"，在 CTF 的框架里属于 (c)，即测试集保密，而不属于题目本身。

#### A5. Hardt, *The Emerging Science of Machine Learning Benchmarks*（在线书）
- 链接：https://mlbenchmarks.org （Ch.1 https://mlbenchmarks.org/01-introduction.html ，Ch.4 https://mlbenchmarks.org/04-holdout-method.html ）
- **【原文】Ch.1**：
  > "Benchmarking is the iron rule of machine learning research and a radically simple contract at that: Anything goes on the training set, competitive ranking on the test set."
- **【原文】Ch.4**：
  > "A core part of any machine learning benchmark is the *leaderboard*, a ranking of all models by empirical risk on the holdout set."
- **【我的归纳】**：在读到的章节里**没有找到对 benchmark 的形式定义**。它强调的组成部分是"训练集/测试集划分"加"排行榜"。

#### A6. Bean et al. 2025, *Measuring what Matters: Construct Validity in Large Language Model Benchmarks*（NeurIPS 2025 D&B）
- 链接：https://arxiv.org/abs/2511.04703
- **【原文】§1**：
  > "we consider a benchmark to be a 'task' and 'metric' which are used together to represent a 'phenomenon' of interest."
  - 脚注 1 以 GSM8K 为例：phenomenon 是 "multi-step mathematical reasoning"。
- **【原文】§3.8** 要求阐明 "the chain of decisions from defining a phenomenon, to operationalising it via a task…"。
- **【我的归纳】**：这是一个 **(phenomenon, task, metric) 三元组**。和你的三元组相比，多了 phenomenon（要测的能力），少了 environment。

### B. 任务层：数学形式化（RL 与 agent）

#### B1. Finn et al. 2017, *Model-Agnostic Meta-Learning*（MAML, ICML 2017）
- 链接：https://arxiv.org/abs/1703.03400
- **【原文】§2.1 "Meta-Learning Problem Set-Up"**：
  > "Formally, each task T = {L(x₁, a₁, …, x_H, a_H), q(x₁), q(x_{t+1} | x_t, a_t), H} consists of a loss function L, a distribution over initial observations q(x₁), a transition distribution q(x_{t+1} | x_t, a_t), and an episode length H. In i.i.d. supervised learning problems, the length H = 1."
  - 同一节随后考虑任务上的分布 p(T)。
- **【我的归纳】这是最接近"任务的通用数学定义"的一条**：
  - q(x₁) 是初始观测，大致对应 Question 加初始材料。
  - q(x_{t+1} | x_t, a_t) 对应 Environment。
  - L 对应 Evaluation。
  - **H 是交互长度或预算，三元组没有**。
  - **p(T) 把 benchmark 看成"任务的分布"**。AutoBenchmark 的生成器本质上就是一个从 p(T) 采样的程序，这一点三元组无法表达。
  - 监督学习是 H=1 的特例，所以这个定义同时覆盖了静态问答和 agent 任务。

#### B2. Zhou et al. 2023, *WebArena*（ICLR 2024）
- 链接：https://arxiv.org/abs/2307.13854
- **【原文】§2.1**："ℰ = ⟨𝒮, 𝒜, 𝒪, 𝒯⟩"，其中 "𝒯: 𝒮×𝒜 → 𝒮 is deterministic"。原文还写道："Given a task described as a natural language intent 𝐢, an agent issues an action a_t ∈ 𝒜 based on intent 𝐢"，以及 "We propose a reward function r(𝐚₁ᵀ, 𝐬₁ᵀ) to measure the success of a task execution"。
- **【原文】§3.2**：
  - 信息查询类任务用 r_info(â, a*)，判定方式包括 exact_match、must_include、fuzzy_match。
  - 导航和配置类任务用 r_prog(𝐬)，"programmatically examine[s] the intermediate states"。
- **【我的归纳】**：
  - 对应关系：Question 是 intent 𝐢，Environment 是 ℰ，Evaluation 是 r。
  - 两点值得注意：
    1. r 的输入是**整条轨迹**（动作序列和中间状态），而不只是最终答案。
    2. **参考答案 a\* 和判分函数 r 是分开的**，而三元组的 Rubrics 把两者合在一起。

#### B3. Xie et al. 2024, *OSWorld*（NeurIPS 2024 D&B）
- 链接：https://arxiv.org/abs/2404.07972
- **【原文】§2.1 "Task Definition"**：
  - 任务被形式化为 POMDP "(𝒮, 𝒪, 𝒜, 𝒯, ℛ)"，其中 𝒯: 𝒮×𝒜→𝒮，ℛ: 𝒮×𝒜→ℝ。
  - 实现上 "we implement an execution-based reward function ℛ: 𝒮×𝒜→[0,1]"。
- **【原文】摘要和 §3.2**：每个任务 "includes a detailed initial state setup configuration and a custom execution-based evaluation script"，并且 "Each example is carefully annotated with a natural language instruction"。
- **【我的归纳】**：
  - 任务实际由三部分组成：instruction、initial state config、evaluation script。这和你的三元组几乎一致。
  - 区别在于：环境（操作系统和应用）是**所有任务共享的**，每个任务只提供**初始状态配置**。所以"Environment"这一项其实应该拆成**共享环境 E**和**单题初始状态 s₀**。

#### B4. Yao et al. 2024, *τ-bench*
- 链接：https://arxiv.org/abs/2406.12045
- **【原文】§3**：
  - 任务被形式化为 POMDP "(𝒮, 𝒜, 𝒪, 𝒯, ℛ, 𝒰)"，其中 𝒯: 𝒮×𝒜→𝒮×𝒪，ℛ: 𝒮→[0,1]，𝒰 是 instruction space。
  - 状态和动作都由数据库和模拟用户两部分组成：𝒮 = 𝒮_db ⊗ 𝒮_user，𝒜 = 𝒜_db ∪ 𝒜_user。
- **【原文】§3 Reward**："r = r_action × r_output ∈ {0,1}"。其中 r_action 检查最终数据库是否 "identical to the unique ground truth outcome database"。
  - 注意：论文自身有一处不一致，元组里写 ℛ→[0,1]，Reward 段落写 {0,1}。
- **【原文】§3 pass^k**：pass^k = 𝔼_task[ C(c,k) / C(n,k) ]，含义是 "the chance that all k i.i.d. task trials are successful, averaged across tasks"。
- **【我的归纳】**：
  - **指令空间 𝒰 被直接放进了 POMDP 元组**，模拟用户也是状态的一部分。也就是说，**Question 不一定独立于 Environment**。
  - pass^k 说明**重复试验的协议**（试验次数 n 和 k）本身就是评价定义的一部分，衡量的是可靠性而不只是能力。

#### B5. Jimenez et al. 2024, *SWE-bench*（ICLR 2024）
- 链接：https://arxiv.org/abs/2310.06770
- **【原文】§2.2**："A model is given an issue text description and a complete codebase."，评价指标是 "the percentage of task instances that are resolved"。
- **【原文】§A.3–A.4**：
  - 测试按状态变化分为 FAIL_TO_PASS 和 PASS_TO_PASS 两组。
  - 判定成功的条件是 "we check that all FAIL_TO_PASS and PASS_TO_PASS tests are found and have a pass status"。
- **【我的归纳】**：评价被拆成两部分的合取，即"**目标达成**"（FAIL_TO_PASS 通过）且"**没有破坏原有功能**"（PASS_TO_PASS 仍然通过）。三元组的 Rubrics 没有显式区分这种"副作用约束"。

#### B6. Osband et al. 2020, *Behaviour Suite for Reinforcement Learning*（bsuite, ICLR 2020）
- 链接：https://arxiv.org/abs/1908.03568
- **【原文】§2 "Experiments"**：
  > "In the context of bsuite, an experiment consists of three parts: 1. Environments: a fixed set of environments determined by some parameters. 2. Interaction: a fixed regime of agent/environment interaction (e.g. 100 episodes). 3. Analysis: a fixed procedure that maps agent behaviour to results and plots."
- **【我的归纳】**：这是 **(Environments, Interaction, Analysis) 三元组**。其中 **Interaction（固定的交互制度）是你的三元组没有的**。另外，Analysis 是"从行为到结果"的映射，层级在单题评分之上。

### C. 工程标准：一个任务由哪些部分组成

#### C1. Harbor（Terminal-Bench 的任务框架）
- 链接：https://docs.harborframework.com/tasks/overview.md
- **【原文】**："A Harbor task is an instruction, environment, and test script."
- 目录结构（原文）：`instruction.md`，`task.toml`，`environment/Dockerfile`，`solution/solve.sh`，`tests/test.sh`。
- `tests/test.sh` "must produce a numerical reward in the environment at `/logs/verifier/reward.txt`"。还支持多步任务，结构为 `steps/step-N/`。
- **【我的归纳】**：
  - 和你的三元组**几乎一一对应**。
  - 但多了 **`solution/`（参考解，即 oracle）** 和 **`task.toml`（任务配置）**。task.toml 的具体字段我没读到，这里不展开。
  - 参考解的作用是证明任务可解。这正是 ABC 所说"任务有效性"的工程实现。

#### C2. METR Task Standard
- 链接：https://github.com/METR/task-standard 。该仓库已于 2026-10 归档，README 写明 METR 现在改用 Inspect 定义任务。
- **【原文】README "What is a task?"**：
  > "A task specifies: 1. An environment for an agent to interact with… 2. A string of instructions for the agent… 3. Optionally, a way to automatically score the agent's attempt…"
  >
  > "Tasks are defined as part of a task family, which are one or more related tasks that may share a bunch of implementation."
- README 示例里出现的接口包括 `get_tasks()`、`get_instructions(t)`、`install()`、`start`、`score(t, submission)`、`get_aux_vm_spec`、permissions，以及在 `manifest.yaml` 里声明的 CPU、内存、GPU 资源。完整列表在 STANDARD.md，我没读到。
- **【我的归纳】**：
  - 同样是 (environment, instructions, scoring) 三元组。
  - 但 **scoring 是可选的**，允许人工评分。
  - 另外引入了 **task family**，即参数化的任务族。一个族可以生成多个任务，这和 AutoBenchmark 的"种子题加算子"在结构上是同一个概念。

#### C3. Inspect AI（英国 AISI）
- 链接：https://inspect.aisi.org.uk/tasks.html ，https://inspect.aisi.org.uk/datasets.html
- **【原文】Tasks 页**："Tasks provide a recipe for an evaluation consisting minimally of a dataset, a solver, and a scorer (and possibly other options)"。
  - Task 的可选项包括 `epochs`、`sandbox`、`approval`、`metrics`、`message_limit`、`token_limit`、`time_limit`、`version`、`metadata` 等。
- **【原文】Datasets 页**：Sample 有 "a required `input` field and several other optional fields"，包括 `target`、`choices`、`id`、`metadata`、`sandbox`、`files`、`setup`。
- **【我的归纳】**：
  1. **solver（被测系统的脚手架）被放进了任务定义**，而三元组和多数学术定义都把它排除在外。
  2. 评价被分成三部分：**target**（参考答案）、**scorer**（单题评分）、**metrics**（汇总）。
  3. **epochs（重复次数）和各种 limit（预算）**都是任务的显式参数。

### D. 测量学与统计

#### D1. JCGM 200:2012, *International Vocabulary of Metrology*（VIM 第 3 版，BIPM）
- 链接：https://www.bipm.org/documents/20126/2071204/JCGM_200_2012.pdf
- **【原文】条款 2.1 measurement**："process of experimentally obtaining one or more quantity values that can reasonably be attributed to a quantity"。
  - NOTE 3："Measurement presupposes a description of the quantity commensurate with the intended use of a measurement result, a measurement procedure, and a calibrated measuring system operating according to the specified measurement procedure, including the measurement conditions."
- **【原文】2.3 measurand**："quantity intended to be measured"。
- **【原文】2.6 measurement procedure**："detailed description of a measurement according to one or more measurement principles and to a given measurement method, based on a measurement model and including any calculation to obtain a measurement result"。
- **【原文】2.26 measurement uncertainty**："non-negative parameter characterizing the dispersion of the quantity values being attributed to a measurand, based on the information used"。
- **【原文】2.48 measurement model**："mathematical relation among all quantities known to be involved in a measurement"。
  - NOTE 1："A general form of a measurement model is the equation h(Y, X₁, …, X_n) = 0, where Y … is the measurand"。
- **【我的归纳】**：
  - 如果把 benchmark 看作一套 measurement procedure，那么 VIM 要求先有 **measurand（被测量）**，最后要给出 **uncertainty（不确定度）**。这两样三元组都没有。
  - NOTE 3 的三个前提，即对被测量的描述、测量程序、按程序运行的已校准测量系统，可以分别类比为：能力定义、任务与评分、harness。这个类比是我的推论。

#### D2. Wallach et al. 2025, *Position: Evaluating Generative AI Systems Is a Social Science Measurement Challenge*（ICML 2025）
- 链接：https://arxiv.org/abs/2502.00561
- **【原文】§3**：
  - 四个层级：background concept、systematized concept、measurement instruments、measurements。
  - "These levels are linked by four processes: *systematization*, *operationalization*, *application*, and *interrogation*."
  - 各过程的定义包括："Systematization is the process of narrowing the background concept into the systematized concept"，以及 "operationalization is the process of drawing on the systematized concept to develop the measurement instruments"。
- **【我的归纳】**：
  - 你的三元组只位于 **measurement instruments** 这一层。
  - 它上面还有两层概念（要测什么）；下面有 measurements；另外还有一个 **interrogation**（检验效度）过程。
  - 对 AutoBenchmark 来说，"生成新题"相当于在**同一个 systematized concept 下**生成新的 instrument。要证明新旧题测的是同一个东西，就要做 interrogation。

#### D3. Miller 2024, *Adding Error Bars to Evals*
- 链接：https://arxiv.org/abs/2411.00640
- **【原文】§2**：题目被假设为 "drawn at random from a (hypothetical, infinite, unseen) super-population of questions"。
- **【原文】§2.1**：
  - 单题得分 s_i = x_i + ε_i，Var(ε_i) = σ_i²。
  - 总体均值 μ = E[s] = E[x]，估计量 μ̂ = s̄ = (1/n) Σ s_i。
  - 标准误：SE_CLT = sqrt( (1/(n−1)) Σ(s_i − s̄)² / n )。
- **【原文】§2.2**：如果题目成簇出现（例如多道题共用同一篇材料），要用聚类标准误：SE_clustered = ( SE_CLT² + (1/n²) Σ_c Σ_i Σ_{j≠i} (s_{i,c} − s̄)(s_{j,c} − s̄) )^{1/2}。
- **【我的归纳】**：
  - 把 benchmark 看成**从题目总体中抽出的样本**，于是"总体分布"、"簇结构"、"不确定度"都成了 benchmark 的变量。
  - 对 AutoFinBench 尤其重要：同一个种子生成的多个变体天然构成一个簇，统计时应该按种子聚类。

#### D4. Polo et al. 2024, *tinyBenchmarks*（ICML 2024）
- 链接：https://arxiv.org/abs/2402.14992
- **【原文】§4.1**：使用 "the two-parameter multidimensional IRT model"：
  > P(Y_il = 1 | θ_l, α_i, β_i) = 1 / (1 + exp(−α_iᵀθ_l + β_i))
  - 参数含义：
    - θ_l："θ_l ∈ ℝ^d denotes the unobserved abilities of LLM l"。
    - α_i："α_i ∈ ℝ^d dictates which dimensions of θ_l are required … to respond to example i correctly"。
    - β_i："β_i ∈ ℝ can be viewed as a bias term"。
- **【我的归纳】**：在 IRT 视角下，**每道题都带有潜参数**（区分度 α_i 和偏置 β_i）。这些是题目本身的属性，三元组里没有对应项。β_i 前面是加号，所以它的作用相当于负的难度。

### E. benchmark 整体性质的形式化定义

#### E1. Li et al. 2025, *AutoBencher*（ICLR 2025）
- 链接：https://arxiv.org/abs/2407.08351
- **【原文】§3**：
  - 数据集是 "a set of question-answer pairs (x_i, y_i) that evaluate mastery of the knowledge or skill required by c"，记为 D_c = {(x_i, y_i)}，由 p(D_c | c) 生成。
  - 准确率向量 v_c = [acc(LM₁, D_c), …, acc(LM_M, D_c)]。
- **【原文】§3.1，四个性质**：
  - Salience(c) ∈ {0,1}。
  - Difficulty(D_c, ℳ) = 1 − max_{m∈ℳ} acc(LM_m, D_c)。
  - Sep(D_c, ℳ) = mean(|v_c − mean(v_c)|)。
  - Novelty(D_c; D_prev; ℳ) = 1 − RankCorr(v̂_c, v_c)，其中 v̂_c 是用已有 benchmark 的成绩做线性回归得到的预测。
  - 目标函数（Eq. 1）：max J(c) = Novelty + β₁·Difficulty + β₂·Sep，约束 c ∈ 𝒮。
- **【我的归纳】**：
  - benchmark 是**关于能力 c 的问答对集合**。
  - 它的性质是**相对于一组被测模型 ℳ 定义的**。同一个数据集换一组模型，难度和区分度就会变。
  - 这是目前**最直接为 AutoBenchmark 服务的形式化**：它把"生成好的 benchmark"写成了一个优化问题。但它只覆盖问答对，没有环境，也没有 GT 可信度。

#### E2. Zhu et al. 2025, *Establishing Best Practices for Building Rigorous Agentic Benchmarks*（ABC 清单）
- 链接：https://arxiv.org/abs/2507.02825
- **【原文】§3**：
  > "An agentic benchmark challenges an AI agent to finish a task in a specific environment with a given set of tools."
  >
  > 评价是严格的 "if and only if (1) the target capability is equivalent to task success"（task validity）以及 "(2) the task success is equivalent to a positive evaluation result"（outcome validity）。
- **【原文】§1**：
  - Task validity："a task should be solvable if and only if the agent possesses the target capability"。
  - Outcome validity："the evaluation result (e.g., tests or checks) truly indicates task success"。
- 清单结构：§4.1 任务有效性分为 Tool、Environment、Implementation；§4.2 结果有效性；§4.3 报告规范。
- **【我的归纳】**：
  - ABC 的组成部分大致是 task、environment、tools 加评价，和你的三元组接近，但把 **tools** 单独列了出来。
  - 更重要的是，它给出了**两个等价条件**，把三元组和"目标能力"连接起来。这可以直接写成三元组的**正确性条件**，见 §5。
  - 我读到的章节里没有正式的数学符号。

#### E3. Liang et al. 2023, *Holistic Evaluation of Language Models*（HELM, TMLR 2023）
- 链接：https://arxiv.org/abs/2211.09110
- **【原文】§2.1**：
  > "A scenario instantiates a desired use case for a language model. … we operationalize scenarios through a list of instances, divided into a training set and one or more test sets. Each instance consists of (i) an input (a string) and (ii) a list of references. Each reference is a string annotated with properties relevant for evaluation"
- **【原文】§2.2**："Adaptation is the procedure that transforms a language model, along with training instances, into a system that can make predictions on new instances."
- **【原文】§2.3**："Metrics concretely operationalize the abstract desiderata we require of useful systems."
- **【原文】§3.1 Figure 8**：
  > "To specify a scenario, we break it down into a task, domain, and language, further subdividing the domain into properties of the text (what), speaker (who), and the time/circumstances (when)."
- **【我的归纳】**：
  - HELM 的结构是 (scenario, adaptation, metric)：scenario 由 instances 组成，每个 instance 是 input 加 references。
  - 和三元组的区别：
    1. references 单列，即 GT 和 metric 分开。
    2. **adaptation（如何把模型变成可答题的系统）是评测定义的一部分**。
    3. domain 里有 **when（时间）**，这和 AutoFinBench 的"信息更新"直接相关：时间是 scenario 的一个坐标。

#### E4. Reuel et al. 2024, *BetterBench*（NeurIPS 2024 D&B）
- 链接：https://arxiv.org/abs/2411.12990
- **【原文】§1 Figure 1**："Five stages of the benchmark lifecycle."
  - §3："(design, implementation, documentation, and maintenance)" 这四个阶段被打分。
  - §4 说明 retirement 阶段 "we do not include specific criteria for this phase"。
- **【我的归纳】**：把 benchmark 当作一个有**生命周期**的对象，引入了时间和版本维度。

---

## 2. 文献里描述 benchmark 的变量（我的归纳）

✓ = 三元组覆盖；◐ = 部分覆盖或隐含；✗ = 没有覆盖。

| # | 变量 | 文献中的叫法 | 来源 | 三元组 |
|---|---|---|---|---|
| 1 | 目标构念（要测什么） | abilities / motivating comparison / phenomenon / measurand / capability c / target capability | Raji, Sim, Bean, VIM, Wallach, AutoBencher, ABC | ✗ |
| 2 | 指令/问题 | intent 𝐢 / instruction / input / 𝒰 | WebArena, OSWorld, τ-bench, HELM, Inspect | ✓ Question |
| 3 | 单题初始状态 | q(x₁) / initial state config / base commit / setup, files | MAML, OSWorld, SWE-bench, Inspect | ◐ Environment |
| 4 | 环境动力学与工具 | ⟨𝒮,𝒜,𝒪,𝒯⟩ / tools / sandbox | WebArena, OSWorld, τ-bench, ABC, Inspect | ✓ Environment |
| 5 | 参考答案或目标状态 | references / target / a* / GT database / FAIL_TO_PASS | HELM, Inspect, WebArena, τ-bench, SWE-bench | ◐ 隐含在 Rubrics 里 |
| 6 | 单题评分函数 | r / L / ℛ / scorer / test script | 全部 B、C 类 | ✓ Rubrics |
| 7 | 参考解（oracle） | solution/solve.sh | Harbor；ABC 的"可解"要求 | ✗ |
| 8 | 交互协议与预算 | H / interaction regime / epochs / limits / k 次试验 | MAML, bsuite, Inspect, τ-bench | ✗ |
| 9 | 被测系统的适配与脚手架 | adaptation / solver | HELM, Inspect | ✗ |
| 10 | 汇总指标 | metric / % resolved / pass^k / leaderboard | Raji, SWE-bench, τ-bench, Hardt | ◐ |
| 11 | 任务总体与抽样 | task sample / super-population / p(T) / p(D_c∣c) | Sim, Miller, MAML, AutoBencher | ✗ |
| 12 | 簇结构 | clusters | Miller | ✗ |
| 13 | 不确定度 | SE / CI / measurement uncertainty | Miller, VIM | ✗ |
| 14 | 数据划分与保密 | training/test split / sequestered test set / holdout | Donoho, Hardt, Raji | ✗ |
| 15 | 参与者、裁判、运行规则 | enrolled competitors / scoring referee / run rules | Donoho, Kistowski | ✗ |
| 16 | 题目潜参数 | α_i, β_i | tinyBenchmarks | ✗ |
| 17 | benchmark 层性质 | difficulty / separability / novelty / salience；relevance … usability；task/outcome validity | AutoBencher, Kistowski, ABC | ✗（这些是约束，不是组成部分） |
| 18 | 领域、时间、语言元数据 | domain (what/who/when), language | HELM | ✗ |
| 19 | 任务族、版本、生命周期 | task family / version / lifecycle | METR, Inspect, BetterBench | ✗ |

---

## 3. 有没有比三元组更全面的定义？（我的归纳）

- **工程层面，三元组有充分的先例**：
  - Harbor："instruction, environment, and test script"。
  - METR："environment + instructions + (optional) scoring"。
  - OSWorld：instruction + initial state config + evaluation script。
  - 所以把它当作**单题的工程规格**是站得住的。
- **更全面的拆解有三类**：
  1. **加入要测的能力**：Bean 的 (phenomenon, task, metric)，Sim 的 (motivating comparison, task sample, performance measures)，Wallach 的四个层级和四个过程。
  2. **加入交互和预算**：MAML 的 {L, q(x₁), q(x_{t+1}∣x_t,a_t), H}，bsuite 的 (Environments, Interaction, Analysis)，Inspect 的 epochs 和 limits。
  3. **加入制度和统计**：Donoho 的 CTF（参赛者、裁判、隔离测试集），Miller 的总体、簇和标准误，AutoBencher 相对于模型集合的性质。
- 没有一篇文献同时覆盖这三类。

---

## 4. 对三元组的评价（我的判断）

1. **缺少"要测的能力"（构念）**。这是所有测量学文献的第一要素。没有它，ABC 的任务有效性就无从定义，因为任务有效性是相对于目标能力而言的。
2. **"Evaluation Rubrics"把三件事混在一起**：参考答案或目标状态、单题评分函数、跨题汇总指标。HELM（references 和 metrics）、Inspect（target、scorer、metrics）、WebArena（a\* 和 r）、Raji（两层 metric）都把它们分开。对你研究的 **GT 可信度**来说，这个拆分是必须的："GT 改了但评分函数没变"和"评分函数改了"是两种不同的风险。
3. **缺少交互协议和预算**。同一道题在不同的 H、k、token 或时间上限下，测到的不是同一个量。τ-bench 的 pass^k 就是一个例子。
4. **Question 和 Environment 的边界不固定**：τ-bench 把指令空间放进了 POMDP；OSWorld 把初始状态作为单题配置；MAML 把初始观测分布 q(x₁) 当作任务的一部分。建议明确划界：Question 是 u，单题初始状态是 s₀，共享环境是 E。
5. **缺少参考解（oracle）**。参考解是证明"可解"的直接证据，Harbor 的 solution/ 就是这个用途。对自动生成的题目来说，它是排除坏题最便宜的手段。
6. **单题定义无法表达 benchmark 层面的性质**：抽样分布、簇结构、不确定度、难度、区分度、新颖性。而这些恰恰是 AutoBenchmark 要优化的东西。
7. **被测系统的脚手架算不算 benchmark 的一部分**，文献意见不一：HELM 和 Inspect 算进去，Raji 和 Sim 不算。我的建议是：不放进任务定义，但作为评测设置必须报告。这和之前发现的"同一道题测什么能力取决于评测设置"是同一件事。

---

## 5. 一个更完整的定义草案（我的归纳，不是文献原文）

**Benchmark 层面**

```
B = ( c, p_T, {τ_i}_{i=1..n}, Π, Agg, U, Meta )
  c     目标构念（systematized concept；Wallach / Bean / VIM 的 measurand）
  p_T   任务分布或生成器（MAML 的 p(T)、AutoBencher 的 p(D_c|c)、METR 的 task family；
        在 AutoFinBench 中 = 种子题 × 算子）
  τ_i   从 p_T 抽出的任务
  Π     交互协议与预算（试验次数 k、步数上限 H、token/时间上限、可用工具、要报告的 harness）
  Agg   汇总方式（均值 / pass^k / Elo …）
  U     不确定度模型（按种子聚类的标准误；Miller）
  Meta  来源、时点（as-of date；HELM 的 "when"）、版本、可见性（公开/隔离；Donoho）
```

**Task 层面**

```
τ = ( u, E, s₀, Y*, R, σ* )
  u    指令/问题
  E    共享环境 ⟨S, A, O, T⟩，含工具
  s₀   单题初始状态（给定的材料、数据库、文件）
  Y*   参考答案或目标状态的集合（允许多个合理口径的变体）
  R    评分函数：轨迹 × 最终状态 × Y* → [0,1]（rubric 是 R 的一种实现）
  σ*   参考解或 oracle 轨迹（证明可解，可选）
```

**正确性条件**（改写自 ABC 的两个等价条件）

```
任务有效性：  Success(τ) ⇔ 具备能力 c
结果有效性：  R(·) = 1   ⇔ Success(τ)
```

**和你的三元组的对应关系**

| 你的三元组 | 草案中的对应项 |
|---|---|
| Question | u（加上 s₀ 中的部分材料） |
| Environment | E + s₀ |
| Evaluation Rubrics | 单题层的 (Y\*, R)，加上 benchmark 层的 Agg |

草案新增的项：c、σ\*、Π、p_T、U、Meta。

**对 AutoFinBench 的直接用处**
- **时间平移算子**：保持 u 的模板和 R 不变，只改变 s₀ 和 Y\*。用这套符号可以把"配对设计"写得很清楚。
- **生成器质量**：用 AutoBencher 的方式，相对于模型集合 ℳ 定义难度、区分度、新颖性。
- **GT 可信度**：可以拆成两条独立的检验，一条检验 Y\*，一条检验 R。

---

## 6. 未核实或排除的文献

| 文献 | 原因 | 处理 |
|---|---|---|
| Sim, Easterbrook & Holt, ICSE 2003 论文本身 | IEEE 付费墙 | 改用 Sim 本人的幻灯片和 Prechelt 讲义；**幻灯片不等于论文** |
| Huppler 2009, *The Art of Building a Good Benchmark*（TPCTC） | Springer 需要登录 | 未引用 |
| AERA/APA/NCME 2014 *Standards for Educational and Psychological Testing* 中对 test 的定义 | 网页无法访问 | 未引用 |
| EleutherAI lm-evaluation-harness 的 task guide | GitHub 返回 503 | 未引用 |
| METR STANDARD.md（完整接口列表） | 503 | 只用了 README |
| Bean et al. 附录 B 编码手册的原句 | 只拿到摘要 | 只引用了 §1 的原句 |
| Harbor 的 task.toml 字段 | 没读到对应页面 | 没有列出字段 |

如果需要，下一步可以补读：lm-eval-harness 的任务 YAML 字段，以及 Sutton & Barto 第 3 章中 MDP 与 task 的关系。
