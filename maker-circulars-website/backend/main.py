import os
import sys

# Ensure the parent directory is in the Python path so that
# 'backend' can be imported as a package when running from the backend/ directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base, UPLOADS_DIR
from backend.api import datasets, records, makers, columns, stats, import_api

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Maker Circulars API",
    description="API for managing maker circular documents imported from Excel",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

app.include_router(import_api.router)
app.include_router(datasets.router)
app.include_router(records.router)
app.include_router(makers.router)
app.include_router(columns.router)
app.include_router(stats.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Maker Circulars API is running"}

# Serve frontend build if present
dist_dir = os.path.join(parent_dir, "frontend", "dist")
if os.path.isdir(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="frontend_dist")



def main():
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True, app_dir=parent_dir)


if __name__ == "__main__":
    main()


