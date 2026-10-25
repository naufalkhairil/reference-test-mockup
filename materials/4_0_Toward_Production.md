# 4.0 Toward Production

After the polishing of the previous stages, your AI system now runs quite stably in the development environment. Evaluation metrics keep improving, Harness Engineering makes the components work together, and the team is confident in the system.

<img src="https://img.alicdn.com/imgextra/i2/O1CN01fOPgYz1Mbz0rdLzgt_!!6000000001454-2-tps-1024-1024.png" alt="123" width="400px">

Company leaders have seen the results and decided to officially launch this system to serve the whole company. But between "it works on your computer" and "the whole company uses it every day" lie several mountains.

**Cost**: Every LLM API call costs money. With 100 people using it simultaneously, what's the monthly token bill? Could you cut cost and boost speed by fine-tuning a smaller model?

<img src="https://img.alicdn.com/imgextra/i4/O1CN01lNnaPD1FOyS8U8ssF_!!6000000000478-2-tps-1024-1024.png" alt="123" width="400px">

**Deployment**: The system only runs on your laptop. The IT department asks you — how do you deploy it to a server? How do you ensure high availability? How do you monitor its status?

<img src="https://img.alicdn.com/imgextra/i1/O1CN01htzqXv1II3JYYWdyV_!!6000000000869-2-tps-1024-1024.png" alt="123" width="400px">

**Security & compliance**: The security team weighs in too — could user input leak sensitive information? Could the model output inappropriate content? Does the system meet industry compliance requirements?

<img src="https://img.alicdn.com/imgextra/i3/O1CN01ESt9tR1w2YXou9eqA_!!6000000006250-2-tps-1024-1024.png" alt="123" width="400px">

Next, you'll solve these problems one by one, taking the system from the development environment into a real production environment.

**Lessons in this stage:**

| Lesson | Title | Notes |
|------|------|------|
| 4.1 | Using Distillation to Give a Small Model Professional Capabilities | Model distillation in practice |
| 4.2 | Deploying Models | Model deployment & inference services |
| 4.3 | Production Practices for LLM Applications | Production-environment best practices |
| 4.4 | Security & Compliance for LLM Applications | Security protection & compliance requirements |
