from huggingface_hub import HfApi
import matplotlib.pyplot as plt
import datetime
import os
from pathlib import Path

# 用户配置
HF_USERNAME = "tyang816"
EXTRA_MODELS_FILE = "extra_hf_models.txt"
EXTRA_DATASETS_FILE = "extra_hf_datasets.txt"
MODEL_LOG_FILE = "model_download_log.txt"
DATASET_LOG_FILE = "dataset_download_log.txt"
PLOT_FILE = "hf_downloads_chart.png"

def read_lines(filepath):
    path = Path(filepath)
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

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

def log_downloads(model_downloads, dataset_downloads):
    today = datetime.date.today().strftime("%Y-%m-%d")
    with open(MODEL_LOG_FILE, "a") as f:
        f.write(f"{today},{model_downloads}\n")
    with open(DATASET_LOG_FILE, "a") as f:
        f.write(f"{today},{dataset_downloads}\n")

def load_log(filepath):
    if not os.path.exists(filepath):
        return [], []
    with open(filepath, "r") as f:
        lines = f.readlines()
    data = [line.strip().split(",") for line in lines if line.strip()]
    dates = [datetime.datetime.strptime(d[0], "%Y-%m-%d") for d in data]
    values = [int(d[1]) for d in data]
    return dates, values

def draw_plot():
    dates_model, values_model = load_log(MODEL_LOG_FILE)
    dates_data, values_data = load_log(DATASET_LOG_FILE)

    all_dates = sorted(list(set(dates_model + dates_data)))
    date_strs = [d.strftime("%Y-%m-%d") for d in all_dates]
    x = range(len(date_strs))

    model_dict = dict(zip([d.strftime("%Y-%m-%d") for d in dates_model], values_model))
    data_dict = dict(zip([d.strftime("%Y-%m-%d") for d in dates_data], values_data))

    model_values = [model_dict.get(d, 0) for d in date_strs]
    data_values = [data_dict.get(d, 0) for d in date_strs]

    bar_width = 0.4

    plt.figure(figsize=(12, 6))
    plt.bar([i - bar_width / 2 for i in x], model_values, width=bar_width, label="Model Downloads", color="#1f77b4")
    plt.bar([i + bar_width / 2 for i in x], data_values, width=bar_width, label="Dataset Downloads", color="#ff7f0e")

    plt.xticks(ticks=x, labels=date_strs, rotation=45)
    plt.ylabel("Total Downloads")
    plt.title("Hugging Face Downloads Over Time")
    plt.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close()

if __name__ == "__main__":
    extra_models = read_lines(EXTRA_MODELS_FILE)
    extra_datasets = read_lines(EXTRA_DATASETS_FILE)
    model_dl, dataset_dl = get_hf_downloads(HF_USERNAME, extra_models, extra_datasets)
    log_downloads(model_dl, dataset_dl)
    draw_plot()
    print("✅ 下载量已记录并生成美化图表。")
