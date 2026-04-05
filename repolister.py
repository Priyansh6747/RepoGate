from fastapi import Query
from utils import list_public_repos



async def lister(username: str = Query(..., description="GitHub username")):
    repos = list_public_repos(username)

    def build_topics(topics):
        return "".join(f'<span class="topic">{t}</span>' for t in (topics or []))

    def build_repo_card(repo):
        topics_html = build_topics(repo["topics"])
        license_text = repo["license"] or "No license"
        desc = repo["description"] or "No description provided."
        lang = repo["language"] or "Unknown"
        updated = repo["updated_at"][:10]
        fork_tag = '<span class="fork-tag">Fork</span>' if repo["is_fork"] else ""

        return f"""
        <div class="card">
            <div class="card-top">
                <a class="repo-name" href="/{repo['name']}" target="_blank">{repo['name']}</a>
                <span class="vis-badge">{repo['visibility']}</span>
            </div>
            <p class="desc">{desc}</p>
            <div class="topics">{topics_html}</div>
            <div class="stats">
                <span>⭐ {repo['stars']}</span>
                <span>🍴 {repo['forks']}</span>
                <span>👁 {repo['watchers']}</span>
                <span>⚠️ {repo['open_issues']}</span>
                <span>💾 {repo['size_kb']} KB</span>
            </div>
            <div class="meta">
                <span class="lang-dot">{lang}</span>
                <span>{license_text}</span>
                <span>Updated {updated}</span>
                {fork_tag}
            </div>
        </div>"""

    def build_lang_options(repos):
        langs = sorted(set(r["language"] for r in repos if r["language"]))
        return "".join(f"<option value='{l}'>{l}</option>" for l in langs)

    def build_repo_js_array(repos):
        entries = []
        for repo in repos:
            entries.append(
                "{"
                f"name: '{repo['name']}',"
                f"lang: '{repo['language'] or ''}',"
                f"stars: {repo['stars']},"
                f"forks: {repo['forks']},"
                f"size: {repo['size_kb']},"
                f"updated: '{repo['updated_at']}',"
                f"isFork: {'true' if repo['is_fork'] else 'false'}"
                "}"
            )
        return "[" + ", ".join(entries) + "]"

    cards = "".join(build_repo_card(r) for r in repos)
    lang_options = build_lang_options(repos)
    repo_js_array = build_repo_js_array(repos)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{username}'s Repos</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f4f4f0; color: #1a1a1a; padding: 2rem; }}
    header {{ margin-bottom: 1.5rem; }}
    header h1 {{ font-size: 1.5rem; font-weight: 500; }}
    header p {{ color: #666; font-size: 0.875rem; margin-top: 4px; }}
    .controls {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 1.5rem; }}
    .controls input, .controls select {{ padding: 0.45rem 0.75rem; border: 0.5px solid #ccc;
      border-radius: 8px; font-size: 0.875rem; background: #fff; outline: none; }}
    .controls input {{ flex: 1; min-width: 200px; }}
    .controls input:focus, .controls select:focus {{ border-color: #888; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }}
    .card {{ background: #fff; border: 0.5px solid #e0e0e0; border-radius: 12px; padding: 1.1rem 1.25rem;
      display: flex; flex-direction: column; gap: 8px; transition: border-color 0.15s; }}
    .card:hover {{ border-color: #aaa; }}
    .card-top {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; }}
    .repo-name {{ font-size: 0.9375rem; font-weight: 500; color: #1a6fcf; text-decoration: none; word-break: break-all; }}
    .repo-name:hover {{ text-decoration: underline; }}
    .vis-badge {{ font-size: 11px; padding: 2px 7px; border-radius: 20px; border: 0.5px solid #ccc;
      color: #555; white-space: nowrap; }}
    .desc {{ font-size: 0.8125rem; color: #555; line-height: 1.5; }}
    .topics {{ display: flex; flex-wrap: wrap; gap: 5px; }}
    .topic {{ font-size: 11px; background: #dbeafe; color: #1e40af; padding: 2px 8px;
      border-radius: 20px; font-weight: 500; }}
    .stats {{ display: flex; flex-wrap: wrap; gap: 10px; font-size: 0.8rem; color: #444; margin-top: 2px; }}
    .meta {{ display: flex; flex-wrap: wrap; gap: 10px; font-size: 0.75rem; color: #888;
      border-top: 0.5px solid #eee; padding-top: 8px; margin-top: 2px; align-items: center; }}
    .lang-dot {{ color: #444; font-weight: 500; }}
    .fork-tag {{ background: #fef3c7; color: #92400e; font-size: 11px; padding: 2px 7px;
      border-radius: 20px; font-weight: 500; }}
    .hidden {{ display: none; }}
    #empty {{ text-align: center; color: #999; padding: 3rem; display: none; font-size: 0.9rem; }}
  </style>
</head>
<body>
  <header>
    <h1>{username}'s public repositories</h1>
    <p>{len(repos)} repositories found</p>
  </header>

  <div class="controls">
    <input type="text" id="search" placeholder="Search by name, description, topic..." oninput="applyFilters()" />
    <select id="lang-filter" onchange="applyFilters()">
      <option value="">All languages</option>
      {lang_options}
    </select>
    <select id="sort" onchange="applyFilters()">
      <option value="updated">Recently updated</option>
      <option value="stars">Most stars</option>
      <option value="forks">Most forks</option>
      <option value="size">Largest size</option>
      <option value="name">Name A–Z</option>
    </select>
    <select id="fork-filter" onchange="applyFilters()">
      <option value="">All repos</option>
      <option value="original">Originals only</option>
      <option value="forks">Forks only</option>
    </select>
  </div>

  <div class="grid" id="grid">{cards}</div>
  <p id="empty">No repositories match your filters.</p>

  <script>
    const grid = document.getElementById('grid');
    const empty = document.getElementById('empty');
    const cards = Array.from(grid.querySelectorAll('.card'));
    const repoData = {repo_js_array};

    function applyFilters() {{
      const q = document.getElementById('search').value.toLowerCase();
      const lang = document.getElementById('lang-filter').value;
      const sort = document.getElementById('sort').value;
      const forkFilter = document.getElementById('fork-filter').value;

      let indices = repoData.map((r, i) => i).filter(i => {{
        const card = cards[i];
        const text = card.innerText.toLowerCase();
        const r = repoData[i];
        if (q && !text.includes(q)) return false;
        if (lang && r.lang !== lang) return false;
        if (forkFilter === 'original' && r.isFork) return false;
        if (forkFilter === 'forks' && !r.isFork) return false;
        return true;
      }});

      indices.sort((a, b) => {{
        const ra = repoData[a], rb = repoData[b];
        if (sort === 'stars')   return rb.stars - ra.stars;
        if (sort === 'forks')   return rb.forks - ra.forks;
        if (sort === 'size')    return rb.size - ra.size;
        if (sort === 'name')    return ra.name.localeCompare(rb.name);
        return rb.updated.localeCompare(ra.updated);
      }});

      cards.forEach(c => c.classList.add('hidden'));
      indices.forEach(i => cards[i].classList.remove('hidden'));
      empty.style.display = indices.length === 0 ? 'block' : 'none';

      indices.forEach(i => grid.appendChild(cards[i]));
    }}
  </script>
</body>
</html>"""

    return html