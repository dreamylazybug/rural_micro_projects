import streamlit as st
import requests
from PIL import Image
import numpy as np

# Page Configuration
st.set_page_config(
    page_title="AP & TS Smart Agro-Economic Recommender",
    page_icon="🌱",
    layout="centered"
)

# App Header
st.title("🌱 Smart Crop & Livelihood Recommender")
st.subheader("స్మార్ట్ పంట మరియు ఆర్థిక సిఫార్సు వ్యవస్థ (AP & Telangana)")
st.markdown("Select location, configure multiple water sources, snap a soil photo, and evaluate economic returns and nearest cold storage.")

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
district_tag = selected_location_str.split(",")[1].strip() if "," in selected_location_str else "AP/TS"

@st.cache_data
def get_coordinates(place_name):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={place_name}&count=1&language=en&format=json"
    try:
        res = requests.get(geo_url, timeout=5).json()
        if "results" in res and len(res["results"]) > 0:
            result = res["results"][0]
            return result["latitude"], result["longitude"], result.get("name", place_name)
    except:
        pass
    return 17.3850, 78.4867, place_name

lat, lon, place_found = get_coordinates(place_input)

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

# --- STEP 2: MULTI-SOURCE WATER & HYDROLOGY ---
st.header("2. Water Sources & Hydrology / నీటి వనరులు మరియు హైడ్రాలజీ")

water_sources = st.multiselect(
    "Select all available irrigation sources / లభిస్తున్న అన్ని నీటి పారుదల వనరులను ఎంచుకోండి:",
    [
        "Borewell / Tube well (బోర్‌వెల్ / ట్యూబ్‌వెల్)",
        "Canal Irrigation / Delta Flow (కాల్వ నీరు / ప్రాజెక్ట్)",
        "Tank / Cheruvu (స్థానిక చెరువు నీరు)",
        "Rainfed / Dryland (వర్షాధారితం - నీటి వసతి లేదు)"
    ],
    default=["Borewell / Tube well (బోర్‌వెల్ / ట్యూబ్‌వెల్)"]
)

borewell_depth = 300
power_hours = 9
canal_status = "Normal Flow"
tank_level = "Half Capacity"

with st.expander("⚙️ Configure Parameters for Selected Water Sources / ఎంచుకున్న నీటి వనరుల వివరాలు"):
    if any("Borewell" in src for src in water_sources):
        st.subheader("Borewell Parameters / బోర్‌వెల్ వివరాలు")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            borewell_depth = st.number_input("Borewell Depth (Feet) / లోతు", min_value=100, max_value=1200, value=350, step=50)
        with col_w2:
            power_hours = st.slider("Daily Power Supply (Hours) / విద్యుత్ గంటలు", min_value=3, max_value=24, value=9)

    if any("Canal" in src for src in water_sources):
        st.subheader("Canal Irrigation Parameters / కాల్వ నీటి సరఫరా")
        canal_status = st.selectbox(
            "Canal Water Availability / కాల్వ నీటి లభ్యత స్థితి:",
            ["Normal Rotation / సక్రమంగా అందుతోంది", "Intermittent / Unreliable / అంతరాయం ఉంది", "Tail-end Scarcity / ఆఖరి ఆయకట్టు నీటి కొరత"]
        )

    if any("Tank" in src for src in water_sources):
        st.subheader("Village Tank (Cheruvu) Parameters / స్థానిక చెరువు నీటి మట్టం")
        tank_level = st.selectbox(
            "Tank Storage Level / చెరువులో నీటి నిల్వ:",
            ["Full Tank (Above 75%) / నిండుగా ఉంది", "Moderate (40-75%) / మధ్యస్థంగా ఉంది", "Low / Depleted (<40%) / నీరు తక్కువగా ఉంది"]
        )

    if any("Rainfed" in src for src in water_sources):
        st.info("🌧️ **Rainfed Mode Active:** Recommending in-situ moisture conservation and drought-tolerant crop lines.")

if any("Borewell" in src for src in water_sources) and borewell_depth > 600:
    st.warning("⚠️ **Deep Aquifer Alert:** High pumping cost and depletion risk detected.")

st.divider()

# --- STEP 3: ECONOMIC & INPUT CONSTRAINTS ---
st.header("3. Financials & Inputs / ఆర్థిక మరియు ఎరువుల లభ్యత")

col_e1, col_e2 = st.columns(2)
with col_e1:
    investment_budget = st.selectbox(
        "Available Capital / పెట్టుబడి బడ్జెట్ (per Acre):",
        [
            "Low (< ₹15,000 / Acre - Low Input)",
            "Medium (₹15,000 - ₹35,000 / Acre)",
            "High (> ₹35,000 / Acre - Intensive Commercial)"
        ]
    )
with col_e2:
    fertilizer_mode = st.selectbox(
        "Fertilizer Access / ఎరువుల సేకరణ మార్గం:",
        [
            "RBK Subsidized Stocks Available (రైతు భరోసా కేంద్రం)",
            "Open Market / Local Agro-Dealer Purchase",
            "Organic / Natural Farming (సేంద్రీయ ఎరువులు)"
        ]
    )

st.divider()

# --- STEP 4: CAMERA INPUT FOR SOIL ANALYSIS ---
st.header("4. Soil Visual Capture / నేల ఫోటో క్యాప్చర్")
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
        
    st.info(f"🔍 **AI Soil Classification / నేల గుర్తింపు:** {detected_soil_type}")

st.divider()

# --- STEP 5: RECOMMENDATION ENGINE, RETURNS & NEAREST COLD STORAGE ---
st.header("5. Crop Viability, Returns & Cold Storage / పంట మరియు శీతల గిడ్డంగి వివరాలు")

cold_storage_db = {
    "Guntur": {"name": "M/s Sri Ramanjaneya Cold Storage (Ankireddypalem)", "capacity": "8,650 MT", "distance": "Nearby Mandal Hub"},
    "Krishna": {"name": "M/s Rasana Cold Storage Pvt Ltd (Gollapudi)", "capacity": "5,000 MT", "distance": "Vijayawada Regional Hub"},
    "West Godavari": {"name": "M/s Vijayadurga Cold Storage (Tadepalligudem)", "capacity": "1,500 MT", "distance": "District Hub"},
    "East Godavari": {"name": "M/s Ratna Ice & Cold Storage (Rajahmundry)", "capacity": "1,500 MT", "distance": "Godavari Logistics Hub"},
    "Warangal": {"name": "M/s Supriya Cold Storage / Akshaya Cold Storage", "capacity": "3,000+ MT", "distance": "Warangal Agro Center"},
    "Khammam": {"name": "M/s Gayathri Cold Storage", "capacity": "2,500 MT", "distance": "Khammam Hub"},
    "Anantapur": {"name": "Premier Cold Storage (Hindupur / Anantapur Hub)", "capacity": "5,500 MT", "distance": "Rayalaseema Storage Grid"},
    "YSR Kadapa": {"name": "Madanapalli Cold Storage Hub", "capacity": "2,000 MT", "distance": "District Agro Center"},
    "Nizamabad": {"name": "Nizamabad Regional Seed & Produce Cold Storage", "capacity": "3,000 MT", "distance": "North Telangana Hub"},
    "Karimnagar": {"name": "Karimnagar District Cooperative Cold Storage", "capacity": "2,500 MT", "distance": "Central Hub"}
}

nearest_storage = cold_storage_db.get(district_tag, {"name": "Local District Co-op Cold Storage Facility", "capacity": "Standard 2,000 MT", "distance": "Within District Radius"})

if st.button("Calculate Complete Agronomic & Economic Plan / పూర్తి ప్రణాళికను రూపొందించు", type="primary"):
    is_only_rainfed = len(water_sources) == 0 or ("Rainfed" in water_sources and len(water_sources) == 1)

    if is_only_rainfed:
        if "Red Sandy" in detected_soil_type:
            crop = "Redgram / Kandi Pappu (కందిపప్పు) or Groundnut (వేరుశెనగ)"
            est_return = "₹25,000 – ₹40,000 net return/acre"
        else:
            crop = "Sorghum / Jonna (జొన్నలు) or Pearl Millet (సజ్జలు)"
            est_return = "₹20,000 – ₹35,000 net return/acre"
    elif "Low" in investment_budget:
        crop = "Millets or Pulses / Green Gram (పెసలు)"
        est_return = "₹25,000 – ₹40,000 net return/acre"
    elif "High" in investment_budget and not is_only_rainfed:
        if "Black Cotton" in detected_soil_type:
            crop = "Commercial Cotton (బిటి పత్తి) or Chillies (మిరప)"
            est_return = "₹70,000 – ₹1,20,000 gross return/acre"
        else:
            crop = "Hybrid Paddy / Varalu (వరి) or Maize (మొక్కజొన్న)"
            est_return = "₹50,000 – ₹80,000 gross return/acre"
    else:
        crop = "Redgram / Kandi Pappu (కందిపప్పు) or Groundnut (వేరుశెనగ)"
        est_return = "₹35,000 – ₹55,000 net return/acre"

    # Extract values cleanly prior to f-string display to prevent syntax errors
    storage_name = nearest_storage['name']
    storage_cap = nearest_storage['capacity']
    storage_dist = nearest_storage['distance']
    fertilizer_clean = fertilizer_mode.split('(')[0].strip()

    st.success(f"✅ **Recommended Crop / సిఫార్సు చేయబడిన పంట:** {crop}")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric(label="Estimated Financial Returns", value=est_return)
    with col_r2:
        st.metric(label="Fertilizer Sourcing Channel", value=fertilizer_clean)
        
    st.info(
        f"❄️ **Nearest Cold Storage Facility ({district_tag} Region):**\n"
        f"- **Facility Name:** {storage_name}\n"
        f"- **Capacity:** {storage_cap} | **Proximity:** {storage_dist}\n"
        f"- *Ideal for safe storage of perishable yields, seed preservation, and post-harvest price buffering.*"
    )
            
    st.warning("💡 **Advisory Note:** Verify input subsidies and storage booking slots directly through your local Rythu Bharosa Kendram (RBK).")
