# DeepSeek 评测方案：答哪些题、提示词、怎么打分

日期：2026-11-21　｜　题目来自 step1（见 `REPORT.md`），本文给 Codex 实现评测时对照用

一句话：把 `eval/prompts.jsonl` 里的 111 道题逐道发给 DeepSeek，把回答存成 `responses.jsonl`，再用 `scripts/score_eval.py` 打分。主分完全按规则算，只有两项文字说明的子分需要 DeepSeek 当评委。

## 1. 答哪些题

`step1/eval/prompts.jsonl` 每行一道题，字段为 `item_id, op, variant, seed_qid, company, system, user`。`system` 和 `user` 原样作为两条消息发出，不加任何别的内容。

| 类型 `op` | 题数 | 计入主分 | 考什么 | 给模型的原文 |
|---|---|---|---|---|
| `base` 基线 | 21 | 21 | 种子题那一期的同一个指标，原文不做任何改动。用来和下面各类对比 | SecQue 原文片段 |
| `trend` 多期追踪 | 22 | 21 | 连续 5 期的数值、哪期最高、是否逐期上升 | 我们从 SEC 原始文件里切出的 5 份财报表格 |
| `cross` 跨公司比较 | 6 | 6 | 两家公司同一指标谁高、高多少 | 两家公司各自财报的表格 |
| `missing` 缺前提 | 2 | 2 | 原文缺一个必需的数，应回答"算不出来"并指出缺什么 | SecQue 片段，清空了一个数 |
| `reconstruct` 重建 | 18 | 18 | 清空的数可以由同表其他行按恒等式还原，应还原后算出结果 | SecQue 片段，清空了一个数 |
| `verify` 计算核验 | 42 | 42 | 判断分析师的一句结论对不对，错了要给出正确值 | SecQue 原文片段 |

说明：
- `verify` 分为 21 道无错对照（`variant=control`）和 21 道注入错误（`variant=injected_error`）。注入的错误中，抄错数字 13 道，期间错配 8 道。
- 不计主分的那 1 道是 AT&T 的多期追踪题：用后来重述的数字，结论会变。照样要答，打分时单独列出。
- 已排除的题有 5 道：
  - 2 道答案直接印在原文里（Nike、Smucker 的缺前提题）；
  - Apple 的 3 道（基线和两道核验）：SecQue 给 Apple 的原文里没有利润表，营业利润根本不在片段中。
- 题目长度：最短约 3,800 字符，中位数约 13,000，最长约 99,500（约 2.5 万 token）。

## 2. 怎么调用 DeepSeek

- **模型**：非思考模式（例如 `deepseek-chat`）必跑；思考模式（例如 `deepseek-reasoner`）可选。模型名以跑的时候官方 API 的为准，并记下实际用的名字和日期。
- **参数**：非思考模式用 `temperature=0`、`max_tokens=4096`；思考模式不设 temperature，`max_tokens` 放大到 16k 左右。
- **每道题单独调用**，不带对话历史，每道跑 1 次。
- **思考模式只把最终回答（`content`）交给打分**，推理过程（`reasoning_content`）另存，不参与打分。
- **回答存成 `responses.jsonl`**，每行格式如下（打分脚本只读前两个字段）：
  ```json
  {"item_id": "...", "response": "<模型最终回答全文>", "model": "...", "finish_reason": "...", "usage": {...}}
  ```
- API 报错可以重试。但回答因长度截断（`finish_reason=length`）时要如实记下，不要悄悄重跑。

## 3. 提示词

### 3.1 system（所有题相同）

```
You are a financial analyst answering questions about SEC filings.
Rules:
1. Use only the filing excerpts in the user message. Do not use figures from memory or any outside source.
2. A figure that is not printed may be derived from other figures in the excerpts when an accounting identity makes it exact (for example, a total minus its other components).
3. If the excerpts still do not contain what is needed, say that the question cannot be answered and name the missing item. Do not estimate.
4. Show brief working, then end your reply with exactly one JSON object in the requested format and nothing after it.
```

为什么要写第 2 条：重建题的标准答案是"能算"。如果不事先说明允许按恒等式还原，模型回答"这一格是空的，所以算不出来"也说得通，标准答案就不唯一了。这条规则对所有题都一样，不算对某道题的提示。

### 3.2 user（模板）

```
FILING EXCERPTS
<原文片段>

QUESTION
<题干>

ANSWER FORMAT
End your reply with one JSON object of this form:
<下面四种格式之一>
```

### 3.3 四种回答格式

- **基线、缺前提、重建**：三类用同一种格式，这样格式本身不会透露这道题能不能算。
  ```
  {"answerable": true or false, "value": <number, or null if not answerable>, "missing_item": "<the missing item, or null>"}
  ```
- **多期追踪**：
  ```
  {"values": [<five numbers, in the order the periods are listed>], "highest_period_end": "<YYYY-MM-DD>", "increased_every_period": true or false}
  ```
- **计算核验**：
  ```
  {"statement_correct": true or false, "error": "<what is wrong, or null>", "correct_value": <number>}
  ```
- **跨公司比较**：
  ```
  {"values": {"<公司 A>": <number>, "<公司 B>": <number>}, "higher": "<公司 A or 公司 B>", "difference": <number>}
  ```

每道题的单位（百分比、倍数或百万美元）在 `prompts.jsonl` 的格式说明里已经写好，例如 "a number in percent, e.g. 12.3 for 12.3%"。

## 4. 怎么打分

### 4.1 主分：按规则判对错，不用模型

```bash
python3 -I scripts/score_eval.py responses.jsonl results/deepseek-chat
```

脚本取回答里最后一个 JSON，对照 `eval/gold.jsonl` 判对错。

**数值容差**：误差不超过 1 个显示单位或 0.5%（取较大者）都算对。
- 显示单位按题而定：百分比是 0.1 个百分点，倍数是 0.01 倍，百万美元题是 $1m 或 $0.1m。
- 这个容差不会把注入的错误值放过去：每个注入错误都至少差 3 个显示单位、且相对差至少 2%。

| 类型 | 判对条件 |
|---|---|
| 基线、重建 | `answerable=true` 且 `value` 在容差内。BNY 的重建题接受 13.5–13.7（除法还原只能精确到显示位数） |
| 缺前提 | `answerable=false` 且没有给出数值。给了估计值就判错 |
| 多期追踪 | 5 个值全部在容差内，最高期正确，是否逐期上升正确。三项都对才算对。最高期可以写日期，也可以写年份（年份在 5 期里唯一时） |
| 计算核验：对照题 | `statement_correct=true` |
| 计算核验：错误题 | `statement_correct=false` 且 `correct_value` 在容差内 |
| 跨公司比较 | 两家的值都在容差内，"谁高"正确，差值在容差内 |

**只是单位写法不同，照样算对，但会记下来**：百分比写成小数（0.514 而不是 51.4）、百万美元题写成美元原值。

### 4.2 子分：用评委判文字说明（不计入主分）

只有两处需要评委：
- **缺前提题**：模型说的缺失项，和标准答案是不是同一个科目、同一期。
- **注入错误题**：模型有没有找到错在哪个输入、错误属于哪一类（期间错配还是抄错数字）。只说结果不对、但没定位到输入的，算没找到。

流程：
1. 第一次运行打分脚本时，它会生成 `judge_requests.jsonl`（每行 `item_id, system, user`）。
2. 把这些请求原样发给评委模型（可以用 DeepSeek，`temperature=0`），回复存成 `judgments.jsonl`，每行 `{"item_id": ..., "judgment": "<评委回复>"}`。
3. 带上这个文件再运行一次：`python3 -I scripts/score_eval.py responses.jsonl results/deepseek-chat judgments.jsonl`。

答题和评委都用 DeepSeek 时，评委可能偏向自己的说法。因此子分只作参考，并请人工随机看 10 条评委判断。

### 4.3 输出什么

- **`summary.md`**：包括以下几部分：
  - 各类题的正确率和 95% 置信区间；
  - 和同一种子基线题的配对比较：基线对、改后错的有几道，反过来又有几道；
  - 诊断计数：把能算的题判成算不出、缺前提题给了数、对照题误报、错误题漏报、多期追踪题用了重述后的数字、回答里没有 JSON。
- **`scores.jsonl`**：每道题的打分明细。
- **`failures.csv`**：所有答错的题，附模型给的 JSON 和标准答案。最后一列"triage"要人工填 `model_error`（模型错）、`item_problem`（题出坏了）或 `unclear`（说不清）。

**这一步不能省。**只有把答错的题逐道判明是模型错了还是题出坏了，才能说"题变难了"。这正是 AutoSciBench 被拒的第二条理由。

### 4.4 打分脚本已做的自测

- 按标准答案构造的回答：111 道全部判对。
- 故意改错的回答：数值偏 3%、对错反转、缺少 JSON 都判错；单位写法不同仍判对并被记录。

## 5. 先告诉 Codex 的局限

1. **缺前提题只剩 2 道，下不了结论。**原因见 `REPORT.md` 开头的更正：只清空一个数时，22 道里有 19 道能由原文里其他数字算回来（17 道靠同一张表里的恒等式），所以除 Apple 外都改成了重建题。要做像样的缺前提题，得换一种构造方法，例如删掉整张表。
2. **多期追踪和跨公司比较的原文是我们自己切的**：取财报里包含所需数字的表格，优先取主报表，并附上表格前的一小段文字。General Mills 的财报是按位置排版的 PDF 式 HTML，没有表格标签，我们按坐标拼回了行，少数行名丢失了。切片明细见 `eval/contexts.json` 的 `sources` 字段。
3. **每类最多 21 道，置信区间很宽**（21 道全对时，下界也只有 85%）。适合看方向，不适合细比。
4. **DeepSeek 可能背过这些财报。**system 第 1 条禁止凭记忆作答，但没法强制。
5. **AT&T 多期追踪题不计主分**，单独列在 `summary.md` 末尾。

## 6. 文件

| 文件 | 内容 |
|---|---|
| `step1/eval/prompts.jsonl` | 111 道题的完整输入（system + user） |
| `step1/eval/gold.jsonl` | 标准答案、单位、显示位数、是否计主分；多期追踪题另附"如果用重述数字"的答案 |
| `step1/eval/contexts.json` | 多期追踪和跨公司比较题的原文片段及来源（文件编号、所需数字各在哪张表） |
| `scripts/build_contexts.py` | 从 SEC 原始文件切原文表格 |
| `scripts/build_eval.py` | 生成 `prompts.jsonl` 和 `gold.jsonl` |
| `scripts/score_eval.py` | 打分 |

重新生成（需要 SecQue 的 4 个 jsonl 放在 `../data/secque_full/`，SEC 原始文件会自动下载到 `data/edgar/`）：
```bash
python3 -I scripts/finalize_ops.py
python3 -I scripts/build_contexts.py
python3 -I scripts/build_eval.py
```
