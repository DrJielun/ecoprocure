import streamlit as st
from google import genai

st.title("🌱 EcoProcure AI: Smart Procurement Auditor")
st.write("Evaluate supplier bids for workshop tools using Total Cost of Ownership (TCO) and sustainability metrics.")

# Input fields for user data
item_name = st.text_input("Item Name", "Heavy-Duty Bench Grinder")
bid_data = st.text_area(
    "Paste Supplier Quotes & Specs",
    "1. Alpha Industrial Tools: Cost = $450, Power = 1.2 kW, Lifespan = 8 yrs, Maint = $25/yr\n"
    "2. Beta Machinery Supply: Cost = $380, Power = 1.8 kW, Lifespan = 5 yrs, Maint = $40/yr"
)

if st.button("Run AI Sustainability Audit"):
  with st.spinner("Analyzing TCO and Environmental Impact..."):
    # Initialize Gemini Client (picks up cloud environment secrets safely)
    client = genai.Client()

    response = client.interactions.create(
        model="gemini-3.7-flash",
        input=f"""
        You are an expert institutional procurement auditor focused on environmental sustainability.
        Evaluate these supplier options for '{item_name}':
        {bid_data}
        Calculate 5-year TCO (assuming $0.28/kWh and 300 usage hours/year), score sustainability, and give a clear recommendation.
        """,
    )

    st.subheader("Audit Results & Recommendation")
    st.markdown(response.output_text)