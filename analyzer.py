import json
import statistics
import glob
import os
from prettytable import PrettyTable
import math

def load_results(file_path):
    """
    Load the performance results from a JSON file.
    """
    try:
        with open(file_path, "r") as infile:
            data = json.load(infile)
        return data.get("results", {})
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def group_by_model(results):
    """
    Group performance data by model, ignoring the baseline entry.
    """
    grouped = {}
    for key, value in results.items():
        # Skip the baseline entry.
        if key == "baseline":
            continue
        # Each key here (e.g. "1", "2", etc.) contains a dict where keys are model names.
        for model, records in value.items():
            if model not in grouped:
                grouped[model] = []
            grouped[model].extend(records)
    return grouped

# def compute_stats(records, baseline):
#     """
#     Compute mean, median, and standard deviation for numeric parameters, and failure rate.
#     For avg_cpu, avg_mem, and avg_gpu, subtract the corresponding baseline values.
#     """
#     metrics = ["duration", "eval_duration", "load_duration", "avg_cpu", "avg_mem", "avg_gpu"]
#     stats = {}
#     for metric in metrics:
#         if metric in ["avg_cpu", "avg_mem", "avg_gpu"]:
#             # Map metric to the corresponding baseline key.
#             baseline_key = "cpu" if metric == "avg_cpu" else "mem" if metric == "avg_mem" else "gpu"
#             baseline_val = baseline.get(baseline_key, 0)
#             values = [record.get(metric, 0) - baseline_val for record in records if metric in record]
#         else:
#             values = [record.get(metric, 0) for record in records if metric in record]
            
#         if values:
#             mean_val = statistics.mean(values)
#             median_val = statistics.median(values)
#             std_val = statistics.stdev(values) if len(values) > 1 else 0
#         else:
#             mean_val = median_val = std_val = 0
#         stats[metric] = {"mean": mean_val, "median": median_val, "std": std_val}
    
#     # Compute failure rate: count records where `done` is False.
#     total = len(records)
#     failures = sum(1 for record in records if not record.get("done", True))
#     failure_rate = (failures / total) * 100 if total > 0 else 0
#     stats["failure_rate"] = failure_rate
#     stats["count"] = total
#     return stats

def compute_stats(records, baseline):
    """
    Compute mean, median, std, and 95% confidence interval (CI) for each metric.
    """
    metrics = ["duration", "eval_duration", "load_duration", "avg_cpu", "avg_mem", "avg_gpu"]
    stats = {}
    n = len(records)

    for metric in metrics:
        values = [record.get(metric, 0) for record in records if metric in record]
        if values:
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0

            # 95% confidence interval (Z = 1.96)
            ci = 1.96 * (std_val / math.sqrt(n)) if n > 1 else 0
            ci_lower = mean_val - ci
            ci_upper = mean_val + ci
            ci_str = f"[{ci_lower:.2f}, {ci_upper:.2f}]"
        else:
            mean_val = median_val = std_val = 0
            ci_str = "[0, 0]"

        stats[metric] = {
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "ci": ci_str
        }

    # Failure rate
    failures = sum(1 for record in records if not record.get("done", True))
    failure_rate = (failures / n) * 100 if n > 0 else 0
    stats["failure_rate"] = failure_rate
    stats["count"] = n
    return stats

def display_stats_transposed(grouped_stats):
    """
    Display the calculated statistics in a transposed table using PrettyTable.
    Each row represents a statistic and each column represents a model.
    """
    models = list(grouped_stats.keys())
    
    # Prepare rows: first rows for count and failure rate,
    # then rows for each metric: mean, median, and std.
    stat_rows = {}
    
    stat_rows["Count"] = {model: grouped_stats[model]["count"] for model in models}
    stat_rows["Failure Rate (%)"] = {model: f"{grouped_stats[model]['failure_rate']:.2f}" for model in models}
    
    metrics = ["duration", "eval_duration", "load_duration", "avg_cpu", "avg_mem", "avg_gpu"]
    for metric in metrics:
        stat_rows[f"{metric} mean"] = {model: f"{grouped_stats[model][metric]['mean']:.2f}" for model in models}
        stat_rows[f"{metric} median"] = {model: f"{grouped_stats[model][metric]['median']:.2f}" for model in models}
        stat_rows[f"{metric} std"] = {model: f"{grouped_stats[model][metric]['std']:.2f}" for model in models}
        stat_rows[f"{metric} 95% CI"] = {model: f"{grouped_stats[model][metric]['ci']}" for model in models}

    headers = ["Statistic"] + models
    table = PrettyTable()
    table.field_names = headers
    
    for stat_label, model_values in stat_rows.items():
        row = [stat_label] + [model_values[model] for model in models]
        table.add_row(row)
    
    print(table)

def main():
    # Look for all performance_results_XX.json files in /Results
    json_files = glob.glob(os.path.join("Results", "performance_results_*.json"))
    
    if not json_files:
        print("No matching performance result files found in /Results.")
        return
    
    # Process each file separately
    for file_path in json_files:
        # Extract initials from filename.
        filename = os.path.basename(file_path)
        prefix, _ = os.path.splitext(filename)
        user_initials = prefix.replace("performance_results_", "")
        
        print(f"\n{'-'*14} Results for user initials: {user_initials} {'-'*14}")
        results = load_results(file_path)
        
        if not results:
            print("No results found in this file.")
            continue
        
        # Retrieve baseline values.
        baseline = results.get("baseline", {"cpu": 0, "mem": 0, "gpu": 0})
        grouped = group_by_model(results)
        
        # Calculate stats for each model, discounting the baseline.
        grouped_stats = {}
        for model, records in grouped.items():
            grouped_stats[model] = compute_stats(records, baseline)
        
        # Display the results in a transposed table.
        display_stats_transposed(grouped_stats)

if __name__ == "__main__":
    main()
