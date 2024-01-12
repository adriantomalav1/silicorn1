from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from conf.router import router
from app.tasks.MessagesTasks import *
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

async def start_periodic_job():
    await asyncio.sleep(3)
    asyncio.create_task(jobs())

app.add_event_handler("startup", start_periodic_job)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
