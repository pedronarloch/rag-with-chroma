from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .router import api_router

app = FastAPI(title="Augmented Personal Finance Assistant Service")


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


app.include_router(api_router)
