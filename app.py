import streamlit as st
import requests
from PIL import Image
import numpy as np
import urllib.parse

# Page Configuration
st.set_page_config(
    page_title="AP & TS Smart Agro-Economic Recommender",
    page_icon="🌱",
    layout="centered"
)

# App Header
st.title("🌱 Smart Crop & Livelihood Recommender / స్మార్ట్ పంట మరియు ఆర్థిక సిఫార్సు వ్యవస్థ")
st.subheader("AP & Telangana Regional Agricultural Decision Support System")
st.markdown("Fully customized parameter-driven recommendations, multi-source hydrology, latest research breakthroughs, and instant WhatsApp sharing.")

# --- DEMO PRE-POPULATION HELPER ---
with st.container():
    st.info("💡 **New here? Click below to load a sample farm profile and see how it works instantly!**\n\n*కొత్తవారా? కింద ఉన్న బటన్‌ను క్లిక్ చేసి ఒక నమూనా ఫామ్ ప్రొఫైల్‌ను లోడ్ చేయండి!*")
    if st.button("🚀 Load Sample Scenario / ఉదాహరణ ప్రొఫైల్‌ను లోడ్ చేయి"):
        st.session_state["demo_loaded"] = True
    else:
        if "demo_loaded" not in st.session_state:
            st.session_state["demo_loaded"] = False

is_demo = st.session_state["demo_loaded"]

st.divider()

# --- STEP 1: BILINGUAL MANDAL AUTO-COMPLETE & VOICE/TEXT SEARCH ---
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

default_mandal_index = 1 if is_demo else 0

selected_location_str = st.selectbox(
    "Search or Select Mandal / Town / మండలం లేదా పట్టణం కోసం వెతకండి:",
    options=ap_ts_mandals,
    index=default_mandal_index
)

place_input = selected_location_str.split("(")[0].strip()
district_tag = selected_location_str.split(",")[1].strip() if "," in selected_location_str else "AP/TS"

@st.cache_data(show_spinner=False)
def get_coordinates(place_name):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={place_name}&count=1&language=en&format=json"
    try:
        res = requests.get(geo_url, timeout=3).json()
        if "results" in res and len(res["results"]) > 0:
            result = res["results"][0]
            return result["latitude"], result["longitude"], result.get("name", place_name)
    except:
        pass
    return 17.3850, 78.4867, place_name

lat, lon, place_found = get_coordinates(place_input)

@st.cache_data(show_spinner=False)
def fetch_weather_data(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m&elevation=true"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        temp = data.get("current", {}).get("temperature_2m", 28.0)
        humidity = data.get("current", {}).get("relative_humidity_2m", 65.0)
        elevation = data.get("elevation", 300.0)
        return temp, humidity, elevation
    except:
        return 28.5, 70.0, 300.0

current_temp, current_humidity, elevation = fetch_weather_data(lat, lon)
st.success(f"📍 **Selected Location / ఎంచుకున్న ప్రాంతం:** {selected_location_str} | **Temp / ఉష్ణోగ్రత:** {current_temp}°C | **Elevation / ఎత్తు:** {elevation}m (Offline Cached Ready)")

st.divider()

# --- STEP 2: MULTI-SOURCE WATER & HYDROLOGY ---
st.header("2. Water Sources & Hydrology / నీటి వనరులు మరియు హైడ్రాలజీ")

default_waters = ["Borewell / Tube well (బోర్‌వెల్ / ట్యూబ్‌వెల్)", "Canal Irrigation / Delta Flow (కాల్వ నీరు / ప్రాజెక్ట్)"] if is_demo else ["Borewell / Tube well (బోర్‌వెల్ / ట్యూబ్‌వెల్)"]

water_sources = st.multiselect(
    "Select all available irrigation sources / లభిస్తున్న అన్ని నీటి పారుదల వనరులను ఎంచుకోండి:",
    [
        "Borewell / Tube well (బోర్‌వెల్ / ట్యూబ్‌వెల్)",
        "Canal Irrigation / Delta Flow (కాల్వ నీరు / ప్రాజెక్ట్)",
        "Tank / Cheruvu (స్థానిక చెరువు నీరు)",
        "Rainfed / Dryland (వర్షాధారితం - నీటి వసతి లేదు)"
    ],
    default=default_waters
)

borewell_depth = 350 if is_demo else 300
power_hours = 9
canal_status = "Normal Flow"
tank_level = "Half Capacity"

with st.expander("⚙️ Configure Parameters for Selected Water Sources / ఎంచుకున్న నీటి వనరుల వివరాలు"):
    if any("Borewell" in src for src in water_sources):
        st.subheader("Borewell Parameters / బోర్‌వెల్ వివరాలు")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            borewell_depth = st.number_input("Borewell Depth (Feet) / బోర్‌వెల్ లోతు (అడుగులలో)", min_value=100, max_value=1200, value=borewell_depth, step=50)
        with col_w2:
            power_hours = st.slider("Daily Power Supply (Hours) / రోజువారీ విద్యుత్ సరఫరా (గంటలు)", min_value=3, max_value=24, value=power_hours)

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

# --- STEP 3: CROP HISTORY & NUTRIENT RESIDUE (FARMER INPUT) ---
st.header("3. Crop History & Soil Health / పంట చరిత్ర మరియు నేల ఆరోగ్యం")

previous_crop = st.selectbox(
    "Select previous season crop / గత సీజన్లో పండించిన పంట:",
    [
        "Legumes / Pulses (e.g., Redgram, Green Gram) - High Residual Nitrogen / అపరాలు (కంది, పెసలు) - అధిక నత్రజని నిల్వలు",
        "Cereals / Paddy (e.g., Rice, Maize) - Heavy Nutrient Depletion / ధాన్యాలు / వరి, మొక్కజొన్న - పోషకాల వినియోగం ఎక్కువ",
        "Commercial Crops (e.g., Cotton, Chillies) - Intensive Input Usage / వాణిజ్య పంటలు (పత్తి, మిరప) - ఎక్కువ ఎరువుల వాడకం",
        "Fallow / Dryland Rest - Natural Recovery / పడావు భూమి / విశ్రాంతి - సహజంగా కోలుకున్న నేల"
    ]
)

soil_health_proxy = "High Residual Fertility (Legume Rotational Benefit)" if "Legumes" in previous_crop else "Standard / Depleted Baseline"

st.divider()

# --- STEP 4: FINANCIALS & INPUTS ---
st.header("4. Financials & Inputs / ఆర్థిక మరియు ఎరువుల లభ్యత")

col_e1, col_e2 = st.columns(2)
with col_e1:
    investment_budget = st.selectbox(
        "Available Capital / పెట్టుబడి బడ్జెట్ (ఎకరాకు):",
        [
            "Medium (₹15,000 - ₹35,000 / Acre)",
            "Low (< ₹15,000 / Acre - Low Input)",
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

# --- STEP 5: STABLE CAMERA INPUT FOR SOIL ANALYSIS ---
st.header("5. Soil Visual Capture / నేల ఫోటో క్యాప్చర్")

if is_demo:
    st.info("🟢 **Demo Mode Active / డెమో మోడ్ సక్రియం:** Sample soil pre-configured as *Black Cotton Soil / నల్ల రేగడి నేల*.")

st.markdown("Take a clear picture of your field soil using your mobile camera. / మీ మొబైల్ కెమెరాతో మీ పొలం నేల ఫోటోను తీయండి.")
soil_image_file = st.camera_input("Snap Soil Sample / నేల ఫోటో తీయండి")

if is_demo:
    detected_soil_type = "Black Cotton Soil / నల్ల రేగడి నేల (Regur)"
else:
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

# --- STEP 6: EXPANDED & CUSTOMIZED RECOMMENDATION ENGINE ---
st.header("6. Complete Customized Crop Advisory & Livelihood Plan / పూర్తి అనుకూలీకరించిన పంట సలహా")

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
        "telugu": "వేరుశెనగ / వేరుశెనగ కాయ (Groundnut)",
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

if st.button("Calculate Complete Agronomic & Economic Plan / పూర్తి ప్రణాళికను రూపొందించు", type="primary") or is_demo:
    is_only_rainfed = len(water_sources) == 0 or ("Rainfed" in water_sources and len(water_sources) == 1)

    water_constraint_risk = "Low"
    if any("Borewell" in src for src in water_sources) and borewell_depth > 500 and power_hours < 7:
        water_constraint_risk = "High (Deep Bore & Low Power)"
    elif is_only_rainfed:
        water_constraint_risk = "Medium (Rainfed Dryland)"

    if is_demo:
        matched_key = "Cotton"
        est_return = "₹75,000 – ₹1,10,000 gross return/acre (Optimized for Black Cotton & Canal Irrigation)"
        recommendation_rationale = "Selected based on demo profile matching heavy alluvial/black soil with reliable canal and supplemental borewell irrigation."
    elif is_only_rainfed:
        if "Red Sandy" in detected_soil_type:
            matched_key = "Redgram"
            est_return = "₹28,000 – ₹42,000 net return/acre (Drought-Resilient Pulses)"
        else:
            matched_key = "Millets"
            est_return = "₹22,000 – ₹36,000 net return/acre (Low-Moisture Tolerance)"
        recommendation_rationale = "Customized for rainfed dryland conditions prioritizing moisture conservation and drought-hardy crops."
    elif "Low" in investment_budget:
        matched_key = "Millets"
        est_return = "₹25,000 – ₹40,000 net return/acre (Low Capital Input)"
        recommendation_rationale = "Customized for low-capital availability, minimizing high chemical/fertilizer overhead."
    elif "Legumes" in previous_crop and not is_only_rainfed:
        if "Black Cotton" in detected_soil_type and "High" in investment_budget:
            matched_key = "Cotton"
            est_return = "₹80,000 – ₹1,25,000 gross return/acre (Nitrogen Credit Boost)"
        else:
            matched_key = "Paddy"
            est_return = "₹55,000 – ₹85,000 gross return/acre (Rotational Yield Bonus)"
        recommendation_rationale = "Customized utilizing preceding legume nitrogen fixation credits to boost high-yield cereal/cash crop returns."
    elif "High" in investment_budget and not is_only_rainfed:
        matched_key = "Cotton" if "Black Cotton" in detected_soil_type else "Paddy"
        est_return = "₹70,000 – ₹1,20,000 gross return/acre (Commercial Intensive)"
        recommendation_rationale = "Customized for high-capital commercial intensity matching soil type and stable irrigation."
    else:
        matched_key = "Groundnut" if "Red Sandy" in detected_soil_type else "Redgram"
        est_return = "₹35,000 – ₹55,000 net return/acre"
        recommendation_rationale = "Customized for balanced input availability and regional soil profile."

    profile = crop_advisory_db.get(matched_key, crop_advisory_db["Redgram"])

    storage_name = nearest_storage['name']
    storage_cap = nearest_storage['capacity']
    storage_dist = nearest_storage['distance']
    fertilizer_clean = fertilizer_mode.split('(')[0].strip()

    st.success(f"✅ **Recommended Crop / సిఫార్సు చేయబడిన పంట:** {profile['telugu']}")
    
    st.info(
        f"📋 **Parameter Customization Rationale / సిఫార్సు వెనుక ఉన్న కారణాలు:**\n"
        f"- {recommendation_rationale}\n"
        f"- *Water Hydrology Risk:* {water_constraint_risk} | *Soil Type:* {detected_soil_type}\n"
        f"- *Previous Crop Legacy:* {soil_health_proxy}"
    )

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
        f"❄️ **Nearest Cold Storage Facility ({district_tag} Region) / సమీప శీతల గిడ్డంగి:**\n"
        f"- **Facility Name / పేరు:** {storage_name}\n"
        f"- **Capacity / సామర్థ్యం:** {storage_cap} | **Distance / దూరం:** {storage_dist}\n"
        f"- **Fertilizer Sourcing Channel / ఎరువుల సేకరణ:** {fertilizer_clean}\n"
        f"- *Ideal for safe storage of perishable yields and market price buffering.*"
    )
            
    st.warning("💡 **Advisory Note / ముఖ్య గమనిక:** Verify input subsidies and storage booking slots directly through your local Rythu Bharosa Kendram (RBK).")

    # --- STEP 7: ADVANCED UNIVERSITY & RESEARCH DISCOVERIES (ANGRAU / PJTSAU / ICRISAT) ---
    st.header("7. Latest Research & University Discoveries / తాజా పరిశోధనలు మరియు విశ్వవిద్యాలయ ఆవిష్కరణలు")

    latest_research_db = {
        "Redgram": {
            "breakthrough": "Integration of genomic-assisted breeding for sterility mosaic disease resistance and early-maturity lines (ICRISAT/ANGRAU trials).\n*తెలుగు:* వంధ్యత్వ తెగును తట్టుకునే శక్తి మరియు త్వరగా కోతకు వచ్చే రకాలపై జన్యుపరమైన అభివృద్ధి.",
            "intercrop": "Intercrop with Pearl Millet or Groundnut (1:7 ratio) combined with biopesticides (Trichoderma seed treatment).\n*తెలుగు:* సజ్జ లేదా వేరుశెనగతో అంతరపంట (1:7 నిష్పత్తి) మరియు ట్రైకోడెర్మాతో విత్తన శుద్ధి.",
            "bund_trees": "Plant Drumstick (Moringa) or Subabul on bunds for secondary income and microclimate regulation.\n*తెలుగు:* పొలం గట్లపై మునగ చెట్లను పెంచడం ద్వారా అదనపు ఆదాయం మరియు అనుకూల వాతావరణం.",
            "moisture": "In-situ moisture conservation using ridge-and-furrow method coupled with nano-zinc foliar application.\n*తెలుగు:* బోదెలు మరియు సాళ్ల పద్ధతి ద్వారా తేమ సంరక్షణ, అలాగే నానో-జింక్ పిచికారీ."
        },
        "Groundnut": {
            "breakthrough": "Dual-stage application of Nano NPK and seaweed extract to combat terminal drought stress and enhance pod filling.\n*తెలుగు:* కరువును తట్టుకోవడానికి మరియు కాయ గట్టిపడటానికి నానో ఎన్పీకే మరియు సీవీడ్ ఎక్స్‌ట్రాక్ట్ వాడకం.",
            "intercrop": "Pair with Castor or Redgram in a 7:1 row arrangement for natural trap-crop pest barrier protection.\n*తెలుగు:* సహజ పురుగుల నివారణ కోసం 7:1 నిష్పత్తిలో ఆముదం లేదా కందిని అంతరపంటగా సాగు చేయాలి.",
            "bund_trees": "Establish Silver Oak or perimeter nitrogen-fixing shrubs without restricting canopy sunlight.\n*తెలుగు:* కాంతికి ఆటంకం కలగకుండా సరిహద్దుల్లో సిల్వర్ ఓక్ లేదా నత్రజని అందించే పొదలను పెంచాలి.",
            "moisture": "Stale seedbed technique with gypsum enrichment (200 kg/acre) at peak flowering stage.\n*తెలుగు:* పూత దశలో జిప్సమ్ (ఎకరానికి 200 కిలోలు) వినియోగం మరియు నేల తేమ సంరక్షణ."
        },
        "Cotton": {
            "breakthrough": "Precision mechanization via single-row parasol pickers and smart pheromone disruption for Pink Bollworm control.\n*తెలుగు:* గులాబీ రంగు పురుగు నివారణకు స్మార్ట్ ఫెరోమోన్ బుట్టలు మరియు సింగిల్ రో కాటన్ పిక్కర్ల వినియోగం.",
            "intercrop": "Short-duration pulse intercropping (Green Gram/Minumulu) during the first 45 days to suppress weed growth.\n*తెలుగు:* కలుపు నివారణకు తొలి 45 రోజులు పెసలు లేదా మినుములు అంతరపంటగా వేయాలి.",
            "bund_trees": "Plant Teak or Casuarina on northern farm borders as a windbreak and future timber capital asset.\n*తెలుగు:* ఈదురు గాలుల నుండి రక్షణ మరియు భవిష్యత్ ఆదాయం కోసం ఉత్తర సరిహద్దులో టేకు చెట్లు.",
            "moisture": "Alternate furrow irrigation and residue incorporation to boost soil organic carbon.\n*తెలుగు:* ప్రత్యామ్నాయ సాళ్లలో నీరు పెట్టడం మరియు పంట అవశేషాలను నేలలో కలియదున్నడం."
        },
        "Paddy": {
            "breakthrough": "Direct Seeded Rice (DSR) protocols combined with Alternate Wetting and Drying (AWD) sensors to save up to 30% water.\n*తెలుగు:* 30% నీటిని ఆదా చేయడానికి డైరెక్ట్ సీడెడ్ రైస్ (DSR) మరియు AWD పద్ధతుల అవలంబన.",
            "intercrop": "Green manuring incorporation (Dhaincha/Sunhemp) 10 days prior to transplanting for natural nitrogen enrichment.\n*తెలుగు:* నాటేయడానికి 10 రోజుల ముందు పచ్చిరొట్ట ఎరువును (జీలుగ/జనుము) నేలలో కలియదున్నాలి.",
            "bund_trees": "Glyricidia and Pongamia plantations along channels for organic green leaf manure and bund reinforcement.\n*తెలుగు:* కాలువల వెంట గ్లైరిసిడియా చెట్లను పెంచడం ద్వారా సహజ ఆకు ఎరువు మరియు గట్ల రక్షణ.",
            "moisture": "Precision laser-land leveling to ensure uniform water distribution and minimize percolation loss.\n*తెలుగు:* నీరు సమానంగా అందడానికి మరియు వృధా కాకుండా లేజర్ ల్యాండ్ లెవెలర్ వాడకం."
        },
        "Millets": {
            "breakthrough": "Deployment of climate-resilient biofortified varieties (e.g., improved Sorghum & Finger Millet lines) resistant to lodging.\n*తెలుగు:* వాతావరణ మార్పులను తట్టుకునే మరియు పడిపోని మెరుగైన జొన్న, రాగి వరి రకాల సాగు.",
            "intercrop": "Intercrop Finger Millet with Cowpea for dual-benefit nitrogen fixation and protein yield.\n*తెలుగు:* నత్రజని స్థిరత్వం మరియు పోషకాల కోసం రాగులతో పాటు అలసందల సాగు.",
            "bund_trees": "Plant fruit-bearing Sapota or Subabul on farm margins for ecological balance and supplemental income.\n*తెలుగు:* అదనపు ఆదాయం మరియు పర్యావరణ సమతుల్యత కోసం సరిహద్దుల్లో సపోటా లేదా సుబాబుల్.",
            "moisture": "Contour bunding and dead-furrow rainwater harvesting to capture every drop of precipitation.\n*తెలుగు:* ప్రతి వర్షపు చుక్కను సంరక్షించడానికి సమతల గట్లు మరియు డెడ్ ఫర్రోస్ నిర్మాణం."
        }
    }

    research_guide = latest_research_db.get(matched_key, latest_research_db["Redgram"])

    with st.expander("🔬 View Latest Research Discoveries & University Guidelines / తాజా పరిశోధన ఆవిష్కరణలు"):
        st.markdown(f"**⚡ Breakthrough Technology / అతధునిక సాంకేతికత:**\n{research_guide['breakthrough']}")
        st.markdown(f"**🌿 Recommended Intercropping / అంతరపంటల విధానం:**\n{research_guide['intercrop']}")
        st.markdown(f"**🌳 Revenue-Bearing Boundary Trees / సరిహద్దు ఆదాయ వృక్షాలు:**\n{research_guide['bund_trees']}")
        st.markdown(f"**💧 Advanced Moisture Conservation / అధునాతన తేమ సంరక్షణ:**\n{research_guide['moisture']}")

    # --- WHATSAPP SHARE BUTTON INTEGRATION ---
    wa_message = (
        f"🌱 *Smart Agro Advisory ({selected_location_str})*\n"
        f"• *Crop / పంట:* {profile['telugu']}\n"
        f"• *Expected Yield / దిగుబడి:* {profile['yield']}\n"
        f"• *Returns / ఆదాయం:* {est_return}\n"
        f"• *Sowing Window / విత్తే సమయం:* {profile['sowing']}\n"
        f"• *Cold Storage / శీతల గిడ్డంగి:* {storage_name} ({storage_dist})\n"
        f"• *Advisory:* Verify via local RBK."
    )
    encoded_message = urllib.parse.quote(wa_message)
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_message}"
    
    st.markdown("---")
    st.markdown(f"### 📲 Share Plan via WhatsApp / వాట్సాప్ ద్వారా షేర్ చేయండి")
    st.markdown(
        f'<a href="{whatsapp_url}" target="_blank">'
        f'<button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; font-size:16px; font-weight:bold; cursor:pointer;">'
        f'💬 Share on WhatsApp / వాట్సాప్‌లో పంపు</button></a>',
        unsafe_allow_html=True
    )
