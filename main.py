import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.utils import env_config as config
from app.utils.logger_init import init_logger

from app.endpoints import adaptor

logger = init_logger(__name__)

@asynccontextmanager
async def lifespan(_):
    """
    Application lifespan context manager.
    This is called when the application starts and stops.
    """
    logger.info(".........................................................")
    logger.info(".................Starting server.........................")
    config.print_config(logger)
    yield
    logger.info("...............Shutting down server......................")

app = FastAPI(
    title=config.PROJECT_NAME,
    description="TRD Adaptor API",
    version=config.PROJECT_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, adjust as needed
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods, adjust as needed
    allow_headers=["*"],  # Allows all headers, adjust as needed
)

app.include_router(adaptor.router, prefix="/adaptor", tags=["adaptor"])


if __name__ == "__main__":

    uvicorn.run("main:app", 
                host=config.HOST, 
                port=config.PORT,
                reload=True,
                ssl_keyfile=config.SSL_KEYFILE,
                ssl_certfile=config.SSL_CERTFILE)