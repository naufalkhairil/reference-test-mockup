# 3.0 From Answering Questions to Solving Problems

After the previous stage's work, the FAQ bot can now accurately answer internal company questions, with a professional and consistent style, and the evaluation system is up and running. Colleagues have started to trust it — but trust brings higher expectations.

"Can you search the latest industry reports for me?" "Update the project schedule for me." "Review this course document for me."

You discover a fundamental limitation: **the bot can only "talk," not "act."** To turn it from an "advisor" into an "assistant," it needs the ability to use tools, plan, and collaborate through division of labor.

But once the Agent learns to act, new problems follow: **every time it starts a new task, it's as if it has amnesia.** It falls into the same pit it fell into last time, and a carefully tuned review process has to be re-explained from scratch in a new conversation window. Good working methods stay buried in chat logs, never solidified into reusable processes.

After solving the problems of memory and knowledge retention, all the parts are in place: tools, planning, division of labor, memory, skills. But having the parts doesn't mean the system is reliable. You ask the Agent to review a document, and the result is great sometimes and inexplicably bad other times. **What's missing is a systematic method to judge whether it did well — to move it from "occasionally right" to "consistently right."**

Next, you will solve these three problems step by step: let the Agent act, retain good experience, and assemble the parts into a reliable system.

**Lessons in this chapter:**

| Lesson | Title | Notes |
|------|------|------|
| 3.1 | Agent Basics & Tool Calling | Function Calling + ReAct + MCP |
| 3.2 | Teaching the Agent to Plan & Execute | Reflection + Workflow + Autonomous Planning |
| 3.3 | Team Collaboration with Multiple Agents | Multi-agent division of labor & collaboration |
| 3.4 | Using Memory to Let the Agent Accumulate Experience | Short/long-term memory + active memory management |
| 3.5 | Using Skills to Solidify Capabilities into Reusable Processes | The evolution from Prompt to Skill |
| 3.6 | Evaluation-Driven Agent Development | End-to-end + white-box evaluation |
| 3.7 | Qwen Code in Practice | Master the day-to-day workflow of a Coding Agent |
| 3.8 | Building Production-Ready Business Capability with Harness Engineering and Loop Engineering | The closed loop of standards, validation, logging, and write-back |
