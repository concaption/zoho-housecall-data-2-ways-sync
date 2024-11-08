#!/usr/bin/env python
import logging
import colorlog
import sys
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from config import settings

from api.housecall.incoming import router as hcp_customers_router
from api.zoho.incoming import router as zoho_estimate_router
from api.zoho.authenticate import router as zoho_authenticate_router
from api.zoho.deals import router as zoho_deals_router

def configure_logging():
    """
    Configure logging for the application
    """
    # Create a root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    if not root_logger.handlers:
        # Create a formatter for formatting log messages
        formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            log_colors={
                'DEBUG':    'cyan',
                'INFO':     'green',
                'WARNING':  'yellow',
                'ERROR':    'red',
                'CRITICAL': 'red,bg_white',
            }
        )

        # Create a handler for logging to stdout
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        # Add the handlers to the root logger
        root_logger.addHandler(stream_handler)


configure_logging()


def include_router(app, router):
    app.include_router(router)

def start_application():
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app, hcp_customers_router)
    include_router(app, zoho_estimate_router)
    include_router(app, zoho_authenticate_router)
    include_router(app, zoho_deals_router)
    return app

app = start_application()


@app.get("/")
def home():
    # redirect to docs
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
