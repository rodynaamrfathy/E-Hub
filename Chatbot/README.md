```
📂 high-perf-ai-chatbot/
│── README.md
│── requirements.txt / pyproject.toml      # Python deps
│── package.json                           # Frontend deps (React/Vue)
│── docker-compose.yml                     # Local dev orchestration
│── .env.example                           # Env variables
│
├── 📂 docs/
│   ├── architecture.md                    # High-level system design
│   ├── rag_pipeline.md                    # Vector store + retriever flow
│   ├── mcp_protocol.md                    # MCP server specs
│   ├── streaming.md                       # Streaming + UX benefits
│   └── api_reference.md                   # REST/WebSocket endpoints
│
├── 📂 backend/
│   ├── main.py                            # FastAPI entrypoint (API Gateway)
│   ├── config.py                          # App configs/env
│   │
│   ├── 📂 services/
│   │   ├── conversation/                  # Orchestration + streaming
│   │   │   ├── router.py                  # Route: text-only vs text+image
│   │   │   ├── streaming.py               # LLM token streaming logic
│   │   │   ├── session_manager.py         # Session state (Postgres + Redis) State persistence
│   │   │   └── orchestration.py           # Multi-source merging, LangChain orchestration (parallel flows)
│   │   │
│   │   ├── rag/                           # Retrieval Augmented Generation
│   │   │   ├── retriever.py               # Top-k chunk retriever w/ threshold
│   │   │   ├── embeddings.py              # Embedding generator
│   │   │   ├── vectorstore_pg.py          # pgvector impl
│   │   │   └── vectorstore_pinecone.py    # Pinecone production impl
│   │   │
│   │   ├── mcp/                           # MCP News Server
│   │   │   ├── server.py                  # MCP protocol server
│   │   │   ├── tools.py                   # query_news, get_latest
│   │   │   └── db_adapter.py              # News DB queries
│   │   │
│   │   ├── image_classifier/              # Gemini Flash image classifier
│   │   │   ├── model.py                   # Waste category classification
│   │   │   └── utils.py                   # Preprocessing + inference helpers
|   |   ├── websearch/                     #  async web search tools
│   |   |    └── search.py
│   │   │
│   │   ├── db/                            # Database access layer
│   │   │   ├── postgres.py                # Chat history + metadata
│   │   │   ├── redis_cache.py             # Hot context cache
│   │   │   └── migrations/                # SQL migrations
│   │   │
│   │   └── utils/                         # Shared helpers
│   │       ├── logger.py
│   │       ├── metrics.py                 # Latency, token streaming metrics
│   │       └── exceptions.py
│   │
│   ├── 📂 tests/
│   │   ├── test_rag.py
│   │   ├── test_mcp.py
│   │   ├── test_router.py
│   │   └── test_streaming.py
│   │
│   └── api/
│       ├── routes_chat.py                 # /chat endpoints
│       ├── routes_news.py                 # /news endpoints
│       ├── routes_classifier.py           # /classify-image
│       └── websocket.py                   # WebSocket / SSE streaming
│
├── 📂 frontend/                           # React / Vue app
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatApp.tsx
│   │   │   ├── StreamingOutput.tsx
│   │   │   └── ImageUpload.tsx
│   │   ├── services/api.ts                # API client
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   └── Chat.tsx
│   │   └── styles/
│   └── public/
│       └── index.html
│
└── 📂 infra/
    ├── Dockerfile.api                     # Backend image
    ├── Dockerfile.frontend                # Frontend image
    ├── k8s/                               # Kubernetes manifests
    │   ├── deployment-api.yaml
    │   ├── deployment-frontend.yaml
    │   ├── redis.yaml
    │   ├── postgres.yaml
    │   └── ingress.yaml
    ├── terraform/                         # Optional cloud IaC
    └── monitoring/
        ├── prometheus.yaml
        └── grafana_dashboards.json

```

