# Skysensio: Stop Guessing, Start Gazing

**Course:** COMP9001

**Author:** Thanh Thien Tran

## Overview
Skysensio is a data-driven stargazing dashboard that analyzes real-time atmospheric thermodynamics to provide precise observing recommendations. Built with a dual-engine architecture, it offers both a rich, interactive web interface and a lightweight, offline-capable terminal application.

## Live Demo (Recommended)

Want to skip the installation and jump straight into the stars? The easiest way to experience the full Skysensio dashboard is through our live, cloud-deployed web application. It requires zero setup and works instantly on any device:

**[www.skysensio.space](https://www.skysensio.space)**

---

## Core Features
* **Dual-Engine Architecture:** Runs as a responsive web dashboard or a robust command-line tool.
* **Live Atmospheric Analysis:** Integrates with real-time weather APIs to calculate a custom 1-10 "Observing Score".
* **Cloud-Native Database:** Utilizes Google Sheets as a headless database for secure, persistent data storage across server restarts.
* **Smart Geolocation:** Features reverse-geocoding to automatically detect and map observer coordinates.
* **Secure Login Gate:** Implements a custom authentication wall to protect unique Stargazer IDs and personal observation logs.

## Tech Stack
* **Language:** Python 3
* **Frontend/Framework:** Streamlit
* **Database:** Google Sheets API (`streamlit-gsheets`)
* **APIs:** Weather API, BigDataCloud (Reverse Geocoding)
* **Environment Management:** `python-dotenv`

---

## Setup & Installation

**1. Clone the Repository**
Ensure you are in the project root directory.

**2. Install Dependencies**
Install the required packages using the included requirements file:
```bash
pip install -r requirements.txt
```

---

## How to Run the Application

Skysensio features a unique "dual-engine" architecture, allowing it to be evaluated either as a rich web dashboard or a lightweight command-line tool.

### Option 1: The Web Dashboard (Full UI Experience)
This option launches the complete graphical interface. It includes the interactive map, the cloud-connected Google Sheets logbook, and the session-based security login gate.

To launch the web app, open your terminal, ensure you are in the project folder, and run:
```bash
streamlit run app.py
```

### Option 2: The Terminal Engine (Lightweight Mode)
This option runs the streamlined, text-based version of the application directly in your console. It deliberately bypasses the web server and cloud database, executing the core atmospheric logic and safely saving your observations to a local history.csv file instead.

**Important:** Even in Lightweight Mode, the engine requires live atmospheric data to calculate observing scores. Ensure your `.env` file is properly configured with your `WEATHER_API_KEY` before launching (python-dotenv).

To run the terminal app, use the standard Python command:
```bash
python skysensio.py
```