import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from fastapi.middleware.cors import CORSMiddleware
from routers import process_step_file

# from utils.helper_func import execute_query

app = FastAPI()

app.include_router(process_step_file.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")


# Default route handler for the root URL
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app!"}


# server Exposure
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8015)