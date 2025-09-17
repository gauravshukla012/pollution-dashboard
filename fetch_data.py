import os
import requests
import pandas as pd
import sqlite3  # <-- 1. IMPORT THE SQLITE LIBRARY

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
    """Processes the data and appends it to an SQLite database."""
    if not records:
        print("No records to process. Exiting.")
        return

    df = pd.DataFrame(records)
    print(f"Successfully converted {len(df)} records into a DataFrame.")

    # --- 2. REPLACE THE CSV SAVING LOGIC WITH DATABASE LOGIC ---
    try:
        # Connect to the SQLite database. A file named 'pollution_history.db' will be created.
        conn = sqlite3.connect('pollution_history.db')
        
        # Append the new data to a table named 'daily_readings'.
        # if_exists='append' is the key part that adds new data without deleting the old.
        df.to_sql('daily_readings', conn, if_exists='append', index=False)
        
        # Close the connection to the database
        conn.close()
        
        print(f"\nSuccessfully appended {len(df)} new records to pollution_history.db!")
    except Exception as e:
        print(f"An error occurred while saving to the database: {e}")

# --- This is the main part of the script that runs everything ---
if __name__ == "__main__":
    api_records = fetch_data()
    if api_records:
        process_and_save_data(api_records)