# Professional Exam: Improving Model Accuracy and Efficiency via Fine-Tuning

Choose the single best answer for each question. This exam is grounded in the course notebook `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` (Alibaba Cloud ACP LLM course). It is a source-grounded practice draft, not a validated or official certification exam.

## Question 1

Your team runs a Q&A bot that answers product-documentation questions well. You now need it to solve multi-step math word problems. The relevant formulas already exist in your RAG knowledge base, yet the bot still fails: it recalls the triangle-area formula but cannot carry the computation through to the correct final answer. According to the notebook's analysis of this exact scenario, what is the best-supported explanation and direction?

A. The retrieval chunking is too coarse; re-index the knowledge base with smaller chunks so formulas are retrieved more precisely.

B. The prompt template lacks step-by-step instructions; add chain-of-thought prompting so the model reasons through the calculation.

C. Math ability depends on logical reasoning rather than knowledge retrieval, so the model must be fine-tuned on expert-crafted problem-solution examples to build that reasoning ability.

D. Retrieval quality is fine, but arithmetic is unreliable in LLMs; integrate a "calculator" plugin and skip any change to the model itself.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Math ability depends on logical reasoning rather than knowledge retrieval, so the model must be fine-tuned on expert-crafted problem-solution examples to build that reasoning ability.**

The notebook argues that prompt engineering and RAG "patch around the model" without changing its inherent reasoning ability. It compares RAG to an open-book exam: "you have never seen an open-book math exam improve scores, because the core of improving math ability lies in enhancing students' logical reasoning and computational skills, rather than knowledge retrieval." It then states that to enhance the bot's math problem-solving, "you must use model fine-tuning to improve the model's logical reasoning ability," feeding it problem-solving examples crafted by domain experts.

Option D is the most tempting alternative because the notebook does mention that "computational ability can be enhanced by integrating a 'calculator' plugin" — but a plugin addresses raw computation only, while the stated failure (and the notebook's stated remedy) concerns logical reasoning, which "must" be addressed through fine-tuning. Options A and B stay within the prompt/RAG family that the notebook explicitly says "often falls short" for this need.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — "🚄 Preface" and Section 1 "Task design" (the passage after the failed radish-harvest example: the open-book-math-exam analogy and the fine-tuning + calculator-plugin recommendation).
</details>

## Question 2

In the notebook's explanation of gradient descent, the parameter-adjustment magnitude is derived from the slope at the current position, multiplied by a coefficient called the learning rate. What role does the learning rate play, according to the source?

A. It determines the direction of parameter updates by computing the gradient of the loss surface at each point.

B. It regulates the step size taken along the descent direction, and choosing it well balances convergence speed against overshooting or wasting compute.

C. It sets how many complete passes over the training dataset occur before parameters are updated.

D. It measures the average loss across all training samples so convergence can be detected.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — It regulates the step size taken along the descent direction, and choosing it well balances convergence speed against overshooting or wasting compute.**

The notebook explains that using the raw slope as the step size can still oscillate on steep curves, so "you multiply the slope by a coefficient to regulate the step size. This coefficient is called the learning rate." It then presents the three-way trade-off: an appropriate rate converges quickly, an excessively low rate still converges but wastes time and resources, and an excessively high rate can skip the optimum and fail to find the lowest point.

Option A confuses the learning rate with the gradient itself, which the notebook assigns the role of determining direction (steepest descent is the opposite of the gradient). Option C describes epochs, and Option D describes the cost function.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.1.3 "Gradient descent algorithm", subsection "Magnitude of parameter adjustment" (learning-rate coefficient and the three illustrated rate regimes).
</details>

## Question 3

You start your first LoRA fine-tuning run of `qwen2.5-1.5b-instruct` with `learning_rate=0.1`, `lora_rank=4`, `num_train_epochs=1` on the 100-sample dataset. Instead of decreasing, both the training loss and validation loss oscillate wildly and trend upward. According to the notebook's diagnosis of this exact experiment, what is the most likely cause and the correct adjustment?

A. The dataset is too small for the task; expand it to 1,000+ samples and rerun with the same learning rate.

B. One epoch is insufficient; increase `num_train_epochs` to 50 so the model has time to converge.

C. `lora_rank=4` gives the model too much learning capacity, causing instability; reduce the rank to 2.

D. The learning rate is far too high, causing the parameters to overshoot and oscillate instead of converging; reduce it drastically (e.g., to 0.00005), after which the loss curve drops smoothly.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — The learning rate is far too high, causing the parameters to overshoot and oscillate instead of converging; reduce it drastically (e.g., to 0.00005), after which the loss curve drops smoothly.**

The notebook's first experiment uses exactly these settings and records: training loss increases, validation loss increases → "Training failed", with the cause analysis "the learning rate is likely too high... the model's parameters oscillate wildly instead of converging," and the adjustment logic "significantly reduce the learning rate to 0.00005." Section 2.1.4 also states that `learning_rate=0.1` causes training to fail completely while 0.00005 makes the loss drop smoothly, and that wild oscillation or a rising loss curve at the start "is almost always because the learning rate is too high."

Option B is tempting because more training time is the fix for underfitting — but underfitting is diagnosed by both losses *decreasing*, not increasing. Rising losses from the start indicate a broken learning setup, not insufficient epochs; training longer at the same rate (B) or adding data (A) would not fix the overshoot.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 3.3.1 "First experiment" (result table: Training failed / cause / adjustment) and Section 2.1.4 "Key Hyperparameters", `learning_rate` entry.
</details>

## Question 4

After correcting the learning rate to 0.00005, you train for 1 epoch on the 100-sample dataset. At the end of the run, both the training loss and the validation loss are still decreasing steadily — neither has flattened or turned upward. Per the notebook, how should this state be classified, and what is the recommended action?

A. Underfitting — the model had not learned enough before training stopped; increase `num_train_epochs` (and optionally increase `batch_size` to speed training) so it can keep learning.

B. Overfitting — the model is beginning to memorize the data; reduce the number of epochs or expand the dataset immediately.

C. Training failure — the learning rate is still misconfigured; reduce it further before continuing.

D. Successful training — stop now and deploy the `last_model_checkpoint` for inference.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Underfitting — the model had not learned enough before training stopped; increase `num_train_epochs` (and optionally increase `batch_size` to speed training) so it can keep learning.**

Section 3.1 defines the state precisely: "Both training loss and validation loss are decreasing: this means the model is underfitting... you should allow training to continue." The notebook's second experiment observes exactly this pattern, labels it "Underfitting," and its adjustment logic is to raise `num_train_epochs` to 50 and increase `batch_size` to 16 to accelerate training.

Option B is the diagnostic inversion: overfitting is signaled by training loss decreasing *while validation loss increases*. Here both are still falling, which the notebook calls evidence the training process is stable and effective — just not finished.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 3.1 "Model training status and metrics" (three states) and Section 3.3.2 "Second experiment" (observation/adjustment table).
</details>

## Question 5

You raise `num_train_epochs` to 50 on the 100-sample dataset. The training loss decreases throughout, but the validation loss decreases only until roughly epoch 10 and then rises. When tested, the model answers the exact training questions correctly but fails on the same problems phrased differently. According to the notebook, what is the best-supported remediation?

A. Increase the learning rate so the model can push through the validation-loss plateau.

B. Increase `batch_size` to smooth the gradient estimates and stabilize the validation loss.

C. Treat it as overfitting: reduce the number of epochs and/or expand the training data (the notebook grows the dataset to 1,000 samples), and consider early stopping that monitors eval loss and halts when it starts rising.

D. Treat it as underfitting: keep training to 100 epochs so the validation loss eventually falls again.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Treat it as overfitting: reduce the number of epochs and/or expand the training data (the notebook grows the dataset to 1,000 samples), and consider early stopping that monitors eval loss and halts when it starts rising.**

The notebook names this signature — training loss down, validation loss up — as overfitting: the model "memorized the answers instead of learning the underlying knowledge," which matches the stem's symptom of failing on rephrased questions. Section 2.1.4 prescribes reducing epochs, increasing training data, or using early stopping on eval loss. The third experiment's adjustment logic does exactly this: cut `num_train_epochs` to 3 and expand the dataset from 100 to 1,000 entries (`train_1k.jsonl`), noting that below ~1,000 high-quality samples the model tends to "memorize questions."

Option A would worsen instability (a high learning rate is the failure mode of experiment 1), and B confuses gradient noise — a batch-size concern — with the memorization dynamic that drives the rising validation loss.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.1.4 `num_train_epochs` entry (underfitting/overfitting/early stopping) and Section 3.3.3 "Third experiment" (overfitting table, 1,000+ sample guidance).
</details>

## Question 6

You plan a LoRA fine-tuning run with about 800 training samples for a simple style-transfer task, on a GPU with limited memory. Based on the notebook's guidance for choosing the LoRA rank `r`, which setting is best supported?

A. r = 32–64, because a larger rank always captures richer task features and improves final quality.

B. A small r such as 4–8, because small datasets and simple tasks need less learning capacity, a high rank on little data invites memorization, and a smaller r uses less GPU memory.

C. r equal to the hidden dimension d (e.g., 1536), because the low-rank decomposition only saves memory when r matches the full weight matrix.

D. An r scaled proportionally to the base model's parameter count, because the LoRA paper shows optimal r grows linearly with model size.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — A small r such as 4–8, because small datasets and simple tasks need less learning capacity, a high rank on little data invites memorization, and a smaller r uses less GPU memory.**

The notebook's rank-selection guidance is explicit on all three factors in the stem: for small datasets or simple tasks (it names format conversion and style transfer), "rank 4–8 is usually sufficient"; "if you have very little data but set a high rank, the model will most likely memorize the training data"; and when GPU memory is limited, choose a smaller r since LoRA parameters (2 × d × r) grow linearly with r.

Option D directly contradicts the source: the notebook cites the LoRA paper's finding that "the optimal choice of r does not scale proportionally with model size" — even GPT-3 (175B) achieved full-fine-tuning-comparable results with r = 1–8. Option A ignores the data-volume and memory constraints, and C misstates the decomposition, whose entire benefit comes from r ≪ d.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.1.4 `lora_rank` entry and Section 2.2.2 "LoRA Fine-tuning" (factors 1–4 for choosing r, including the LoRA-paper note on rank vs. model size).
</details>

## Question 7

Your fine-tuning job crashes midway with a `CUDA out of memory` error at `batch_size=16`. You want the gradient stability of an effective batch of 16, but the GPU can only hold 4 samples per step; `max_length=512` is already correctly sized to your data. According to the notebook, what is the recommended solution?

A. Use gradient accumulation — e.g., `batch_size=4` with `gradient_accumulation_steps=4` — to obtain the effective behavior of batch 16 with the memory footprint of batch 4.

B. Drop `batch_size` to 1, which minimizes memory use regardless of the effect on the loss curve.

C. Raise the learning rate to compensate for the smaller number of samples seen per step.

D. Increase `lora_rank` so that fewer optimizer states need to be stored per batch.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Use gradient accumulation — e.g., `batch_size=4` with `gradient_accumulation_steps=4` — to obtain the effective behavior of batch 16 with the memory footprint of batch 4.**

The notebook presents gradient accumulation as exactly this fix: "If you want the stability of a large batch but don't have enough memory, gradient accumulation is the solution: for example, batch_size=4 with gradient_accumulation_steps=4 gives you the effective behavior of batch_size=16 while only using the memory footprint of batch_size=4."

Option B is tempting because it does avoid OOM, but the notebook warns that at batch_size=1 "the loss curve will be extremely noisy — estimating the gradient from a single sample introduces too much randomness, causing the model's learning direction to zigzag erratically," so it fails the stem's stability requirement. C addresses neither memory nor stability, and D is backwards: a larger rank increases memory usage.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.1.4 "Key Hyperparameters in Model Training", `batch_size` entry (OOM symptom, batch-size-1 noise, gradient accumulation example).
</details>

## Question 8

A colleague plans a 50-epoch run with `eval_steps` set so large that evaluation happens only once, at the very end. According to the notebook, why is this risky, and what does the ms-swift framework do at each evaluation that makes periodic evaluation doubly valuable?

A. Evaluation is only for reporting; a single final evaluation is sufficient because ms-swift independently reconstructs the best model from training-loss history.

B. `eval_steps` controls how often the training data is reshuffled, and ms-swift merges the LoRA weights into the base model at every evaluation.

C. Evaluating every single step is the recommended guideline, because evaluation adds negligible overhead and ms-swift deletes all but the best checkpoint automatically.

D. Setting `eval_steps` too high risks missing the overfitting turning point entirely — wasting the remaining epochs — and ms-swift saves a checkpoint at each evaluation and marks the one with the lowest validation loss as `best_model_checkpoint`, so proper evaluation frequency also ensures the best model is preserved.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Setting `eval_steps` too high risks missing the overfitting turning point entirely — wasting the remaining epochs — and ms-swift saves a checkpoint at each evaluation and marks the one with the lowest validation loss as `best_model_checkpoint`, so proper evaluation frequency also ensures the best model is preserved.**

The notebook motivates `eval_steps` with precisely the colleague's scenario: setting epoch=50, discovering only afterwards that eval loss started rising at epoch 10, and burning 40 wasted epochs. Setting `eval_steps` too high "risks missing the overfitting turning point entirely"; the practical guideline is evaluating every 5–10% of total training steps. The accompanying note explains that ms-swift "automatically saves a model checkpoint at each evaluation, and marks the checkpoint with the lowest validation loss as `best_model_checkpoint` when training completes."

Option C inverts the guidance (evaluating every step "slows down training noticeably"). A and B misdescribe both the purpose of evaluation and ms-swift's checkpoint behavior.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.1.4 `eval_steps` entry, including the 💡 note on ms-swift checkpoints and `best_model_checkpoint`; see also Section 3.3 on ms-swift retaining the lowest-validation-loss version.
</details>

## Question 9

For the base model `qwen2.5-1.5b-instruct` with hidden dimension d = 1536, the notebook compares full-parameter fine-tuning of one weight matrix against LoRA with rank r = 8. Which statement correctly reports that comparison?

A. LoRA trains 2,359,296 parameters per matrix but avoids storing optimizer states, saving roughly 1% of disk space.

B. LoRA and full fine-tuning train the same 24,576 parameters; the savings come from freezing the activation function.

C. Full-parameter fine-tuning trains 1536 × 1536 = 2,359,296 parameters for that matrix, while LoRA trains only A(1536×8) + B(8×1536) = 24,576 parameters — a savings of about 98.96% — with the pre-trained weights left frozen.

D. LoRA replaces the original 1536 × 1536 weight matrix with a new 24,576-parameter matrix, discarding the pre-trained weights.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Full-parameter fine-tuning trains 1536 × 1536 = 2,359,296 parameters for that matrix, while LoRA trains only A(1536×8) + B(8×1536) = 24,576 parameters — a savings of about 98.96% — with the pre-trained weights left frozen.**

This reproduces the notebook's worked table in the LoRA section: full-parameter fine-tuning requires W(1536×1536) = 2,359,296 parameters, while LoRA requires A(d×r) + B(r×d) = 1536×8 + 8×1536 = 24,576, a 98.96% savings ratio, per the formula W^fine-tuned = A·B + W^pre-trained with the original pre-trained weights frozen (unchanged).

Option D is the most instructive error to reject: LoRA does not discard or overwrite the pre-trained matrix — the low-rank product is *added* to it, which is also why results can be reverted simply by removing the added low-rank matrices. A and B garble the numbers and the mechanism.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.2.2 "LoRA Fine-tuning" (decomposition formula and the Method / Parameter Calculation / Number of Parameters / Savings Ratio comparison table for d = 1536, r = 8).
</details>

## Question 10

Which statement about the relationship between pre-training and fine-tuning is directly supported by the notebook?

A. Both stages rely on self-supervised learning over massive unlabeled internet text, differing only in dataset size.

B. Pre-training learns general features from large-scale general data via self-supervised learning, while fine-tuning adapts the model to a specific task via supervised learning on a small-scale annotated dataset — typically a few thousand to tens of thousands of samples.

C. Fine-tuning must update every parameter of the model; methods that freeze most weights consistently degrade performance far below full fine-tuning.

D. Pre-training is task-specific and supervised, while fine-tuning builds the general base model from unlabeled web text.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Pre-training learns general features from large-scale general data via self-supervised learning, while fine-tuning adapts the model to a specific task via supervised learning on a small-scale annotated dataset — typically a few thousand to tens of thousands of samples.**

The notebook's comparison table pairs pre-training (objective: learning general features; data: large-scale general; method: self-supervised/unsupervised) with fine-tuning (objective: adapting to specific tasks; data: small-scale task-related; method: supervised). The surrounding text adds that pre-training uses massive internet text without manual annotation, while fine-tuning requires small-scale annotated data and "typically requir[es] only a few thousand to tens of thousands of samples."

Option C is the strongest distractor: full fine-tuning does update all parameters, but the notebook states that PEFT methods such as LoRA update only a small subset of parameters (0.1%–1% trainable) while "achiev[ing] performance close to full fine-tuning" — so freezing most weights does not condemn a model to far worse results. A collapses the distinct learning paradigms, and D swaps the two stages' roles.

**Source:** `2_7_Improve_Model_Accuracy_and_Efficiency_via_Fine_Tuning.ipynb` — Section 2.2.1 "Pre-training and fine-tuning" (feature comparison table; self-supervised vs. supervised paragraphs) and the PEFT/LoRA discussion at the end of the same section.
</details>

---

**Answer-key balance check:** C, B, D, A, C, B, A, D, C, B — A×2, B×3, C×3, D×2; no consecutive-letter pattern.
