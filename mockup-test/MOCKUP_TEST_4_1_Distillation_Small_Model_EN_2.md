# Professional Exam: Model Distillation — Giving a Small Model Specialized Skills

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` (Alibaba Cloud ACP LLM course, Lesson 4.1)

Choose the single best answer for each question. This exam assesses applied judgment on the data-synthesis distillation pipeline: teacher labeling, quality filtering, LoRA training with ms-swift, evaluation metrics, troubleshooting, and cost-benefit deployment decisions.

## Question 1

A team is adapting the small Qwen3-0.6B model for a structured request-understanding task. One engineer argues, "distillation is just fine-tuning by another name — there is nothing fundamentally different about how the model trains." According to the lesson, what is the accurate characterization of the relationship between distillation and fine-tuning?

A. Distillation skips gradient-based training entirely and instead transfers weights directly from the teacher to the student

B. Distillation updates all model weights, while fine-tuning trains only an attached adapter layer

C. The training procedure is nearly identical (both are SFT); the fundamental difference is where the training data comes from — teacher-model-generated data for distillation, human-annotated data for fine-tuning

D. Distillation requires access to the teacher model's weights, while fine-tuning needs only API access to the base model

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The training procedure is nearly identical (both are SFT); the fundamental difference is where the training data comes from — teacher-model-generated data for distillation, human-annotated data for fine-tuning**

Section 2.1 states that the training procedure for both is nearly identical (both are SFT) and that "the difference is **where the training data comes from**," with a comparison table contrasting data source (human annotation vs. teacher-generated), data cost, scale, and quality ceiling. In essence, distillation adds a high-quality data-construction step before fine-tuning. Option D inverts the white-box requirement: teacher weights are needed for knowledge distillation (KD), not for distillation in general — the hands-on black-box path needs only API access. Option B conflates an orthogonal choice (LoRA vs. full-parameter training), and option A contradicts the source, since the student is genuinely trained with gradient descent on the synthesized data.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "2.1 The Core Idea of Distillation" (fine-tuning vs. distillation comparison table and the "core logic" paragraph).
</details>

## Question 2

You would like a student model to fit not only the teacher's final answers but also the probability distribution the teacher assigns to each output token (soft labels / "dark knowledge"). The only teacher available to you is a commercial API model (qwen3.6-plus). According to the lesson's three distillation paths, what is the correct assessment?

A. Soft labels can be reconstructed by sampling the API repeatedly, so white-box KD remains feasible

B. Reasoning compression is the only viable path, because it needs only the teacher's API outputs

C. Black-box distillation also requires the teacher's weights, so no distillation path works through an API

D. White-box KD is not feasible, because commercial APIs do not expose the teacher's weights or internal state; data-synthesis (black-box) distillation is the practical path when only API access is available

<details>
<summary>Show answer and rationale</summary>

**Answer: D — White-box KD is not feasible, because commercial APIs do not expose the teacher's weights or internal state; data-synthesis (black-box) distillation is the practical path when only API access is available**

Section 2.2 explains that white-box KD requires access to the teacher's weights and internal state, and that "commercial APIs don't expose weights, so this approach isn't usable with them." Data-synthesis (black-box) distillation requires only teacher API access and is described as "the most practical form of distillation, well suited to cases where the teacher model is a commercial API" — exactly the situation in the stem, and the reason section 2.3 chooses it for this chapter. Option B is wrong twice over: reasoning compression is not the *only* API-viable path (data synthesis is), and it targets multi-step reasoning tasks rather than soft-label fitting. Options A and C contradict the black-box/white-box definitions in the source.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "2.2 Three Distillation Paths" (Path 1/Path 2 descriptions and summary table) and "2.3 Why This Chapter Chooses Data Synthesis."
</details>

## Question 3

Which task in an enterprise Q&A bot system does the lesson identify as the best fit for distillation into a 0.6B model?

A. Answering HR policy questions whose content changes weekly

B. Turning each incoming employee question into a fixed-schema JSON ticket (intents, department, urgency, entities, route)

C. Producing multi-step mathematical derivations for analytics requests

D. Drafting open-ended, empathetic prose responses to employee complaints

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Turning each incoming employee question into a fixed-schema JSON ticket (intents, department, urgency, entities, route)**

Sections 1.3 and 7.3 give the suitability criteria: the output format is fixed and automatically validatable by a rule (JSON schema), the task does not depend on real-time external knowledge (judging intent and urgency only requires the input text), and it runs on every request (high-frequency path). Section 7.2 summarizes that a 0.6B model is suited to "high-frequency, fixed-domain, single-step judgment" tasks and acts as a preprocessor, not a general assistant. Option A is the lesson's own example of a poor fit — the distilled model's knowledge is frozen at training time, so weekly-changing policy content calls for RAG. Option C needs multi-step reasoning (keep the large model, or use reasoning-compression distillation), and option D is open-ended generation beyond the 0.6B model's role.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "1.3 Why This Task Is a Good Fit for Distillation," "7.2 The Limits of Distillation," and "7.3 Is Your Task a Good Fit for Distillation?" (not-suited scenarios table).
</details>

## Question 4

While teacher-labeling several hundred synthesized employee questions with qwen3.6-plus, some labels come back with truncated JSON, missing required fields, or out-of-range values. According to the lesson's quality-filtering design, how should the pipeline handle these samples?

A. Apply automated outcome validation — a JSON parse check, a required-fields check (all five fields present), and a value-range check — and filter out any sample that fails

B. Keep them, because exposure to imperfect labels makes the student model more robust

C. Manually review each failing label and hand-correct it before training

D. Increase the teacher's temperature so it produces more varied label candidates

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Apply automated outcome validation — a JSON parse check, a required-fields check (all five fields present), and a value-range check — and filter out any sample that fails**

Section 3.4 warns that even a strong teacher makes mistakes in bulk labeling (JSON cut off, missing fields, nonexistent department values), and that if these "bad samples" enter the training set, "the student model will learn the mistakes along with everything else." The prescribed fix is an automated quality check with exactly the three checks in the option, implemented in the `validate_label` function and mirrored in the Qwen Code filtering prompt; the lesson frames this as "outcome validation" rather than "process validation." Option B contradicts the stated risk; option C is not the lesson's approach (filtering is automated, discarding failures rather than repairing them by hand); option D is backwards — the lesson sets `temperature=0.1` during labeling specifically to *reduce* randomness and keep labels consistent.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "3.4 Quality Filtering" (with the `validate_label` code cell), the Qwen Code filtering prompt, and "3.3 Teacher Labeling" (temperature=0.1 rationale).
</details>

## Question 5

The course trains on only around 100 samples yet uses `--lora_rank 8`, even though the parameter-tuning table suggests lowering the rank to 4 for fewer than 200 training samples. What is the lesson's stated justification for keeping r=8?

A. ms-swift requires rank 8 whenever `--model_type qwen3` is specified

B. The 10% validation split consumes rank capacity, so the rank must be doubled for small datasets

C. The task must jointly learn five output dimensions at once — multi-label intents (8-way), department, urgency, entity extraction, and routing — which is more complex than the one- or two-field tasks the "under 200 samples → r=4" guidance assumes

D. Rank 4 systematically overfits small datasets, so rank 8 is the safe minimum for any LoRA run

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The task must jointly learn five output dimensions at once — multi-label intents (8-way), department, urgency, entity extraction, and routing — which is more complex than the one- or two-field tasks the "under 200 samples → r=4" guidance assumes**

The 💡 note beneath the tuning table in section 6.2 anticipates exactly this apparent contradiction and resolves it: r=8 was chosen because "request understanding" requires jointly learning five dimensions (intent recognition as 8-way multi-label, department, urgency, entity extraction, and routing), which is more complex than typical single-label classification; the "under 200 samples → lower to 4" guidance applies to scenarios whose output is just one or two simple fields. Options A, B, and D invent mechanical-sounding rules that appear nowhere in the lesson.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "6.2 Starting Training" (parameter tuning table and the 💡 note explaining the r=8 choice).
</details>

## Question 6

A service will make about 20,000 request-understanding calls per day (≈200 input tokens and ≈100 output tokens each). The large-model API option (qwen3.6-plus at 2 yuan/million input tokens and 12 yuan/million output tokens) costs about 32 yuan/day, ≈960 yuan/month. The distilled 0.6B model can instead run on a PAI-EAS T4 GPU billed at 3.6 yuan/hour, kept online only during work hours (≈8 h/day, ≈864 yuan/month). According to the lesson's break-even analysis, what is the sound conclusion at this volume?

A. The API remains cheaper, because its per-call cost (≈0.0016 yuan) is far below the GPU's hourly price

B. The two options cost roughly the same at this volume, so the decision should be made on latency alone

C. The GPU option only becomes cost-effective above about 54,000 requests/day, regardless of the deployment mode

D. The GPU option is already about 10% cheaper at 20,000 requests/day, because that volume exceeds the work-hours (8 h) mode's break-even point of roughly 18,000 requests/day

<details>
<summary>Show answer and rationale</summary>

**Answer: D — The GPU option is already about 10% cheaper at 20,000 requests/day, because that volume exceeds the work-hours (8 h) mode's break-even point of roughly 18,000 requests/day**

Section 8.2 computes precisely this: for the work-hours (8 h) mode, the GPU daily cost of 28.8 yuan breaks even at around 18,000 requests/day, and at 20,000 requests/day the GPU (864 yuan/month) is already about 10% cheaper than the API (960 yuan/month). Option C misapplies the 24-hour mode's break-even (≈54,000 requests/day) to all modes — the lesson stresses the break-even "varies significantly depending on the deployment mode." Option A compares incompatible units and contradicts the computed monthly totals; option B is false given the ~10% gap (and while the lesson does list non-cost factors such as latency, data security, offline operation, and reliability, "latency alone" misstates them).

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "8.1 Cost Comparison" (Options A/B cost tables) and "8.2 Break-Even Point."
</details>

## Question 7

Your company plans to distill from a teacher model and ship the resulting student model in a commercial product. According to the lesson's compliance note, which teacher choice requires a careful terms-of-service review before proceeding?

A. An Apache-2.0-licensed open-source model such as the Qwen series

B. A commercial API model (e.g., GPT-4 or Claude) whose terms of service may prohibit using its outputs to train a competing model

C. A model your team previously fine-tuned in-house from open weights

D. Any model called through an OpenAI-compatible endpoint

<details>
<summary>Show answer and rationale</summary>

**Answer: B — A commercial API model (e.g., GPT-4 or Claude) whose terms of service may prohibit using its outputs to train a competing model**

The ⚠️ compliance note at the end of section 8.3 states that with an open-source teacher (e.g., the Qwen series under Apache 2.0), the distilled student can be used commercially without restriction, but "some commercial models (e.g. GPT-4, Claude) have terms of service that explicitly prohibit using their output to train a competing model — be sure to check the compliance terms before you proceed." Option A is the explicitly safe case per the source. Option C involves no third-party model outputs, and option D confuses an interface convention with licensing — the endpoint style says nothing about usage rights.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "8.3 The Deployment Decision," ⚠️ Compliance note.
</details>

## Question 8

During a LoRA training run with ms-swift, the training loss decreases steadily, but the evaluation loss decreases at first and then rises steadily over subsequent checkpoints. According to the lesson's training-state guidance, what is the diagnosis and the appropriate response?

A. Overfitting — the model is starting to memorize the training set; reduce the number of training epochs, use the checkpoint with the lowest validation loss, and prioritize adding more high-quality samples over simply training longer

B. Training failure — the learning rate is likely too high; restart with a lower learning rate

C. Underfitting — the model has not learned enough yet; increase the number of epochs and continue training

D. Normal successful convergence — no action is needed as long as the training loss keeps decreasing

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Overfitting — the model is starting to memorize the training set; reduce the number of training epochs, use the checkpoint with the lowest validation loss, and prioritize adding more high-quality samples over simply training longer**

The state table in section 5.3 maps "training loss decreasing + evaluation loss decreasing then rising" to **overfitting** ("the model is 'memorizing the answers' — needs more data or fewer training epochs"), and the troubleshooting table in section 6.5 adds the concrete remedies used in the option, including using the lowest-validation-loss checkpoint and preferring more high-quality samples over longer training. Option B matches a different row (both losses not decreasing/rising → training failure, possibly too-high learning rate); option C matches the "both decreasing" underfitting row; option D ignores the evaluation-loss reversal, which is precisely the signal the lesson says to act on.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "5.3 Judging Training State" (training-loss/evaluation-loss state table) and "6.5 Common Issues and Troubleshooting" ("Validation loss decreases then rises" row).
</details>

## Question 9

The lesson scores intent recognition with an F1 metric rather than plain accuracy. Given that the ticket schema allows multiple intents per question, why?

A. F1 measures generation speed alongside correctness, aligning the metric with production SLOs

B. Plain accuracy requires human review to compute, while F1 is fully automatic

C. F1 is the only metric defined for JSON-structured outputs

D. Plain accuracy cannot distinguish "missed one of two intents" from "got everything wrong," whereas F1 combines precision (nothing wrong) and recall (everything found) over the multi-label intent sets

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Plain accuracy cannot distinguish "missed one of two intents" from "got everything wrong," whereas F1 combines precision (nothing wrong) and recall (everything found) over the multi-label intent sets**

Section 4.1 explains that intents are multi-label (one sentence may contain two intents), so plain accuracy cannot distinguish partial from total failure; F1 captures both whether the model "found everything" (recall) and "didn't get anything wrong" (precision), computed per sample between predicted and true intent sets and then averaged — as implemented in `compute_intent_f1`. Options A, B, and C attribute properties to F1 (speed measurement, human-review requirements, JSON exclusivity) that the lesson never claims.

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "4.1 Evaluation Metrics" (Intents F1 bullet) and the `compute_intent_f1` function in the evaluation code cell.
</details>

## Question 10

After deployment, the distilled model achieves 100% JSON compliance, but production logs show it frequently misses the second intent in multi-intent employee requests, while single-intent requests are handled well. According to the lesson's troubleshooting guidance, what is the most appropriate remedy?

A. Increase the learning rate to 1e-4 and retrain on the existing dataset

B. Increase the maximum generation length so the model has room to list all intents

C. Add more multi-intent, easily-confused, and real business edge-case samples to the training data — covering the high-frequency production errors rather than chasing a fixed ratio

D. Switch from LoRA to full-parameter fine-tuning to give the model more capacity

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Add more multi-intent, easily-confused, and real business edge-case samples to the training data — covering the high-frequency production errors rather than chasing a fixed ratio**

The "Intent recognition still misses things" row of the section 6.5 troubleshooting table matches the stem's symptom exactly (single-intent samples do well; multi-intent or similar requests are often missed), attributes it to insufficient coverage of multi-intent, boundary-case, and similar-intent samples, and prescribes adding those samples — explicitly advising to "check whether you've covered the high-frequency errors seen in production" rather than chasing a fixed ratio. Section 7.3 reinforces this with the data-distribution-mismatch warning: synthetic data phrasing may differ from real users, and mixing in real data helps. Option A addresses the "loss decreases very slowly" symptom, not coverage; option B misdiagnoses a recognition problem as an output-length problem; option D is not among the lesson's remedies for this symptom (section 7.1 instead suggests a larger *student* model, e.g. 1.5B/4B, if higher accuracy is needed overall).

**Source:** `4_1_Distillation_Small_Model_EN.ipynb` — "6.5 Common Issues and Troubleshooting" ("Intent recognition still misses things" row) and "7.3 Is Your Task a Good Fit for Distillation?" (data-distribution mismatch paragraph).
</details>
