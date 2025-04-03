import requests
from huggingface_hub import HfApi

USERNAME = "tyang816"
README_PATH = "README.md"

EXTRA_REPOS = [
    ("ai4protein", "VenusFactory"),
    ("ai4protein", "ProtSSN"),
    ("ai4protein", "VenusREM"),
    ("ai4protein", "ProSST"),
]

def get_github_stats(username, extra_repos):
    total_stars = 0
    total_forks = 0

    # 当前用户名下的所有仓库
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    response = requests.get(repos_url)
    repos = response.json()

    if isinstance(repos, dict) and "message" in repos:
        raise Exception(f"GitHub API error: {repos['message']}")

    total_stars += sum(repo["stargazers_count"] for repo in repos)
    total_forks += sum(repo["forks_count"] for repo in repos)

    # 手动列出的额外仓库
    for owner, repo_name in extra_repos:
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        resp = requests.get(repo_url)
        if resp.status_code == 200:
            repo_data = resp.json()
            total_stars += repo_data.get("stargazers_count", 0)
            total_forks += repo_data.get("forks_count", 0)
        else:
            print(f"⚠️ Failed to fetch {owner}/{repo_name}: {resp.status_code}")

    return total_stars, total_forks

def get_huggingface_downloads(username):
    api = HfApi()
    models = api.list_models(author=username)
    datasets = api.list_datasets(author=username)

    model_downloads = sum(m.downloads for m in models)
    dataset_downloads = sum(d.downloads for d in datasets)
    return model_downloads, dataset_downloads

def update_readme(stars, forks, model_downloads, dataset_downloads):
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "<!-- 🔄 stars -->" in line:
            lines[i] = f"![Total Stars](https://img.shields.io/badge/Stars-{stars}-blue?logo=github&style=flat-square) <!-- 🔄 stars -->\n"
        if "<!-- 🔄 forks -->" in line:
            lines[i] = f"![Total Forks](https://img.shields.io/badge/Forks-{forks}-blue?logo=github&style=flat-square) <!-- 🔄 forks -->\n"
        if "<!-- 🔄 hf_models -->" in line:
            lines[i] = f"![Model Downloads](https://img.shields.io/badge/HuggingFace%20Models-{model_downloads}-orange?logo=huggingface&style=flat-square) <!-- 🔄 hf_models -->\n"
        if "<!-- 🔄 hf_datasets -->" in line:
            lines[i] = f"![Dataset Downloads](https://img.shields.io/badge/HuggingFace%20Datasets-{dataset_downloads}-orange?logo=huggingface&style=flat-square) <!-- 🔄 hf_datasets -->\n"

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    try:
        stars, forks = get_github_stats(USERNAME, EXTRA_REPOS)
        model_downloads, dataset_downloads = get_huggingface_downloads(USERNAME)
        update_readme(stars, forks, model_downloads, dataset_downloads)
        print(f"✅ Updated README.md — Stars: {stars}, Forks: {forks}, Models: {model_downloads}, Datasets: {dataset_downloads}")
    except Exception as e:
        print(f"❌ Error: {e}")
