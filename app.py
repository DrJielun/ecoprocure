from google import genai
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="EcoProcure AI: Smart Procurement Auditor", page_icon="🌱", layout="wide"
)

st.title("🌱 EcoProcure AI: Smart Procurement Auditor")
st.write(
    "Upload your completed EcoProcure Excel template to generate TCO scores,"
    " sustainability ratings, and vendor recommendations."
)

# File uploader for your exact template structure
uploaded_file = st.file_uploader(
    "Upload EcoProcure Excel Template (.xlsx or .csv)", type=["csv", "xlsx"]
)

if uploaded_file is not None:
  try:
    # Read the file depending on its extension
    if uploaded_file.name.endswith(".csv"):
      df = pd.read_csv(uploaded_file)
    else:
      df = pd.read_excel(uploaded_file)

    st.write("### 📊 Preview of Uploaded Data Template:")
    st.dataframe(df)

    # Convert the structured table into clean text for Gemini to analyze
    template_data_string = df.to_string(index=False)

    if st.button("Run AI TCO & Sustainability Audit"):
      # Safely retrieve the API key from Streamlit Secrets
      api_key = st.secrets.get("GEMINI_API_KEY", None)

      if not api_key:
        st.error(
            "⚠️ GEMINI_API_KEY is missing! Please configure it in your Streamlit"
            " Cloud 'Settings > Secrets'."
        )
      else:
        with st.spinner(
            "Calculating TCO scores, evaluating sustainability, and generating"
            " recommendations..."
        ):
          try:
            client = genai.Client(api_key=api_key)

            # Generate content using the stable flash model and correct SDK method
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                    You are an expert institutional procurement auditor focused on environmental sustainability, data analytics, and trusted governance.
                    Analyze the following structured procurement data from our EcoProcure template:
                    
                    {template_data_string}
                    
                    You MUST structure your output into three distinct sections for every item evaluated:
                    1. **TCO Score / Analysis:** Review or calculate the 5-year Total Cost of Ownership (Initial Bid + [Rated Power * Lifespan * Usage Hours * Electricity Cost] + [Maintenance Cost * Lifespan]).
                    2. **Sustainability Score:** Provide a clear score out of 100 based on energy efficiency (rated power draw) and expected lifespan (durability against e-waste).
                    3. **Strategic Recommendations:** Give a definitive verdict (Approved / Rejected / Alternative) with a justified rationale on which supplier provides the best long-term institutional value.
                    """,
            )

            st.subheader(
                "💡 AI Audit Report: TCO, Sustainability Scores & Recommendations"
            )
            st.markdown(response.text)

          except Exception as api_err:
            st.error(f"An error occurred during AI generation: {api_err}")

  except Exception as e:
    st.error(
        f"Error processing the file: {e}. Please ensure your Excel file matches"
        " the expected column headers."
    )
else:
  st.info(
      "👆 Please upload your Excel template file above to generate the audit"
      " report."
  )
