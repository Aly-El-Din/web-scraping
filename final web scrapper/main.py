from router import router_scrap
from fastapi import FastAPI
app = FastAPI()
app.include_router(router_scrap.router, prefix="/api")

