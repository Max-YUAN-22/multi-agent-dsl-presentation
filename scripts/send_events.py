import requests
import pandas as pd
import time
import argparse
import json

def send_events(file_path, api_endpoint):
    """
    Reads events from a CSV file and sends them to the specified API endpoint.

    Args:
        file_path (str): The path to the CSV file.
        api_endpoint (str): The API endpoint to send the events to.
    """
    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        event_data = row.to_dict()
        try:
            response = requests.post(api_endpoint, json=event_data)
            if response.status_code == 200:
                print(f"Successfully sent event: {event_data}")
            else:
                print(f"Failed to send event: {event_data}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
        time.sleep(0.1)  # To avoid overwhelming the server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send events from a CSV file to an API endpoint.")
    parser.add_argument("--file", type=str, required=True, help="Path to the CSV file.")
    parser.add_argument("--api", type=str, required=True, help="API endpoint to send the events to.")
    args = parser.parse_args()

    send_events(args.file, args.api)