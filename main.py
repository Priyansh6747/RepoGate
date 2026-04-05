import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from repolister import lister
from utils import list_public_repos

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


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    ua = request.headers.get("user-agent", "").lower()
    if "curl" in ua or "wget" in ua or "httpie" in ua:
        repos = list_public_repos(USERNAME)
        lines = [f"{USERNAME}'s repositories ({len(repos)} total)", ""]
        for r in repos:
            lang = r['language'] or 'unknown'
            desc = r['description'] or 'No description'
            lines.append(f"  {r['name']:<40} [{lang}]")
            lines.append(f"    {desc}")
            lines.append(f"    curl {request.base_url}{r['name']}  →  downloads {r['name']}.zip")
            lines.append("")
        return PlainTextResponse("\n".join(lines))
    return await lister(USERNAME)


async def _stream_zip(url: str):
    async with httpx.AsyncClient(follow_redirects=True, timeout=60) as client:
        async with client.stream("GET", url) as resp:
            async for chunk in resp.aiter_bytes(65536):
                yield chunk


@app.get("/{repo}")
async def download_repo(repo: str, request: Request):
    for branch in ("main", "master"):
        zip_url = f"https://github.com/{USERNAME}/{repo}/archive/refs/heads/{branch}.zip"
        # probe HEAD first to avoid downloading just to check status
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            probe = await client.head(zip_url)
        if probe.status_code == 200:
            return StreamingResponse(
                _stream_zip(zip_url),
                media_type="application/zip",
                headers={"Content-Disposition": f"attachment; filename={repo}.zip"},
            )

    raise HTTPException(status_code=404, detail=f"Repo '{repo}' not found or has no main/master branch")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
    )