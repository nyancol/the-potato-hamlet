from potato_pyserver.database import engine
from potato_pyserver.models import reset_tables
from potato_pyserver.routers import users, hamlets, households, world_items

import logging
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse



reset_tables(engine)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(users.router)
app.include_router(hamlets.router)
app.include_router(households.router)
app.include_router(world_items.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)
