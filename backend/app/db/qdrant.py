from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.core.config import settings

qdrant_client: QdrantClient | None = None

def get_qdrant() -> QdrantClient | None:
    global qdrant_client
    if qdrant_client:
        return qdrant_client
    try:
        if settings.QDRANT_API_KEY:
            qdrant_client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY, timeout=5)
        else:
            qdrant_client = QdrantClient(url=settings.QDRANT_URL, timeout=5)
        # ensure collection
        try:
            qdrant_client.get_collection(settings.QDRANT_COLLECTION)
        except Exception:
            qdrant_client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
            )
        return qdrant_client
    except Exception as e:
        print(f"Qdrant not available: {e}")
        return None
