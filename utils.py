import requests

import requests

def list_public_repos(username: str) -> list[dict]:
    repos = []
    page = 1

    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {"per_page": 100, "page": page, "type": "public"}
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        repos.extend({
            "name": repo["name"],
            "language": repo["language"],
            "description": repo["description"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "watchers": repo["watchers_count"],
            "open_issues": repo["open_issues_count"],
            "visibility": repo["visibility"],
            "is_fork": repo["fork"],
            "default_branch": repo["default_branch"],
            "url": repo["html_url"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
            "topics": repo.get("topics", []),
            "license": repo["license"]["name"] if repo.get("license") else None,
            "size_kb": repo["size"],
        } for repo in data)

        page += 1

    return repos


if __name__ == "__main__":
    username = "Monkey-hmm"
    repos = list_public_repos(username)

    print(f"Public repos for '{username}' ({len(repos)} total):")
    for i, repo in enumerate(repos, 1):
        print(f"  {i}. {repo}")