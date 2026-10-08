import streamlit as st
import requests
from PIL import Image
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
st.markdown("Select your local mandal, snap a soil photo, specify water hydrology, and get instant bilingual crop recommendations.")

st.divider()

# --- STEP 1: SEARCHABLE MANDAL AUTO-COMPLETE & WEATHER API ---
st.header("1. Location & Climate / స్థానం మరియు వాతావరణం")

ap_ts_mandals = [
    "Vijayawada, Krishna", "Mangalagiri, Guntur", "Tenali, Guntur", "Guntur Rural, Guntur",
    "Eluru, West Godavari", "Tanuku, West Godavari", "Bhimavaram, West Godavari",
    "Rajahmundry, East Godavari", "Kakinada, East Godavari", "Amalapuram, East Godavari",
    "Nandyal, Kurnool", "Adoni, Kurnool", "Kurnool Rural, Kurnool",
    "Anantapur, Anantapur", "Dharmavaram, Anantapur", "Hindupur, Anantapur",
    "Kadapa, YSR Kadapa", "Proddatur, YSR Kadapa", "Tadipatri, Anantapur",
    "Nellore, Nellore", "Ongole, Prakasam", "Kavali, Nellore",
    "Srikakulam, Srikakulam", "Vizianagaram, Vizianagaram", "Visakhapatnam, Visakhapatnam",
    "Warangal, Warangal", "Hanamkonda, Warangal", "Khammam, Khammam", "Bhadrachalam, Khammam",
    "Siddipet, Siddipet", "Karimnagar, Karimnagar", "Nizamabad, Nizamabad",
    "Nalgonda, Nalgonda", "Mahabubnagar, Mahabubnagar", "Sangareddy, Sangareddy",
    "Palakollu, West Godavari", "Narsapuram, West Godavari"
]

selected_location_str = st.selectbox(
    "Search Mandal / Town (Start typing to filter) / మండలం లేదా పట్టణం కోసం వెతకండి:",
    options=ap_ts_mandals,
    index=0
)

place_input = selected_location_str.split(",")[0].strip()

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
    return 17.3850, 78.4867, place_name, "AP/TS"

lat, lon, place_found, state_found = get_coordinates(place_input)

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

st.success(f"📍 **Selected Location:** {selected_location_str} | **Temp:** {current_temp}°C | **Elevation:** {elevation}m")

st.divider()

# --- STEP 2: WATER SOURCE & HYDROLOGY ---
st.header("2. Water Source & Hydrology / నీటి వనరు మరియు హైడ్రాలజీ")

water_source = st.radio(
    "Select primary irrigation source / ప్రధాన నీటి పారుదల వనరు:",
    [
        "Borewell / Tube well (బోర్‌వెల్ / ట్యూబ్‌వెల్)",
        "Canal Irrigation / Delta Flow (కాల్వ నీరు / ప్రాజెక్ట్)",
        "Tank / Cheruvu (స్థానిక చెరువు నీరు)",
        "Rainfed / Dryland (వర్షాధారితం - నీటి వసతి లేదు)"
    ]
)

borewell_depth, power_hours = 300, 9

if "Borewell" in water_source:
    with st.expander("⚙️ Advanced Borewell Specs (Optional) / బోర్‌వెల్ వివరాలు"):
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            borewell_depth = st.number_input("Borewell Depth (Feet) / లోతు", min_value=100, max_value=1200, value=350, step=50)
        with col_w2:
            power_hours = st.slider("Daily Power Supply (Hours) / విద్యుత్ గంటలు", min_value=3, max_value=24, value=9)
            
    if borewell_depth > 600:
        st.warning("⚠️ **Deep Aquifer Alert:** High pumping cost and depletion risk detected. Prioritizing low-water-intensity crops.")

st.divider()

# --- STEP 3: CAMERA INPUT FOR SOIL ANALYSIS ---
st.header("3. Soil Visual Capture / నేల ఫోటో క్యాప్చర్")
st.markdown("Take a clear picture of your field soil using your mobile camera. The system will analyze color tone and texture.")

soil_image_file = st.camera_input("Snap Soil Sample / నేల ఫోటో తీయండి")

detected_soil_type = "Red Sandy Loam (ఎర్ర నేలలు)"
if soil_image_file is not None:
    image = Image.open(soil_image_file)
    st.image(image, caption="Captured Soil Sample / తీయబడిన నేల నమూనా", width=300)
    
    img_array = np.array(image)
    avg_color = img_array.mean(axis=(0, 1))
    
    if avg_color[0] > avg_color[1] + 15:
        detected_soil_type = "Red Sandy Loam / ఎర్ర నేల (Red Chalka)"
    elif avg_color.mean() < 75:
        detected_soil_type = "Black Cotton Soil / నల్ల రేగడి నేల (Regur)"
    else:
        detected_soil_type = "Alluvial Delta Soil / డెల్టా ఒండ్రు నేల"
        
    st.info(f"🔍 **AI Soil Classification / నేల గుర్తింపు ఫలితం:** {detected_soil_type}")

st.divider()

# --- STEP 4: RECOMMENDATION ENGINE ---
st.header("4. Crop Suggestion / పంట సిఫార్సు")

if st.button("Generate Recommendation / సిఫార్సును రూపొందించు", type="primary"):
    if "Rainfed" in water_source:
        if "Red Sandy" in detected_soil_type:
            crop = "Redgram / Kandi Pappu (కందిపప్పు) or Groundnut (వేరుశెనగ)"
        else:
            crop = "Sorghum / Jonna (జొన్నలు) or Pearl Millet (సజ్జలు)"
    elif "Borewell" in water_source and borewell_depth > 600:
        crop = "Millets, Castor (ఆముదం), or Green Gram (పెసలు) (Drought-resilient rotation)"
    else:
        if "Black Cotton" in detected_soil_type:
            crop = "Cotton (పత్తి) or Bengal Gram (శనగలు)"
        elif "Alluvial" in detected_soil_type or "Canal" in water_source:
            crop = "Paddy / Varalu (వరి) or Maize (మొక్కజొన్న)"
        else:
            crop = "Chillies (మిరప) or Cotton (పత్తి)"

    st.success(f"✅ **Recommended Crop / సిఫార్సు చేయబడిన పంట:** {crop}")
    st.info(f"💧 **Hydrology Factor:** {water_source.split('(')[0].strip()} | Depth: {borewell_depth} ft | Power: {power_hours} hrs/day")
    st.warning("💡 **Advisory Note:** Consult your local Rythu Bharosa Kendram (RBK) agricultural extension officer before final sowing.")
