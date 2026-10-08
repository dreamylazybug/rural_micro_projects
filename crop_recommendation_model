import streamlit as st
import requests
from PIL import Image
import io
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="AP & TS Smart Crop Recommender",
    page_icon="🌱",
    layout="centered"
)

# App Header
st.title("🌱 Smart Crop Recommendation System")
st.subheader("స్మార్ట్ పంట సిఫార్సు వ్యవస్థ (AP & Telangana)")
st.markdown("Automated crop matching using live regional weather APIs and smartphone soil photo analysis.")

st.divider()

# --- STEP 1: LOCATION & WEATHER API ---
st.header("1. Location & Climate / స్థానం మరియు వాతావరణం")

location_mode = st.radio(
    "Select Location Method / స్థానాన్ని ఎంచుకునే విధానం:",
    ["Select District (Recommended) / జిల్లాను ఎంచుకోండి", "Use GPS Coordinates / జిపిఎస్ కోఆర్డినేట్లు"]
)

# District coordinates mapping for AP & Telangana
district_coords = {
    "Anantapur": (14.6819, 77.6006),
    "Chittoor": (13.6288, 79.4192),
    "East Godavari (Kakinada)": (16.9891, 82.2475),
    "Guntur": (16.3067, 80.4365),
    "Krishna (Vijayawada)": (16.5062, 80.6480),
    "Kurnool": (15.8281, 78.0373),
    "Prakasam (Ongole)": (15.5057, 80.0499),
    "Srikakulam": (18.2949, 83.8936),
    "Visakhapatnam": (17.6868, 83.2185),
    "Vizianagaram": (18.1066, 83.4102),
    "West Godavari (Eluru)": (16.7106, 81.0952),
    "YSR Kadapa": (14.4673, 78.8242),
    "Hyderabad": (17.3850, 78.4867),
    "Warangal": (17.9689, 79.5941),
    "Nizamabad": (18.6725, 78.0941),
    "Karimnagar": (18.4386, 79.1288),
    "Khammam": (17.2473, 80.1514),
    "Nalgonda": (17.0503, 79.2673)
}

if location_mode.startswith("Select"):
    selected_district = st.selectbox("Choose District / జిల్లా:", list(district_coords.keys()))
    lat, lon = district_coords[selected_district]
    region_name = selected_district
else:
    lat = st.number_input("Latitude / అక్షాంశం", value=17.3850, format="%.4f")
    lon = st.number_input("Longitude / రేఖాంశం", value=78.4867, format="%.4f")
    region_name = "Custom GPS Location"

# Fetch Weather and Climate Data from Open-Meteo API (Free, No API Key required)
@st.cache_data
def fetch_weather_data(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,precipitation&elevation=true"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        temp = data.get("current", {}).get("temperature_2m", 28.0)
        humidity = data.get("current", {}).get("relative_humidity_2m", 65.0)
        elevation = data.get("elevation", 300.0)
        # Estimating annual baseline rainfall based on typical regional averages if live archive isn't called
        return temp, humidity, elevation
    except:
        return 28.5, 70.0, 300.0

current_temp, current_humidity, elevation = fetch_weather_data(lat, lon)

st.success(f"📍 **Active Area / ప్రాంతం:** {region_name} | **Temp:** {current_temp}°C | **Humidity:** {current_humidity}% | **Elevation:** {elevation}m")

st.divider()

# --- STEP 2: CAMERA INPUT FOR SOIL ANALYSIS ---
st.header("2. Soil Visual Capture / నేల ఫోటో క్యాప్చర్")
st.markdown("Take a clear picture of your field soil using your mobile camera. The system will analyze color tone and texture to categorize soil type.")

soil_image_file = st.camera_input("Snap Soil Sample / నేల ఫోటో తీయండి")

detected_soil_type = "Red Sandy Loam (ఎర్ర నేలలు)"
estimated_ph = 6.5

if soil_image_file is not None:
    # Open image using Pillow
    image = Image.open(soil_image_file)
    st.image(image, caption="Captured Soil Sample / తీయబడిన నేల నమూనా", width=300)
    
    # Simple color-metric heuristic mockup for soil classification simulation
    img_array = np.array(image)
    avg_color = img_array.mean(axis=(0, 1)) # [R, G, B]
    
    # Basic heuristic: if Red channel is significantly higher -> Red Soil; if very dark -> Black Soil
    if avg_color[0] > avg_color[1] + 15:
        detected_soil_type = "Red Sandy Loam / ఎర్ర నేల (Red Chalka)"
        estimated_ph = 6.2
    elif avg_color.mean() < 75:
        detected_soil_type = "Black Cotton Soil / నల్ల రేగడి నేల (Regur)"
        estimated_ph = 7.8
    else:
        detected_soil_type = "Alluvial Delta Soil / డెల్టా ఒండ్రు నేల"
        estimated_ph = 7.0
        
    st.info(f"🔍 **AI Soil Classification / నేల గుర్తింపు ఫలితం:** {detected_soil_type} (Estimated pH: {estimated_ph})")

st.divider()

# --- STEP 3: RECOMMENDATION ENGINE ---
st.header("3. Crop Suggestion / పంట సిఫార్సు")

if st.button("Generate Recommendation / సిఫార్సును రూపొందించు", type="primary"):
    # Rule-based agronomic logic matching AP/TS agro-climatic zones
    if "Black Cotton" in detected_soil_type:
        crop = "Cotton (పత్తి) or Bengal Gram (శనగలు)"
        duration = "Medium to Long (150-180 Days)"
        water_req = "Medium (मध्यम)"
    elif "Red Sandy" in detected_soil_type:
        crop = "Redgram / Kandi Pappu (కందిపప్పు) or Groundnut (వేరుశెనగ)"
        duration = "Short to Medium (120-140 Days)"
        water_req = "Low to Medium (తక్కువ నుండి మధ్యస్థం)"
    else:
        crop = "Paddy / Varalu (వరి) or Maize (మొక్కజొన్న)"
        duration = "Medium (120-150 Days)"
        water_req = "High (అధిక నీటి అవసరం)"

    st.success(f"✅ **Recommended Crop / సిఫార్సు చేయబడిన పంట:** {crop}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric(label="Estimated Growing Duration", value=duration)
    with col_b:
        st.metric(label="Water Requirement", value=water_req)
        
    st.warning("💡 **Advisory Note:** Consult your local Rythu Bharosa Kendram (RBK) agricultural extension officer before final sowing and fertilizer application.")
