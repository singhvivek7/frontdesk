from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from app.db import get_db, StatusEnum
from app.db import Queries
import time
import uuid


def addQuery(question: str):
    db = next(get_db())
    query = Queries(
        id=str(uuid.uuid4()),
        query=question,
        status=StatusEnum.UNRESOLVED,
        created_at=int(time.time()),
        updated_at=int(time.time()),
    )
    db.add(query)
    db.commit()
    db.refresh(query)
    return query


def solveQuery(query_id: str, answer: str):
    db = next(get_db())
    query = db.query(Queries).filter(Queries.id == query_id).first()
    if not query:
        return None
    query.status = StatusEnum.RESOLVED
    query.response = answer
    query.updated_at = int(time.time())
    db.commit()
    db.refresh(query)
    return query


def getQuery(query_id: str):
    db = next(get_db())
    query = db.query(Queries).filter(Queries.id == query_id).first()
    if not query:
        return None
    return query


app = FastAPI(
    title="LiveKit Agent API",
    description="API for LiveKit Agent",
    version="0.1.0",
    openapi_tags=[
        {
            "name": "queries",
            "description": "Queries management",
        },
    ],
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/queries",
    tags=["queries"],
    summary="Get all queries",
)
async def get_all_queries(status: str = None):
    db = next(get_db())
    queries = db.query(Queries)
    if status:
        queries = queries.filter(Queries.status == status)
    queries = queries.all()
    return queries


@app.patch(
    "/queries/{query_id}",
    tags=["queries"],
    summary="Update a query",
)
async def update_query(
    query_id: str,
    body=Body({"answer": "This is the answer to the query."}),
):
    db = next(get_db())
    query = db.query(Queries).filter(Queries.id == query_id).first()
    if not query:
        return {"error": "Query not found"}
    query.response = body["answer"]
    query.status = StatusEnum.RESOLVED
    db.commit()
    db.refresh(query)

    # IMP: call the webhook here
    print(f"Query {query.id} updated with answer: {query.response}")
    return query
