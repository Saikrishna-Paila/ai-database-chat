<p align="center">
  <img src="https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/Emojis/Objects/Card%20File%20Box.png" alt="AI Database Chat" width="120"/>
</p>

<h1 align="center">AI Database Chat</h1>

<p align="center">
  <strong>Natural Language to SQL/MongoDB Query Engine with Smart Routing</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#tech-stack">Tech Stack</a>
</p>

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Chainlit](https://img.shields.io/badge/Chainlit-1.0+-FF6B6B?style=for-the-badge&logo=chainlit&logoColor=white)](https://chainlit.io)
[![Claude](https://img.shields.io/badge/Claude-API-CC785C?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-47A248?style=for-the-badge&logo=mongodb&logoColor=white)](https://mongodb.com)

[![Langfuse](https://img.shields.io/badge/Langfuse-Observability-4F46E5?style=for-the-badge)](https://langfuse.com)
[![MCP](https://img.shields.io/badge/MCP-Protocol-8B5CF6?style=for-the-badge)](https://modelcontextprotocol.io)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"/>
  <img src="https://img.shields.io/badge/Project-6%20of%2012-blue.svg?style=flat-square" alt="Project 6"/>
</p>

<br />

### Built With

<table>
<tr>
<td align="center" width="100">
<img src="https://avatars.githubusercontent.com/u/76263028?s=200&v=4" width="48" height="48" alt="Anthropic" />
<br /><b>Claude AI</b>
</td>
<td align="center" width="100">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="48" height="48" alt="Python" />
<br /><b>Python</b>
</td>
<td align="center" width="100">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" width="48" height="48" alt="PostgreSQL" />
<br /><b>PostgreSQL</b>
</td>
<td align="center" width="100">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/mongodb/mongodb-original.svg" width="48" height="48" alt="MongoDB" />
<br /><b>MongoDB</b>
</td>
<td align="center" width="100">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" width="48" height="48" alt="Docker" />
<br /><b>Docker</b>
</td>
</tr>
<tr>
<td align="center" width="100">
<img src="https://avatars.githubusercontent.com/u/117592510?s=200&v=4" width="48" height="48" alt="Langfuse" />
<br /><b>Langfuse</b>
</td>
<td align="center" width="100">
<img src="https://avatars.githubusercontent.com/u/182288589?s=200&v=4" width="48" height="48" alt="MCP" />
<br /><b>MCP</b>
</td>
<td align="center" width="100">
<img src="https://avatars.githubusercontent.com/u/128686189?s=200&v=4" width="48" height="48" alt="Chainlit" />
<br /><b>Chainlit</b>
</td>
<td align="center" width="100">
<img src="https://avatars.githubusercontent.com/u/21206976?s=200&v=4" width="48" height="48" alt="Pandas" />
<br /><b>Pandas</b>
</td>
<td align="center" width="100">
<img src="https://avatars.githubusercontent.com/u/6043126?s=200&v=4" width="48" height="48" alt="SQLAlchemy" />
<br /><b>SQLAlchemy</b>
</td>
</tr>
</table>

</div>

---

## Overview

An intelligent natural language interface for querying databases. Ask questions in plain English and get instant SQL or MongoDB queries with results. Supports both relational and document databases with smart keyword-based routing.

```
You: "What are the top 5 customers by total spending?"

AI: Generated SQL:
    SELECT c.name, SUM(o.total_amount) as total_spent
    FROM customers c
    JOIN orders o ON c.id = o.customer_id
    GROUP BY c.id, c.name
    ORDER BY total_spent DESC
    LIMIT 5

Results: 5 rows returned

| name           | total_spent |
|----------------|-------------|
| John Smith     | $12,450.00  |
| Sarah Johnson  | $9,875.50   |
| Mike Williams  | $8,320.00   |
| ...            | ...         |
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Natural Language Queries** | Ask questions in plain English about your data |
| **Multi-Database Support** | PostgreSQL (SQL) and MongoDB (NoSQL) in one interface |
| **Smart Query Routing** | Fast keyword-based routing to the right database |
| **Text-to-SQL Generation** | Converts natural language to optimized SQL queries |
| **Text-to-MongoDB** | Generates MongoDB find/aggregate pipelines |
| **Schema-Aware** | Uses database schema context for accurate queries |
| **LLM Observability** | Full tracing with Langfuse v3 for debugging |
| **MCP Architecture** | Model Context Protocol for clean database abstraction |
| **Real-time Chat UI** | Interactive Chainlit interface with markdown tables |
| **Query Safety** | Read-only queries with injection protection |

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────────────┐
│                         CHAINLIT FRONTEND                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐ │
│  │   Chat Input    │  │   Data Table    │  │      Query Display          │ │
│  │   (NL Query)    │  │   (Results)     │  │   (Generated SQL/MongoDB)   │ │
│  └────────┬────────┘  └────────▲────────┘  └──────────────▲──────────────┘ │
└───────────┼─────────────────────┼──────────────────────────┼────────────────┘
            │                     │                          │
            ▼                     │                          │
┌────────────────────────────────────────────────────────────────────────────┐
│                         DATABASE AGENT                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                        Query Processing Pipeline                      │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │  │
│  │  │  Fast Router │  │  LLM Query   │  │     Query Executor         │  │  │
│  │  │  (Keywords)  │  │  Generator   │  │     (MCP Tools)            │  │  │
│  │  └──────┬───────┘  └──────┬───────┘  └─────────────┬──────────────┘  │  │
│  └─────────┼─────────────────┼────────────────────────┼──────────────────┘  │
│            │                 │                        │                     │
│            ▼                 ▼                        ▼                     │
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────────┐    │
│  │  SQL Gen     │  │  MongoDB Gen     │  │      Langfuse Tracing      │    │
│  │  (Claude)    │  │  (Claude)        │  │      (Observability)       │    │
│  └──────────────┘  └──────────────────┘  └────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────────────┘
            │                                           │
            ▼                                           ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           MCP LAYER                                         │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐  │
│  │   PostgreSQL MCP Server     │  │      MongoDB MCP Server             │  │
│  │   • Schema introspection    │  │      • Collection discovery         │  │
│  │   • Query execution         │  │      • Find/Aggregate execution     │  │
│  │   • Result formatting       │  │      • Document sampling            │  │
│  └─────────────┬───────────────┘  └──────────────────┬──────────────────┘  │
└────────────────┼──────────────────────────────────────┼─────────────────────┘
                 │                                      │
                 ▼                                      ▼
┌────────────────────────────┐          ┌────────────────────────────────────┐
│      PostgreSQL            │          │           MongoDB                   │
│  ┌──────────────────────┐  │          │  ┌──────────────────────────────┐  │
│  │  customers           │  │          │  │  events                      │  │
│  │  orders              │  │          │  │  logs                        │  │
│  │  products            │  │          │  │  sessions                    │  │
│  │  order_items         │  │          │  │  analytics                   │  │
│  └──────────────────────┘  │          │  └──────────────────────────────┘  │
└────────────────────────────┘          └────────────────────────────────────┘
```

### Query Flow

```
1. USER INPUT           2. FAST ROUTING         3. QUERY GENERATION      4. EXECUTION & RESPONSE
─────────────────       ─────────────────       ─────────────────        ─────────────────
"Top customers by       Keyword match:          Claude generates         Execute via MCP,
 total spending"        "customers" →           optimized SQL with       return formatted
        │               PostgreSQL              JOINs & GROUP BY         results
        │                     │                        │                        │
        ▼                     ▼                        ▼                        ▼
   ┌─────────┐          ┌─────────┐            ┌─────────────┐          ┌─────────────┐
   │  Query  │ ───────► │  Route  │ ─────────► │   Generate  │ ───────► │   Results   │
   │         │          │ (No LLM)│            │  (1 LLM call)│          │   + Table   │
   └─────────┘          └─────────┘            └─────────────┘          └─────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **LLM** | Claude 3.5 Sonnet (Anthropic) | Natural language to query conversion |
| **Frontend** | Chainlit | Interactive chat interface |
| **SQL Database** | PostgreSQL 16 | Relational data storage |
| **NoSQL Database** | MongoDB 7 | Document data storage |
| **Observability** | Langfuse v3 | LLM tracing and monitoring |
| **Architecture** | MCP (Model Context Protocol) | Database abstraction layer |
| **Containerization** | Docker Compose | Database orchestration |
| **Data Display** | Pandas + Tabulate | Result formatting |

---

## Project Structure

```
06-ai-database-chat/
├── app.py                        # Chainlit frontend application
│
├── src/
│   ├── agent/                    # AI Agent Layer
│   │   ├── __init__.py
│   │   ├── database_agent.py     # Main orchestrator
│   │   ├── query_router.py       # Database routing logic
│   │   ├── sql_generator.py      # Text-to-SQL with Claude
│   │   └── mongo_generator.py    # Text-to-MongoDB with Claude
│   │
│   ├── mcp/                      # MCP Database Layer
│   │   ├── __init__.py
│   │   ├── manager.py            # MCP tool orchestrator
│   │   ├── postgres_server.py    # PostgreSQL MCP server
│   │   └── mongodb_server.py     # MongoDB MCP server
│   │
│   ├── observability/            # Monitoring Layer
│   │   ├── __init__.py
│   │   ├── langfuse_client.py    # Langfuse v3 integration
│   │   └── tracing.py            # Query tracing decorators
│   │
│   ├── visualization/            # Data Visualization
│   │   └── charts.py             # Auto chart generation
│   │
│   ├── config.py                 # Settings & environment
│   └── utils.py                  # Utility functions
│
├── docker/
│   ├── docker-compose.yml        # PostgreSQL + MongoDB setup
│   └── seed/                     # Sample data scripts
│       ├── postgres_seed.sql     # E-commerce sample data
│       └── mongo_seed.js         # Events/logs sample data
│
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Installation

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.11+ |
| Docker | 20+ |
| Anthropic API Key | Required |
| Langfuse Account | Optional (for observability) |

### Step 1: Navigate to Project

```bash
cd 06-ai-database-chat
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Anthropic API (Required)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# PostgreSQL (Docker default)
POSTGRES_HOST=localhost
POSTGRES_PORT=5438
POSTGRES_DB=ecommerce_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# MongoDB (Docker default)
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=ai_database_chat

# Langfuse (Optional - for observability)
LANGFUSE_SECRET_KEY=sk-lf-xxxxx
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxx
LANGFUSE_HOST=https://us.cloud.langfuse.com
```

### Step 5: Start Databases

```bash
cd docker
docker-compose up -d
```

### Step 6: Run Application

```bash
chainlit run app.py --port 8000
```

Open http://localhost:8000 in your browser.

---

## Usage

### Example Queries

#### PostgreSQL (E-commerce Data)

```
"Show me all customers"
"What are the top 10 products by revenue?"
"Which customers have spent the most money?"
"Count orders by status"
"What's the average order value?"
```

#### MongoDB (Events/Logs Data)

```
"Show recent user events"
"What are the most common event types?"
"Find all login events from today"
"Show me error logs"
```

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Show help message |
| `/schema` | Display database schema |
| `/clear` | Clear conversation history |

---

## How It Works

### Query Processing Pipeline

1. **User Input**: User types a natural language question
2. **Fast Routing**: Keyword-based routing (no LLM call) to select database
3. **Query Generation**: Claude converts natural language to SQL/MongoDB
4. **Safety Validation**: Checks for dangerous operations
5. **Execution**: Runs query through MCP client
6. **Response**: Returns formatted results as markdown table

### Smart Routing Keywords

| Database | Trigger Keywords |
|----------|-----------------|
| **PostgreSQL** | customers, orders, products, sales, revenue, purchases |
| **MongoDB** | events, logs, sessions, clicks, analytics, metrics |

### Safety Features

- Read-only queries only (no INSERT, UPDATE, DELETE)
- Blocked SQL keywords (DROP, TRUNCATE, etc.)
- Blocked MongoDB operators ($where, $function)
- Query timeout limits
- Row count limits (default: 100)

---

## Observability

### Langfuse Integration

All queries are traced with:
- Query routing decisions
- LLM generation calls
- Query execution time
- Success/failure scores

View traces at: https://cloud.langfuse.com

### Trace Structure

```
database_query (trace)
├── query_routing (span)
├── query_generation (span)
│   └── llm_call (generation)
└── query_execution (span)
```

---

## Sample Data

### PostgreSQL Tables

| Table | Description | Sample Size |
|-------|-------------|-------------|
| `customers` | Customer information | 100 records |
| `products` | Product catalog | 50 records |
| `orders` | Order headers | 500 records |
| `order_items` | Order line items | 1500 records |

### MongoDB Collections

| Collection | Description | Sample Size |
|------------|-------------|-------------|
| `events` | User activity events | 1000 documents |
| `logs` | Application logs | 500 documents |
| `sessions` | User sessions | 200 documents |

---

## Troubleshooting

### Database Connection Issues

```bash
# Check if databases are running
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs
```

### Common Errors

| Error | Solution |
|-------|----------|
| "PostgreSQL not connected" | Check Docker and env variables |
| "MongoDB not connected" | Check Docker and env variables |
| "Query contains blocked keyword" | Use SELECT queries only |
| "Failed to generate query" | Rephrase your question |

---

## Roadmap

- [ ] Query result caching
- [ ] Multi-turn conversation context
- [ ] Chart visualization (Plotly)
- [ ] Export results to CSV/Excel
- [ ] Query history and favorites
- [ ] Support for MySQL/SQLite
- [ ] Query optimization suggestions

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### Built with using

[![Anthropic](https://img.shields.io/badge/Anthropic-Claude_AI-CC785C?style=flat-square&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Chainlit](https://img.shields.io/badge/Chainlit-FF6B6B?style=flat-square)](https://chainlit.io)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white)](https://mongodb.com)
[![Langfuse](https://img.shields.io/badge/Langfuse-4F46E5?style=flat-square)](https://langfuse.com)

<br />

**Built with love by Saikrishna**

<sub>Project 6 of <a href="../README.md">12 AI Projects for 2025</a></sub>

</div>
