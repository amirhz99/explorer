import uvicorn
from src.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        reload=True,
        host=settings.HOST,
        port=settings.PORT,
        # workers=settings.WORKERS,
        # log_level="info"
        # ssl_keyfile="##############",
        # ssl_certfile="##############",
    )
