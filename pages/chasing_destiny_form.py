import streamlit as st
import requests
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook/chasing-destiny-studios"

st.set_page_config(page_title="Chasing Destiny Studios | Production Booking", layout="wide", page_icon="🎬")

# -------------------------
# CUSTOM CSS
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #0a0a0a;
    color: #f0ead6;
}
.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1008 50%, #0a0a0a 100%);
}
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #d4a843 !important;
    letter-spacing: 0.05em;
}
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input,
.stTextArea textarea {
    background-color: #1a1a1a !important;
    color: #f0ead6 !important;
    border: 1px solid #3a2e1a !important;
    border-radius: 4px !important;
}
.stButton > button {
    background: linear-gradient(90deg, #d4a843, #b8861f) !important;
    color: #0a0a0a !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.1em !important;
    border: none !important;
    padding: 0.75rem 3rem !important;
    border-radius: 2px !important;
    text-transform: uppercase;
}
.stButton > button:hover {
    background: linear-gradient(90deg, #e8bc57, #d4a843) !important;
    transform: translateY(-1px);
}
.stHeader {
    border-bottom: 1px solid #3a2e1a;
}
.studio-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
    border-bottom: 1px solid #3a2e1a;
    margin-bottom: 2rem;
}
.studio-tagline {
    font-family: 'Montserrat', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.3em;
    color: #8a7a5a;
    text-transform: uppercase;
}
.divider {
    border: none;
    border-top: 1px solid #3a2e1a;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# HEADER
# -------------------------
st.markdown("""
<div class="studio-header">
    <h1 style="font-size: 2.8rem; margin-bottom: 0.2rem;">🎬 Chasing Destiny Studios</h1>
    <p class="studio-tagline">Production Booking & Project Intake Form</p>
</div>
""", unsafe_allow_html=True)

# -------------------------
# SECTION 1: CLIENT / PRODUCTION COMPANY INFO
# -------------------------
st.header("Client & Production Company")

col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Contact Full Name", "Jane Smith")
    company_name = st.text_input("Production Company / Studio Name", "Visionary Films LLC")
    email = st.text_input("Email Address", "jane@visionaryfilms.com")

with col2:
    phone = st.text_input("Phone Number", "(404) 555-0192")
    role = st.selectbox("Your Role", ["Producer", "Director", "Line Producer", "Production Coordinator", "Executive Producer", "AD", "Other"])
    contact_method = st.selectbox("Preferred Contact Method", ["Email", "Phone", "Text"])

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -------------------------
# SECTION 2: PROJECT DETAILS
# -------------------------
st.header("Project Details")

col1, col2 = st.columns(2)

with col1:
    project_title = st.text_input("Project Title / Working Title", "Untitled Feature #1")
    project_type = st.selectbox("Project Type", [
        "Feature Film", "Short Film", "TV Series / Pilot", "Documentary",
        "Commercial / Ad", "Music Video", "Corporate / Brand Film", "Web Series", "Other"
    ])
    genre = st.selectbox("Genre", [
        "Drama", "Action / Thriller", "Comedy", "Horror", "Sci-Fi / Fantasy",
        "Romance", "Documentary", "Animation", "Mixed / Other"
    ])

with col2:
    budget_tier = st.selectbox("Production Budget Tier", [
        "Micro (<$50K)", "Low ($50K–$250K)", "Mid ($250K–$1M)", "High ($1M–$5M)", "Studio ($5M+)"
    ])
    union_status = st.selectbox("Union / Non-Union", ["Non-Union", "SAG-AFTRA", "DGA", "IATSE", "Mixed"])
    script_status = st.selectbox("Script Status", ["Concept / Treatment", "First Draft", "Revised Draft", "Final Draft", "Production Draft"])

logline = st.text_area("Logline / Brief Project Description", "A young woman discovers her destiny is tied to an ancient map…", height=100)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -------------------------
# SECTION 3: PRODUCTION SCHEDULE
# -------------------------
st.header("Production Schedule")

col1, col2, col3 = st.columns(3)

with col1:
    shoot_start = st.date_input("Shoot Start Date")
    shoot_end = st.date_input("Shoot End Date")

with col2:
    total_shoot_days = st.number_input("Total Shoot Days", min_value=1, value=20)
    shoot_days_per_week = st.selectbox("Shoot Days Per Week", ["5 Days", "6 Days", "7 Days"])

with col3:
    time_of_day = st.multiselect("Shooting Hours", ["Days", "Nights", "Mixed Days/Nights", "Magic Hour"], default=["Days"])
    production_phase = st.selectbox("Current Phase", ["Pre-Production", "Production", "Post-Production", "Development"])

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -------------------------
# SECTION 4: LOCATIONS & CREW
# -------------------------
st.header("Locations & Crew")

col1, col2 = st.columns(2)

with col1:
    primary_location = st.text_input("Primary Filming Location / City", "Atlanta, GA")
    location_types = st.multiselect("Location Types", [
        "Studio / Soundstage", "Practical Interior", "Exterior / Outdoor",
        "Remote / Wilderness", "Urban / City Street", "Water / Maritime"
    ], default=["Studio / Soundstage", "Practical Interior"])
    permits_needed = st.radio("Permits Required?", ["Yes", "No", "TBD"])

with col2:
    crew_size = st.selectbox("Estimated Crew Size", [
        "Skeleton (<10)", "Small (10–30)", "Medium (30–75)", "Large (75–150)", "Full Studio (150+)"
    ])
    cast_size = st.number_input("Number of Principal Cast", min_value=1, value=5)
    extras_needed = st.radio("Background / Extras Needed?", ["Yes", "No"])

services_needed = st.multiselect(
    "Services Needed from Chasing Destiny Studios",
    [
        "Full Production Package", "Equipment Rental", "Studio Space / Soundstage",
        "Casting Services", "Post-Production / Editing", "Color Grading",
        "Sound Design / Mixing", "VFX / Visual Effects", "Script Supervision",
        "Location Scouting", "Production Insurance", "Catering / Craft Services"
    ],
    default=["Full Production Package", "Equipment Rental"]
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -------------------------
# SECTION 5: EQUIPMENT & TECHNICAL
# -------------------------
st.header("Equipment & Technical Requirements")

col1, col2 = st.columns(2)

with col1:
    camera_preference = st.selectbox("Camera Preference", [
        "ARRI Alexa", "RED", "Sony Venice", "Blackmagic", "Canon Cinema",
        "Available at Studio", "Client Provided", "TBD"
    ])
    frame_rate = st.selectbox("Frame Rate", ["24fps", "25fps", "30fps", "48fps", "60fps", "Other"])

with col2:
    delivery_format = st.multiselect("Delivery Format(s)", [
        "DCP (Theater)", "4K UHD", "1080p HD", "SDR", "HDR / Dolby Vision",
        "Streaming (Netflix / Prime)", "Broadcast TV", "Web / Social Media"
    ], default=["4K UHD", "DCP (Theater)"])
    aspect_ratio = st.selectbox("Aspect Ratio", ["2.39:1 (Scope)", "1.85:1 (Flat)", "1.78:1 (16:9)", "1.33:1 (4:3)", "Other"])

special_requirements = st.text_area("Special Technical Requirements / Notes", "Green screen, drone footage, underwater housing…", height=80)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -------------------------
# SECTION 6: ACCESS & LOGISTICS
# -------------------------
st.header("Access & Logistics")

col1, col2 = st.columns(2)

with col1:
    parking = st.text_input("Parking / Load-In Access", "Studio lot parking available")
    nda_required = st.radio("NDA Required?", ["Yes", "No"])

with col2:
    insurance_provided = st.radio("Client Providing Production Insurance?", ["Yes", "No", "Need Studio Coverage"])
    accessibility = st.radio("Accessibility Requirements on Set?", ["Yes", "No"])

additional_notes = st.text_area("Additional Notes / Special Instructions", "High-priority project — discretion required.", height=80)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# -------------------------
# SECTION 7: CONFIRMATION
# -------------------------
st.header("Confirmation & Agreement")

col1, col2 = st.columns(2)

with col1:
    how_did_you_hear = st.selectbox("How Did You Hear About Us?", [
        "Referral", "Film Commission", "Social Media", "Industry Directory", "Website", "Other"
    ])
    terms = st.checkbox("I agree to the Terms & Conditions and Privacy Policy", value=True)

with col2:
    newsletter = st.checkbox("Subscribe to Chasing Destiny Studios newsletter", value=False)
    priority_booking = st.checkbox("Request Priority Booking Consultation", value=False)

# -------------------------
# SUBMIT
# -------------------------
st.markdown("<br>", unsafe_allow_html=True)
col_center = st.columns([1, 2, 1])
with col_center[1]:
    submitted = st.button("🎬 Submit Production Booking")

if submitted:
    payload = {
        "client_info": {
            "full_name": full_name,
            "company_name": company_name,
            "email": email,
            "phone": phone,
            "role": role,
            "contact_method": contact_method
        },
        "project_details": {
            "project_title": project_title,
            "project_type": project_type,
            "genre": genre,
            "budget_tier": budget_tier,
            "union_status": union_status,
            "script_status": script_status,
            "logline": logline
        },
        "production_schedule": {
            "shoot_start": str(shoot_start),
            "shoot_end": str(shoot_end),
            "total_shoot_days": total_shoot_days,
            "shoot_days_per_week": shoot_days_per_week,
            "time_of_day": time_of_day,
            "production_phase": production_phase
        },
        "locations_crew": {
            "primary_location": primary_location,
            "location_types": location_types,
            "permits_needed": permits_needed,
            "crew_size": crew_size,
            "cast_size": cast_size,
            "extras_needed": extras_needed == "Yes",
            "services_needed": services_needed
        },
        "technical": {
            "camera_preference": camera_preference,
            "frame_rate": frame_rate,
            "delivery_format": delivery_format,
            "aspect_ratio": aspect_ratio,
            "special_requirements": special_requirements
        },
        "logistics": {
            "parking": parking,
            "nda_required": nda_required == "Yes",
            "insurance_provided": insurance_provided,
            "accessibility": accessibility == "Yes",
            "additional_notes": additional_notes
        },
        "confirmation": {
            "how_did_you_hear": how_did_you_hear,
            "agreed_to_terms": terms,
            "newsletter": newsletter,
            "priority_booking": priority_booking
        },
        "meta": {
            "source": "chasing_destiny_studios_booking_app",
            "submitted_at": datetime.utcnow().isoformat()
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            st.success("✅ Production booking submitted! A Chasing Destiny Studios representative will be in touch within 24 hours.")
        else:
            st.error(f"❌ Error: {response.status_code} — {response.text}")
    except Exception as e:
        st.error(f"🚨 Failed to submit booking: {e}")
