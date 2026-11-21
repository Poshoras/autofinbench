# DeepSeek 原题联网评测提示词

答题模型：`deepseek-flash`，`temperature=0`，`reasoning_effort=none`，`max_tokens=4096`。启用 `deepseek_web_search` 和 `deepseek_read_url`。每题独立调用，只发送下面的 system 与原始 `Question`；不发送财报片段或标准答案。

## System

```text
You are a financial analyst answering the user's question. Before answering, search the web for relevant primary sources, especially the company's SEC filings or investor-relations reports. Check the exact company, period, metric, units and figures. Open source pages when needed. Answer every part of the question, show brief calculations, and cite source URLs. If some required figures cannot be verified, state what is uncertain; do not invent numbers.
```

## User

```text
<该题在 SecQue 数据集中的原始 Question 字段，原样发送>
```

若首次回答没有实际调用搜索工具，仅重试一次，并在 system 末尾追加：

```text
 You must perform a web search before answering.
```

若重试后仍未搜索，保存回答并标记搜索次数为 0。22 道原始题目及标准答案保存在 `original_questions_used.jsonl`；其中标准答案仅用于评分，不进入答题请求。
