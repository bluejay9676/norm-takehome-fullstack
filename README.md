## Setup guide:

- setup llama parse & openai api account and set the api keys as env var
  LLAMA_CLOUD_API_KEY
  OPENAI_API_KEY
- run the following to get the docker up and running

```
// From the base of the repo
docker build -t norm-takehome-fullstack .
```

```
docker run -d -p 8080:80 -e OPENAI_API_KEY=$OPENAI_API_KEY -e LLAMA_CLOUD_API_KEY=$LLAMA_CLOUD_API_KEY norm-takehome-fullstack
```

- check the local server's endpoint (or use the swagger)

```
curl -X POST http://localhost:8080/query -H "Content-Type: application/json" -d '{"query": "What happens if I steal a bread?"}'
```

Then run frontend from the frontend/

```
npm run dev
```

## Context:

- I think the only part that requires deeper explanation than just reading the code is DocumentService.create_documents

What unique challenges do you foresee in developing and integrating AI regulatory agents for legal
compliance from a full-stack perspective? How would you address these challenges to make the system
robust and user-friendly?

Norm Ai is automating compliance processes, making them more efficient, cost-effective, and accurate than
ever before, while also ensuring democratic guardrails for AI in autonomous roles. By converting complex
regulations into intelligent AI programs, we enable compliance teams to operate with unprecedented speed
and precision. Our vision extends beyond just assisting compliance teams; we aim to enable the integration of
AI agents into daily life, ensuring that AI-driven business processes adhere to legal and societal norms
through adoption of our Regulatory AI agents as oversight. At Norm Ai, we're committed to aligning AI with
public policy, reflecting our society's collective will, and ushering in a new era of regulatory intelligence and
societal-AI alignment.
