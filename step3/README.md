# Step 3: question and answer exchange

Put newly generated questions in `questions/`, preferably one Markdown file per question with a stable filename or ID. Include any data, source links, and answer format needed to solve the question.

Answers go in `answers/` using the same basename as the question (for example, `questions/q001.md` -> `answers/q001.md`). Each answer should identify the question revision it addresses, show the result and essential reasoning, and flag any missing information or uncertain ground truth.

The monitor checks for new or revised question files and updates only the corresponding answer files. It ignores changes to `answers/` when looking for new questions. No change requires no notification.
