import argparse
import json
import time
import psutil
import os
import random
import threading
import ollama

# Try to import GPUtil for GPU utilization monitoring; if unavailable, default to None.
try:
    import GPUtil
except ImportError:
    GPUtil = None

from formatted_reply import FormattedReply

def measure_utilization(stop_event, samples, interval=0.1):
    """
    Periodically sample CPU, memory, and GPU utilization.

    Args:
        stop_event (threading.Event): Signal to stop sampling.
        samples (list): A list to which each sample (a dict) is appended.
        interval (float): Time (in seconds) between samples.
    """
    while not stop_event.is_set():
        cpu = psutil.cpu_percent(interval=interval)
        mem = psutil.virtual_memory().percent
        gpu = 0
        if GPUtil is not None:
            gpus = GPUtil.getGPUs()
            if gpus:
                # Average GPU load percentage across all GPUs.
                gpu = sum(g.load * 100 for g in gpus) / len(gpus)
        samples.append({"cpu": cpu, "mem": mem, "gpu": gpu})

def measure_baseline_utilization(duration=1.0, interval=0.1):
    """
    Measures baseline resource utilization by running a dummy task.

    Args:
        duration (float): How long (in seconds) to run the dummy task.
        interval (float): Sampling interval.
        
    Returns:
        A tuple (avg_cpu, avg_mem, avg_gpu) representing the baseline usage.
    """
    samples = []
    stop_event = threading.Event()
    baseline_thread = threading.Thread(target=measure_utilization, args=(stop_event, samples, interval))
    baseline_thread.start()
    # Dummy task: here we simply sleep.
    time.sleep(duration)
    stop_event.set()
    baseline_thread.join()

    if samples:
        avg_cpu = sum(s["cpu"] for s in samples) / len(samples)
        avg_mem = sum(s["mem"] for s in samples) / len(samples)
        avg_gpu = sum(s["gpu"] for s in samples) / len(samples)
    else:
        avg_cpu = avg_mem = avg_gpu = 0
    return avg_cpu, avg_mem, avg_gpu

def read_jsons():
    """
    Reads the configurable contents of .jsons.
    """
    try:
        with open('models.json', 'r') as f:
            models_data = json.load(f)
    except Exception as e:
        print("Error reading models.json:", e)
        return None, None

    try:
        with open('queries.json', 'r') as f:
            queries_data = json.load(f)
    except Exception as e:
        print("Error reading queries.json:", e)
        return None, None
    
    return models_data.get("models", []), queries_data.get("queries", [])

def send_query_to_model(client, model, query):
    """
    Sends a query to a model using the ollama client.
    Replace this with your actual interaction code if needed.
    """
    response = client.generate(model=model, prompt=query, keep_alive=10)
    return response

def progress_message(completed_queries, total_queries, query_number, model, iteration):
    """
    Prints a multi-line progress update with a progress bar.
    """
    percent_complete = int((completed_queries / total_queries) * 100)
    bar_length = 100
    filled_length = int(round(bar_length * completed_queries / total_queries))
    progress_bar = '■' * filled_length + '-' * (bar_length - filled_length)

    line1 = f"|{progress_bar}|"
    line2 = f"    Percent complete: {percent_complete:>8}%"
    line3 = f"    Test iteration: {iteration:>11}"
    line4 = f"    Testing model: {model:>12}"
    line5 = f"    Testing query: {query_number:>12}"
    progress_msg = f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}"

    if completed_queries > 0:
        print("\033[F" * 5, end="")
    print(progress_msg)

def main():
    # Prompt the user for their initials.
    user_initial = input("Please enter your initials: ")

    # Parse arguments.
    parser = argparse.ArgumentParser(description="Test performance of local LLMs")
    parser.add_argument(
        '--max-queries',
        type=int,
        default=-1,
        help="Maximum number of queries to test on (default: all queries)"
    )
    parser.add_argument(
        '--test-iterations',
        type=int,
        default=1,
        help="Number of iterations to run this test"
    )
    args = parser.parse_args()

    # Read the data from JSON files.
    models, queries = read_jsons()
    if models is None or queries is None:
        return

    if args.max_queries != -1 and args.max_queries < len(queries):
        queries = queries[:args.max_queries]

    total_queries = len(models) * len(queries) * args.test_iterations
    completed_queries = 0
    client = ollama.Client()
    results = {}

    # Measure baseline resource utilization once (e.g., when idle).
    baseline_cpu, baseline_mem, baseline_gpu = measure_baseline_utilization(duration=1.0, interval=0.1)
    results["baseline"] = {
        "cpu": baseline_cpu,
        "mem": baseline_mem,
        "gpu": baseline_gpu
    }

    # Run the tests per iteration.
    for iteration in range(1, args.test_iterations + 1):
        results[str(iteration)] = {}
        for model in models:
            model_results = []
            for query_number, query in enumerate(queries, start=1):
                progress_message(completed_queries, total_queries, query_number, model, iteration)
                
                # Start monitoring resource utilization for this query.
                samples = []
                stop_event = threading.Event()
                monitor_thread = threading.Thread(target=measure_utilization, args=(stop_event, samples))
                monitor_thread.start()
                
                # Send the query.
                response = send_query_to_model(client, model, query)
                
                # Stop monitoring.
                stop_event.set()
                monitor_thread.join()
                
                # Calculate average usage during the query.
                if samples:
                    avg_cpu = sum(s["cpu"] for s in samples) / len(samples)
                    avg_mem = sum(s["mem"] for s in samples) / len(samples)
                    avg_gpu = sum(s["gpu"] for s in samples) / len(samples)
                else:
                    avg_cpu = avg_mem = avg_gpu = 0
                
                formatted_reply = FormattedReply.decompose_ollama_reply(response)
                model_results.append({
                    "query": query,
                    "response": formatted_reply.response,
                    "done": formatted_reply.done,
                    "done_reason": formatted_reply.done_reason,
                    "duration": formatted_reply.duration,
                    "eval_duration": formatted_reply.eval_duration,
                    "load_duration": formatted_reply.load_duration,
                    "avg_cpu": avg_cpu,
                    "avg_mem": avg_mem,
                    "avg_gpu": avg_gpu
                })
                completed_queries += 1
            results[str(iteration)][model] = model_results

    progress_message(total_queries, total_queries, "----", "----", "----")
    print("Test complete!")

    # Build the output filename with user initials.
    output_filename = f"./Results/performance_results_{user_initial}.json"
    print(f"Dumping the stats to {output_filename} ...")
    with open(output_filename, "w") as outfile:
        json.dump({"results": results}, outfile, indent=2)
    
    print("Test complete!")

if __name__ == '__main__':
    main()
