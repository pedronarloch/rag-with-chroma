# RAG with ChromaDB - Brazilian Asset Investment Intelligence

A multi-agentic AI system powered by Retrieval Augmented Generation (RAG) to augment and analyze data for asset investing in Brazil, with a focus on stocks and REITs.

## Overview

This project combines ChromaDB vector database with LlamaIndex and OpenAI embeddings to create an intelligent data augmentation system for Brazilian financial assets. The system ingests, processes, and semantically searches investment profiles to provide context-aware insights for stock and REIT analysis.

## Key Features

- **Vector-based Semantic Search**: Leverages ChromaDB for efficient similarity search across investment profiles
- **RAG Pipeline**: Uses LlamaIndex to streamline retrieval and generation workflows
- **Multi-Agentic Architecture**: Designed to support multiple AI agents for different investment analysis tasks
- **OpenAI Embeddings**: Utilizes `text-embedding-3-small` for high-quality vector representations
- **RESTful API**: FastAPI-based endpoints for easy integration

## Technology Stack

- **Vector Database**: ChromaDB
- **RAG Framework**: LlamaIndex
- **Embeddings**: OpenAI (text-embedding-3-small)
- **API Framework**: FastAPI
- **Container**: Docker & Docker Compose
- **Language**: Python 3.11+


## Prerequisites

- Docker & Docker Compose
- OpenAI API Key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-with-chroma
```

2. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

3. Configure your environment variables in `.env`:
```env
CHROMA_HOST=localhost
CHROMA_PORT=8000
CHROMA_PERSIST_DIR=/data
CHROMA_COLLECTION=profiles_v1

APP_PORT=8001

OPENAI_API_KEY=your-openai-api-key-here
EMBEDDING_PROVIDER=openai
```

4. Build and start the services:
```bash
docker compose up --build
```

## Usage

### Health Check

Verify the services are running:
```bash
curl http://localhost:8001/health
```

### Initialize Collection

Create or reset the ChromaDB collection:
```bash
curl -X POST http://localhost:8001/init
```

### API Documentation

Access the interactive Swagger documentation at:
```
http://localhost:8001/docs
```

## Development

### Local Development Setup

For local development outside Docker:

1. Install dependencies using `uv`:
```bash
uv sync
```

2. Run ChromaDB separately:
```bash
docker compose up chroma
```

3. Update `.env` with `CHROMA_HOST=localhost`

4. Run the FastAPI app:
```bash
uvicorn app.src.services.api.main:app --reload --port 8001
```

### Adding New Features

This project is designed to support multi-agentic workflows. Future enhancements may include:
- Agent for fundamental analysis of Brazilian stocks
- Agent for REIT market analysis
- Agent for portfolio optimization
- Agent for sentiment analysis of Brazilian financial news

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `CHROMA_HOST` | ChromaDB hostname | `localhost` |
| `CHROMA_PORT` | ChromaDB port | `8000` |
| `CHROMA_PERSIST_DIR` | Data persistence directory | `/data` |
| `CHROMA_COLLECTION` | Collection name | `profiles_v1` |
| `APP_PORT` | FastAPI application port | `8001` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `EMBEDDING_PROVIDER` | Embedding provider | `openai` |

## Troubleshooting

### Internal Server Error on /init

If you get an internal server error when calling the `/init` endpoint, ensure:
1. The `CHROMA_COLLECTION` environment variable is set in docker-compose.yml
2. ChromaDB service is healthy (check `/health` endpoint)
3. Environment variables are properly loaded

### Connection Refused

If the app can't connect to ChromaDB:
- Ensure ChromaDB container is running: `docker ps`
- Check ChromaDB logs: `docker logs chroma`
- Verify `CHROMA_HOST=chroma` in the app service environment
