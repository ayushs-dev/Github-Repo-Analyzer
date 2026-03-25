# This is the entry point of the entire backend app.
# FastAPI is the web framework — it handles incoming HTTP requests and routes them
# to the right function. Think of it as the "front door" of the backend.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import repos  # the file that handles all /repos/... routes

# Create the FastAPI app instance with some metadata.
# This metadata shows up in the auto-generated API docs at /docs.
app = FastAPI(
    title="GitHub Repo Analyzer",
    description="Analyze any GitHub repo — stars, forks, contributors, languages",
    version="0.1.0",
)

# CORS = Cross-Origin Resource Sharing.
# Browsers block requests from one domain to another by default (a security feature).
# This middleware says "it's okay for our frontend (running on localhost:5173) to
# talk to this backend". Without this, the browser would refuse to load the data.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # the Vite dev server port
    allow_methods=["*"],   # allow GET, POST, etc.
    allow_headers=["*"],   # allow any headers
)

# Register our repos router — this plugs in all the /repos/... endpoints
# defined in routers/repos.py into the main app.
app.include_router(repos.router)


# A simple health-check endpoint.
# Useful for Docker/Kubernetes to ping and confirm the server is alive.
@app.get("/health")
async def health():
    return {"status": "ok"}
