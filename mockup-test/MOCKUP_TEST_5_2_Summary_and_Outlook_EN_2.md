# Professional Exam: Summary and Outlook — Applying AI Solutions and Industry Cases

Choose the single best answer for each question. All items are grounded in the lesson `5_2_Summary_and_Outlook_EN.ipynb` (Alibaba Cloud LLM ACP course, Section 5.2). This is a source-grounded practice draft, not a validated or official certification exam.

## Question 1

The lesson recaps the five stages of the course — from getting a bot talking and calculating cost, through knowledge, conventions, and evaluation, then acting, planning, memory, and Harness Engineering, then cost, deployment, and security for production, and finally the RIDE methodology for business judgment. What does it say about how those stages arose, and what mindset should you carry into your own AI project?

A. Each stage was specified in advance as a fixed reference architecture, so the mindset is to select the most advanced stage your budget allows.

B. Each stage was adopted by benchmarking against competing products, so the mindset is to make the system reliable before you make it work.

C. Stages were added only when a production incident forced a change, so the mindset is to prioritize cost control above answer quality.

D. Each step emerged naturally because finishing the previous step surfaced a new problem, and the mindset is: first make it work, then make it good, then make it reliable, and finally take it live.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — Each step emerged naturally because finishing the previous step surfaced a new problem, and the mindset is: first make it work, then make it good, then make it reliable, and finally take it live.**

The recap states that "none of these steps were designed out of thin air — each one emerged naturally because finishing the previous step surfaced a new problem", and then offers that four-step sequence explicitly as "the mindset you'll want to bring the next time you build an AI system on your own."

Options A and B assert a pre-planned or benchmark-driven design, which is the opposite of the lesson's claim. Option C also reverses the stated order of the mindset (reliability comes *after* the system works and is good), and the lesson never subordinates quality to cost here.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — opening recap cell under the title "5.2 Summary and Outlook" (the five-stage list, the "emerged naturally" sentence, and the "first make it work…" mindset sentence).
</details>

## Question 2

A retailer holds ten thousand clothing product photos and needs to extract attributes such as the pattern and the collar style; doing it by hand is slow and labor-intensive. What does the lesson recommend, and what does the accompanying deployment walkthrough provide?

A. Build an AI customer-service bot in ten minutes and have customers describe the attributes to it in chat.

B. Use a vision-understanding large model via the multimodal data-information extraction solution; the walkthrough guides you through automatically building a vision application and provides complete source code.

C. Use the AI script generation and animation creation solution to render each attribute into a short demonstration video.

D. Use the real-time audio/video interaction solution so human agents can dictate attributes while reviewing the photos.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — Use a vision-understanding large model via the multimodal data-information extraction solution; the walkthrough guides you through automatically building a vision application and provides complete source code.**

The lesson opens its hands-on catalog with exactly this scenario — ten thousand clothing photos, extracting pattern or collar style, slow and labor-intensive by hand — and says you can automate it with a vision-understanding large model, adding that the same approach extends to paper forms and video content. Its Technical Solutions link "will walk you through automatically building a vision application, and provides complete source code for you to reference."

The other options all name real solutions from the same catalog, which is what makes them tempting, but each is aimed at a different job: A and D serve customer interaction, C serves content creation. None of them extracts structured attributes from a large photo archive.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 1.1 "Multimodal Data-Information Extraction" (the ten-thousand-photos example, the vision-understanding model, and the "try this solution right now" walkthrough description).
</details>

## Question 3

A team wants hands-on practice constructing a multi-agent workflow, with reference source code, while producing one-click videos from characters and a story outline it designs itself. Which solution does the lesson point to?

A. AI Script Generation and Animation Creation — deploying an instance walks you through building a multi-agent workflow and provides complete source code.

B. Build an AI Assistant in 10 Minutes — it needs no code at all, so the team can study the configuration instead of a workflow.

C. Multimodal Data-Information Extraction — it builds a vision application capable of generating animation frames from source photos.

D. The Enterprise-Grade Intelligent Coding Solution — it converts committed code into a pipeline that renders animation assets.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — AI Script Generation and Animation Creation — deploying an instance walks you through building a multi-agent workflow and provides complete source code.**

The lesson describes this solution as one-click video creation where "you and your family or friends can design the animation's characters and story outline together, and leave the rest entirely to AI", and states that deploying an instance "will walk you through building a multi-agent workflow, and provides complete source code for you to reference" — precisely the two learning goals in the stem.

Option B is the strongest distractor: that solution genuinely is no-code, but it connects a client application to a Bailian AI application for knowledge-base Q&A, so it teaches configuration rather than multi-agent workflow construction. Option C overstates the vision solution, which extracts information rather than generating animation. Option D attaches pipeline automation to an unrelated outcome; the coding solution runs code checks and unit tests, not rendering.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 1.2 "AI Script Generation and Animation Creation"; contrast Section 1.3 "Build an AI Assistant in 10 Minutes" and Section 1.1 "Multimodal Data-Information Extraction".
</details>

## Question 4

A non-developer operations team wants an AI assistant answering customer inquiries around the clock in its DingTalk groups, drawing on the company's private knowledge base, and it cannot write code. According to the lesson, how is this delivered?

A. By deploying a real-time audio/video interaction instance on the ARTC network and pointing it at the knowledge base.

B. By fine-tuning a Qwen model on the private documents and hosting the resulting model inside the group.

C. By supplying the relevant configuration information to connect the client application with a Bailian AI application, on which the dedicated assistant provides private-knowledge-base Q&A service.

D. By installing Lingma in the DingTalk client so that it generates answers from the group's message history.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — By supplying the relevant configuration information to connect the client application with a Bailian AI application, on which the dedicated assistant provides private-knowledge-base Q&A service.**

The lesson's note on the "Build an AI Customer-Service Bot in 10 Minutes" family of solutions is explicit: "you just need to supply the relevant configuration information — no code required — to connect various client applications with a Bailian AI application. And on Bailian, you can build and refine a dedicated AI assistant that offers private-knowledge-base Q&A service, powering your client application with AI capability." The same section lists DingTalk, a WeChat Official Account, WeCom, and a website as supported channels with round-the-clock response.

Option A substitutes the real-time interaction solution, which addresses voice/video conversations rather than a configuration-driven group bot. Option B invents a fine-tuning step the lesson does not describe here. Option D misapplies Lingma, which the lesson presents as a programming partner for developers.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 1.3 "Build an AI Assistant in 10 Minutes", including the blockquoted note on configuration-only integration with a Bailian AI application and the DingTalk / WeChat Official Account / WeCom deployment table.
</details>

## Question 5

A customer-service center handles thousands of complex inquiries a day, and human agents cannot respond to and resolve every one in real time. Which solution does the lesson recommend, and on what stated basis does it treat that solution as production-ready?

A. The Build an AI Assistant in 10 Minutes series, because it supports DingTalk, WeChat Official Account, and WeCom channels around the clock.

B. The AI Real-Time Audio/Video Interaction solution, built on the ARTC video-cloud network and described as stable, efficient, and extremely low-latency — fully capable of handling commercial-scale use; an audio-only assistant is offered as an alternative to compare.

C. The multimodal data-information extraction solution, because recorded video content can be understood and answered asynchronously.

D. The AI Script Generation and Animation Creation solution, because animated agents can hold many conversations in parallel.

<details>
<summary>Show answer and rationale</summary>

**Answer: B — The AI Real-Time Audio/Video Interaction solution, built on the ARTC video-cloud network and described as stable, efficient, and extremely low-latency — fully capable of handling commercial-scale use; an audio-only assistant is offered as an alternative to compare.**

The lesson poses this exact scenario — thousands of complex daily inquiries that human agents cannot all handle in real time — and points to the AI Real-Time Audio/Video Interaction solution, attributing its stability, efficiency, and extremely low latency to the ARTC video-cloud network and stating it is "fully capable of handling commercial-scale use." It then adds that you can instead build an audio-only conversational assistant and see which fits the business better.

Option A names a real solution but one the lesson frames around embedding a knowledge-base assistant into chat channels, not real-time conversational capacity at this scale; the stem's constraint is real-time response to high inquiry volume. Options C and D are catalog items aimed at data extraction and content creation.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 1.4 "Real-Time Audio/Video Calls with AI" (the call-center scenario, ARTC basis, commercial-scale claim, and the audio-only alternative).
</details>

## Question 6

A development team wants committed code to automatically trigger a pipeline that runs automated code checks and unit tests, managing the whole flow from development through CI/CD. What does the lesson point to for this?

A. Lingma on its own, because its one-click workflow already covers unit tests and CI/CD pipeline management.

B. The real-time audio/video interaction solution, because pipeline failures require immediate human escalation by voice.

C. A Bailian AI application, because private-knowledge-base Q&A can answer build questions during a pipeline run.

D. The Enterprise-Grade Intelligent Coding Solution, which combines Lingma with Yunxiao to strengthen project-management capability and help ensure software ships on time and at high quality.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — The Enterprise-Grade Intelligent Coding Solution, which combines Lingma with Yunxiao to strengthen project-management capability and help ensure software ships on time and at high quality.**

The lesson introduces this in a note attached to the pair-programming section: "If you'd like committed code to automatically trigger a pipeline, running automated code checks and unit tests, managing the entire flow from development through CI/CD — Alibaba Cloud also offers an Enterprise-Grade Intelligent Coding Solution, combining Lingma with Yunxiao…" The stem restates that trigger-to-pipeline requirement, so the combination is the answer.

Option A is the tempting misreading: Lingma's one-click workflow does span "implementing requirements to writing unit tests", but commit-triggered pipeline management across CI/CD is exactly what the Yunxiao combination adds, so Lingma alone does not meet the stated need. Options B and C reuse catalog items with no pipeline role.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 1.5 "Pair Program with an AI Developer, and Become a Full-Stack Developer in an Instant", the blockquoted note on the Enterprise-Grade Intelligent Coding Solution (Lingma + Yunxiao).
</details>

## Question 7

A hospital group is reviewing the lesson's healthcare examples: DAMO Academy's DaYi Zhiying, developed in 2020, analyzing a patient's CT scan to diagnose a suspected COVID-19 case in about 20 seconds with accuracy above 96%; imaging analysis for lung-disease screening cut from hours to minutes; and a partnership with AstraZeneca using medical literature and clinical data to generate drug adverse-reaction reports. What constraint does the lesson attach to clinical use?

A. AI suggestions and AI-generated prescriptions are only reference information — medical decisions should be made by a qualified physician based on the patient's actual condition.

B. Because DaYi Zhiying exceeds 96% accuracy, it may issue final diagnoses without physician review in screening scenarios.

C. Large models may be applied only to research-side tasks such as generating drug adverse-reaction reports from literature.

D. Diagnostic assistance must be limited to hospitals that partnered with Alibaba Cloud on lung-disease screening.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — AI suggestions and AI-generated prescriptions are only reference information — medical decisions should be made by a qualified physician based on the patient's actual condition.**

This is the note the lesson places immediately after its healthcare cases, and it is the governance boundary a professional must carry into any deployment discussion: impressive speed and accuracy figures do not transfer decision authority to the model.

Option B reads the metrics as a delegation of authority, which the note explicitly refuses. Option C over-restricts the field — the lesson presents diagnosis assistance, health management, and R&D productivity as live application areas, not research-only ones. Option D invents an eligibility condition that appears nowhere in the source.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 2.1 "Healthcare: Diagnostic Assistance and Health Management" (the AstraZeneca, DaYi Zhiying, and lung-disease screening examples, followed by the blockquoted "Note: AI suggestions and AI-generated prescriptions are only reference information…").
</details>

## Question 8

A tutoring company wants to replicate the personalization the lesson describes in Jingzhunxue's ultra-lifelike AI one-on-one teacher, built on Alibaba's Qwen large model. Which mechanism does the lesson credit for that personalization?

A. Assigning each student a fixed curriculum track selected at enrollment by a human advisor.

B. Replacing teachers with round-the-clock homework help so every student receives the same instruction.

C. Automatically adjusting teaching content and difficulty based on the student's progress and weak spots, so each student gets the learning resources best suited to them.

D. Presenting every student with the same ultra-lifelike teacher interface and personalizing only its voice and appearance.

<details>
<summary>Show answer and rationale</summary>

**Answer: C — Automatically adjusting teaching content and difficulty based on the student's progress and weak spots, so each student gets the learning resources best suited to them.**

The lesson states that the system "can automatically adjust teaching content and difficulty based on a student's progress and weak spots, ensuring every student gets learning resources best suited to them" — adaptive content and difficulty driven by learner state is the mechanism, not a static assignment.

Option B distorts the source's own commentary: round-the-clock homework help is described as *assisting* teachers and broadening potential, and uniform instruction is the opposite of personalization. Option D confuses presentation ("ultra-lifelike") with adaptation. Option A is a manual process the lesson does not describe. The section also notes the related inclusivity program with DingTalk and Qwen extending AI-assisted resources to remote areas and disadvantaged groups, which is a distribution effort rather than the personalization mechanism asked about here.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 2.3 "Education: Personalized Learning and Intelligent Tutoring" (Jingzhunxue on Qwen, adaptive content and difficulty, and the DingTalk/Qwen inclusivity program).
</details>

## Question 9

A team is selecting a model for an agent that must call tools and return strictly structured JSON, while also reasoning deeply over long documents. It is considering the QwQ series. Based on the lesson, what is the right assessment?

A. QwQ fits, because its extremely long context and multi-turn conversation support together cover long documents and tool orchestration.

B. QwQ fits, because the commercial version's reinforcement learning improves math, code, and general-purpose tasks, which includes structured output.

C. QwQ fits if the team uses the open-source version such as qwq-32b, which adds the tool calling that the commercial version lacks.

D. QwQ does not fit this agent: the lesson states it does not support tool calling or structured output, although it does support a 131,072-token context and multi-turn conversation and suits scenarios needing deep thinking.

<details>
<summary>Show answer and rationale</summary>

**Answer: D — QwQ does not fit this agent: the lesson states it does not support tool calling or structured output, although it does support a 131,072-token context and multi-turn conversation and suits scenarios needing deep thinking.**

The lesson's profile of QwQ pairs real strengths with two explicit exclusions: a strong-reasoning model trained on the Qwen2.5 series, commercial (qwq-plus) and open-source (qwq-32b) versions, an extremely long context of 131,072 tokens, multi-turn conversation, and a design that prioritizes reasoning quality — "but doesn't support features like tool calling or structured output." A selection decision must be driven by the exclusions, since both are hard requirements in the stem.

Options A and B take genuine facts (long context, multi-turn support, reinforcement-learning gains on math, code, and general tasks) and extend them to capabilities the lesson denies. Option C invents a version difference that does not exist in the source; the open-source version is credited with surpassing comparable distilled models, not with adding tool calling.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — Section 3.1 "Further Reading: The Deep-Thinking Model QwQ" (versions, reinforcement learning, the 131,072-token context and multi-turn support, the unsupported features, and the intended deep-thinking scenarios).
</details>

## Question 10

You are asked to validate a newly available AI tool in a business setting as quickly as possible. Which strategy does the lesson endorse, and why?

A. Choose a small, representative group of users to run a pilot, because a small-scale pilot effectively controls risk and avoids project failure caused by immature technology or a poor fit with the business scenario.

B. Conduct broad, comprehensive market research before implementation, so the eventual rollout rests on complete demand data.

C. Move straight into a large-scale rollout, because the widest user base produces validation evidence fastest.

D. Wait for a competitor to test the approach first, then follow their lead to avoid being the first to fail.

<details>
<summary>Show answer and rationale</summary>

**Answer: A — Choose a small, representative group of users to run a pilot, because a small-scale pilot effectively controls risk and avoids project failure caused by immature technology or a poor fit with the business scenario.**

The lesson's own quiz item asks for an effective strategy to validate a new AI tool quickly in a business setting and keys the small, representative pilot group, with the stated rationale that a small-scale pilot controls risk and prevents failure from immature technology or poor scenario fit. The professional judgment being tested is that speed and risk containment are achieved by narrowing scope, not by widening it.

Options B, C, and D are the alternatives the lesson presents and rejects: broad research first and a large-scale rollout both delay or amplify risk rather than validating quickly, and following a competitor delegates the fit question you still have to answer for your own scenario.

**Source:** `5_2_Summary_and_Outlook_EN.ipynb` — "🔥 Quiz" section, Multiple Choice 5.2.1 ("What's an effective strategy for quickly validating a new AI tool in a business setting?"), answer B and its explanation. The stem above is adapted from that item.
</details>
