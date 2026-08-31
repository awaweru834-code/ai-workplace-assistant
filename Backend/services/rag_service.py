import os
import uuid
from io import BytesIO
from typing import List  # noqa: UP035

import PyPDF2
from pinecone import Pinecone

EMBEDDING_MODEL     = "multilingual-e5-large"
RELEVANCE_THRESHOLD = 0.60
TOP_K               = 5

def _get_index():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "hr-policies")
    return pc.Index(index_name)

def _embed(text: str) -> List[float]:  # noqa: UP006
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    result = pc.inference.embed(
        model=EMBEDDING_MODEL,
        inputs=[text],
        parameters={"input_type": "query"},
    )
    return result[0].values

def run_rag_query(user_message: str) -> str:
    """Embeds query and returns raw context from Pinecone."""
    query_vector = _embed(user_message)
    index = _get_index()
    results = index.query(vector=query_vector, top_k=TOP_K, include_metadata=True)

    context_parts = []
    for match in results.matches:
        if match.score >= RELEVANCE_THRESHOLD:
            text = match.metadata.get("text", "").strip()
            source = match.metadata.get("source", "HR Document")
            context_parts.append(f"[Source: {source}]\n{text}")

    context = "\n\n---\n\n".join(context_parts) if context_parts \
              else "No sufficiently relevant HR documents were found."

    return context
def ingest_pdf(file_bytes: bytes, filename: str):
    text = "".join(p.extract_text() for p in PyPDF2.PdfReader(BytesIO(file_bytes)).pages)
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    vectors = [{"id": str(uuid.uuid4()), "values": _embed(c), "metadata": {"text": c, "source": filename}} for c in chunks if c.strip()]
    _get_index().upsert(vectors)