import streamlit as st
import requests
from PIL import Image
import numpy as np

st.set_page_config(page_title="AP & TS Granular Crop Recommender", page_icon="🌱", layout="centered")

st.title("🌱 Granular Smart Crop Recommender")
st.subheader("మండల స్థాయి పంట సిఫార్సు వ్యవస్థ")

st.markdown("Type your Mandal, Town, or Village name to pull precise local weather and elevation.")

# --- GRANULAR LOCATION SEARCH ---
location_input = st.text_input("Enter Mandal / Village Name (e.g., Mangalagiri, Siddipet):", value="Vijayawada")

# Fetch coordinates dynamically using Open-Meteo Geocoding API (Free, no key required)
@st.cache_data
def get_coordinates(place_name):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={place_name}&count=1&language=en&format=json"
    try:
        res = requests.get(geo_url, timeout=5).json()
        if "results" in res and len(res["results"]) > 0:
            result = res["results"][0]
            return result["latitude"], result["longitude"], result.get("name", place_name), result.get("admin1", "AP/TS")
    except:
        pass
    # Default fallback to Hyderabad if search fails
    return 17.3850, 78.4867, "Hyderabad (Default)", "Telangana"

lat, lon, place_found, state_found = get_coordinates(location_input)

# Fetch live weather for these precise coordinates
@st.cache_data
def fetch_weather_data(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m&elevation=true"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        temp = data.get("current", {}).get("temperature_2m", 28.0)
        humidity = data.get("current", {}).get("relative_humidity_2m", 65.0)
        elevation = data.get("elevation", 300.0)
        return temp, humidity, elevation
    except:
        return 28.5, 70.0, 300.0

current_temp, current_humidity, elevation = fetch_weather_data(lat, lon)

st.success(📍 **Found Location:** {place_found} ({state_found}) | **Temp:** {current_temp}°C | **Elevation:** {elevation}m)

st.divider()

# --- CAMERA INPUT FOR SOIL ANALYSIS ---
st.header("2. Soil Visual Capture / నేల ఫోటో క్యాప్చర్")
soil_image_file = st.camera_input("Snap Soil Sample / నేల ఫోటో తీయండి")

detected_soil_type = "Red Sandy Loam (ఎర్ర నేలలు)"
if soil_image_file is not None:
    image = Image.open(soil_image_file)
    st.image(image, caption="Captured Soil Sample", width=300)
    img_array = np.array(image)
    avg_color = img_array.mean(axis=(0, 1))
    
    if avg_color[0] > avg_color[1] + 15:
        detected_soil_type = "Red Sandy Loam / ఎర్ర నేల (Red Chalka)"
    elif avg_color.mean() < 75:
        detected_soil_type = "Black Cotton Soil / నల్ల రేగడి నేల (Regur)"
    else:
        detected_soil_type = "Alluvial Delta Soil / డెల్టా ఒండ్రు నేల"
        
    st.info(🔍 **AI Soil Classification:** {detected_soil_type})

st.divider()

# --- RECOMMENDATION ENGINE ---
st.header("3. Crop Suggestion / పంట సిఫార్సు")
if st.button("Generate Recommendation / సిఫార్సును రూపొందించు", type="primary"):
    if "Black Cotton" in detected_soil_type:
        crop = "Cotton (పత్తి) or Bengal Gram (శనగలు)"
    elif "Red Sandy" in detected_soil_type:
        crop = "Redgram / Kandi Pappu (కందిపప్పు) or Groundnut (వేరుశెనగ)"
    else:
        crop = "Paddy / Varalu (వరి) or Maize (మొక్కజొన్న)"

    st.success(✅ **Recommended Crop / సిఫార్సు చేయబడిన పంట:** {crop})
    st.warning("💡 **Advisory Note:** Consult your local Rythu Bharosa Kendram (RBK) agricultural extension officer.")
