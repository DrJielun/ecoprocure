import os
import time
import pandas as pd
import streamlit as st
from google import genai
from google.genai import errors

# --- Page Configuration ---
st.set_page_config(
    page_title="EcoProcure: Smart Procurement Auditor",
    page_icon="🌱",
    layout="wide",
)

# --- Custom Styling (Green Minimalist Theme) ---
st.markdown(
    """
    <style>
    :root {
        --primary: #0F5132;
        --primary-light: #D1E7DD;
        --accent: #198754;
    }
    .main {
        background-color: #F8F9FA;
    }
    h1, h2, h3 {
        color: #0F5132 !important;
    }
    .stButton>button {
        background-color: #198754;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #0F5132;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- Header Section ---
st.title("🌱 EcoProcure AI: Smart Procurement Auditor")
st.markdown(
    "Upload your completed EcoProcure Excel template to generate TCO scores,"
    " sustainability ratings, and vendor recommendations."
)

# --- Template Download Section ---
template_path = "template.xlsx"  # Ensure this file exists in your GitHub repo

if os.path.exists(template_path):
  with open(template_path, "rb") as file:
    template_bytes = file.read()

  col1, col2 = st.columns([3, 1])
  with col1:
    st.info(
        "Need the official evaluation layout? Download the template file below"
        " to populate your ITQ data."
    )
  with col2:
    st.download_button(
        label="📥 Download Template",
        data=template_bytes,
        file_name="EcoProcure_Template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
  st.warning(
      "⚠️ Note: `template.xlsx` not found in root directory. File upload is"
      " still fully functional."
  )

st.markdown("---")

# --- API Key Resolution ---
api_key = None
if "GEMINI_API_KEY" in st.secrets:
  api_key = st.secrets["GEMINI_API_KEY"]
else:
  api_key = os.environ.get("GEMINI_API_KEY")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "Upload EcoProcure Excel Template (.xlsx or .csv)", type=["xlsx", "csv"]
)

if uploaded_file is not None:
  try:
    # Read file based on extension
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.subheader("📊 Preview of Uploaded Data Template:")
    st.dataframe(df, use_container_width=True)

    # Convert dataframe to string payload for the model
    data_text = df.to_string(index=True)

    if st.button("Run AI TCO & Sustainability Audit"):
      if not api_key:
        st.error(
            "❌ Missing Gemini API Key. Please configure `GEMINI_API_KEY` in"
            " Streamlit Cloud Secrets."
        )
      else:
        with st.spinner(
            "Running multi-criteria TCO calculation and sustainability audit..."
        ):
          try:
            # Initialize client using modern google-genai SDK
            client = genai.Client(api_key=api_key)

            system_instruction = (
                "You are an expert institutional procurement auditor focused on"
                " environmental sustainability, data analytics, and trusted"
                " governance. For every dataset provided, you must structure"
                " your output into three distinct sections: 1. TCO Score /"
                " Analysis (Review or calculate the 5-year Total Cost of"
                " Ownership based on Initial Bid + [Rated Power * Lifespan *"
                " Usage Hours * Electricity Cost] + [Maintenance Cost *"
                " Lifespan]), 2. Sustainability Score (out of 100 based on"
                " energy efficiency and expected lifespan against e-waste), and"
                " 3. Strategic Recommendations with a definitive verdict"
                " (Approved / Rejected / Alternative) and justified rationale."
            )

            prompt = (
                "Analyze the following structured procurement data from our"
                f" EcoProcure template:\n\n{data_text}"
            )

            # Call gemini-3.7-flash with system instructions
            response = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                ),
            )

            st.success("Audit analysis completed successfully!")
            st.markdown("### 📋 AI Procurement Audit Report")
            st.markdown(response.text)

          except Exception as api_err:
            error_str = str(api_err)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
              st.error(
                  "⚠️ API Quota limit reached for the free tier. Please"
                  " generate a new API key in Google AI Studio or use Google"
                  " AI Studio directly to bypass limits during your presentation."
              )
            else:
              st.error(f"An error occurred during AI generation: {api_err}")

  except Exception as e:
    st.error(
        f"Error reading the uploaded file. Ensure it is a valid Excel or CSV"
        f" format. Details: {e}"
    )
else:
  st.info("👆 Please upload your Excel template file above to generate the audit report.")
