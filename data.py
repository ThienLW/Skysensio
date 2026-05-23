import csv
from datetime import datetime

# The name of the file where we will store the logs
FILENAME = 'history.csv'

def save_log(city, score):
    """Saves the date, city, and observing score to a CSV file"""
    today = datetime.now().strftime("%d/%m/%Y") 
    
    log_entry = [today, city, f"{score} out of 10"]
    
    with open(FILENAME, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(log_entry)

def read_history():
    """Reads and prints all past observations from the CSV file."""
    # WEEK 8 FLOW CONTROL: Catch the error if the file doesn't exist yet
    try:
        with open(FILENAME, mode='r') as file:
            reader = csv.reader(file)
            
            # Print a neat header
            print(f"{'DATE':<15} | {'CITY':<20} | {'SCORE'}")
            print("-" * 45)
            
            # Loop through the rows and print them
            for row in reader:
                if row: # Make sure the row isn't empty
                    print(f"{row[0]:<15} | {row[1]:<20} | {row[2]}")
                    
    except FileNotFoundError:
        print("Your logbook is empty! Check some skies to create your first entry.")

# --- TESTING BLOCK ---
if __name__ == "__main__":
    print("Testing the Database...")
    
    # Test saving a fake log
    save_log("Test City", 8)
    print("Log saved successfully!")
    
    # Test reading the log
    print("\nReading History:")
    read_history()