from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import sys
import pyprojroot
root = pyprojroot.find_root(pyprojroot.has_dir("config"))
sys.path.append(str(root))

from config import settings, logger

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Allow requests from these origins
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all types of HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers in requests
)

from src.api import chat_api

app.include_router(chat_api.router)


@app.get(
    path="/",
    response_description="Root endpoint is accessed successfully",
    summary="Root endpoint",
    description="Root endpoint of the API service"
)
async def home():
    return {"Service Name": settings.APP_NAME, "Version": settings.VERSION}


@app.get(
    path="/error",
    response_description="Error endpoint is accessed successfully",
    summary="Error endpoint",
    description="Error endpoint of the API service"
)
async def error():
    try:
        1 / 0
    except ZeroDivisionError as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": "An internal error occurred."}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)