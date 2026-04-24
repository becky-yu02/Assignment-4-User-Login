from contextlib import asynccontextmanager

from typing import Annotated

from fastapi import FastAPI, APIRouter, HTTPException, Path
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from reservation_routes import reservation_router
from auth_routes import auth_router
from reservation_db import init

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init()
    yield


app = FastAPI(title="Dance Studio Reservations", lifespan=lifespan)


@app.get("/")
async def home():
    return FileResponse("./frontend/index.html")


app.include_router(reservation_router, tags=["Reservations"], prefix="/Reservations")

app.include_router(auth_router, tags=["Auth"], prefix="/auth")

app.mount("/", StaticFiles(directory="frontend"), name="static")
