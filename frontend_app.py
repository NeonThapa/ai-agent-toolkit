import streamlit as st
import requests
import json

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8081" 

# --- SESSION STATE INITIALIZATION ---
# This is a best practice to prevent errors on the first run.
if 'download_info' not in st.session_state:
    st.session_state['download_info'] = None

# --- HELPER FUNCTIONS ---
@st.cache_data
def get_location():
    try:
        response = requests.get("http://ip-api.com/json")
        data = response.json()
        city, region = data.get("city", ""), data.get("regionName", "")
        location_str = f"{city}, {region}" if city and region else "India"
        return location_str
    except Exception:
        return "India"

def call_api(endpoint: str, payload: dict):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=payload, stream=True)
        response.raise_for_status()
        content_type = response.headers.get('content-type')
        return response.json() if 'application/json' in content_type else response.content
    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {e}")
        return None

# --- STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="AI Agent Toolkit", layout="wide")
st.title("🤖 AI Agent Toolkit for Tata Strive")

detected_location = get_location()
st.info(f"📍 Location Detected: **{detected_location}**. Prompts tailored for this region.")

tab1, tab2, tab3 = st.tabs(["📝 Assessment Creator", "🗓️ Lesson Planner", "📚 Content Generator"])

# --- TAB 1: ASSESSMENT CREATOR ---
with tab1:
    st.header("Create a New Assessment")
    with st.form("assessment_form"):
        assessment_query = st.text_area("Topic for the assessment:", "Create a quiz about greeting guests at a hotel.", key="ass_query")
        assessment_lang = st.selectbox("Language:", ["English", "Bengali", "Hindi", "Marathi"], key="ass_lang")
        assessment_format = st.radio("Output Format:", ["json", "docx", "pdf"], key="ass_format")
        
        submitted = st.form_submit_button("Generate Assessment")
        if submitted:
            # Clear previous download info before starting a new request
            st.session_state['download_info'] = None
            with st.spinner("Generating your assessment..."):
                payload = {"query": assessment_query, "language": assessment_lang, "location": detected_location, "output_format": assessment_format}
                result = call_api("/create/assessment", payload)
                
                if result:
                    if assessment_format == 'json':
                        st.write("### English Answer"); st.markdown(result['english_answer'])
                        st.write("---"); st.write(f"### Translated Answer ({result['language']})"); st.markdown(result['translated_answer'])
                        st.write("---"); st.write("#### Sources:"); st.write(result['sources'])
                    else: # For docx or pdf
                        st.success("✅ Document generated successfully!")
                        mime_types = {"docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "pdf": "application/pdf"}
                        # Store file info in session state instead of showing the button here
                        st.session_state['download_info'] = {
                            "data": result,
                            "file_name": f"assessment.{assessment_format}",
                            "mime": mime_types[assessment_format]
                        }

    # --- DOWNLOAD BUTTON LOGIC (MOVED OUTSIDE THE FORM) ---
    if st.session_state.get('download_info') and 'assessment' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(label=f"📥 Download {info['file_name']}", data=info['data'], file_name=info['file_name'], mime=info['mime'])

# --- TAB 2: LESSON PLANNER ---
with tab2:
    st.header("Create a New Lesson Plan")
    with st.form("lesson_planner_form"):
        lp_query = st.text_area("Topic for the lesson plan:", "A 30-minute lesson on the check-in procedure.", key="lp_query")
        lp_lang = st.selectbox("Language:", ["English", "Bengali", "Hindi", "Marathi"], key="lp_lang")
        lp_format = st.radio("Output Format:", ["json", "docx", "pdf"], key="lp_format")
        
        submitted = st.form_submit_button("Generate Lesson Plan")
        if submitted:
            st.session_state['download_info'] = None
            with st.spinner("Generating your lesson plan..."):
                payload = {"query": lp_query, "language": lp_lang, "location": detected_location, "output_format": lp_format}
                result = call_api("/create/lesson_plan", payload)
                
                if result:
                    if lp_format == 'json':
                        st.write("### English Answer"); st.markdown(result['english_answer'])
                        st.write("---"); st.write(f"### Translated Answer ({result['language']})"); st.markdown(result['translated_answer'])
                        st.write("---"); st.write("#### Sources:"); st.write(result['sources'])
                    else: # For docx or pdf
                        st.success("✅ Lesson plan generated successfully!")
                        mime_types = {"docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "pdf": "application/pdf"}
                        st.session_state['download_info'] = {
                            "data": result,
                            "file_name": f"lesson_plan.{lp_format}",
                            "mime": mime_types[lp_format]
                        }

    # --- DOWNLOAD BUTTON LOGIC (MOVED OUTSIDE THE FORM) ---
    if st.session_state.get('download_info') and 'lesson_plan' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(label=f"📥 Download {info['file_name']}", data=info['data'], file_name=info['file_name'], mime=info['mime'])

# --- TAB 3: CONTENT GENERATOR ---
with tab3:
    st.header("Generate Supplementary Content")
    st.write("Content Generator feature coming soon.")