from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.upload import router as upload_router

app = FastAPI(
    title="Gerador XML - Prefeitura de Caieiras",
    description="Motor automático de processamento e faturamento de NFS-e (Caieiras)",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "*"  # To be restricted in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api", tags=["Lote XML Upload"])

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Backend operando normalmente."}

