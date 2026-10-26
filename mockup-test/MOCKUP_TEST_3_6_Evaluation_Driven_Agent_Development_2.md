# Professional Exam: Evaluation-Driven Agent Development

Choose the single best answer for each question. This is a source-grounded practice exam based on the course notebook `3_6_Evaluation_Driven_Agent_Development.ipynb` (Alibaba Cloud ACP LLM course, Lesson 3.6); it is not a validated or official certification instrument.

## Question 1

A developer tunes her course-writing Agent's prompt so concept explanations use everyday analogies. She tests the topic "introduce Python for loops," skims the output, and feels "this time it's pretty good." After deployment, new complaints appear — including awkward, inappropriate analogies in a simple "Pandas data filtering" lesson. She now cannot tell whether her change improved or damaged overall performance. According to the notebook, what is the fundamental problem?

A. The underlying model is not powerful enough to apply analogies selectively, so no prompt wording could have worked.

B. She tested only one topic; testing three or more topics by feel would have reliably revealed the regression.

C. She lacks an objective, quantifiable yardstick: subjective "feels good" judgment is hard to quantify, lacks a stable standard across testers and time, and cannot support reproducible regression testing.

D. She deployed the change without a monitoring plan, so user complaints arrived too late to inform the fix.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — She lacks an objective, quantifiable yardstick: subjective "feels good" judgment is hard to quantify, lacks a stable standard across testers and time, and cannot support reproducible regression testing.**

Sections 1–2 use this exact overfitting-analogy scenario to motivate Evaluation-Driven Development, listing three inherent flaws of "feels good" testing: hard to quantify ("feels better" can't support an engineering decision — was it 10% or 20% better?), lacks a standard (mood and tester shift the bar), and can't reproduce (no systematic regression testing, so fixing the "inappropriate analogy" may silently damage "clear explanation"). Because LLM generation is probabilistic and lacks a self-check mechanism, a small prompt tweak can cause an unpredictable butterfly effect. Option B is the most tempting alternative, but the source's point is that manual spot-testing at any sample size still suffers all three flaws — the fix is a systematic evaluation framework, not more subjective testing.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Sections 1 "Why 'Feels About Right' Isn't Reliable" and 2 "What Can't Be Measured Can't Be Improved" (three flaws; butterfly effect).
</details>

## Question 2

A team is classifying candidate metrics for its course-writing Agent. According to the notebook's objective/subjective metric table in Section 3.1.2, which grouping is correct?

A. Objective: content accuracy and language style; subjective: code executability.

B. Objective: code executability, format check (required sections present), and word-count limit; subjective: content accuracy, teaching effectiveness, and language style.

C. Objective: teaching effectiveness and code executability; subjective: format check and word-count limit.

D. Objective: content accuracy and teaching effectiveness; subjective: format check and code executability.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Objective: code executability, format check (required sections present), and word-count limit; subjective: content accuracy, teaching effectiveness, and language style.**

The notebook defines objective metrics as those "judged directly by code rules, with a deterministic result" — its examples are code executability (does the snippet run?), format check (are sections like "pain-point case," "solution," "summary" present?), and word-count limits (300–500 characters per section). Subjective metrics "involve semantics, logic, and quality, usually requiring stronger intelligence to judge" — its examples are content accuracy (factual errors in concept explanations), teaching effectiveness (interest, easy-to-hard progression), and language style (conforming to the "rigorous, precise, calm" setting). Every other option misplaces at least one item — most commonly by assuming "content accuracy" sounds objective, while the source classifies judging factual correctness of explanations as a subjective, semantics-level metric.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 3.1.2, "Designing evaluation metrics: objective and subjective" (two-column table with course-writing Agent cases).
</details>

## Question 3

A startup is beginning work on a support-ticket Agent. The engineering lead proposes spending the first month defining a complete catalog of evaluation metrics covering every quality dimension up front, so development never proceeds blind. According to Section 3.1.1 of the notebook, how should the team instead establish evaluation standards?

A. The lead's plan is correct: for a complex Agent system, all evaluation metrics should be preset before the project starts so nothing is missed.

B. Defer metrics entirely until real users complain, since only production feedback identifies genuine problems.

C. Adopt an off-the-shelf metric suite from an evaluation framework, since community metrics remove the need for project-specific standards.

D. Build a minimum viable version quickly, run it in real scenarios, observe where it makes mistakes, and distill the highest-priority observed errors into evaluation metrics — repeating this loop so the system grows with the Agent.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Build a minimum viable version quickly, run it in real scenarios, observe where it makes mistakes, and distill the highest-priority observed errors into evaluation metrics — repeating this loop so the system grows with the Agent.**

Section 3.1.1 states directly that "you can't preset all the perfect evaluation metrics before the project starts. The right approach is to embrace iteration — evaluation is important, but starting quickly is even more important," and prescribes the three-step loop: build quickly (MVP) → observe problems in real runs → summarize the key points into metrics. The source's example: noticing missing `import` statements yields the first metric ("code runnability"), and noticing overused analogies yields the second ("explanation clarity"). Option A is precisely the approach the source rejects; the evaluation system is meant to become "more complete and precise as the Agent evolves," not to be complete on day one.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 3.1.1, "Establishing evaluation standards iteratively" (Build quickly → Observe problems → Summarize the key points; closed-loop figure).
</details>

## Question 4

A technical team built an Agent, found the output unsatisfactory, and now plans to interview senior instructional designers — asking "what do you think a good course looks like?" — then return to their desks and translate the answers into evaluation rules. According to Section 3.1.2, why is this approach inefficient, and what does the notebook recommend instead?

A. It fails because experts positioned as "knowledge providers" lack motivation, tacit knowledge is lost in translation, and the feedback cycle is long; instead, make business experts the owners of the evaluation system from day one, mobilize them with concrete business goals, and lower the participation barrier with structured tools (metric workshops, scoring-rubric templates, case-annotation tools) plus a continuous collaboration mechanism.

B. It fails because experts cannot articulate quality criteria at all; instead, derive the metrics from the Agent's execution traces and let the LLM judge define the standard.

C. It is sound in principle but slow; instead, have the technical team draft the metrics first and obtain expert sign-off only before production launch.

D. It fails because interviews produce qualitative data; instead, collect a large labeled dataset of courses and compute metric thresholds statistically.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — It fails because experts positioned as "knowledge providers" lack motivation, tacit knowledge is lost in translation, and the feedback cycle is long; instead, make business experts the owners of the evaluation system from day one, mobilize them with concrete business goals, and lower the participation barrier with structured tools plus a continuous collaboration mechanism.**

The notebook describes this "extract knowledge afterwards" mode as a common pitfall with exactly three failure causes: experts lack motivation (they are not co-builders), knowledge-translation loss (technical staff misinterpret or omit tacit knowledge), and a long feedback cycle (rework by the time validation returns). The prescribed alternative is to make senior business experts the owners/designers of the evaluation system from day one, with the technical team as facilitator: frame participation around business goals (e.g., "shorten course production from 2 weeks to 3 days at 90%+ satisfaction"), provide structured scaffolding (workshops, fill-in 1–5 scoring rubrics, case annotation on real outputs), and hold weekly review meetings so the standard stays a living document. Option C preserves the same extract-then-translate structure the source rejects; B and D have no support in the source.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 3.1.2, "But the core question here is: who defines these metrics?" (three pitfalls; three facilitation practices; "experts… become the true owners of the evaluation system").
</details>

## Question 5

An LLM-as-a-Judge consistently scores longer, more detailed lesson drafts higher than concise but on-point ones. According to the notebook, how should this be characterized and addressed?

A. It is position bias; mitigate it by randomly shuffling the order of the content being evaluated.

B. It is style bias; mitigate it by forbidding specific writing styles in the judge prompt.

C. It is length bias, one of the known biases of LLM evaluators; the recommended practice is to calibrate the judge against a human-expert "gold test set" for scoring consistency, then periodically spot-check for drift.

D. It is "yes-man" bias; mitigate it by instructing the judge to be more critical.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — It is length bias, one of the known biases of LLM evaluators; the recommended practice is to calibrate the judge against a human-expert "gold test set" for scoring consistency, then periodically spot-check for drift.**

The "LLM evaluator's mindset" further-reading box defines length bias as the tendency to "consider longer, more detailed explanations as 'more complete,' thereby unfairly penalizing 'concise but on-point' answers" — exactly the observed behavior. The box's stated best practice is: use human-expert evaluation early to establish a high-quality gold test set, use that set to calibrate the LLM evaluator's consistency with human experts, and periodically spot-check manually so the automated system hasn't drifted. Option A pairs a real bias with its real mitigation (shuffling addresses position bias), which makes it tempting, but the symptom described is about answer length, not ordering; likewise "yes-man" bias (D) is about excessive positivity to avoid conflict, not length-sensitivity.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 3.1.3, further-reading box "the LLM evaluator's 'mindset'" (style/length/yes-man/position biases; gold-test-set calibration practice).
</details>

## Question 6

A team has switched from human scoring to automated LLM evaluation for speed. According to Section 3.1.3, what role should human-expert evaluation continue to play in this system?

A. Humans should score every production output, since LLM evaluation is too biased to be trusted at any scale.

B. Humans establish the early "gold test set" used to calibrate the LLM evaluator's consistency with expert scoring, and periodic manual spot-checks guard against evaluator drift afterwards.

C. Humans only adjudicate cases where two LLM judges disagree, keeping the automated pipeline otherwise untouched.

D. Humans write the judge's system prompt once; after that, no human involvement is needed.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Humans establish the early "gold test set" used to calibrate the LLM evaluator's consistency with expert scoring, and periodic manual spot-checks guard against evaluator drift afterwards.**

The source calls human evaluation "the most reliable 'gold standard'" that especially early in the project calibrates the definition of good and bad, while acknowledging it is too costly and slow for large-scale, high-frequency use. The prescribed best practice is therefore hybrid: human experts build the gold test set, that set calibrates the LLM evaluator (checking scoring consistency), and manual spot-checks periodically verify the automated system hasn't drifted. Option A overcorrects — the source explicitly adopts LLM automation for scale; the human role becomes calibration and spot-checking, not scoring everything.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 3.1.3, "Improving the stability of subjective evaluation" (human vs. LLM evaluation; closing best-practice paragraph of the further-reading box).
</details>

## Question 7

A course-writing Agent contains a "concept-explanation" component and a "code-generation" component. End-to-end evaluation shows low overall course scores, but the team cannot tell whether explanations or code examples are at fault; each end-to-end iteration also requires running the entire pipeline. According to Section 3.2, what does the notebook recommend?

A. Increase the number of end-to-end test cases so the average score pinpoints which component is weaker.

B. Have engineers manually read a sample of full course outputs and vote on which component seems worse.

C. Replace the suspected weaker component's model or service first, then re-run end-to-end evaluation to confirm.

D. Add white-box evaluation: build separate test sets for each component (e.g., a list of technical terms for the explanation component; task descriptions for the code component) and evaluate them independently, yielding interference-free signals, faster iteration, and precisely measurable optimization.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Add white-box evaluation: build separate test sets for each component and evaluate them independently, yielding interference-free signals, faster iteration, and precisely measurable optimization.**

Section 3.2 introduces white-box evaluation for exactly this situation: when the flow is complex and a low end-to-end score can't be attributed ("it's hard for you to judge whether the concept explanation was poor or the code example was terrible"). It prescribes designing a separate evaluation system for key components and gives the exact test-set examples in option D, with three core advantages: clear (interference-free) signal to find the real bottleneck, fast iteration (test one component without running the whole flow), and precise optimization (effects of parameter or service changes are measurable, making decisions evidence-based). Option A cannot work because an aggregate score carries no attribution; Option C is the "blind investment" pattern — acting before locating the fault.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 3.2, "Evaluation method two: white-box evaluation" (component examples and three core advantages).
</details>

## Question 8

In the AgentScope evaluation demo (Section 4.1), the `LLMEvalMetric` class snapshots the evaluator agent's state (`copy.deepcopy(self.eval_agent.state_dict())`) at construction and reloads it at the start of every scoring call. According to the code and its comments, why?

A. To reset the evaluator's state before each scoring call so that every task is judged from a pristine baseline, avoiding cross-task contamination from earlier scoring conversations.

B. To reduce API latency by reusing cached model responses from the first evaluation call.

C. To synchronize the evaluator with the tracing backend enabled by `agentscope.init`.

D. To force the evaluator's output into the `EvalScore` structured schema.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — To reset the evaluator's state before each scoring call so that every task is judged from a pristine baseline, avoiding cross-task contamination from earlier scoring conversations.**

The demo code comments state the purpose explicitly: "Take a snapshot of the evaluator's pristine state so every call starts clean" and, inside `__call__`, "Reset evaluator state before scoring to avoid cross-task contamination." Without the reset, an evaluator agent carrying memory of previous tasks' drafts could let earlier scoring leak into later judgments. Structured output (option D) is enforced separately, via `structured_model=EvalScore` on the evaluator call — a distinct mechanism the demo uses "to improve evaluation stability" (parsable numeric values); tracing (C) is optional and configured through environment variables, unrelated to state reset.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 4.1 code cell, `LLMEvalMetric.__init__` / `__call__` state-reset comments, and the section's bullet on pydantic structured output.
</details>

## Question 9

A team evaluates its `CourseTestingSkill` with a prompt CSV in which every row has `should_trigger=true` (explicit, implicit, and contextual invocations). In production, the Skill activates for the request "Help me fix the CSS style problem in the course page," which it should not handle. According to Section 4.2, what is the indicated fix to the evaluation set?

A. Expand the prompt set to at least 100 cases so trigger accuracy can be measured with statistical significance.

B. Add negative-control prompts — cases where the Skill should NOT trigger — to the CSV, and keep adding each newly discovered failure case, since the prompt set is a living document.

C. Add a deterministic checker that inspects the execution trace for the unwanted tool calls.

D. Add a rubric-scoring layer with a JSON Schema so the false trigger is scored as a failure.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Add negative-control prompts — cases where the Skill should NOT trigger — to the CSV, and keep adding each newly discovered failure case, since the prompt set is a living document.**

Section 4.2 defines trigger correctness as covering both directions: "triggers when it should, doesn't when it shouldn't." Its example CSV includes a negative control (`test-04,false,"Help me fix the CSS style problem in the course page"`) whose stated purpose is "to catch false triggering" — exactly the production failure in the stem — and instructs: "As you discover new failure cases, add them to this list — this small CSV becomes a living document," noting that 10–20 prompts are enough to discover regressions (contra option A's scale-up). Options C and D describe the SOP-compliance check layer, which verifies "what was done and how well" after triggering; neither addresses whether the Skill should have activated at all.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 4.2, "Building a prompt set: positive triggers and negative controls" (CSV example; four case types; living-document paragraph).
</details>

## Question 10

A team must check its testing Skill's SOP compliance on two requirements: (i) "a screenshot command was actually executed during the run," and (ii) "the generated test report's descriptions are accurate and unambiguous." According to Section 4.2's two-layer check, how should these be evaluated?

A. Both via rubric scoring sent to a model, since SOP compliance is inherently qualitative.

B. Both via deterministic checkers, since execution traces contain all the needed evidence.

C. (i) via a deterministic checker that scans the execution-trace event sequence for the tool call; (ii) via model-assisted rubric scoring returning a structured JSON response conforming to a schema.

D. (i) via model-assisted rubric scoring; (ii) via a deterministic checker over the generated report file.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — (i) via a deterministic checker that scans the execution-trace event sequence for the tool call; (ii) via model-assisted rubric scoring returning a structured JSON response conforming to a schema.**

Section 4.2 splits SOP checks into "what was done" (objective → deterministic checker) and "how well it was done" (subjective → rubric scoring). Requirement (i) is exactly the source's `check_screenshot_taken(events)` example — a deterministic, debuggable scan of the event sequence for a `tool_call` event whose name contains "screenshot." Requirement (ii) matches the source's listed qualitative requirements (report structure, coverage, description accuracy) handled by sending a rubric prompt plus a JSON Schema (with `overall_pass`, `score`, per-check `id`/`pass`/`notes`, including an `accuracy` check id) to a scoring model. Option D inverts the mapping; A and B each collapse the two layers the source deliberately separates.

**Source:** `3_6_Evaluation_Driven_Agent_Development.ipynb` — Section 4.2, "Two-layer check: objective + subjective" (`check_screenshot_taken` code cell; rubric JSON Schema and prompt).
</details>
