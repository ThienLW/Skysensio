import urllib.request
import urllib.error
import urllib.parse
import json

def search_location(query, api_key):
    """Uses WeatherAPI's lightning-fast search to find matching locations."""
    safe_query = urllib.parse.quote(query)
    url = f"https://api.weatherapi.com/v1/search.json?key={api_key}&q={safe_query}"
    
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        return data # Returns a list of dictionaries with matching locations
        
    except urllib.error.HTTPError as e:
        raise Exception(f"Search Error: {e.code}")
    except urllib.error.URLError:
        raise Exception("Network error. Please check your internet connection.")

def get_weather(query, api_key):
    """Fetches live weather data using an exact query (like lat,lon)."""
    safe_query = urllib.parse.quote(str(query))
    url = f"https://api.weatherapi.com/v1/current.json?key={api_key}&q={safe_query}&aqi=no"
    
    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read().decode('utf-8'))
        return data
        
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise Exception("API Key unauthorized. Please check your key.")
        else:
            raise Exception(f"HTTP Error: {e.code}")
    except urllib.error.URLError:
        raise Exception("Network error while fetching weather.")

    
def get_auto_location():
    """Fetches the user's current city based on their IP address."""
    try:
        # No-key API to keep the zero-setup requirement safe
        response = urllib.request.urlopen("http://ip-api.com/json/")
        data = json.loads(response.read().decode('utf-8'))
        
        if data['status'] == 'success':
            return data['city']
        else:
            raise Exception("Could not determine location from IP.")
            
    except Exception:
        raise Exception("Network error while finding location.")

# Important logic for observing score
def calculate_score(weather_data):
    """
    Calculates a continuous floating-point observing score (1.0 to 10.0)
    using non-linear algorithmic deductions and astronomical thermodynamics.
    """
    # 1. Extract Core Variables (Defensive Extraction)
    current = weather_data.get('current', {})

    """
    We use .get(key, safe_default). If the API breaks, we assume the worst-case 
    scenario for stargazing so the app safely returns a low score instead of crashing.
    """
    clouds = current.get('cloud', 100)               # Default to 100% cloudy
    humidity = current.get('humidity', 100)          # Default to 100% humidity
    visibility_km = current.get('vis_km', 0)         # Default to 0 visibility
    visibility = visibility_km * 1000
    wind_kph = current.get('wind_kph', 100)          # Default to extreme wind
    wind_speed = wind_kph / 3.6
    is_day = current.get('is_day', 1)                # Default to daytime
    precip_mm = current.get('precip_mm', 1.0)        # Default to raining
    
    temp_c = current.get('temp_c', 15.0)             # Default to a standard 15C
    pressure_mb = current.get('pressure_mb', 1000)   # Default to neutral pressure
    dewpoint_c = current.get('dewpoint_c', temp_c - ((100 - humidity) / 5.0))

    # 2. Dealbreaker Checks (Returns exact 1.0)
    if is_day == 1:
        return 1.0
    if precip_mm > 0.0:
        return 1.0

    # 3. The Algorithmic Base Score
    score = 10.0

    # FACTOR A: Cloud Cover (Non-linear Exponential Decay)
    # 20% clouds is manageable, but 80% is catastrophic. We use an exponent of 1.5 
    # so the penalty accelerates as the sky fills up.
    cloud_ratio = clouds / 100.0
    score -= (cloud_ratio ** 1.5) * 6.0

    # FACTOR B: Atmospheric Transparency (Polynomial Visibility)
    # Dropping from 10km to 8km visibility is fine, but dropping from 4km to 2km is terrible.
    # Squaring the ratio creates a harsher penalty for severe haze.
    vis_penalty = ((10000 - visibility) / 10000.0) ** 2 * 2.0
    score -= vis_penalty

    # FACTOR C: Wind Shear & Telescope Vibration (Square of Velocity)
    # The physical force of wind shaking a telescope increases with the square of its speed.
    wind_penalty = min((wind_speed / 5.0) ** 2, 2.0)
    score -= wind_penalty

    # FACTOR D: Thermodynamics & Dew Risk (Temperature vs. Dew Point)
    # Real astronomers watch the "Spread". If the air temperature drops to within 2°C 
    # of the dew point, water will rapidly condense and fog the glass lenses.
    temp_spread = temp_c - dewpoint_c
    if temp_spread < 2.0:
        score -= (2.0 - temp_spread) * 1.5  # Severe penalty for imminent dew
    elif humidity > 85:
        score -= 0.5  # Minor penalty for general atmospheric moisture

    # FACTOR E: Atmospheric Stability (Barometric Bonus)
    # High pressure systems (>1015 mb) generally mean stable, calm, non-turbulent air.
    # This is called good astronomical "seeing".
    if pressure_mb > 1015:
        score += 0.5

    # 4. Final Formatting (Float precision)
    # Clamp the score strictly between 1.0 and 10.0, rounded to 1 decimal place.
    final_score = max(1.0, min(10.0, round(score, 1)))

    return final_score

# --- TESTING BLOCK ---
if __name__ == "__main__":
    print("Testing the Advanced Skysensio Engine...")
    
    
    TEST_API_KEY = "517d684d7d7a4b3da8002621262305" 
    TEST_CITY = "Sydney"
    
    try:
        weather = get_weather(TEST_CITY, TEST_API_KEY)
        final_score = calculate_score(weather)
        print(f"Success! The algorithmic score for {TEST_CITY} is {final_score}/10.")
    except Exception as e:
        print(f"Test Failed: {e}")