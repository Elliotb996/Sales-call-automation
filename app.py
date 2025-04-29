import streamlit as st
import openai
import pandas as pd
import json
from fpdf import FPDF
import datetime

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None

# ---- CONFIG ----
st.set_page_config(page_title="Broker Buddy", layout="wide")
openai.api_key = ""  # Initialize empty, set via input

# ---- HEADER ----
st.title("📈 Broker Buddy - AI Compliance & Sales Assistant")
st.markdown("""
**Paste your call transcript below** to generate:
- Compliance Review 🚦
- Sales Coaching 📈  
- CRM Data Extraction 💼
- Lender Recommendations 🏦
""")

# ---- SIDEBAR FOR API KEY ----
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter OpenAI API Key:", type="password")
    if api_key:
        if not api_key.startswith('sk-'):
            st.warning("⚠️ Please enter a valid OpenAI API key")
        else:
            openai.api_key = api_key
            st.success("✅ API Key validated")

# ---- MAIN INPUT ----
transcript = st.text_area("Paste Call Transcript Here:", height=300, help="Minimum 500 characters for best results")

# ---- AI PROCESSING FUNCTIONS ----
def run_compliance_check(transcript):
    try:
        prompt = f"""Act as a senior FCA compliance officer. Analyze this financial services transcript:
        - Check Consumer Duty (PROD) compliance
        - Identify vulnerable customer indicators
        - Verify product explanations (PCP/HP/Lease)
        - Detect potential fraud indicators
        - Assess information symmetry

        Use UK financial regulations. Format response as:
        🟢 [Compliant Areas]
        🟠 [Minor Issues]  
        🔴 [Critical Failures]

        Transcript: {transcript}"""

        with st.spinner("🔍 Running compliance check..."):
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=400,
                temperature=0.2
            )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Compliance check failed: {str(e)}")
        return "Error in compliance analysis"

def run_sales_coaching(transcript):
    try:
        prompt = f"""As a top-performing sales coach, analyze this sales call:
        - Rapport building effectiveness
        - Needs discovery process
        - Objection handling
        - Closing techniques
        - 3 actionable improvement suggestions

        Focus on UK motor finance context. Use markdown bullet points.

        Transcript: {transcript}"""

        with st.spinner("💡 Generating sales insights..."):
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=400,
                temperature=0.3
            )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Sales coaching failed: {str(e)}")
        return "Error in sales analysis"

def extract_crm_data(transcript):
    try:
        prompt = f"""Extract structured data from this transcript. Return valid JSON:
        {{
            "deposit": "currency amount",
            "term": "months", 
            "annual_mileage": "number",
            "monthly_budget": "currency",
            "vehicle_type": "string",
            "business_use": "boolean"
        }}
        Use null for missing values. Transcript: {transcript}"""

        with st.spinner("📂 Extracting CRM data..."):
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
        return json.loads(response['choices'][0]['message']['content'])
    except Exception as e:
        st.error(f"CRM extraction failed: {str(e)}")
        return {"error": "Failed to extract CRM data"}

def recommend_lender(transcript):
    try:
        prompt = f"""Classify lender suitability from UK motor finance transcript:
        Options:
        - Aldermore (Business/commercial use)
        - Alphera (Standard personal)
        - Close Brothers (Adverse credit)
        - Blackhorse (Prime credit)
        - Specialist (Unique circumstances)
        
        Return only the lender name. Transcript: {transcript}"""

        with st.spinner("🤖 Analyzing lender match..."):
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": prompt}],
                max_tokens=50,
                temperature=0.1
            )
        return response['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Lender recommendation failed: {str(e)}")
        return "Error in lender recommendation"

# ---- REPORT GENERATION ----
def generate_pdf():
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Header
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt="Broker Buddy Analysis Report", ln=1, align='C')
        pdf.set_font("Arial", size=10)
        pdf.cell(200, 10, txt=f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=1, align='C')
        pdf.ln(15)
        
        # Compliance Section
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Compliance Review", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, st.session_state.results['compliance'])
        pdf.ln(10)
        
        # Sales Coaching
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Sales Coaching", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, st.session_state.results['sales'])
        pdf.ln(10)
        
        # CRM Data
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="CRM Data", ln=1)
        pdf.set_font("Arial", size=10)
        for key, value in st.session_state.results['crm'].items():
            pdf.multi_cell(0, 8, f"{key.replace('_', ' ').title()}: {value or 'N/A'}")
        pdf.ln(10)
        
        # Lender Recommendation
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Lender Recommendation", ln=1)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(0, 8, st.session_state.results['lender'])
        
        return pdf.output(dest='S').encode('latin-1')
    except Exception as e:
        st.error(f"PDF generation failed: {str(e)}")
        return None

# ---- MAIN PROCESSING ----
if st.button("🚀 Run Full Analysis"):
    if not api_key or not api_key.startswith('sk-'):
        st.error("Please provide a valid OpenAI API key in the sidebar")
    elif len(transcript) < 500:
        st.warning("Please provide a longer transcript for meaningful analysis")
    else:
        with st.status("🔮 Processing transcript...", expanded=True) as status:
            try:
                st.write("Starting compliance analysis...")
                compliance = run_compliance_check(transcript)
                
                st.write("Analyzing sales performance...")
                sales = run_sales_coaching(transcript)
                
                st.write("Extracting CRM data...")
                crm = extract_crm_data(transcript)
                
                st.write("Determining lender match...")
                lender = recommend_lender(transcript)
                
                st.session_state.results = {
                    'compliance': compliance,
                    'sales': sales,
                    'crm': crm,
                    'lender': lender
                }
                
                status.update(label="Analysis complete!", state="complete", expanded=False)
                st.toast("✅ Analysis completed!", icon="✅")
                
            except openai.error.AuthenticationError:
                st.error("❌ Invalid API key - please verify in sidebar")
            except openai.error.APIError as e:
                st.error(f"🚨 OpenAI API Error: {str(e)}")
            except Exception as e:
                st.error(f"⚠️ Unexpected error: {str(e)}")

# ---- DISPLAY RESULTS ----
if st.session_state.results:
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚦 Compliance Review")
        st.markdown(st.session_state.results['compliance'])
        
        st.subheader("📊 CRM Data")
        st.json(st.session_state.results['crm'])
    
    with col2:
        st.subheader("📈 Sales Coaching")
        st.markdown(st.session_state.results['sales'])
        
        st.subheader("🏦 Lender Recommendation")
        st.success(st.session_state.results['lender'])

    st.divider()
    
    # PDF Download
    pdf_bytes = generate_pdf()
    if pdf_bytes:
        st.download_button(
            label="📥 Download Full Report (PDF)",
            data=pdf_bytes,
            file_name=f"Broker_Buddy_Report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            help="Download comprehensive PDF report with all analysis"
        )

# ---- FOOTER ----
st.markdown("""
---
**Broker Buddy v1.0** | Developed for FCA-regulated UK brokers  
Next features: Audio transcription | Client dashboards | Custom lender matrices
""")
