# PokéPipeline

A production-ready ETL pipeline that fetches Pokémon data from the PokeAPI, transforms it with enrichment and validation, and loads it into PostgreSQL. Includes an optional GraphQL API for querying the loaded data.

## Architecture

```
Extract → Transform → Quality Check → Load
   ↓           ↓            ↓          ↓
PokeAPI    Normalize    Validate   PostgreSQL
   ↓           ↓            ↓          ↓
async      Enrich      Drop bad   Idempotent
HTTP       DTOs        records     UPSERTs
```

The pipeline is organized into modular layers:
- **extract/**: Async HTTP client with rate limiting and retries
- **transform/**: Data mapping, normalization, and enrichment (BST, bulk index)
- **quality/**: Validation checks to filter invalid records
- **load/**: Idempotent database operations with schema auto-creation
- **orchestrator/**: Coordinates the ETL pipeline with logging and metrics

## Tech Stack

- **Python 3.11+** with type hints
- **SQLAlchemy 2.x** for ORM and migrations
- **Typer** for CLI interface
- **httpx** for async HTTP requests
- **PostgreSQL** for data storage
- **Pydantic v2** for data validation
- **Strawberry** + **FastAPI** for GraphQL API
- **Docker** for containerization

## Setup & Run

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Docker (optional)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd PokePipeline

# Install dependencies
make install
# or
pip install -e .[dev]

# Configure environment (optional)
cp .env.example .env
```

### Run the Pipeline

**Using CLI:**
```bash
# Start PostgreSQL
docker run -d --name poke-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=poke -p 5432:5432 postgres:15-alpine

# Run pipeline
make run
# or
python -m pokepipeline.cli --limit 20
```

**Using Docker:**
```bash
make docker-up
```

### GraphQL API (Optional)

```bash
# Install GraphQL dependencies
pip install -r requirements-graphql.txt

# Set database URL (PowerShell)
$env:DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/poke"

# Run the API
python scripts/graphql_min.py
```

Access GraphiQL at http://localhost:8001/graphql

### Development

```bash
# Run tests
make test

# Format and lint
make fmt
make lint
```

## Key Design Choices

- **Modular Architecture**: Clean separation of extract, transform, quality, and load layers
- **Type Safety**: Full type hints with Pydantic DTOs and SQLAlchemy ORM models
- **Async I/O**: Concurrent API requests with rate limiting and timeout handling
- **Idempotent Operations**: PostgreSQL UPSERTs ensure safe re-runs without duplicates
- **Quality Gates**: Validation checks to drop incomplete or invalid records
- **Structured Logging**: JSON logging with metrics for observability
- **Schema Evolution**: Auto-creates missing tables on first run

## Example Output

After running the pipeline, verify the loaded data:

**Via PostgreSQL:**
```sql
SELECT name, base_stat_total, bulk_index 
FROM pokemon 
ORDER BY base_stat_total DESC 
LIMIT 5;
```

**Via GraphQL:**
```graphql
query {
  pokemons(limit: 10, order_by: "base_stat_total", desc_order: true) {
    id
    name
    base_stat_total
    bulk_index
    height_m
    weight_kg
  }
}
```

 

