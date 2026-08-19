from google import genai
import pandas as pd
import streamlit as st

st.title("🌱 EcoProcure AI: Smart Procurement Auditor")
st.write(
    "Upload your completed EcoProcure Excel template to audit supplier bids"
    " and calculate Total Cost of Ownership (TCO)."
)

# File uploader for the exact Excel template
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
          "Analyzing TCO, energy consumption, and lifecycle impact..."
      ):
        api_key = st.secrets.get("GEMINI_API_KEY", None)
        client = genai.Client(api_key=api_key) if api_key else genai.Client()

        response = client.interactions.create(
            model="gemini-3.7-flash",
            input=f"""
                You are an expert institutional procurement auditor focused on environmental sustainability and trusted governance.
                Analyze the following structured procurement data from our EcoProcure template:
                
                {template_data_string}
                
                Your tasks:
                1. Review the Initial Bids, Rated Power, Lifespan, and Maintenance costs provided in the table.
                2. Verify the 5-year Total Cost of Ownership (TCO) calculations.
                3. Evaluate the sustainability and e-waste impact based on equipment durability and power draw.
                4. Provide a clear, structured recommendation on which supplier should be approved or rejected based on long-term institutional value.
                """,
        )

        st.subheader("💡 AI Procurement Audit & Recommendations")
        st.markdown(response.output_text)

  except Exception as e:
    st.error(
        f"Error processing the file: {e}. Please ensure you are uploading the"
        " correct EcoProcure template structure."
    )
else:
  st.info(
      "👆 Please upload your Excel template file above to begin the audit."
  )
