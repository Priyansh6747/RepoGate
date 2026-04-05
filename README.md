# RepoGate 🚪

A nice way to download zipped GitHub repos. Why? I don't know, just for fun! 🤷‍♂️🎉

## What is this?
RepoGate provides a clean, visual web portal displaying your public GitHub repositories. Instead of funneling you off to GitHub, clicking on any repository card will **instantly download a zip archive** of that repository!

## How to use
1. Run the FastAPI server:
   ```bash
   uv run main.py
   ```
2. Open your browser to `http://127.0.0.1:8000/`.
3. Enjoy the neatly sorted, visually satisfying grid of repos.
4. Click anything to grab that sweet `.zip` file of the source code.

## Tech Stack
- **FastAPI** – Super-fast Python web framework
- **httpx** – Async HTTP client (for fetching those zips)
- **Vanilla JS/CSS** – The front-end is rendered natively over HTML responses

Have fun clicking and downloading!
