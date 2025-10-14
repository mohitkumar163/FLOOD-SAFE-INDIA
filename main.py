# floodsafe_india_full.py
import streamlit as st
import base64
import folium
from streamlit_folium import st_folium
import math
import pandas as pd

# ---------------------------
# Configuration - set your image path
# ---------------------------
image_path = r"C:\Users\STM\Downloads\Dam_image.png"  # Update with your image path

# ---------------------------
# Encode hero image safely
# ---------------------------
encoded = ""
try:
    if image_path:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        encoded = base64.b64encode(img_bytes).decode()
except Exception:
    encoded = ""

# ---------------------------
# Streamlit Page Config
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

# ---------------------------
# Helper functions
# ---------------------------
def set_page(p):
    st.session_state.page = p

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = math.sin(d_lat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ---------------------------
# Dams List (Major)
# ---------------------------
DAMS = [
    {"name":"Bhakra Nangal","state":"HP/Punjab","lat":31.4167,"lon":76.4333,"capacity":9860},
    {"name":"Pong (Maharana Pratap Sagar)","state":"HP","lat":32.0833,"lon":75.9167,"capacity":8570},
    {"name":"Tehri","state":"Uttarakhand","lat":30.3750,"lon":78.4800,"capacity":3540},
    {"name":"Sardar Sarovar","state":"Gujarat","lat":21.8250,"lon":73.7333,"capacity":9500},
    {"name":"Hirakud","state":"Odisha","lat":21.5167,"lon":83.8667,"capacity":8136},
    {"name":"Nagarjuna Sagar","state":"Telangana","lat":16.5667,"lon":79.3167,"capacity":11500},
    {"name":"Ukai","state":"Gujarat","lat":21.3333,"lon":73.5667,"capacity":8410},
    {"name":"Indira Sagar","state":"MP","lat":22.0500,"lon":76.4700,"capacity":9750},
    {"name":"Tungabhadra","state":"Karnataka/AP","lat":15.2500,"lon":76.3333,"capacity":3764},
    {"name":"Mettur","state":"Tamil Nadu","lat":11.8000,"lon":77.8000,"capacity":2640},
    {"name":"Almatti","state":"Karnataka","lat":16.3833,"lon":75.8833,"capacity":3170},
    {"name":"Bhatsa","state":"Maharashtra","lat":19.4167,"lon":73.2500,"capacity":942},
    {"name":"Rihand","state":"UP","lat":24.2000,"lon":83.0000,"capacity":4460},
    {"name":"Maithon","state":"Jharkhand","lat":23.7500,"lon":86.8333,"capacity":1010},
    {"name":"Kallanai (Grand Anicut)","state":"Tamil Nadu","lat":10.8849,"lon":79.5341,"capacity":400},
    {"name":"Mullaperiyar","state":"TN/Kerala","lat":9.6075,"lon":77.1500,"capacity":443},
    {"name":"Idukki","state":"Kerala","lat":9.8420,"lon":76.9969,"capacity":1644},
    {"name":"Koyna","state":"Maharashtra","lat":17.1036,"lon":73.9356,"capacity":2394},
    {"name":"Banasura Sagar","state":"Kerala","lat":11.6786,"lon":76.0186,"capacity":209},
    {"name":"Srisailam","state":"Telangana/AP","lat":16.0667,"lon":78.8700,"capacity":9000},
    {"name":"Bisalpur","state":"Rajasthan","lat":25.9833,"lon":75.6167,"capacity":309.0},
    {"name":"Jawai","state":"Rajasthan","lat":25.1333,"lon":73.0667,"capacity":207.5},
    {"name":"Mansagar","state":"Rajasthan","lat":26.9496,"lon":75.8462,"capacity":35.0},
    {"name":"Ghatol","state":"Rajasthan","lat":23.5667,"lon":74.4500,"capacity":145.3},
    {"name":"Gandhisagar","state":"MP/Rajasthan","lat":24.5000,"lon":75.0000,"capacity":680},
    {"name":"Rana Pratap Sagar","state":"Rajasthan/Madhya Pradesh","lat":24.5,"lon":75.2,"capacity":54},
    {"name":"Jawahar Sagar","state":"Rajasthan","lat":24.5,"lon":75.0,"capacity":18.67},
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
                rows.append({
                    "from": a["name"], "to": b["name"], "distance_km": round(dist_km, 2)
                })
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

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🏠 Home"): set_page("Home")
with col2:
    if st.button("📍 Map"): set_page("Dashboard")
with col3:
    if st.button("ℹ️ About Us"): set_page("Chatbot")
with col4:
    if st.button("🔑 Login / Signup"): set_page("Login")

# ---------------------------
# Auto-redirect after login
# ---------------------------
if st.session_state.login_success and st.session_state.logged_in_user:
    st.session_state.page = "Dashboard"
    st.session_state.login_success = False

# ---------------------------
# HOME PAGE
# ---------------------------
if st.session_state.page == "Home":
    st.markdown(f"""
    <div style="background-image:url('data:image/png;base64,{encoded}');
                background-size:cover;background-position:center;
                height:400px;border-radius:10px;position:relative;">
        <div style="position:absolute;top:0;left:0;width:100%;height:100%;
                    background:rgba(0,0,0,0.5);border-radius:10px;"></div>
        <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
                    text-align:center;color:white;">
            <h1>🌊 FloodSafe India</h1>
            <p>Monitor Indian dams, explore nearest ones, and understand flood risk awareness.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Login to explore the interactive dam map.")

# ---------------------------
# LOGIN PAGE
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
# DASHBOARD / MAP PAGE
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
            if d["capacity"] >= 9000: color = "darkred"
            elif d["capacity"] >= 5000: color = "red"
            elif d["capacity"] >= 2000: color = "orange"
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
# ABOUT US PAGE (Replaces Chatbot)
# ---------------------------
elif st.session_state.page == "Chatbot":
    st.title("🌊 About FloodSafe India")

    st.markdown("""
    ### 🛰️ Project Overview
    **FloodSafe India** is a smart, data-driven platform built to monitor major Indian dams
    and promote flood preparedness across the nation.  
    It integrates geospatial data, dam statistics, and real-time mapping to help citizens,
    researchers, and authorities understand flood risks better.

    ---

    ### 🎯 Mission
    To build a **flood-resilient India** through technology, awareness, and collaboration.
    We aim to:
    - 📊 Provide easy access to dam information  
    - 🗺️ Map locations and capacities of major dams  
    - ⚙️ Support early-warning and planning systems  
    - 🤝 Encourage public participation in disaster awareness

    ---

    ### 💡 Key Features
    - Interactive map of India’s major dams  
    - Distance calculator between dams for study and research  
    - User login for personalized access  
    - Data export for researchers and officials  

    ---

    ### 👨‍💻 Developed By
    ** Team name - CODE STORM **  
    Passionate about using AI, data analytics, and geospatial tools to support national safety and sustainability.

    ---

    ### 🕊️ Tagline
    **“Predict • Prepare • Protect – Building a Flood-Resilient India.”**
    """)

    st.info("FloodSafe India — Empowering India Against Floods with Knowledge and Technology.")
