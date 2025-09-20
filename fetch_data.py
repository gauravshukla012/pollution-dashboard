import os
import requests
import pandas as pd

def fetch_data():
    """Fetches data from the API and returns it as a list of records."""
    API_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
    API_KEY = os.environ.get("DATA_GOV_API_KEY")
    full_api_url = f"{API_URL}?api-key={API_KEY}&format=json&limit=1000"
    
    try:
        print(f"Fetching data from: {API_URL}")
        response = requests.get(full_api_url)
        response.raise_for_status()
        data = response.json()
        records = data.get('records', [])
        if not records:
            print("Warning: No records found in the response.")
        return records
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def process_and_save_data(records):
    """Processes the data and saves it to a CSV file."""
    if not records:
        print("No records to process. Exiting.")
        return

    df = pd.DataFrame(records)
    print(f"Successfully converted {len(df)} records into a DataFrame.")
    
    # Save the cleaned data to a CSV file, overwriting it each time
    df.to_csv('pollution_data.csv', index=False)
    print("\nData successfully saved to pollution_data.csv!")


if __name__ == "__main__":
    api_records = fetch_data()
    if api_records:
        process_and_save_data(api_records)