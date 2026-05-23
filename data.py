import csv
import random
from datetime import datetime

# Define our storage locations
FILENAME = 'history.csv'
SHEET_URL = "https://docs.google.com/spreadsheets/d/1XVOPCiWZkX5POEcTjv5n-_G6HaNX3rZs1uYs_CWvSok/edit?usp=drive_web"

def validate_user(username, pin):
    """Checks if a username exists, and ensures the PIN matches if it does."""
    try:
        import streamlit as st
        from streamlit_gsheets import GSheetsConnection
        import pandas as pd
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Read the sheet (ttl=0 ensures we check the live, most up-to-date data)
        df = conn.read(spreadsheet=SHEET_URL, usecols=[0, 1, 2, 3, 4], ttl=0)
        df = df.dropna(how="all") 
        
        # Clean the PIN column
        df["PIN"] = df["PIN"].astype(str).str.replace(".0", "", regex=False)
        
        # Filter the database for the requested username
        user_rows = df[df['Observer'] == username]
        
        if not user_rows.empty:
            # The username exists! Let's check what PIN they used on their very first log
            registered_pin = user_rows.iloc[0]['PIN']
            
            if registered_pin != str(pin):
                return False # The PIN is incorrect for this username
                
        return True # The username is either brand new, or the PIN perfectly matches!
        
    except Exception as e:
        # If the cloud check fails, return True so the app doesn't crash
        return True

def save_log(city, score, username="Guest", pin="0000"):
    """Saves to local CSV (for terminal) AND tries to save to Google Sheets (for web)."""
    
    # --- 1. LOCAL TERMINAL ENGINE ---
    today = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Save 5 columns to the CSV to match the cloud format
    log_entry = [today, city, f"{score}/10", username, str(pin)]
    
    with open(FILENAME, mode='a', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(log_entry)

    # --- 2. CLOUD WEB ENGINE ---
    try:
        import streamlit as st
        from streamlit.runtime import exists
        
        # This silently checks if the Streamlit web server is actively running
        if exists():
            from streamlit_gsheets import GSheetsConnection
            import pandas as pd
            
            conn = st.connection("gsheets", type=GSheetsConnection)
            existing_data = conn.read(spreadsheet=SHEET_URL, usecols=[0, 1, 2, 3, 4])
            
            new_row = pd.DataFrame([{
                "Date": today, 
                "Location": city, 
                "Score": f"{score}/10",
                "Observer": username,
                "PIN": str(pin)
            }])
            
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, worksheet="Skysensio_Logbook", data=updated_data)
            
    except Exception as e:
        import streamlit as st
        from streamlit.runtime import exists
        # If we are in the web app, show the error on the screen!
        if exists():
            st.error(f"Google Cloud Save Error: {e}")

def read_history():
    """Reads and prints all past observations from the CSV for the TERMINAL."""
    try:
        with open(FILENAME, mode='r', encoding="utf-8") as file:
            reader = csv.reader(file)
            
            print(f"{'DATE':<20} | {'CITY':<20} | {'SCORE':<10} | {'USER'}")
            print("-" * 65)
            
            for row in reader:
                if row: 
                    # Defensive check: handles older CSV entries that only had 3 columns
                    user = row[3] if len(row) > 3 else "Unknown"
                    print(f"{row[0]:<20} | {row[1]:<20} | {row[2]:<10} | {user}")
                    
    except FileNotFoundError:
        print("Your logbook is empty! Check some skies to create your first entry.")

def get_user_logs(username, pin):
    """Retrieves specific user logs from Google Sheets for the WEB APP."""
    try:
        import streamlit as st
        from streamlit_gsheets import GSheetsConnection
        import pandas as pd
        
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # Add ttl=0 to bypass the cache and fetch live data instantly!
        df = conn.read(spreadsheet=SHEET_URL, usecols=[0, 1, 2, 3, 4], ttl=0)
        df = df.dropna(how="all") 
        
        # Safe PIN conversion to stop pandas from adding ".0" to passwords
        df["PIN"] = df["PIN"].astype(str).str.replace(".0", "", regex=False)
        
        # Run the security filter
        user_df = df[(df['Observer'] == username) & (df['PIN'] == str(pin))]
        
        return user_df.drop(columns=["PIN"])
        
    except Exception as e:
        import streamlit as st
        st.error(f"Read Error: {e}")
        import pandas as pd
        return pd.DataFrame()

def get_random_fact():
    """Reads a text file of space facts and returns one at random."""
    try:
        with open("space_facts.txt", "r", encoding="utf-8") as file:
            facts = file.readlines()
            clean_facts = [fact.strip() for fact in facts if fact.strip()]
            return random.choice(clean_facts)
            
    except FileNotFoundError:
        return "Did you know? The universe is vast and full of mysteries!"

# --- TESTING BLOCK ---
if __name__ == "__main__":
    print("Testing the Database...")
    
    # Will save locally because it is being run from the terminal
    save_log("Test City", 8, "TerminalAdmin", "1234")
    print("Log saved successfully!")
    
    print("\nReading History:")
    read_history()