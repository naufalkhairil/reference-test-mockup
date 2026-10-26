# Professional Exam: Project Background — From Document Libraries to LLM-Based Intelligent Q&A

Choose the single best answer for each question.

> **Source-limitation note:** This exam is based on `2_0_Project_Background.ipynb`, a short section introduction (~1 page of narrative text) that presents a four-stage problem-evolution story: Q&A cost pressure → document library → rule-based Q&A system → planned LLM-based application. The source supports only a limited number of rigorous, non-repetitive items, so this exam contains **5 questions** instead of the default 10. No items were padded with speculation or outside knowledge.

## Question 1

An educational content development company compiled a comprehensive document library covering company policies, writing standards, and day-to-day tool guides, expecting new employees to look things up on their own. After a while, however, new employees' work still did not comply with policies and errors remained frequent. According to the company's analysis, what was the cause?

A. The library lacked coverage of company policies and writing standards.

B. The documents became outdated because policies changed frequently.

C. The library held too much information for new employees to read and absorb thoroughly.

D. New employees could not access the library without manager approval.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — The library held too much information for new employees to read and absorb thoroughly.**

The source states that after the document library was introduced, "new employees' work still didn't comply with the policies and errors were frequent," and that analysis showed the cause: "the document library held too much information for new employees to read and absorb thoroughly." The stem reproduces exactly this situation, so the source's stated root cause is the best answer.

Option A is the most tempting alternative because poor coverage is a common real-world failure mode, but it directly contradicts the source, which describes the library as "comprehensive" and covering policies, writing standards, and tool guides. Options B and D introduce problems (staleness, access control) that the source never mentions.

**Source:** `2_0_Project_Background.ipynb` — "Text version" section, passage following the second image ("After a while, the company found that new employees' work still didn't comply with the policies... Analysis showed the cause: the document library held too much information for new employees to read and absorb thoroughly.").
</details>

## Question 2

The company next built a Q&A system pre-configured with employees' high-frequency questions. After it ran for a while, the volume of employee inquiries and work errors had still not dropped significantly. According to the source, what was the chief reason the system often could not answer when employees phrased questions differently?

A. It required employees to submit questions in a standardized written format.

B. It relied on fixed rules and similarity matching, which often could not handle differently phrased questions.

C. It had been pre-configured with too few high-frequency questions to cover employee needs.

D. It searched only the document library rather than the configured question-answer pairs.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — It relied on fixed rules and similarity matching, which often could not handle differently phrased questions.**

The source explicitly identifies this as the chief limitation: the Q&A system "relied on fixed rules and similarity matching, it often couldn't answer when employees phrased questions differently." A system based on matching against pre-configured questions breaks precisely when the user's wording diverges from the stored phrasing, which is what the stem describes.

Option C is the most tempting alternative — it seems plausible that coverage gaps cause missed answers — but the source attributes the failure to the matching mechanism itself, not to an insufficient number of configured pairs; the pairs were specifically chosen to cover "high-frequency questions." Options A and D describe behaviors the source never mentions.

**Source:** `2_0_Project_Background.ipynb` — "Text version" section, passage after the fourth image ("Company leaders realized the current Q&A system had many limitations — chiefly, because it relied on fixed rules and similarity matching...").
</details>

## Question 3

Beyond its inability to handle varied phrasings, the rule-based Q&A system was judged to have "a very low return on investment." Which characteristic of the system's operating model most directly explains that judgment?

A. Manually configuring question-answer pairs was labor-intensive.

B. The system answered questions using fixed rules and similarity matching.

C. Employees submitted more inquiries than the system could process.

D. The document library duplicated much of the Q&A system's content.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Manually configuring question-answer pairs was labor-intensive.**

The source pairs the two limitations of the rule-based system: the fixed-rules/similarity-matching weakness, and the fact that "manually configuring question-answer pairs was labor-intensive, with a very low return on investment." Low return on investment is a statement about the cost side of the operating model — heavy ongoing manual configuration effort — which is exactly what option A captures.

Option B is tempting because it is also a stated limitation, but it explains the system's answer-quality failures (Question 2's topic), not its poor investment return. Options C and D are not supported by the source.

**Source:** `2_0_Project_Background.ipynb` — "Text version" section ("Moreover, manually configuring question-answer pairs was labor-intensive, with a very low return on investment.").
</details>

## Question 4

Faced with the rule-based Q&A system's poor results, a manager proposes hiring additional staff to configure several thousand more question-answer pairs, arguing this will fix the system. Based solely on the analysis presented in the source, what is the strongest assessment of this proposal?

A. It is sound, because the system's chief limitation was insufficient coverage of high-frequency questions.

B. It will fix the phrasing problem but not the cost problem, because more pairs would let similarity matching handle varied wording.

C. It will fix the cost problem but not the phrasing problem, because a larger pair inventory spreads the configuration effort over more answers.

D. It addresses neither stated root cause: the system would still rely on fixed rules and similarity matching that fail on differently phrased questions, and more manual pair configuration would deepen the labor-intensive, low-return model — which is why the company turned to an LLM-based application that answers from the knowledge base without configuring question-answer pairs.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — It addresses neither stated root cause: the system would still rely on fixed rules and similarity matching that fail on differently phrased questions, and more manual pair configuration would deepen the labor-intensive, low-return model.**

This is an application of the source's two stated limitations to a new proposal. Adding pairs does not change the matching mechanism, so differently phrased questions would still go unanswered; and it intensifies exactly the manual, labor-intensive work the source already judged to have very low return on investment. The source's chosen resolution — an LLM-based application that "without configuring question-answer pairs, can accurately answer questions from the company's internal knowledge base" — confirms that scaling pair configuration runs against the direction the company took.

Options B and C each credit the proposal with fixing one root cause; both fail, because more pairs neither overcome the fixed-rules/similarity-matching weakness nor lower the configuration cost per answer. Option A misidentifies coverage as the chief limitation, contradicting the source.

**Source:** `2_0_Project_Background.ipynb` — "Text version" section, passages on the Q&A system's limitations and on the decision to build an LLM-based intelligent Q&A application. (The assessment itself is an application of these stated facts to the manager's proposal.)
</details>

## Question 5

Company leaders put you in charge of solving the Q&A problem "once and for all," and you plan to use LLM technology. According to the source, which combination of characteristics defines the intelligent Q&A application you intend to build?

A. It automatically pre-configures question-answer pairs from the document library and routes employee inquiries to them.

B. It understands human language well and, without configuring question-answer pairs, can accurately answer questions from the company's internal knowledge base, aiming to reduce employee inquiries and improve work efficiency.

C. It replaces the document library with a condensed version so new employees can read and absorb it thoroughly.

D. It enforces policy compliance by checking employee work products against a fixed set of rules.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — It understands human language well and, without configuring question-answer pairs, can accurately answer questions from the company's internal knowledge base, aiming to reduce employee inquiries and improve work efficiency.**

The source describes the planned application almost verbatim: "An LLM-based intelligent application understands human language well and, without configuring question-answer pairs, can accurately answer questions from the company's internal knowledge base — truly and effectively reducing employee inquiries and improving work efficiency." Each element of option B maps to a stated capability or goal.

Option A is the most tempting alternative because it involves the knowledge base and sounds like an automation of the old system, but it preserves the question-answer-pair paradigm that the source identifies as labor-intensive and low-return; the LLM application explicitly eliminates pair configuration. Options C and D restate the earlier, failed approaches (condensing reading material; rule-based checking) rather than the planned solution.

**Source:** `2_0_Project_Background.ipynb` — "Text version" section, final narrative paragraphs ("After some research, you plan to use today's most advanced LLM technology to build an intelligent Q&A application...").
</details>
