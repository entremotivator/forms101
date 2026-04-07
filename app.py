import streamlit as st
import requests
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
WEBHOOK_URL = "https://agentonline-u29564.vm.elestio.app/webhook/b0b99781-cab8-4967-b87e-88cbbc87b8ba"

st.set_page_config(page_title="Cleaning Booking System", layout="wide")

st.title("🧼 Cleaning Service Booking Form")

# -------------------------
# SECTION 1: CLIENT INFO
# -------------------------
st.header("Client Information")

col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Full Name", "John Doe")
    email = st.text_input("Email", "johndoe@email.com")

with col2:
    phone = st.text_input("Phone", "(555) 123-4567")
    contact_method = st.selectbox("Preferred Contact Method", ["Phone", "Email", "Text"], index=2)

# -------------------------
# SECTION 2: PROPERTY
# -------------------------
st.header("Property Details")

col1, col2, col3 = st.columns(3)

with col1:
    address = st.text_input("Address", "123 Main St, Atlanta, GA")
    property_type = st.selectbox("Property Type", ["Apartment", "Condo", "House", "Office", "Airbnb"], index=2)

with col2:
    sqft = st.number_input("Square Footage", value=2000)
    bedrooms = st.number_input("Bedrooms", value=3)

with col3:
    bathrooms = st.number_input("Bathrooms", value=2)
    floors = st.number_input("Floors", value=2)

# -------------------------
# SECTION 3: CLEANING DETAILS
# -------------------------
st.header("Cleaning Details")

col1, col2 = st.columns(2)

with col1:
    service_type = st.selectbox("Cleaning Type", [
        "Standard", "Deep Cleaning", "Move-In", "Move-Out", "Post-Construction", "Commercial"
    ], index=1)

    frequency = st.selectbox("Frequency", [
        "One-Time", "Weekly", "Bi-Weekly", "Monthly"
    ])

with col2:
    date = st.date_input("Preferred Date")
    time_window = st.selectbox("Time Window", ["Morning", "Afternoon", "Evening"])

duration = st.slider("Estimated Duration (hours)", 1, 12, 4)

# -------------------------
# SECTION 4: SCOPE
# -------------------------
st.header("Cleaning Scope")

areas = st.multiselect(
    "Areas to Clean",
    ["Kitchen", "Bathrooms", "Bedrooms", "Living Areas", "Garage", "Basement"],
    default=["Kitchen", "Bathrooms", "Bedrooms", "Living Areas"]
)

addons = st.multiselect(
    "Add-ons",
    ["Inside Fridge", "Inside Oven", "Windows", "Carpet Cleaning", "Laundry"],
    default=["Inside Oven", "Windows"]
)

col1, col2 = st.columns(2)

with col1:
    supplies = st.radio("Will you provide supplies?", ["No", "Yes"], index=0)
with col2:
    pets = st.radio("Pets in home?", ["Yes", "No"], index=0)

pet_details = st.text_input("Pet Details", "Small dog, friendly")

# -------------------------
# SECTION 5: ACCESS
# -------------------------
st.header("Access & Instructions")

entry_method = st.text_input("Entry Method", "Key under mat")
parking = st.text_input("Parking", "Driveway available")
alarm = st.radio("Alarm System?", ["No", "Yes"], index=0)
instructions = st.text_area("Special Instructions", "Focus on kitchen and bathrooms")

# -------------------------
# SECTION 6: BILLING
# -------------------------
st.header("Pricing & Confirmation")

budget = st.selectbox("Budget Range", ["$100–$200", "$200–$400", "$400+"], index=1)
terms = st.checkbox("Agree to Terms", value=True)
sms = st.checkbox("Receive SMS Updates", value=True)

# -------------------------
# SUBMIT
# -------------------------
if st.button("🚀 Submit Booking"):
    
    payload = {
        "client_info": {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "contact_method": contact_method
        },
        "property_details": {
            "address": address,
            "type": property_type,
            "square_footage": sqft,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "floors": floors
        },
        "cleaning_details": {
            "service_type": service_type,
            "frequency": frequency,
            "date": str(date),
            "time_window": time_window,
            "duration_hours": duration
        },
        "cleaning_scope": {
            "areas": areas,
            "addons": addons,
            "supplies_provided": supplies == "Yes",
            "pets": pets == "Yes",
            "pet_details": pet_details
        },
        "access_details": {
            "entry_method": entry_method,
            "parking": parking,
            "alarm": alarm == "Yes",
            "instructions": instructions
        },
        "billing": {
            "budget_range": budget,
            "agreed_to_terms": terms,
            "sms_updates": sms
        },
        "meta": {
            "source": "streamlit_booking_app",
            "submitted_at": datetime.utcnow().isoformat()
        }
    }

    try:
        response = requests.post(WEBHOOK_URL, json=payload)

        if response.status_code == 200:
            st.success("✅ Booking submitted successfully!")
        else:
            st.error(f"❌ Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"🚨 Failed to send booking: {e}")
