from fastapi import FastAPI
from app.api.api_v1.endpoints.routers import router

app = FastAPI()
app.include_router(router=router, prefix="")
