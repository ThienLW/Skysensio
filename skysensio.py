import logic
import data
import random
from datetime import datetime
import os
from dotenv import load_dotenv

# 1. Load the secret variables from the .env file
load_dotenv()

# 2. Securely grab the key. If the .env file is missing, it returns None.
API_KEY = os.getenv("WEATHER_API_KEY")

if not API_KEY:
    raise ValueError("Missing API Key! Please create a .env file with WEATHER_API_KEY.")

def get_advice(score):
    """Returns randomized stargazing advice based on the final score."""
    if score >= 9.0:
        advice_options = [
            "Pristine conditions. Set up the telescope! Perfect for faint deep-sky objects.",
            "Incredible skies tonight. Grab your best eyepieces and hunt for nebulae.",
            "A rare, perfect night for astronomy. Make the most of it!"
        ]
    elif score >= 6.0:
        advice_options = [
            "Good conditions. Great night for viewing bright targets like the Moon and planets.",
            "Solid skies. You might see some atmospheric blurring, but planetary details will be visible.",
            "A nice night to observe. Perfect for lunar craters or the rings of Saturn."
        ]
    elif score >= 3.0:
        advice_options = [
            "Sub-optimal. High clouds or wind. Stick to binoculars or naked-eye constellations.",
            "Tough conditions for a telescope. A good night for wide-field binocular scanning.",
            "Seeing is poor tonight. Focus on the brightest stars and constellations."
        ]
    else:
        advice_options = [
            "Stargazing is currently impossible. Great time to clean your lenses or study star charts!",
            "The sky is completely uncooperative. Stay inside and plan your next observing session.",
            "Dealbreaker conditions. Keep the telescope packed away and read up on astronomy."
        ]
    
    # random.choice() automatically picks one item from the list
    return random.choice(advice_options)

def get_random_fact():
    """Reads a text file of space facts and returns one at random."""
    try:
        # Open the file in read mode ('r')
        with open("space_facts.txt", "r", encoding="utf-8") as file:
            # Read all lines into a list
            facts = file.readlines()
            
            # Clean up the list by removing invisible newline characters (\n) and blank lines
            clean_facts = [fact.strip() for fact in facts if fact.strip()]
            
            # Return one random fact
            return random.choice(clean_facts)
            
    except FileNotFoundError:
        # Defensive coding: If the file is missing, provide a safe default so the app doesn't crash
        return "Did you know? The universe is vast and full of mysteries!"

def main():
    print("Welcome to Skysensio: The Stargazer's Logbook")
    
    # WEEK 8 FLOW CONTROL: The main application loop
    while True:
        print("\n" + "="*30)
        print("1. Check Skies (Calculate Score)")
        print("2. View History (Logbook)")
        print("3. Exit")
        print("="*30)
        
        choice = input("Select an option (1-3): ")
        
        if choice == '1':
           
            while True:
                 # Ask the user for permission to auto-detect
                use_auto = input("\nDo you want to use your current location? (y/n): ").strip().lower()
            
                city_input = ""
                if use_auto == 'y':
                    print("Detecting your location...")
                    try:
                        city_input = logic.get_auto_location()
                        print(f"Detected City: {city_input}")
                    except Exception as e:
                        print(f"Auto-detect failed ({e}).")
                        city_input = input("\nEnter city name or code manually (e.g., Sydney, Tokyo, LA): ")
                    break
                elif use_auto == 'n':
                    city_input = input("\nEnter city name or code (e.g., Sydney, Tokyo, LA): ")
                    break
                else:
                    print("Please choose (y) or (n)")
                    continue
            
            try:
                # --- SEARCH & SELECT LOGIC ---
                search_results = logic.search_location(city_input, API_KEY)
                
                if len(search_results) == 0:
                    print(f"Could not find any location matching '{city_input}'.")
                    continue # Skips the rest of the loop and goes back to the main menu
                
                # If there are multiple matches, let the user choose
                if len(search_results) > 1:
                    print("\nMultiple locations found. Please select the correct one:")
                    for i, loc in enumerate(search_results):
                        print(f"  {i + 1}. {loc['name']}, {loc['region']}, {loc['country']}")
                    
                    # Loop until the user provides a valid selection
                    while True:
                        try:
                            # Get the user's choice and subtract 1 to match the Python list index
                            choice_idx = int(input("\nSelect a number: ")) - 1
                            
                            # Check if the number is within the valid bounds of the list
                            if 0 <= choice_idx < len(search_results):
                                selected_loc = search_results[choice_idx]
                                break  # Valid choice made, exit the selection loop
                            else:
                                print(f"Invalid selection. Please enter a number between 1 and {len(search_results)}.")
                                
                        except ValueError:
                            # Catches if the user types a letter or leaves it blank
                            print("Invalid input. Please enter a number.")
                else:
                    selected_loc = search_results[0]
                
                # We use the exact latitude and longitude to guarantee 100% accuracy
                exact_coords = f"{selected_loc['lat']},{selected_loc['lon']}"
                
                print(f"\nFetching live weather for {selected_loc['name']}...\n")
                weather_data = logic.get_weather(exact_coords, API_KEY)
                score = logic.calculate_score(weather_data)
                
                # Extracting specific location details
                loc_name = selected_loc['name']
                loc_country = selected_loc['country']
                
                raw_time = weather_data['location']['localtime']
                loc_time = datetime.strptime(raw_time, "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
                
                # Get the randomized advice, and the fact from the text file
                advice = get_advice(score)
                space_fact = get_random_fact()
                
                # Printing the dashboard
                print("-" * 55)
                print(f"Location: {loc_name}, {loc_country}")
                print(f"Local Time: {loc_time}")
                print(f"Score: {score}/10")
                print(f"Advice: {advice}")
                print(f"{space_fact}")
                print("-" * 55 + "\n")
                
                save = input("Do you want to save this to your logbook? (y/n): ").lower()
                if save == 'y':
                    full_location = f"{loc_name}, {loc_country}"
                    data.save_log(full_location, score)
                    print("Saved to logbook!")
                    
            except ValueError:
                print("\nInvalid number selected. Please try again.")
            except Exception as e:
                print(f"\nError: {e}")
                
        elif choice == '2':
            print("\n" + "-"*45)
            print("                YOUR LOGBOOK")
            print("-"*45)
            data.read_history()
            
        elif choice == '3':
            print("\nClear skies! Goodbye.")
            break
            
        else:
            print("\nInvalid choice. Please type 1, 2, or 3.")

if __name__ == "__main__":
    main()