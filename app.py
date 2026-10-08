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
st.markdown("Select location in English/Telugu, configure water sources, snap a soil photo, and evaluate complete bilingual crop advisories and cold storage.")

st.divider()

# --- STEP 1: BILINGUAL MANDAL AUTO-COMPLETE & WEATHER API ---
st.header("1. Location & Climate / స్థానం మరియు వాతావరణం")

ap_ts_mandals = [
    "Vijayawada (విజయవాడ), Krishna", "Mangalagiri (మంగళగిరి), Guntur", "Tenali (తెనాలి), Guntur", "Guntur Rural (గుంటూరు గ్రామీణ), Guntur",
    "Eluru (ఏలూరు), West Godavari", "Tanuku (తణుకు), West Godavari", "Bhimavaram (భీమవరం), West Godavari",
    "Rajahmundry (రాజమహేంద్రవరం), East Godavari", "Kakinada (కాకినాడ), East Godavari", "Amalapuram (అమలాపురం), East Godavari",
    "Nandyal (నంద్యాల), Kurnool", "Adoni (ఆదోని), Kurnool", "Kurnool Rural (కర్నూలు గ్రామీణ), Kurnool",
    "Anantapur (అనంతపురం), Anantapur", "Dharmavaram (ధర్మవరం), Anantapur", "Hindupur (హిందూపూర్), Anantapur",
    "Kadapa (కడప), YSR Kadapa", "Proddatur (ప్రొద్దుటూరు), YSR Kadapa", "Tadipatri (తాడిపత్రి), Anantapur",
    "Nellore (నెల్లూరు), Nellore", "Ongole (ఒంగోలు), Prakasam", "Kavali (కావలి), Nellore",
    "Srikakulam (శ్రీకాకుళం), Srikakulam", "Vizianagaram (విజయనగరం), Vizianagaram", "Visakhapatnam (విశాఖపట్నం), Visakhapatnam",
    "Warangal (వరంగల్), Warangal", "Hanamkonda (హనుమకొండ), Warangal", "Khammam (ఖమ్మం), Khammam", "Bhadrachalam (భద్రాచలం), Khammam",
    "Siddipet (సిద్దిపేట), Siddipet", "Karimnagar (కరీంనగర్), Karimnagar", "Nizamabad (నిజామాబాద్), Nizamabad",
    "Nalgonda (నల్గొండ), Nalgonda", "Mahabubnagar (మహబూబ్‌నగర్), Mahabubnagar", "Sangareddy (సంగారెడ్డి), Sangareddy",
    "Palakollu (పాలకొల్లు), West Godavari", "Narsapuram (నరసాపురం), West Godavari"
]

selected_location_str = st.selectbox(
    "Search Mandal / Town (Start typing to filter) / మండలం లేదా పట్టణం కోసం వెతకండి:",
    options=ap_ts_mandals,
    index=0
)

place_input = selected_location_str.split("(")[0].strip()
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
st.success(f"📍 **Selected Location / ఎంచుకున్న ప్రాంతం:** {selected_location_str} | **Temp:** {current_temp}°C | **Elevation:** {elevation}m")

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
            borewell_depth = st.number_input("Borewell Depth (Feet) / లోతు", min_value=100, max_value=1200, value=350, step, 50)
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
        st.info("🌧️ **Rainfed Mode Active / వర్షాధారిత విధానం:** Recommending in-situ moisture conservation and drought-tolerant crop lines.")

if any("Borewell" in src for src in water_sources) and borewell_depth > 600:
    st.warning("⚠️ **Deep Aquifer Alert / లోతైన భూగర్భ జల హెచ్చరిక:** High pumping cost and depletion risk detected.")

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
            "RBK Subsidized Stocks Available (రైతు భరోసా కేంద్రం సబ్సిడీ ఎరువులు)",
            "Open Market / Local Agro-Dealer Purchase (ఓపెన్ మార్కెట్ / స్థానిక డీలర్)",
            "Organic / Natural Farming (సేంద్రీయ / ప్రకృతి వ్యవసాయ ఎరువులు)"
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

# --- STEP 5: BILINGUAL COMPREHENSIVE AGRONOMIC & ECONOMIC ADVISORY ---
st.header("5. Complete Crop Advisory & Livelihood Plan / పూర్తి పంట మరియు ఆర్థిక సలహా")

crop_advisory_db = {
    "Redgram": {
        "telugu": "కందిపప్పు / కంది పంట (Redgram)",
        "sowing": "June – July / జూన్ – జూలై (With onset of Southwest Monsoon / తొలి తొలకరి వర్షాలు)",
        "harvest": "December – January / డిసెంబర్ – జనవరి (150-180 Days / రోజులు)",
        "yield": "6 - 8 Quintals / Acre (క్వింటాళ్లు / ఎకరా)",
        "fertilizers": "Basal dose: 20 kg N, 40 kg P2O5 per acre. Foliar spray of 2% Urea at flowering.\n*తెలుగు వివరాలు:* ఎకరానికి 20 కిలోల నత్రజని, 40 కిలోల భాస్వరం అందించాలి. పూత దశలో 2% యూరియా పిచికారీ చేయాలి.",
        "pests": "Pod Borer & Maruca. Mitigation: Spray Chlorantraniliprole or Neem oil.\n*తెలుగు వివరాలు:* కాయ తొలుచు పురుగు (శనగ పచ్చ పురుగు). నివారణ: క్లోరాంట్రానిలిప్రోల్ లేదా వేప నూనె పిచికారీ చేయాలి.",
        "issues": "Sensitive to waterlogging; requires well-drained red soils.\n*తెలుగు వివరాలు:* నీరు నిల్వ ఉండటాన్ని తట్టుకోలేదు; నీరు ఇంకిపోయే ఎర్ర నేలలు అనుకూలం."
    },
    "Groundnut": {
        "telugu": "వేరుశెనగ / వేరుశనగ కాయ (Groundnut)",
        "sowing": "July (Kharif) or November (Rabi) / జూలై (ఖరీఫ్) లేదా నవంబర్ (రబీ)",
        "harvest": "October (Kharif) / March (Rabi) (105-120 Days / రోజులు)",
        "yield": "8 - 10 Quintals / Acre (Shell kernels / కాయ దిగుబడి)",
        "fertilizers": "Gypsum @ 200 kg/acre at flowering stage for pod filling; 16-20-0 NPK base.\n*తెలుగు వివరాలు:* కాయ గట్టిపడే దశలో ఎకరానికి 200 కిలోల జిప్సమ్ వేయాలి; 16-20-0 ఎన్పీకే బేస్.",
        "pests": "Leaf Miner & Collar Rot. Mitigation: Seed treatment with Trichoderma; neem-based sprays.\n*తెలుగు వివరాలు:* ఆకు ముడుత పురుగు మరియు వేరు కుళ్ళు తెగులు. నివారణ: ట్రైకోడెర్మాతో విత్తన శుద్ధి మరియు వేప మందుల పిచికారీ.",
        "issues": "Terminal drought vulnerability; requires critical irrigation at pegging stage.\n*తెలుగు వివరాలు:* చివరి దశలో కరువు ప్రమాదం ఉంది; పిందె దశలో తప్పనిసరిగా తడి ఇవ్వాలి."
    },
    "Cotton": {
        "telugu": "బిటి పత్తి / పత్తి పంట (Bt Cotton)",
        "sowing": "June – July (Rainfed/Irrigated) / జూన్ – జూలై (వర్షాధారితం / నీటి వసతి)",
        "harvest": "November – February (Multi-picking over 150-180 Days)\n*తెలుగు వివరాలు:* నవంబర్ – ఫిబ్రవరి (150-180 రోజుల్లో విడతల వారీగా ఏరుకోలు)",
        "yield": "10 - 15 Quintals / Acre (Seed cotton / పత్తి దిగుబడి)",
        "fertilizers": "Balanced NPK (120:60:60 kg/ha split across 4 stages) + Magnesium Sulphate spray.\n*తెలుగు వివరాలు:* సమతుల్య ఎరువులు (120:60:60 కిలోలు/హెక్టారుకు 4 విడతలుగా) + మెగ్నీషియం సల్ఫేట్ పిచికారీ.",
        "pests": "Pink Bollworm & Sucking Pests. Mitigation: Pheromone traps (5/acre), Flonicamid sprays.\n*తెలుగు వివరాలు:* గులాబీ రంగు ఆశించే పురుగు మరియు రసపీల్చు పురుగులు. నివారణ: లింగాకర్షక బుట్టలు (ఎకరానికి 5), ఫ్లోనికామిడ్ పిచికారీ.",
        "issues": "High capital investment required; strict pesticide resistance management needed.\n*తెలుగు వివరాలు:* ఎక్కువ పెట్టుబడి అవసరం; పురుగు మందుల నిరోధకతను నిర్వహించడం ముఖ్యం."
    },
    "Paddy": {
        "telugu": "వరి / ధాన్యం పంట (Paddy / Rice)",
        "sowing": "July (Kharif) / January (Rabi) / జూలై (ఖరీఫ్ - వానకాలం) / జనవరి (రబీ - యాసంగి)",
        "harvest": "November / April (120-140 Days / రోజులు)",
        "yield": "22 - 28 Quintals / Acre (Raw paddy / ముడి ధాన్యం)",
        "fertilizers": "Split application of Nitrogen (N) across basal, tillering, and panicle initiation stages.\n*తెలుగు వివరాలు:* నత్రజని ఎరువును దుక్కిలో, పిలకల దశలో మరియు తిలక దశలో విడతల వారీగా అందించాలి.",
        "pests": "Stem Borer & Brown Planthopper (BPH). Mitigation: Light traps, cartap hydrochloride granules.\n*తెలుగు వివరాలు:* కాండం తొలుచు పురుగు మరియు ఆశించే సుడి దోమ. నివారణ: కాంతి బుట్టలు, కార్టాప్ హైడ్రోక్లోరైడ్ గుళికలు.",
        "issues": "High water intensity; vulnerable to unseasonal cyclone rains during harvest.\n*తెలుగు వివరాలు:* అధిక నీరు అవసరం; కోత సమయంలో అకాల తుఫాను వర్షాల వల్ల నష్టం జరిగే అవకాశం ఉంది."
    },
    "Millets": {
        "telugu": "శ్రీ ధాన్యాలు / జొన్నలు (Millets / Sorghum)",
        "sowing": "July (Monsoon onset) / జూలై (రుతుపవనాల ప్రారంభం)",
        "harvest": "October – November (100-110 Days / రోజులు)",
        "yield": "7 - 10 Quintals / Acre (క్వింటాళ్లు / ఎకరా)",
        "fertilizers": "Low input requirement; organic compost or minimal NPK.\n*తెలుగు వివరాలు:* తక్కువ ఎరువులు సరిపోతాయి; సేంద్రీయ ఎరువులు లేదా తక్కువ మోతాదులో ఎన్పీకే.",
        "pests": "Shoot Fly. Mitigation: Seed treatment with Imidacloprid, timely sowing.\n*తెలుగు వివరాలు:* ఈగ తెగులు (షూ ఫ్లై). నివారణ: ఇమిడాక్లోప్రిడ్‌తో విత్తన శుద్ధి మరియు సరైన సమయంలో విత్తనాలు వేయడం.",
        "issues": "Bird damage during grain filling stage; requires community scare tactics or nets.\n*తెలుగు వివరాలు:* గింజ పాలు పోసే సమయంలో పిచ్చుకలు/పక్షుల బెడద; కాపలా కాయడం లేదా వలలు అవసరం."
    }
}

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
        matched_key = "Redgram" if "Red Sandy" in detected_soil_type else "Millets"
        est_return = "₹25,000 – ₹40,000 net return/acre"
    elif "Low" in investment_budget:
        matched_key = "Millets"
        est_return = "₹25,000 – ₹40,000 net return/acre"
    elif "High" in investment_budget and not is_only_rainfed:
        matched_key = "Cotton" if "Black Cotton" in detected_soil_type else "Paddy"
        est_return = "₹70,000 – ₹1,20,000 gross return/acre"
    else:
        matched_key = "Groundnut" if "Red Sandy" in detected_soil_type else "Redgram"
        est_return = "₹35,000 – ₹55,000 net return/acre"

    profile = crop_advisory_db.get(matched_key, crop_advisory_db["Redgram"])

    storage_name = nearest_storage['name']
    storage_cap = nearest_storage['capacity']
    storage_dist = nearest_storage['distance']
    fertilizer_clean = fertilizer_mode.split('(')[0].strip()

    st.success(f"✅ **Recommended Crop / సిఫార్సు చేయబడిన పంట:** {profile['telugu']}")
    
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        st.metric(label="Estimated Yield / అంచనా దిగుబడి", value=profile['yield'])
    with col_r2:
        st.metric(label="Estimated Returns / నికర ఆదాయం", value=est_return)

    st.markdown("---")
    st.subheader("📅 Crop Schedule & Management / పంట కాలపట్టిక మరియు యాజమాన్యం")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"**🌱 Sowing Window / విత్తే సమయం:**\n{profile['sowing']}")
    with col_s2:
        st.markdown(f"**🌾 Harvest Window / కోత సమయం:**\n{profile['harvest']}")

    st.markdown(f"**🧪 Recommended Fertilizers & Telugu Info / ఎరువుల మోతాదు మరియు వివరాలు:**\n{profile['fertilizers']}")
    st.markdown(f"**🐛 Expected Pests & Mitigation / తెగుళ్లు మరియు నివారణ పద్ధతులు:**\n{profile['pests']}")
    st.markdown(f"**⚠️ Agronomic Risks / ఇతర వ్యవసాయ సవాళ్లు:**\n{profile['issues']}")

    st.info(
        f"❄️ **Nearest Cold Storage Facility ({district_tag} Region):**\n"
        f"- **Facility Name / శీతల గిడ్డంగి పేరు:** {storage_name}\n"
        f"- **Capacity / సామర్థ్యం:** {storage_cap} | **Distance / దూరం:** {storage_dist}\n"
        f"- **Fertilizer Sourcing Channel / ఎరువుల సేకరణ మార్గం:** {fertilizer_clean}\n"
        f"- *Ideal for safe storage of perishable yields, seed preservation, and post-harvest price buffering.*"
    )
            
    st.warning("💡 **Advisory Note / ముఖ్య గమనిక:** Verify input subsidies and storage booking slots directly through your local Rythu Bharosa Kendram (RBK).")
