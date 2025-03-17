import argparse
import json
import time
import psutil
import os
import random
import ollama

from formatted_reply import FormattedReply

def read_jsons():
    """
    Reads the configurable contents of .jsons.
    """
    # Read models.
    try:
        with open('models.json', 'r') as f:
            models_data = json.load(f)
    except Exception as e:
        print("Error reading models.json:", e)
        return None, None

    # Read queries.
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
    response = client.generate(model=model, prompt=query)
    return response

def progress_message(completed_queries, total_queries, query_number, model, iteration):
    """
    Prints a multi-line progress update with a progress bar.
    """
    percent_complete = int((completed_queries / total_queries) * 100)
    bar_length = 100
    filled_length = int(round(bar_length * completed_queries / total_queries))
    progress_bar = '■' * filled_length + '-' * (bar_length - filled_length)

    # Build each line with fixed-width formatting
    line1 = f"|{progress_bar}|"
    line2 = f"    Percent complete: {percent_complete:>8}%"
    line3 = f"    Test iteration: {iteration:>11}"
    line4 = f"    Testing model: {model:>12}"
    line5 = f"    Testing query: {query_number:>12}"
    progress_msg = f"{line1}\n{line2}\n{line3}\n{line4}\n{line5}"

    # Move cursor up 3 lines if this is not the first update
    if completed_queries > 0:
        print("\033[F" * 5, end="")
    print(progress_msg)

def main():
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

    # Adjust the length of queries if specified by user.
    if args.max_queries != -1 and args.max_queries < len(queries):
        queries = queries[:args.max_queries]

    total_queries = len(models) * len(queries) * args.test_iterations
    completed_queries = 0
    client = ollama.Client()
    results = {}  # Nested dictionary to store results per iteration and per model.

    for iteration in range(1, args.test_iterations + 1):
        results[str(iteration)] = {}
        for model in models:
            model_results = []
            for query_number, query in enumerate(queries, start=1):
                progress_message(completed_queries, total_queries, query_number, model, iteration)
                response = send_query_to_model(client, model, query)
                formatted_reply = FormattedReply.decompose_ollama_reply(response)
                model_results.append({
                    "query": query,
                    "response": formatted_reply.response,
                    "done" : formatted_reply.done,
                    "done_reason" : formatted_reply.done_reason,
                    "duration" : formatted_reply.duration,
                    "eval_duration": formatted_reply.eval_duration,
                    "load_duration" : formatted_reply.load_duration
                })
                completed_queries += 1
            results[str(iteration)][model] = model_results

    # Clean up the progress bar display.
    progress_message(total_queries, total_queries, "----", "----", "----")
    print("Test complete!")

    # Save performance results to a JSON file for later analysis.
    print("Dumping the stats...")
    with open("performance_results.json", "w") as outfile:
        json.dump({"results": results}, outfile, indent=2)
    
    print("Done!")

if __name__ == '__main__':
    main()
