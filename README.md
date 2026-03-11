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

### Assumptions:

- I made a choice to outsource pdf parsing - i would make the same choice in prod setting since i expect llama parse to be more accurate
- I would have to account for how often we have to parse new documents (does it make sense economically?) but in this particular situation we only have to parse 1 document once.

### Next step

- Spend more time on more robust pdf parsing
- Show citations - click to actual parts of pdf
- allow user to correct the parsing
- SSE for a true chat-like experience
- Clean up hardcoded codes and put in remote secret keys (vault, aws sk) and read on server init & frontend init

### Q

1. What unique challenges do you foresee in developing and integrating AI regulatory agents for legal
   compliance from a full-stack perspective?

>

https://www.anthropic.com/research/labor-market-impacts

- there is always an element of taste
- that's especially true for things like sales and legal in my opinion
- I've seen this firsthand when I made AI call copilot for SDRs
- It works, it's fast but it was not good enough for the opinionated users to see it as truly 'valuable'
- I think the foundational model is very close to solving "what law should we look at for this?" "what pdf should I look at for my prospect's question?" type of tasks
- what it fails to do is processing the info in a way that's usable
- when it comes to regulatory screening / liability evaluation - I think a lot of "taste" can come to play
- great attorneys will be able to see loophole by connecting multiple information that might look irrelevant while a normal attorneys wouldn't be able to connect the dots.
- The defensibility of a business probably comes down to how well we can capture a universal "taste" that works for most of the users.

2. How would you address these challenges to make the system robust and user-friendly?

>

- very different answer now vs 2 months ago
- before i wouldve said typical be close to your users etc
- now you can actually give the power to the users to personalize their experience 
- this isnt impossible anymore imo

- Quick anecdote:
- the CTO I worked with at Glencoco is building major.build - an internal tool vibecoding platform.
- Micah - who was a killer sales guy on Glencoco, later joined in as a full time design partner, then sort of took over the whole operation after we shutdown - now with tools like loveable is making some insane tools and workflows.
  - Glencoco closed out Feb with 250k in rev without engineers / ops people involved. Mainly Micah and other callers running the ship.
- The takeaway here is that you really have to be as close as possible to these opinionated users - or even give them the tool to make changes themselves.
- This is only now possible because of AI. Any company should double down on this wave.

```
Norm Ai is automating compliance processes, making them more efficient, cost-effective, and accurate than
ever before, while also ensuring democratic guardrails for AI in autonomous roles. By converting complex
regulations into intelligent AI programs, we enable compliance teams to operate with unprecedented speed
and precision. Our vision extends beyond just assisting compliance teams; we aim to enable the integration of
AI agents into daily life, ensuring that AI-driven business processes adhere to legal and societal norms
through adoption of our Regulatory AI agents as oversight. At Norm Ai, we're committed to aligning AI with
public policy, reflecting our society's collective will, and ushering in a new era of regulatory intelligence and
societal-AI alignment.
```
