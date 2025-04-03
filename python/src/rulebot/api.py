from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import numpy as np
from contextlib import asynccontextmanager

from .auth import get_api_key
from .rag_pipeline import RagPipeline
from .config import ApiConfig


class QueryRequest(BaseModel):
    gpt_model: str
    embedder_model_name: str
    embedding_dim: int
    top_k_chunks: int
    top_k_rules: int
    top_k_situations: int
    threshold: float
    situation_threshold: float
    question: str
    temperature: float
    max_length: int


class QueryResponse(BaseModel):
    answer: str
    prompt: str
    retrieved_all_rules: list
    retrieved_top_rules: list
    retrieved_situations: list

def convert_np_floats(item):
    """
    Rekursive Funktion zur Umwandlung von numpy.float32/float64 in native Python-Floats.
    """
    if isinstance(item, dict):
        return {k: convert_np_floats(v) for k, v in item.items()}
    elif isinstance(item, list):
        return [convert_np_floats(x) for x in item]
    elif isinstance(item, (np.float32, np.float64)):
        return float(item)
    else:
        return item

@asynccontextmanager
async def lifespan(app: FastAPI):
    # initialize pipeline and store in app.state
    pipeline_instance = RagPipeline(
            openai_api_key="",
            embedder_model_name=ApiConfig["embedder_model_name"],
            embedding_dim=ApiConfig["embedding_dim"],
            top_k_chunks=ApiConfig["top_k_chunks"],
            top_k_rules=ApiConfig["top_k_rules"],
            top_k_situations=ApiConfig["top_k_situations"],
            threshold=ApiConfig["threshold"],
            situation_threshold=ApiConfig["situation_threshold"],
            model=ApiConfig["model"],
            temperature=ApiConfig["temperature"],
            max_length=ApiConfig["max_length"],
            index_path=ApiConfig["index_path"],
            mapping_path=ApiConfig["chunk_mapping_path"],
            casebook_index_path=ApiConfig["casebook_index_path"],
            casebook_mapping_path=ApiConfig["casebook_chunk_mapping_path"],
        )

    # persistently save pipeline
    app.state.pipeline_instance = pipeline_instance
    print("Pipeline (Index und Mapping) was loaded successfully.")
    yield

app = FastAPI(title="Ice Hockey Rule Assistant API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://rulebot.kennethenglisch.de", "http://rulebot.kennethenglisch.de"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask", response_model=QueryResponse)
async def ask_question(query: QueryRequest, api_key: str = Depends(get_api_key)):
    """
    Verarbeitet die USER_QUESTION unter Verwendung der GptRagPipeline.
    Der API-Schlüssel wird sicher über einen HTTP-Header übergeben (via get_api_key).
    """
    try:
        # getting pipeline instance and overwrite the parameters from request
        pipeline = app.state.pipeline_instance

        pipeline._openai_api_key = api_key
        pipeline._embedder_model_name = query.embedder_model_name
        pipeline._embedding_dim = query.embedding_dim
        pipeline.top_k_chunks = query.top_k_chunks
        pipeline._top_k_rules = query.top_k_rules
        pipeline._top_k_situations = query.top_k_situations
        pipeline._threshold = query.threshold
        pipeline._situation_threshold = query.situation_threshold
        pipeline._model_name = query.gpt_model
        pipeline._temperature = query.temperature
        pipeline._max_length = query.max_length

        answer, prompt, retrieved_all_rules, retrieved_top_rules, retrieved_situations = pipeline.process_query(query.question)

        print(prompt)

        return QueryResponse(
            answer=convert_np_floats(answer),
            prompt=convert_np_floats(prompt),
            retrieved_all_rules=convert_np_floats(retrieved_all_rules),
            retrieved_top_rules=convert_np_floats(retrieved_top_rules),
            retrieved_situations=convert_np_floats(retrieved_situations),
        )
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
