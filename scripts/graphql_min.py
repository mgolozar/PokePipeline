# scripts/graphql_min.py
import os
from typing import Optional, List

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from sqlalchemy import create_engine, text

# === super simple DB engine (sync) ===
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres",
)
engine = create_engine(DATABASE_URL, future=True)

# === GraphQL types ===
@strawberry.type
class GPokemon:
    id: int
    name: str
    height: int
    weight: int
    base_experience: int
    height_m: float
    weight_kg: float
    base_stat_total: int
    bulk_index: float

# === tiny helpers ===
_WHITELIST_ORDER = {
    "id": "id",
    "name": "name",
    "base_stat_total": "base_stat_total",
    "bulk_index": "bulk_index",
    "height_m": "height_m",
    "weight_kg": "weight_kg",
}

def _row_to_gpokemon(row) -> GPokemon:
    return GPokemon(
        id=row["id"],
        name=row["name"],
        height=row["height"],
        weight=row["weight"],
        base_experience=row["base_experience"],
        height_m=float(row.get("height_m") or 0),
        weight_kg=float(row.get("weight_kg") or 0),
        base_stat_total=int(row.get("base_stat_total") or 0),
        bulk_index=float(row.get("bulk_index") or 0),
    )

# === resolvers ===
@strawberry.type
class Query:
    @strawberry.field
    def pokemon(self, id: int) -> Optional[GPokemon]:
        sql = text("""
            SELECT id, name, height, weight, base_experience,
                   height_m, weight_kg, base_stat_total, bulk_index
            FROM pokemon
            WHERE id = :id
            LIMIT 1
        """)
        with engine.connect() as conn:
            res = conn.execute(sql, {"id": id}).mappings().first()
        return _row_to_gpokemon(res) if res else None

    @strawberry.field
    def pokemons(
        self,
        limit: int = 20,
        offset: int = 0,
        name_contains: Optional[str] = None,
        min_base_stat_total: Optional[int] = None,
        order_by: str = "id",
        desc_order: bool = False,
    ) -> List[GPokemon]:
        order_col = _WHITELIST_ORDER.get(order_by, "id")
        direction = "DESC" if desc_order else "ASC"

        where = []
        params = {"limit": limit, "offset": offset}
        if name_contains:
            where.append("name ILIKE :name_like")
            params["name_like"] = f"%{name_contains}%"
        if min_base_stat_total is not None:
            where.append("base_stat_total >= :min_bst")
            params["min_bst"] = min_base_stat_total

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""
        sql = text(f"""
            SELECT id, name, height, weight, base_experience,
                   height_m, weight_kg, base_stat_total, bulk_index
            FROM pokemon
            {where_sql}
            ORDER BY {order_col} {direction}
            LIMIT :limit OFFSET :offset
        """)

        with engine.connect() as conn:
            rows = conn.execute(sql, params).mappings().all()
        return [_row_to_gpokemon(r) for r in rows]

schema = strawberry.Schema(query=Query)

# === FastAPI app with GraphiQL ===
app = FastAPI(title="GraphQL-Min")
app.include_router(GraphQLRouter(schema, graphql_ide="graphiql"), prefix="/graphql")

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Use port 8001 if 8000 is busy
    port = 8001
    
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    print(f"Starting GraphQL server on http://0.0.0.0:{port}")
    print(f"Access GraphiQL at: http://localhost:{port}/graphql")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
