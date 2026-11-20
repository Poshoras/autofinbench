# step0：预实验第一轮（SecQue q_Ra001–q_Ra010）

先看 **`REPORT.md`**。

| 文件 | 内容 |
|---|---|
| `REPORT.md` | 本轮结果报告 |
| `new_benchmark_agent.csv` | C 组（模拟 agent）生成的新题：题干、答案文本、答案 JSON、目标文件编号与报告期 |
| `runs/<QID>.json` | 每道题的完整处理记录（6 步的输入、输出、修订记录） |
| `specs/<QID>.json` | agent 中"需要判断"的部分：学到的模式、规划决策、新题干、审校结论、修订记录 |
| `baseline_B_prompt.md` | B 组（简单提示词）的提示词模板 |

复现：

```bash
python3 -I scripts/run_agent.py          # 跑全部 specs，生成 runs/ 和 new_benchmark_agent.csv
python3 -I scripts/summarize_runs.py     # 打印每道题的简要过程
```

SEC 原始数据会自动下载到 `data/edgar/`（不进仓库）。
