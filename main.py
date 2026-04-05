import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from repolister import lister

USERNAME = "Monkey-hmm"

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.get("/",response_class=HTMLResponse)
async def root():
    return await lister(USERNAME)


@app.get("/{repo}")
async def download_repo(repo: str):
    zip_url = f"https://github.com/{USERNAME}/{repo}/archive/refs/heads/main.zip"

    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(zip_url)

        if resp.status_code == 404:
            # try master branch as fallback
            zip_url_master = f"https://github.com/{USERNAME}/{repo}/archive/refs/heads/master.zip"
            resp = await client.get(zip_url_master)

        if resp.status_code != 200:
            raise HTTPException(status_code=404, detail=f"Could not download repo '{repo}'")

    return StreamingResponse(
        iter([resp.content]),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={repo}.zip"},
    )


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )