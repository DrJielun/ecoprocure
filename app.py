from google import genai
import pandas as pd
import streamlit as st

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
      with st.spinner(
          "Calculating TCO scores, evaluating sustainability, and generating"
          " recommendations..."
      ):
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        client = genai.Client(api_key=api_key) if api_key else genai.Client()

        response = client.interactions.create(
            model="gemini-3.7-flash",
            input=f"""
                You are an expert institutional procurement auditor focused on environmental sustainability, data analytics, and trusted governance.
                Analyze the following structured procurement data from our EcoProcure template (which includes Item Category, Item Name, Supplier Name, Initial Bid, Rated Power, Lifespan, Usage Hours, Electricity Cost, and Maintenance Cost):
                
                {template_data_string}
                
                You MUST structure your output into three distinct sections for every item evaluated:
                1. **TCO Score / Analysis:** Review or calculate the 5-year or total lifecycle Cost of Ownership (Initial Bid + [Rated Power * Lifespan * Usage Hours * Electricity Cost] + [Maintenance Cost * Lifespan]).
                2. **Sustainability Score:** Provide a clear score out of 100 based on energy efficiency (rated power draw) and expected lifespan (durability against e-waste).
                3. **Strategic Recommendations:** Give a definitive verdict (e.g., Approved / Rejected / Alternative) with a justified rationale on which supplier provides the best long-term institutional value.
                """,
        )

        st.subheader(
            "💡 AI Audit Report: TCO, Sustainability Scores & Recommendations"
        )
        st.markdown(response.output_text)

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
