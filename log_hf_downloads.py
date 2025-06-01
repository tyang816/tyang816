from huggingface_hub import HfApi
import matplotlib.pyplot as plt
import datetime
import os
from pathlib import Path

# 用户配置
HF_USERNAME = "tyang816"
README_PATH = "README.md"
EXTRA_MODELS_FILE = "extra_hf_models.txt"
EXTRA_DATASETS_FILE = "extra_hf_datasets.txt"
MODEL_LOG_FILE = "log_model_download.txt"
DATASET_LOG_FILE = "log_dataset_download.txt"
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

    # 获取所有日期并排序
    all_dates = sorted(list(set(dates_model + dates_data)))
    
    # 计算12个月前的日期
    today = datetime.date.today()
    twelve_months_ago = today - datetime.timedelta(days=365)
    
    # 创建月份字典来存储每月下载量
    monthly_model_downloads = {}
    monthly_dataset_downloads = {}
    
    # 处理模型下载数据
    for date, value in zip(dates_model, values_model):
        if date.date() >= twelve_months_ago:
            month_key = date.strftime("%Y-%m")
            if month_key in monthly_model_downloads:
                monthly_model_downloads[month_key] += value
            else:
                monthly_model_downloads[month_key] = value
    
    # 处理数据集下载数据
    for date, value in zip(dates_data, values_data):
        if date.date() >= twelve_months_ago:
            month_key = date.strftime("%Y-%m")
            if month_key in monthly_dataset_downloads:
                monthly_dataset_downloads[month_key] += value
            else:
                monthly_dataset_downloads[month_key] = value
    
    # 获取所有有记录的月份并排序
    all_months = sorted(list(set(monthly_model_downloads.keys()) | set(monthly_dataset_downloads.keys())))
    
    # 只保留最近12个月的数据
    if len(all_months) > 12:
        all_months = all_months[-12:]
    
    # 获取每月的下载量
    model_monthly_values = [monthly_model_downloads.get(month, 0) for month in all_months]
    dataset_monthly_values = [monthly_dataset_downloads.get(month, 0) for month in all_months]
    
    # 美化月份标签显示
    display_months = [f"{month[-2:]}/{month[:4]}" for month in all_months]
    x = range(len(display_months))

    plt.figure(figsize=(12, 6))
    
    # 设置样式
    plt.style.use('default')
    
    # 设置背景色和网格
    plt.gca().set_facecolor('#f8f9fa')
    plt.gcf().set_facecolor('white')
    
    # 绘制折线图
    plt.plot(x, model_monthly_values, label="Monthly Model Downloads", color="#1f77b4", linewidth=2, marker='o', markersize=6)
    plt.plot(x, dataset_monthly_values, label="Monthly Dataset Downloads", color="#ff7f0e", linewidth=2, marker='s', markersize=6)

    # 设置x轴标签
    plt.xticks(ticks=x, labels=display_months, rotation=45)
    
    # 设置y轴标签和标题
    plt.ylabel("Monthly Downloads", fontsize=12, fontweight='bold', color='#2c3e50')
    plt.title("Monthly Hugging Face Downloads (Last 12 Months)", fontsize=14, fontweight='bold', pad=20, color='#2c3e50')
    
    # 添加图例
    plt.legend(fontsize=10, loc='upper left', framealpha=0.9)
    
    # 添加网格
    plt.grid(True, linestyle='--', alpha=0.3, color='#bdc3c7')
    
    # 设置坐标轴颜色
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_color('#bdc3c7')
    plt.gca().spines['bottom'].set_color('#bdc3c7')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(PLOT_FILE, dpi=300, bbox_inches='tight')
    plt.close()

def get_downloads():
    total_model_downloads, total_dataset_downloads = 0, 0
    with open(MODEL_LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            total_model_downloads += int(line.split(',')[1])
            
    with open(DATASET_LOG_FILE, 'r') as f:
        for line in f:
            line = line.strip()
            total_dataset_downloads += int(line.split(',')[1])
    
    # 加上千分位
    total_model_downloads = "{:,}".format(total_model_downloads)
    total_dataset_downloads = "{:,}".format(total_dataset_downloads)
    
    return total_model_downloads, total_dataset_downloads


if __name__ == "__main__":
    extra_models = read_lines(EXTRA_MODELS_FILE)
    extra_datasets = read_lines(EXTRA_DATASETS_FILE)
    model_dl, dataset_dl = get_hf_downloads(HF_USERNAME, extra_models, extra_datasets)
    log_downloads(model_dl, dataset_dl)
    draw_plot()
    print("✅ 下载量已记录并生成美化图表。")
