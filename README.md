# PokéPipeline

A data pipeline for fetching, transforming, and loading Pokémon data from the PokeAPI into a PostgreSQL database.

## Quickstart

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd PokePipeline

# Install dependencies
make install
# or
pip install -e .

# Copy environment file
cp .env.example .env
```

### Environment Configuration

Edit `.env` to customize settings:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/poke
HTTP_CONCURRENCY=5
RATE_LIMIT_PER_SEC=4
TARGET_LIMIT=20
ENABLE_EVOLUTION=false
```

### Running the Pipeline

**Option 1: Using Docker (Recommended)**
```bash
make docker-up
```

**Option 2: Using CLI (requires PostgreSQL running)**
```bash
# Start PostgreSQL first
docker run -d --name poke-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=poke -p 5432:5432 postgres:15-alpine

# Run the pipeline
make run
# or
python -m pokepipeline.cli run
```

### Development

```bash
# Run tests
make test
```

---

# **Coding Challenge: Build a PokéPipeline**

Welcome, future innovator\! At Aventa, we frequently build data pipelines for our clients in the insurance sector. This often involves fetching data from various sources (like REST APIs), transforming it, and loading it into different systems (like databases or exposing it via GraphQL). This challenge is designed to see your approach to such tasks.

# **Project Mission:**

Your core task is to design and build a data pipeline that fetches data about Pokémon from the public PokeAPI (pokeapi.co), transforms this data in a meaningful way, and stores it in a SQL database.

This is an open-ended challenge. We're interested in seeing how you approach the problem and the choices you make. You can decide on the complexity and scope of your solution.

# **Core Requirements:**

1. Data Extraction: Fetch data for at least 10-20 Pokémon from the PokeAPI. You can choose which specific data points you want to extract (e.g., name, types, abilities, stats, evolution chain, etc.).  
2. Data Transformation & Mapping: This is a key part\! Transform the raw data from the API into a more structured format suitable for a relational database. Think about how you would map the often nested and varied API responses to your chosen database schema. Document your mapping decisions.  
3. Data Loading: Store the transformed Pokémon data in a SQL database of your choice (e.g., SQLite, PostgreSQL). You'll need to define the database schema.  
4. README.md: This is mandatory. Your README.md file should include:  
   1. A clear description of your project.  
   2. Instructions on how to set up and run your solution.  
   3. An explanation of your design choices, especially regarding data transformation, mapping, and database schema.  
   4. Any assumptions you made.  
   5. A brief discussion of potential improvements or features you'd add if you had more time.

