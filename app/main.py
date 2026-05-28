import uuid
import logging
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.models import SignalRequest, SignalResponse, HealthResponse
from app.redis_client import set_signal, get_signal, batch_get, is_connected
from app.sanitizer import sanitize_for_log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Trade Signal API", version="1.0.0")

REQUEST_COUNT = Counter(
    "trade_signal_requests_total",
    "Total requests by endpoint and status",
    ["endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "trade_signal_request_duration_seconds",
    "Request latency by endpoint",
    ["endpoint"]
)

CACHE_HITS = Counter("trade_signal_cache_hits_total", "Cache hits")
CACHE_MISSES = Counter("trade_signal_cache_misses_total", "Cache misses")


@app.post("/signals", response_model=SignalResponse)
async def create_signal(signal: SignalRequest):
    with REQUEST_LATENCY.labels(endpoint="/signals").time():
        signal_id = str(uuid.uuid4())
        payload = signal.model_dump()
        payload["timestamp"] = payload["timestamp"].isoformat()

        logger.info(f"Creating signal: {sanitize_for_log(payload)}")

        success = set_signal(signal_id, payload)
        if not success:
            REQUEST_COUNT.labels(endpoint="/signals", status="error").inc()
            raise HTTPException(status_code=503, detail="Cache write failed")

        REQUEST_COUNT.labels(endpoint="/signals", status="success").inc()
        return SignalResponse(signal_id=signal_id, cached=True, **signal.model_dump())


@app.get("/signals/{signal_id}", response_model=SignalResponse)
async def get_signal_by_id(signal_id: str):
    with REQUEST_LATENCY.labels(endpoint="/signals/{id}").time():
        data = get_signal(signal_id)

        if not data:
            CACHE_MISSES.inc()
            REQUEST_COUNT.labels(endpoint="/signals/{id}", status="miss").inc()
            raise HTTPException(status_code=404, detail="Signal not found or expired")

        CACHE_HITS.inc()
        REQUEST_COUNT.labels(endpoint="/signals/{id}", status="hit").inc()
        return SignalResponse(signal_id=signal_id, cached=True, **data)


@app.get("/signals/batch/lookup")
async def batch_lookup(ids: str):
    with REQUEST_LATENCY.labels(endpoint="/signals/batch").time():
        signal_ids = ids.split(",")
        results = batch_get(signal_ids)
        REQUEST_COUNT.labels(endpoint="/signals/batch", status="success").inc()
        return {"results": results, "count": len(results)}


@app.get("/health", response_model=HealthResponse)
async def health():
    redis_ok = is_connected()
    status = "healthy" if redis_ok else "degraded"
    REQUEST_COUNT.labels(endpoint="/health", status=status).inc()
    return HealthResponse(status=status, redis_connected=redis_ok)


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
