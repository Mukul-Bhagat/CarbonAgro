import streamlit as st
import pandas as pd
from pathlib import Path

# ================================
# Path Setup
# ================================
# This ensures your app can find the files reliably
base_path = Path(__file__).parent
yield_csv_path = base_path / "crop_yield_with_carbon_footprint.csv"
measures_csv_path = base_path / "crop_measures.csv"
image_path = base_path / "image1.webp"


# ================================
# Load Data
# ================================
@st.cache_data
def load_data():
    df = pd.read_csv(yield_csv_path)
    measures = pd.read_csv(measures_csv_path)
    
    # Standardize column names
    df.columns = [c.lower().strip() for c in df.columns]
    measures.columns = [c.lower().strip() for c in measures.columns]
    
    return df, measures

df, measures = load_data()

# ================================
# Streamlit UI
# ================================
st.sidebar.title("🌱 CarbonAgro")
app_mode = st.sidebar.selectbox("Select Page", ["Home", "About", "Crop Analysis"])

if app_mode == "Home":
    st.header("Welcome to the Crop Carbon Footprint System 🌿")
    st.image(str(image_path), use_container_width=True)

    st.markdown("""
    <div style='text-align: center; font-size: 18px;'>
        This app helps analyze <b>crop yield and carbon footprint</b> 
        and provides <b>necessary measures</b> to reduce environmental impact. 🌍 
        <br><br>
        By leveraging data-driven insights, farmers and researchers can 
        make informed decisions that promote sustainable agriculture, 
        reduce greenhouse gas emissions, and improve food security. 🌱🌾 
        <br><br>
        👉 Use the sidebar to start your <b>Crop Analysis</b> today!
    </div>
    """, unsafe_allow_html=True)

elif app_mode == "About":
    st.header("About this Project")
    st.markdown("""
    - *Dataset 1:* Crop yield with carbon footprint (crop_yield_with_carbon_footprint.csv) 
    - *Dataset 2:* Measures for crops (crop_measures.csv) 

    #### What this app does:
    1. User enters *Crop Name*, *Area*, *Fertilizer*, and *Pesticide*. 
    2. Model estimates *carbon footprint*. 
    3. Displays *recommended measures* for sustainability. 
    """)

elif app_mode == "Crop Analysis":
    st.header("🔎 Crop Analysis")

    # User inputs
    crop_list = df["crop"].unique()
    selected_crop = st.selectbox("Select a Crop", crop_list)
    area = st.number_input("Enter Area (in hectares):", min_value=0.0, step=0.1)
    fertilizer = st.number_input("Enter Fertilizer Used (in kg):", min_value=0.0, step=1.0)
    pesticide = st.number_input("Enter Pesticide Used (in kg):", min_value=0.0, step=1.0)

    if area > 0:
        crop_data = df[df["crop"].str.lower() == selected_crop.lower()]

        if not crop_data.empty:
            st.subheader(f"📊 Analysis for {selected_crop}")

            # --- Safe Carbon Footprint Calculation ---
            # Base factor: take avg from dataset if exists, else default
            if "carbon_footprint" in crop_data.columns:
                base_factor = crop_data["carbon_footprint"].replace([float("inf"), -float("inf")], float("nan")).dropna().mean()
                if pd.isna(base_factor) or base_factor <= 0:
                    base_factor = 1.0
            else:
                base_factor = 1.0

            # Emission factors (example constants — tweak as needed)
            fertilizer_factor = 0.002  # footprint units per kg fertilizer
            pesticide_factor = 0.001   # footprint units per kg pesticide

            # Final footprint calculation
            predicted_cf = (area * base_factor) + (fertilizer * fertilizer_factor) + (pesticide * pesticide_factor)

            # Display results
            st.write(f"*Entered Area:* {area} hectares")
            st.write(f"*Fertilizer Used:* {fertilizer} kg")
            st.write(f"*Pesticide Used:* {pesticide} kg")
            st.success(f"🌍 Estimated Carbon Footprint: **{predicted_cf:.2f} units**")

            # Show recommended measures
            crop_measures = measures[measures["crop"].str.lower() == selected_crop.lower()]
            if not crop_measures.empty:
                st.subheader("🌱 Recommended Measures")
                unique_measures = crop_measures["necessary_measures"].drop_duplicates().tolist()
                for measure in unique_measures:
                    st.write(f"- {measure}")
            else:
                st.warning("No specific measures found for this crop.")
