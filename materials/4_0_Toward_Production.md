# 4.0 Toward Production

After the polishing of the previous stages, your AI system now runs quite stably in the development environment. Evaluation metrics keep improving, Harness Engineering makes the components work together, and the team is confident in the system.

Company leaders have seen the results and decided to officially launch this system to serve the whole company. But between "it works on your computer" and "the whole company uses it every day" lie several mountains.

**Cost**: Every LLM API call costs money. With 100 people using it simultaneously, what's the monthly token bill? Could you cut cost and boost speed by fine-tuning a smaller model?

**Deployment**: The system only runs on your laptop. The IT department asks you — how do you deploy it to a server? How do you ensure high availability? How do you monitor its status?

**Security & compliance**: The security team weighs in too — could user input leak sensitive information? Could the model output inappropriate content? Does the system meet industry compliance requirements?

Next, you'll solve these problems one by one, taking the system from the development environment into a real production environment.

**Lessons in this stage:**

| Lesson | Title | Notes |
|------|------|------|
| 4.1 | Using Distillation to Give a Small Model Professional Capabilities | Model distillation in practice |
| 4.2 | Deploying Models | Model deployment & inference services |
| 4.3 | Production Practices for LLM Applications | Production-environment best practices |
| 4.4 | Security & Compliance for LLM Applications | Security protection & compliance requirements |
