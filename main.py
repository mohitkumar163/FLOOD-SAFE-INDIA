# floodsafe_india.py

import streamlit as st
import base64
import folium
from streamlit_folium import st_folium
import math
import pandas as pd
import openai
from difflib import get_close_matches

# ---------------------------
# Configuration
# ---------------------------
image_path = r"C:\Users\STM\Downloads\Dam.jpg"  
# ---------------------------
# Encode hero image
# ---------------------------
encoded = ""
try:
    with open(image_path, "rb") as f:
        img_bytes = f.read()
    encoded = base64.b64encode(img_bytes).decode()
except Exception as e:
    encoded = ""
    st.warning(f"Image load error: {e}")

# ---------------------------
# Streamlit Config
# ---------------------------
st.set_page_config(page_title="FloodSafe India", page_icon="🌊", layout="wide")

# ---------------------------
# Session State
# ---------------------------
if "page" not in st.session_state:
    st.session_state.page = "Home"
if "users" not in st.session_state:
    st.session_state.users = {}
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "login_success" not in st.session_state:
    st.session_state.login_success = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ---------------------------
# Helper Functions
# ---------------------------
def set_page(p):
    st.session_state.page = p

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------
# Dams List
# ---------------------------
DAMS = [
    {"name": "Bhakra Nangal", "state": "HP/Punjab", "lat": 31.4167, "lon": 76.4333, "capacity": 9860},
    {"name": "Pong (Maharana Pratap Sagar)", "state": "HP", "lat": 32.0833, "lon": 75.9167, "capacity": 8570},
    {"name": "Tehri", "state": "Uttarakhand", "lat": 30.3750, "lon": 78.4800, "capacity": 3540},
    {"name": "Sardar Sarovar", "state": "Gujarat", "lat": 21.8250, "lon": 73.7333, "capacity": 9500},
    {"name": "Hirakud", "state": "Odisha", "lat": 21.5167, "lon": 83.8667, "capacity": 8136},
    {"name": "Nagarjuna Sagar", "state": "Telangana", "lat": 16.5667, "lon": 79.3167, "capacity": 11500},
    {"name": "Ukai", "state": "Gujarat", "lat": 21.3333, "lon": 73.5667, "capacity": 8410},
    {"name": "Indira Sagar", "state": "MP", "lat": 22.0500, "lon": 76.4700, "capacity": 9750},
    {"name": "Tungabhadra", "state": "Karnataka/AP", "lat": 15.2500, "lon": 76.3333, "capacity": 3764},
    {"name": "Mettur", "state": "Tamil Nadu", "lat": 11.8000, "lon": 77.8000, "capacity": 2640},
]

# ---------------------------
# Compute distances
# ---------------------------
@st.cache_data(show_spinner=False)
def compute_distances(dams_list):
    rows = []
    for i, a in enumerate(dams_list):
        for j, b in enumerate(dams_list):
            if i != j:
                dist_km = haversine(a["lat"], a["lon"], b["lat"], b["lon"])
                rows.append({"from": a["name"], "to": b["name"], "distance_km": round(dist_km, 2)})
    return pd.DataFrame(rows)

DIST_DF = compute_distances(DAMS)

def convert_df_to_csv_bytes(df):
    return df.to_csv(index=False).encode('utf-8')

# ---------------------------
# Navbar
# ---------------------------
st.markdown("""
<style>
.navbar {background-color:#003366;padding:10px;border-radius:8px;margin-bottom:10px;}
.navbtn {background-color:#0078D7;color:white;padding:6px 12px;border-radius:6px;border:none;margin-right:8px;}
.navbtn:hover {background-color:#FFD700;color:black;}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🏠 Home"): set_page("Home")
with col2:
    if st.button("📍 Map"): set_page("Dashboard")
with col3:
    if st.button("ℹ️ About Us"): set_page("About")
with col4:
    if st.button("🤖 AI Chatbot"): set_page("AI Chatbot")
with col5:
    if st.button("🔑 Login / Signup"): set_page("Login")

# ---------------------------
# Home Page
# ---------------------------
if st.session_state.page == "Home":
    st.markdown(f"""
    <div style="background-image:url('data:image/jpeg;base64,{encoded}');
                background-size:cover;background-position:center;height:400px;border-radius:10px;position:relative;">
        <div style="position:absolute;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);border-radius:10px;"></div>
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;color:white;">
            <h1>🌊 FloodSafe India</h1>
            <p>Monitor Indian dams, explore nearest ones, and understand flood risk awareness.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Login to explore the interactive dam map.")

# ---------------------------
# Login / Signup
# ---------------------------
elif st.session_state.page == "Login":
    st.title("🔑 Login / Signup")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login Now"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in_user = email
                st.session_state.login_success = True
                st.success("✅ Login successful! Redirecting to map...")
            else:
                st.error("Invalid credentials. Try again or sign up.")
    with tab2:
        new_email = st.text_input("New Email")
        new_pass = st.text_input("New Password", type="password")
        if st.button("Signup Now"):
            if new_email and new_pass:
                if new_email not in st.session_state.users:
                    st.session_state.users[new_email] = new_pass
                    st.success("🎉 Signup successful! Please login now.")
                else:
                    st.warning("User already exists!")

# ---------------------------
# Dashboard / Map
# ---------------------------
elif st.session_state.page == "Dashboard":
    st.title("📍 Dam Map & Distance Explorer")
    if not st.session_state.logged_in_user:
        st.warning("Please login first to access the map.")
        st.stop()
    left, right = st.columns([1.2, 2])
    with left:
        dam_names = [d["name"] for d in DAMS]
        sel = st.selectbox("Select a dam:", dam_names)
        top_n = st.number_input("Nearest N dams:", 1, 10, 5)
        min_capacity = st.slider("Min capacity (MCM):", 0, 12000, 0, 100)
        st.download_button("Download all distances CSV", convert_df_to_csv_bytes(DIST_DF), "dam_distances.csv")
    with right:
        m = folium.Map(location=[22.0, 79.0], zoom_start=5, tiles="CartoDB positron")
        for d in DAMS:
            if d["capacity"] < min_capacity:
                continue
            color = "green"
            if d["capacity"] >= 9000:
                color = "darkred"
            elif d["capacity"] >= 5000:
                color = "red"
            elif d["capacity"] >= 2000:
                color = "orange"
            folium.CircleMarker([d["lat"], d["lon"]], radius=6, color=color, fill=True,
                                popup=f"<b>{d['name']}</b><br>{d['state']}<br>{d['capacity']} MCM").add_to(m)
        selected = next((x for x in DAMS if x["name"] == sel), None)
        if selected:
            others = []
            for d in DAMS:
                if d["name"] != selected["name"]:
                    dist = haversine(selected["lat"], selected["lon"], d["lat"], d["lon"])
                    others.append({**d, "distance_km": round(dist, 2)})
            nearest = sorted(others, key=lambda x: x["distance_km"])[:top_n]
            folium.Marker([selected["lat"], selected["lon"]],
                          popup=f"<b>{selected['name']}</b>",
                          icon=folium.Icon(color="blue", icon="star")).add_to(m)
            for n in nearest:
                folium.PolyLine([[selected["lat"], selected["lon"]], [n["lat"], n["lon"]]],
                                color="blue", tooltip=f"{n['name']}: {n['distance_km']} km").add_to(m)
            st.subheader(f"Nearest {top_n} dams to {selected['name']}")
            st.dataframe(pd.DataFrame(nearest)[["name", "state", "capacity", "distance_km"]])
        st_folium(m, width=1000, height=700)

# ---------------------------
# AI Chatbot with Misinformation Guard
# ---------------------------
elif st.session_state.page == "AI Chatbot":
    st.title("🤖 AI Chatbot")

    for chat in st.session_state["messages"]:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    user_input = st.chat_input("Ask FloodSafe India AI anything...")
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # ----------------------
        # Improved Dam Detection
        # ----------------------
        dam_names_lower = [d["name"].lower() for d in DAMS]
        match = get_close_matches(user_input.lower(), dam_names_lower, cutoff=0.3)

        if match:
            # Call OpenAI GPT
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_input}],
                    temperature=0.7,
                    max_tokens=400
                )
                answer = response['choices'][0]['message']['content']
            except Exception as e:
                answer = "⚠️ AI service not available. Try again later."
        else:
            answer = "⚠️ Sorry, this information cannot be verified. Please consult official sources."

        with st.chat_message("assistant"):
            st.write(answer)
        st.session_state["messages"].append({"role": "assistant", "content": answer})

