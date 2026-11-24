# Real-book evaluation

After verifying the current science-stream editions, add at least ten cases per subject to `cases.json`: definitions, paraphrases, numericals, exercises spanning pages, missing-data questions and unrelated questions. Include expected page references and teacher-reviewed solution steps. Never use generated answers as ground truth.

Run each question through `/ask`. Review factual support, correct subject/chapter/page, algebra and units, citation completeness, abstention and response time. Record failures and repair extraction/retrieval before tuning the model. Run adversarial questions asking the assistant to ignore excerpts or invent sources. No real-book cases have passed yet.
