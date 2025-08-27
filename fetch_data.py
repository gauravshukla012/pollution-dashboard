import os
import requests
import pandas as pd

# --- Step 1: Replace these placeholders with your actual API details ---
# Make sure the URL includes a placeholder for the API key if needed
API_URL = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
API_KEY = os.environ.get("DATA_GOV_API_KEY")

# Example of how to structure the final URL with the key
# Most data.gov.in APIs look something like this:
# final_url = f"{API_URL}?api-key={API_KEY}&format=json&limit=1000"
# For this example, we will build it inside the function.

def fetch_data():
    """Fetches data from the API and returns it as a list of records."""
    
    # Construct the full URL with all necessary parameters
    # The 'limit=1000' part asks for up to 1000 records. Adjust if needed.
    full_api_url = f"{API_URL}?api-key={API_KEY}&format=json&limit=1000"
    
    try:
        print(f"Fetching data from: {API_URL}")
        response = requests.get(full_api_url)
        # This will stop the script if the request failed (e.g., wrong key or bad URL)
        response.raise_for_status()  
        
        data = response.json()
        
        # --- IMPORTANT ---
        # The actual data is often inside a key like 'records'. 
        # You MUST check the API's documentation or output to find the correct key.
        # Print data here to inspect it if you are unsure: print(data)
        records = data.get('records', [])
        
        if not records:
            print("Warning: No records found in the response. Check the 'records' key in your JSON.")
        
        return records

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

def process_and_save_data(records):
    """Processes the data with pandas and saves it to a CSV file."""
    if not records:
        print("No records to process. Exiting.")
        return

    # Convert the data into a table-like structure
    df = pd.DataFrame(records)
    
    print(f"Successfully converted {len(df)} records into a DataFrame.")
    print("DataFrame columns:", df.columns.tolist())
    print("First 5 rows of data:")
    print(df.head())

    # Save the cleaned data to a CSV file. The file will be named 'pollution_data.csv'
    df.to_csv('pollution_data.csv', index=False)
    print("\nData successfully saved to pollution_data.csv!")


# --- This is the main part of the script that runs everything ---
if __name__ == "__main__":
    api_records = fetch_data()
    if api_records:
        process_and_save_data(api_records)