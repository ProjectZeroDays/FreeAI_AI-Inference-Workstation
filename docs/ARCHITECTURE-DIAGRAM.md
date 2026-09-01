# FreeAI Architecture Diagram

## System Overview

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Web[Next.js Website\n:3000]
        Dashboard[React Dashboard\n:8080]
        CLI[FreeAI CLI\nfreeai.py]
    end

    subgraph API["API Gateway Layer"]
        Flask[Flask Backend\n:5000]
        Router[Router API\n:8010]
        Campaign[Campaign API\n:8192]
    end

    subgraph Services["Service Layer"]
        Auth[Auth Service\nJWT/RBAC]
        Agents[Agent Registry]
        Skills[Skills Catalog\n299+ skills]
        MCP[MCP Servers]
        Browser[Knight-Shade Browser]
        RAG[RAG Sidecar\nQdrant]
    end

    subgraph AI["AI Provider Layer"]
        Agnes[Agnes API\nagnes-2.0-flash]
        Ollama[Ollama\nLocal Models]
        OpenAI[OpenAI API]
        Claude[Claude API]
    end

    subgraph Storage["Data Layer"]
        SQLite[(SQLite)]
        Redis[(Redis Cache)]
        FS[(File System)]
    end

    Web --> Flask
    Dashboard --> Flask
    CLI --> Router
    CLI --> Campaign
    
    Flask --> Auth
    Flask --> Agents
    Flask --> Skills
    Flask --> MCP
    Flask --> Browser
    Flask --> RAG
    
    Router --> Agnes
    Router --> Ollama
    Router --> OpenAI
    Router --> Claude
    
    Flask --> SQLite
    Flask --> Redis
    Flask --> FS
```

## Component Details

### Client Layer
- **Next.js Website** - Landing page, documentation, agent showcase
- **React Dashboard** - Main UI for FreeAI operations
- **CLI** - Command-line interface for automation

### API Gateway Layer
- **Flask Backend** - Main API server with 562+ endpoints
- **Router API** - LLM request routing with fallback chains
- **Campaign API** - Phishing campaign management

### Service Layer
- **Auth Service** - JWT authentication, RBAC, user management
- **Agent Registry** - 100+ specialized agents
- **Skills Catalog** - 299+ AI skills
- **MCP Servers** - Model Context Protocol integration
- **Knight-Shade Browser** - Stealth browser automation
- **RAG Sidecar** - Vector search with Qdrant

### AI Provider Layer
- **Agnes API** - Primary LLM provider
- **Ollama** - Local model inference
- **OpenAI/Claude** - Third-party providers

### Data Layer
- **SQLite** - Primary database
- **Redis** - Caching layer
- **File System** - Skill storage, configs, logs
