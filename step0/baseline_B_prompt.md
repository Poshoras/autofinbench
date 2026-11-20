# B 组（简单提示词 baseline）提示词模板

**规则**：每道题只调用一次模型；不用工具、不回测、不审校、不修订。
必须在**看不到 C 组结果**的新上下文中运行（新开会话 / 另一个模型），否则不公平。
输入与 C 组相同：同一道原题 + 同一份目标文件。

---

```text
You are updating an item of a financial question-answering benchmark to a newer reporting period.

Original question:
{seed_question}

Original ground-truth answer:
{seed_ground_truth_answer}

New filing: {company}, Form {form} for the period ended {report_period} (SEC accession {accession_number}).
Relevant excerpts from the new filing:
{filing_excerpts}

Task: Rewrite the question so that it asks about the latest period covered by the new filing,
keeping the same company, metric(s) and comparison structure. Then answer the rewritten question
using only the excerpts above, showing the calculation.

Return JSON: {"question": "...", "answer": "..."}
```

---

待定：`{filing_excerpts}` 用哪些页面（建议与"附原文作答"评测时给受测模型的原文片段相同）。
