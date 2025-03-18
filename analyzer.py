#!/usr/bin/env python3

import json
import statistics
from prettytable import PrettyTable

def load_results(file_path="performance_results.json"):
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

def compute_stats(records):
    """
    Compute mean, median, and standard deviation for numeric parameters, and failure rate.
    """
    metrics = ["duration", "eval_duration", "load_duration", "avg_cpu", "avg_mem", "avg_gpu"]
    stats = {}
    for metric in metrics:
        values = [record.get(metric, 0) for record in records if metric in record]
        if values:
            mean_val = statistics.mean(values)
            median_val = statistics.median(values)
            std_val = statistics.stdev(values) if len(values) > 1 else 0
        else:
            mean_val = median_val = std_val = 0
        stats[metric] = {"mean": mean_val, "median": median_val, "std": std_val}
    
    # Compute failure rate: record where `done` is False.
    total = len(records)
    failures = sum(1 for record in records if not record.get("done", True))
    failure_rate = (failures / total) * 100 if total > 0 else 0
    stats["failure_rate"] = failure_rate
    stats["count"] = total
    return stats

def display_stats_transposed(grouped_stats):
    """
    Display the calculated statistics in a transposed table using PrettyTable.
    Each row represents a statistic and each column represents a model.
    """
    models = list(grouped_stats.keys())
    
    # Prepare rows: first two rows for count and failure rate,
    # then three rows per metric: mean, median, and std.
    stat_rows = {}
    
    # Count and Failure Rate rows:
    stat_rows["Count"] = {model: grouped_stats[model]["count"] for model in models}
    stat_rows["Failure Rate (%)"] = {model: f"{grouped_stats[model]['failure_rate']:.2f}" for model in models}
    
    metrics = ["duration", "eval_duration", "load_duration", "avg_cpu", "avg_mem", "avg_gpu"]
    for metric in metrics:
        stat_rows[f"{metric} mean"] = {model: f"{grouped_stats[model][metric]['mean']:.2f}" for model in models}
        stat_rows[f"{metric} median"] = {model: f"{grouped_stats[model][metric]['median']:.2f}" for model in models}
        stat_rows[f"{metric} std"] = {model: f"{grouped_stats[model][metric]['std']:.2f}" for model in models}
    
    headers = ["Statistic"] + models
    table = PrettyTable()
    table.field_names = headers
    
    for stat_label, model_values in stat_rows.items():
        row = [stat_label] + [model_values[model] for model in models]
        table.add_row(row)
    
    print(table)

def main():
    results = load_results("performance_results.json")
    if not results:
        print("No results found.")
        return
    
    grouped = group_by_model(results)
    
    # Calculate stats for each model.
    grouped_stats = {}
    for model, records in grouped.items():
        grouped_stats[model] = compute_stats(records)
    
    # Display the results in a transposed table.
    display_stats_transposed(grouped_stats)

if __name__ == "__main__":
    main()
