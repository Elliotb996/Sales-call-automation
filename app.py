import streamlit as st
import openai
import pandas as pd
from fpdf import FPDF
import datetime

from openai import OpenAI
client = OpenAI(api_key=api_key)

# ---- CONFIG ----
st.set_page_config(page_title="Broker Buddy", layout="wide")

# ---- HEADER ----
st.title("Broker Buddy - AI Compliance & Sales Assistant")
st.write("Paste your call transcript below and click **Run Analysis** to generate compliance checks, sales coaching, CRM data extraction, and lender recommendations.")

# ---- API KEY INPUT ----
api_key = st.text_input("Enter your OpenAI API Key:", type="password")

if api_key:
    openai.api_key = api_key

# ---- TRANSCRIPT INPUT ----
transcript = st.text_area("Paste Call Transcript Here:", height=300)

# ---- AI PROCESSING FUNCTIONS ----

def run_compliance_check(transcript):
    prompt = f"""
    You are a UK financial compliance officer. Review this transcript for:
    1. FCA Consumer Duty adherence.
    2. Vulnerability checks.
    3. Correct product explanation (PCP, HP, etc).
    4. Fraud red flags.

    Give Traffic Light status (Green, Amber, Red) and key points.

    Transcript:
    {transcript}
    """

   response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "system", "content": prompt}],
    max_tokens=300
)
return response.choices[0].message.content



def run_sales_coaching(transcript):
    prompt = f"""
    You are a UK motor finance sales coach. Review this transcript and provide:
    - Feedback on rapport, structure, opportunity awareness.
    - 2 practical improvement tips.

    Transcript:
    {transcript}
    """

    response = client.chat.completions.create(
    model="gpt-4-turbo",
    messages=[{"role": "system", "content": prompt}],
    max_tokens=300
)
return response.choices[0].message.content



def extract_crm_data(transcript):
    return {
        "Deposit": "£2,000",
        "Term": "48 months",
        "Annual Mileage": "10,000",
        "Budget": "£300/month"
    }

def recommend_lender(transcript):
    if "business owner" in transcript.lower() or "limited company" in transcript.lower():
        return "Suggested Lender: Aldermore - Meets business lending criteria."
    else:
        return "Suggested Lender: Alphera - Suitable for standard regulated customer."

# ---- RUN ANALYSIS ----
if st.button("Run Analysis"):

    if not transcript or not api_key:
        st.error("Please provide both your OpenAI API Key and a transcript.")
    else:
        with st.spinner("Analyzing call..."):

            compliance_result = run_compliance_check(transcript)
            sales_result = run_sales_coaching(transcript)
            crm_data = extract_crm_data(transcript)
            lender_recommendation = recommend_lender(transcript)

            st.subheader("Compliance Review")
            st.success(compliance_result)

            st.subheader("Sales Coaching")
            st.info(sales_result)

            st.subheader("CRM Data Extracted")
            st.write(pd.DataFrame([crm_data]))

            st.subheader("Lender Recommendation")
            st.warning(lender_recommendation)

            if st.button("Download PDF Report"):
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt="Broker Buddy - Call Report", ln=True, align='C')
                pdf.cell(200, 10, txt=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')
                pdf.ln(10)
                pdf.multi_cell(0, 10, f"{compliance_result}\n\n{sales_result}\n\nLender: {lender_recommendation}")
                pdf.output("Broker_Buddy_Report.pdf")
                st.success("PDF Report Generated! Check your app folder.")
