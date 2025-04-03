import os
import datetime
import matplotlib.pyplot as plt
from huggingface_hub import HfApi

# 配置
HF_USERNAME = "tyang816"
MODEL_LOG_FILE = "model_download_log.txt"
DATASET_LOG_FILE = "dataset_download_log.txt"
PLOT_FILE = "hf_downloads_chart.png"

def get_hf_downloads(username):
    api = HfApi()
    models = api.list_models(author=username)
    datasets = api.list_datasets(author=username)

    model_downloads = sum(m.downloads for m in models)
    dataset_downloads = sum(d.downloads for d in datasets)
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

    if not dates_model or not dates_data:
        print("⚠️ No data to plot.")
        return

    plt.figure(figsize=(10, 5))
    bar_width = 10  # days
    plt.bar(dates_model, values_model, width=bar_width, label="Model Downloads")
    plt.bar(dates_data, values_data, width=bar_width, label="Dataset Downloads", alpha=0.6)

    plt.xticks(rotation=45)
    plt.ylabel("Total Downloads")
    plt.title("Hugging Face Downloads Over Time")
    plt.legend()
    plt.tight_layout()
    plt.savefig(PLOT_FILE)
    plt.close()
    print(f"✅ Plot saved to {PLOT_FILE}")

if __name__ == "__main__":
    model_dl, dataset_dl = get_hf_downloads(HF_USERNAME)
    log_downloads(model_dl, dataset_dl)
    draw_plot()
    print("✅ Logs updated and chart generated.")
