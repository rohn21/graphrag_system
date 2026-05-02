import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from extract import extract_from_folder
from graph_db import load_graph, get_full_graph, get_driver, clear_graph
from rag import query_graph
from config import setup_logging, validate_config

# Initialize logging and config
setup_logging()
validate_config()
logger = logging.getLogger(__name__)

app = FastAPI()

# Allow requests from the React frontend running on port 5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.post("/api/ingest")
async def ingest_documents():
    try:
        logger.info("Starting ingestion...")
        data = extract_from_folder("./documents")

        if not data["entities"]:
            return {"status": "warning", "message": "No entities extracted. Check your documents folder."}

        driver = get_driver()
        clear_graph(driver)
        driver.close()

        load_graph(data)

        return {
            "status": "success",
            "entities": len(data["entities"]),
            "relationships": len(data["relationships"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query")
async def query(request: QueryRequest):
    try:
        answer = query_graph(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/graph")
async def get_graph():
    try:
        driver = get_driver()
        graph = get_full_graph(driver)
        driver.close()
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}