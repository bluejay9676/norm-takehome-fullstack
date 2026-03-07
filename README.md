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

## Context:

- I think the only part that requires deeper explanation than just reading the code is DocumentService.create_documents
- TODO
