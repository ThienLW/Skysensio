import streamlit as st
import logic
import data
import random
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from PIL import Image

# --- SECURE API LOADING ---
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

if not API_KEY:
    st.error("Missing API Key! Please check your .env file or Streamlit Secrets.")
    st.stop()

# --- HELPER FUNCTIONS ---
def get_advice(score):
    """Returns randomized stargazing advice based on the final score."""
    if score >= 9.0:
        return random.choice(["Pristine conditions. Set up the telescope immediately!", "Incredible skies tonight. Perfect for nebulae and galaxies."])
    elif score >= 6.0:
        return random.choice(["Good conditions. Great night for viewing bright targets like the Moon and planets.", "Solid skies. Planetary details will be visibly stunning."])
    elif score >= 3.0:
        return random.choice(["Sub-optimal. High clouds or wind. Stick to binoculars or wide-field observing.", "Tough conditions for a telescope. Focus on bright constellations."])
    else:
        return random.choice(["Stargazing is currently impossible. Perfect time to clean your lenses!", "Dealbreaker conditions. Stay inside and study star charts."])

im = Image.open("Skysensio_logo.png")

# --- UI CONFIGURATION & CSS ANIMATION ---
st.set_page_config(
    page_title="Skysensio Dashboard", 
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded"
)

def set_background():
    st.markdown("""
    <style>
    /* The Deep Space Background */
    [data-testid="stAppViewContainer"] {
        background-color: #050814; 
        background-image: 
            radial-gradient(1.5px 1.5px at 100px 50px, rgba(255, 255, 255, 0.9), transparent),
            radial-gradient(2px 2px at 200px 150px, rgba(255, 255, 255, 0.8), transparent),
            radial-gradient(1.5px 1.5px at 300px 90px, rgba(255, 255, 255, 1), transparent),
            radial-gradient(2.5px 2.5px at 400px 250px, rgba(255, 255, 255, 0.7), transparent),
            radial-gradient(1px 1px at 50px 300px, rgba(255, 255, 255, 0.6), transparent),
            radial-gradient(2px 2px at 150px 400px, rgba(255, 255, 255, 0.9), transparent),
            radial-gradient(1.5px 1.5px at 350px 450px, rgba(255, 255, 255, 0.8), transparent);
        background-size: 500px 500px;
        animation: animateStars 10s linear infinite;
    }
    
    [data-testid="stHeader"] { background-color: transparent !important; }

    @keyframes animateStars {
        0% { background-position: 0 0; }
        100% { background-position: 500px 500px; } 
    }

    /* Force text to be readable starlight-white */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp label {
        color: #E2E8F0 !important; 
    }

    /* --- INPUT BOX UI --- */
    [data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: #0F172A !important; 
        border: 1px solid #38BDF8 !important;
        box-shadow: 0 0 8px rgba(56, 189, 248, 0.5) !important;
        border-radius: 6px !important;
    }
    [data-testid="stTextInput"] input {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important; 
    }
    [data-testid="stTextInput"] div[data-baseweb="base-input"]:focus-within {
        box-shadow: 0 0 18px rgba(56, 189, 248, 0.9) !important;
        border-color: #7DD3FC !important;
    }

    /* Beautiful Glowing Nebula Buttons */
    div[data-testid="stButton"] > button, div[data-testid="stFormSubmitButton"] > button {
        background: linear-gradient(135deg, #1e3a8a 0%, #312e81 100%) !important;
        color: #ffffff !important;
        border: 1px solid #60a5fa !important;
        box-shadow: 0 0 10px rgba(96, 165, 250, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s ease !important;
        width: 100% !important; 
    }
    
    div[data-testid="stButton"] > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: #93c5fd !important;
        box-shadow: 0 0 20px rgba(147, 197, 253, 0.8) !important;
        transform: translateY(-2px); 
    }

    /* Glass-morphism panels */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 15, 30, 0.75) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    [data-testid="metric-container"] {
        background-color: rgba(20, 25, 40, 0.6) !important;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        padding: 15px !important; 
    }

    /* --- EXPANDER --- */
    [data-testid="stExpander"] details {
        background-color: #0F172A !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        border-radius: 8px !important;
    }
    [data-testid="stExpander"] summary, 
    [data-testid="stExpander"] summary p, 
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        background-color: #0F172A !important;
        color: #FFFFFF !important;
        fill: #FFFFFF !important;
        border-radius: 8px !important;
    }
                
    /* --- PULL MAIN CONTENT UP --- */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
        z-index: 1;
    }
                
    /* --- FORM HINT TEXT --- */
    div[data-baseweb="base-input"] > div {
        color: #94A3B8 !important; 
        font-weight: 500 !important;
    }
    div[data-baseweb="base-input"] input::placeholder {
        color: #64748B !important; 
        opacity: 0.7 !important;   
        font-style: italic !important; 
    }
    /* --- HIDE THE GEOLOCATION TEXT BOX --- */
    [data-testid="stSidebar"] iframe {
        width: 44px !important;  
        height: 44px !important; 
        border-radius: 5px !important;
        border: 1px solid #38BDF8 !important;
        filter: invert(1) hue-rotate(180deg) brightness(1.2) !important; 
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.4) !important;
        transition: all 0.3s ease !important;
        overflow: hidden !important;
    }
    
    [data-testid="stSidebar"] iframe:hover {
        box-shadow: 0 0 20px rgba(147, 197, 253, 0.9) !important;
        transform: scale(1.05);
    }
    /* --- FIX THE WHITE SPINNERS --- */
    div[data-testid="stSpinner"] > div {
        background-color: #0F172A !important;
        border: 1px solid #38BDF8 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }
    div[data-testid="stSpinner"] p {
        color: #7DD3FC !important;
        font-family: monospace !important; /* Gives the raw python text a cool terminal look */
        font-weight: 500 !important;
    }
    </style>
    """, unsafe_allow_html=True)

set_background()

# --- STATE MANAGEMENT ---
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'active_location' not in st.session_state:
    st.session_state.active_location = None
    
# NEW: Session variables to control the Login Gate
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = ""
if 'current_pin' not in st.session_state:
    st.session_state.current_pin = ""

# Session variable to reset the GPS button
if 'gps_visible' not in st.session_state:
    st.session_state.gps_visible = True

# --- MAIN TITLE (Renders for everyone) ---
st.title("Skysensio: Stop Guessing, Start Gazing")
st.markdown(f"**Random Space Fact:** *{data.get_random_fact()}*")
st.divider()

# --- SIDEBAR: THE LOGIN GATE ---
with st.sidebar:
    st.sidebar.image("Skysensio_logo.png", width=200, caption="SKYSENSIO - COMP9001")
    st.markdown("---")
    st.markdown("**Version 1.0**")
    
    if not st.session_state.authenticated:
        st.subheader("Observer Login")
        st.caption("Enter any Name and PIN to create a new profile, or use an existing one to unlock your saved cloud logs.")
        
        login_user = st.text_input("Stargazer ID:", value="", placeholder="e.g., Tian").strip().lower()
        login_pin = st.text_input("PIN:", value="", placeholder="e.g., 0203", type="password").strip().lower()
        
        # The Authentication Button
        if st.button("Access Observatory", use_container_width=True):
            if login_user == "" or login_pin == "":
                st.warning("Please enter both an ID and a PIN.")
            else:
                with st.spinner("Authenticating..."):
                    # Check the database via data.py
                    is_valid = data.validate_user(login_user, login_pin)
                    
                    if is_valid:
                        # Success! Lock in the session state
                        st.session_state.authenticated = True
                        st.session_state.current_user = login_user
                        st.session_state.current_pin = login_pin
                        st.rerun() # Refresh the page to unlock the dashboard
                    else:
                        st.error(f"The ID '{login_user}' is already taken. Please enter the correct PIN.")

# --- THE SECURITY WALL ---
if not st.session_state.authenticated:
    st.info("Please log in using the sidebar to access the observatory dashboard and your personal logbook.", icon=":material/lock:")
    st.stop() # This halts the entire app here if they aren't logged in!

# =====================================================================
# EVERYTHING BELOW THIS LINE ONLY RUNS IF THE USER IS AUTHENTICATED
# =====================================================================

with st.sidebar:
    # Show who is logged in and provide a Logout button
    st.success(f"Welcome back, {st.session_state.current_user.capitalize()}!")
    if st.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.current_user = ""
        st.session_state.current_pin = ""
        st.session_state.search_results = []
        st.session_state.active_location = None
        st.rerun()
        
    st.markdown("---")
    st.subheader("Location Search")
    
    with st.form(key="search_form"):
        city_input = st.text_input("Enter city (e.g., Sydney, Tokyo):")
        submit_button = st.form_submit_button("Search Database")
    
    if submit_button:
        if city_input:
            with st.spinner("Scanning coordinates..."):
                st.session_state.search_results = logic.search_location(city_input, API_KEY)
                st.session_state.active_location = None  
                
                # Briefly hide the GPS button to permanently wipe its memory
                st.session_state.gps_visible = False
                
                if not st.session_state.search_results:
                    st.warning("No matches found.")
        else:
            st.warning("Please enter a city name.")

    # --- TRUE CLOUD-SAFE GPS DETECTION WITH REVERSE GEOCODING ---
    st.markdown("<p style='text-align: center; margin: 10px 0; color: #64748B;'>— OR —</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9rem; color: #E2E8F0; margin-bottom: 10px;'>Auto-Detect Location</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.session_state.gps_visible:
            # Load the component normally without the 'key' argument
            location = streamlit_geolocation()
        else:
            # Provide empty data while it is hidden, and immediately turn it back on
            location = {'latitude': None, 'longitude': None}
            st.session_state.gps_visible = True
    
    if location['latitude'] is not None and location['longitude'] is not None:
        with st.spinner("Analyzing local sky coordinates..."):
            try:
                lat = location['latitude']
                lon = location['longitude']
                
                geo_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
                geo_data = requests.get(geo_url).json()
                
                detected_city = geo_data.get("city") or geo_data.get("locality") or "Unknown City"
                detected_country = geo_data.get("countryName") or "Unknown Country"
                
                st.session_state.search_results = [{
                    "name": detected_city,
                    "country": detected_country,
                    "lat": lat,
                    "lon": lon
                }]
                st.session_state.active_location = st.session_state.search_results[0]
            except Exception as e:
                st.error("Could not process GPS coordinates.")

# --- MAIN DASHBOARD AREA ---
tab1, tab2 = st.tabs(["Live Analysis", "My Logbook"])

with tab1:
    st.markdown("### Current Observing Conditions")
    
    if st.session_state.search_results:
        if len(st.session_state.search_results) == 1:
            st.session_state.active_location = st.session_state.search_results[0]
            st.success(f"Perfect match found: **{st.session_state.active_location['name']}, {st.session_state.active_location['country']}**")
        else:
            options = [f"{loc['name']}, {loc['country']}" for loc in st.session_state.search_results]
            selected_str = st.selectbox("Multiple matches found. Confirm specific location:", options)
            
            if st.button("Calculate Observing Score"):
                choice_idx = options.index(selected_str)
                st.session_state.active_location = st.session_state.search_results[choice_idx]

        # --- THE ENGINE ---
        if st.session_state.active_location:
            selected_loc = st.session_state.active_location
            exact_coords = f"{selected_loc['lat']},{selected_loc['lon']}"
            
            # 1. Check if we need to run the API, or if we already memorized it!
            if 'last_coords' not in st.session_state or st.session_state.last_coords != exact_coords:
                with st.spinner('Calculating atmospheric thermodynamics...'):
                    try:
                        weather_data = logic.get_weather(exact_coords, API_KEY)
                        score = logic.calculate_score(weather_data)
                        loc_time = datetime.strptime(weather_data['location']['localtime'], "%Y-%m-%d %H:%M").strftime("%d/%m/%Y %H:%M")
                        advice = get_advice(score)
                        
                        # Save the calculation results into session memory
                        st.session_state.current_analysis = {
                            "score": score,
                            "loc_time": loc_time,
                            "advice": advice
                        }
                        # Update the memorized coordinates
                        st.session_state.last_coords = exact_coords
                        
                    except Exception as e:
                        st.error(f"Error during analysis: {e}")
                        st.stop() # Halts execution if the API fails
            
            # 2. Render the UI using the memorized data (No spinner on re-runs!)
            if 'current_analysis' in st.session_state:
                analysis = st.session_state.current_analysis
                score = analysis["score"]
                loc_time = analysis["loc_time"]
                advice = analysis["advice"]
                
                st.markdown("---")
                st.markdown(f"#### Stargazing Analysis for {selected_loc['name']}")
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Location", selected_loc['name'], f"{selected_loc['country']}")
                col2.metric("Local Date", loc_time.split(" ")[0], loc_time.split(" ")[1])
                col3.metric("Observing Score", f"{score}/10")
                
                st.markdown("---")
                
                with st.expander("Final Advice & Details", expanded=True):
                    st.markdown(f"**Advice:** {advice}")
                
                st.markdown(" ") 
                if st.button("Save Observation to Logbook"):
                    full_location = f"{selected_loc['name']}, {selected_loc['country']}"
                    
                    # We securely save using the locked-in session variables
                    data.save_log(full_location, score, st.session_state.current_user, st.session_state.current_pin)
                    st.toast("Observation securely logged!", icon=":material/check_circle:")
    else:
        st.info("Use the sidebar to search for a city and begin your analysis.")

with tab2:
    # Pull the display name directly from the locked session state
    user_name = st.session_state.current_user.capitalize()
    st.markdown(f"### {user_name}'s Secured Logbook")
    
    # Read using the locked session variables
    df = data.get_user_logs(st.session_state.current_user, st.session_state.current_pin)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        total_logs = len(df)
        average_score = df["Score"].astype(str).str.extract(r'([\d.]+)')[0].astype(float).mean()
        
        st.markdown("---")
        col1, col2 = st.columns(2)
        col1.metric("Total Recorded Observations", total_logs)
        col2.metric("Average Observing Score", f"{average_score:.1f}")
            
    else:
        st.warning(f"No logs found for {user_name}. Start gazing to build your logbook!")