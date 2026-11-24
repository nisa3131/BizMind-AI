# Render cloud demo deployment

The portfolio demo uses a single Docker image containing FastAPI and the React build. The local Docker Compose setup remains separate.

Hosted demo: [Open dashboard](https://bizmind-ai-gc1c.onrender.com) · [API docs](https://bizmind-ai-gc1c.onrender.com/docs) · [Health check](https://bizmind-ai-gc1c.onrender.com/api/v1/health).

## Render configuration

| Setting | Value |
|---|---|
| Source | https://github.com/nisa3131/BizMind-AI |
| Runtime | Docker |
| Branch | main |
| Root directory | Repository root (leave blank) |
| Instance type | Free, when available |
| Dockerfile path | ./Dockerfile.cloud |
| Docker build context | . |
| Docker command | Leave blank |
| Health check path | /api/v1/health |

Choose only a free instance and review the current [Render free service limits](https://render.com/docs/free). Do not activate paid resources.

## Secrets

Set JWT_SECRET to at least 32 random characters and BIZMIND_INVITE_CODE to at least 16 random characters. Configure both in Render's Environment section. Use the private invite code when registering a demonstration account.

Never put secret values in source control, screenshots, documentation or a public demo link.

## Verify after deploy

1. Open the public service URL displayed in the Render dashboard.
2. Open /api/v1/health and /docs on the same origin.
3. Register a demo account, upload examples/demo-faq.txt, ask about its return policy, and confirm source references and analytics.
4. The free cloud demo uses lightweight lexical retrieval, not the local ChromaDB embedding index. No paid hosted LLM is required.
5. If the application sleeps, reopen it before an interview and allow it to start. Free service storage is ephemeral: database records, accounts and uploaded documents may reset.

## Interview use

Open the public dashboard in a browser, use synthetic inputs, and keep secrets private. See [the interview guide](INTERVIEW_GUIDE.md). This is a portfolio prototype, not a production service or a comprehensive security guarantee.
