import requests
from huggingface_hub import HfApi
from pathlib import Path

USERNAME = "tyang816"
README_PATH = "README.md"

GITHUB_REPO_FILE = "extra_github_repos.txt"
HF_MODEL_FILE = "extra_hf_models.txt"
HF_DATASET_FILE = "extra_hf_datasets.txt"

def read_lines(filepath):
    path = Path(filepath)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def get_github_stats(username, extra_repos):
    total_stars = 0
    total_forks = 0

    # 当前用户的所有 repo
    url = f"https://api.github.com/users/{username}/repos?per_page=100"
    response = requests.get(url)
    repos = response.json()

    if isinstance(repos, dict) and "message" in repos:
        raise Exception(f"GitHub API error: {repos['message']}")

    total_stars += sum(repo["stargazers_count"] for repo in repos)
    total_forks += sum(repo["forks_count"] for repo in repos)

    for full_name in extra_repos:
        owner, repo_name = full_name.split("/")
        repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        resp = requests.get(repo_url)
        if resp.status_code == 200:
            data = resp.json()
            total_stars += data.get("stargazers_count", 0)
            total_forks += data.get("forks_count", 0)
        else:
            print(f"⚠️ Failed to fetch {full_name}: {resp.status_code}")

    return total_stars, total_forks

def get_hf_downloads(username, extra_models, extra_datasets):
    api = HfApi()
    models = api.list_models(author=username)
    datasets = api.list_datasets(author=username)

    model_downloads = sum(m.downloads for m in models)
    dataset_downloads = sum(d.downloads for d in datasets)

    for model_id in extra_models:
        try:
            info = api.model_info(model_id)
            model_downloads += info.downloads
        except Exception as e:
            print(f"⚠️ Failed to fetch model {model_id}: {e}")

    for dataset_id in extra_datasets:
        try:
            info = api.dataset_info(dataset_id)
            dataset_downloads += info.downloads
        except Exception as e:
            print(f"⚠️ Failed to fetch dataset {dataset_id}: {e}")

    return model_downloads, dataset_downloads

def update_readme(stars, forks, model_downloads, dataset_downloads):
    with open(README_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "<!-- 🔄 stars -->" in line:
            lines[i] = f"![Total Stars](https://img.shields.io/badge/Stars-{stars}-blue?logo=github&style=flat-square) <!-- 🔄 stars -->\n"
        if "<!-- 🔄 forks -->" in line:
            lines[i] = f"![Total Forks](https://img.shields.io/badge/Forks-{forks}-blue?logo=github&style=flat-square) <!-- 🔄 forks -->\n"
        if "<!-- 🔄 total_hf_models -->" in line:
            lines[i] = f"![Total Model Downloads](https://img.shields.io/badge/Total%20Model%20Downloads-{model_downloads}-orange?logo=huggingface&style=flat-square) <!-- 🔄 total_hf_models -->\n"
        if "<!-- 🔄 total_hf_datasets -->" in line:
            lines[i] = f"![Total Dataset Downloads](https://img.shields.io/badge/Total%20Dataset%20Downloads-{dataset_downloads}-orange?logo=huggingface&style=flat-square) <!-- 🔄 total_hf_datasets -->\n"
        
        
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    try:
        extra_repos = read_lines(GITHUB_REPO_FILE)
        extra_models = read_lines(HF_MODEL_FILE)
        extra_datasets = read_lines(HF_DATASET_FILE)

        stars, forks = get_github_stats(USERNAME, extra_repos)
        model_downloads, dataset_downloads = get_hf_downloads(USERNAME, extra_models, extra_datasets)

        update_readme(stars, forks, model_downloads, dataset_downloads)
        print(f"✅ Updated README.md — ⭐ {stars}, 🍴 {forks}, 🤗 Models: {model_downloads}, 📊 Datasets: {dataset_downloads}")
    except Exception as e:
        print(f"❌ Error: {e}")
