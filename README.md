# autofinbench
This repo is bulit for autofinbench

| 目录 | 内容 |
|---|---|
| `survey/` | 金融 benchmark 调研：数据池、各自测出的能力缺陷、能否用于 SecQue；`LAB_BENCHMARKS_2026-11.md`：主流大模型公司在用的 benchmark 与 agent 问题 |
| `step0/` | 预实验：SecQue q_Ra001–030 只改时间（成对新旧题） |
| `step1/` | 把其他 benchmark 的方向（多期追踪、缺前提、计算核验、跨公司）套到 SecQue 每家公司 1 道题上；专题 `GT_CREDIBILITY.md`；DeepSeek 评测方案 `EVAL_PLAN.md` 和 `eval/` |
| `scripts/` | 取数、出题、核对脚本 |
