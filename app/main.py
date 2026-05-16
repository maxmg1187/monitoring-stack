from fastapi import FastAPI
from prometheus_client import Gauge, make_asgi_app
import psutil

app = FastAPI()
# adding comment here to check ci/cd works finally
# Define metrics
CPU_USAGE = Gauge("cpu_usage_percent", "Current CPU usage percentage")
MEMORY_USAGE = Gauge("memory_usage_percent", "Current memory usage percentage")
DISK_USAGE = Gauge("disk_usage_percent", "Current disk usage percentage")

def collect_metrics():
    CPU_USAGE.set(psutil.cpu_percent(interval=1))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    DISK_USAGE.set(psutil.disk_usage("/").percent)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics-check")
def metrics_check():
    collect_metrics()
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
    }

# Mount the Prometheus metrics endpoint
metrics_app = make_asgi_app()

@app.middleware("http")
async def collect_before_metrics(request, call_next):
    if request.url.path == "/metrics":
        collect_metrics()
    return await call_next(request)

app.mount("/metrics", metrics_app)
