import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8081"

# --- SESSION STATE INITIALIZATION ---
if 'download_info' not in st.session_state:
    st.session_state['download_info'] = None
if 'email_results' not in st.session_state:
    st.session_state['email_results'] = None
if 'detected_location' not in st.session_state:
    st.session_state['detected_location'] = None
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = {'courses': False, 'holidays': False, 'guidelines': False}
if 'available_documents' not in st.session_state:
    st.session_state['available_documents'] = []
if 'documents_loaded' not in st.session_state:
    st.session_state['documents_loaded'] = False

# --- HELPER FUNCTIONS ---
def detect_location():
    """Detect user location from IP"""
    try:
        response = requests.post(f"{API_BASE_URL}/detect_location", json={})
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def fetch_available_documents():
    """Fetch list of available documents from Pinecone"""
    try:
        response = requests.get(f"{API_BASE_URL}/get_documents")
        if response.status_code == 200:
            data = response.json()
            return data.get('documents', [])
        return []
    except Exception as e:
        st.error(f"Error fetching documents: {e}")
        return []

def call_api(endpoint: str, payload: dict):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.post(url, json=payload, stream=True, timeout=120)
        response.raise_for_status()
        content_type = response.headers.get('content-type')
        return response.json() if 'application/json' in content_type else response.content
    except requests.exceptions.RequestException as e:
        st.error(f"API Connection Error: {e}")
        return None

def upload_file_to_api(endpoint: str, file):
    try:
        url = f"{API_BASE_URL}{endpoint}"
        files = {'file': file}
        response = requests.post(url, files=files, timeout=300)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

# --- STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="AI Agent Toolkit", layout="wide")

# --- LOAD AVAILABLE DOCUMENTS ON STARTUP ---
if not st.session_state['documents_loaded']:
    with st.spinner("Loading available documents from knowledge base..."):
        docs = fetch_available_documents()
        if docs:
            st.session_state['available_documents'] = docs
            st.session_state['documents_loaded'] = True

# --- SIDEBAR FOR DATA UPLOADS ---
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    st.subheader("📊 Upload Reference Data")
    st.markdown("*Upload these files once to enable enhanced features*")
    
    with st.expander("📚 Course Duration Data"):
        course_file = st.file_uploader("Upload Course CSV", type=['csv'], key="course_upload")
        if course_file and st.button("Load Courses"):
            with st.spinner("Loading course data..."):
                result = upload_file_to_api("/upload/course_data", course_file)
                if result and result.get('success'):
                    st.success(f"✅ Loaded {result.get('courses_loaded')} courses")
                    st.session_state['data_loaded']['courses'] = True
                else:
                    st.error("❌ Failed to load courses")
    
    with st.expander("🗓️ Holiday Calendar"):
        holiday_file = st.file_uploader("Upload Holidays CSV", type=['csv'], key="holiday_upload")
        if holiday_file and st.button("Load Holidays"):
            with st.spinner("Loading holiday data..."):
                result = upload_file_to_api("/upload/holidays", holiday_file)
                if result and result.get('success'):
                    st.success(f"✅ Loaded holidays for {result.get('states_loaded')} states")
                    st.session_state['data_loaded']['holidays'] = True
                else:
                    st.error("❌ Failed to load holidays")
    
    with st.expander("📝 Assessment Guidelines"):
        guidelines_file = st.file_uploader("Upload Guidelines TXT", type=['txt'], key="guidelines_upload")
        if guidelines_file and st.button("Load Guidelines"):
            with st.spinner("Loading guidelines..."):
                result = upload_file_to_api("/upload/guidelines", guidelines_file)
                if result and result.get('success'):
                    st.success(f"✅ Loaded guidelines ({result.get('guidelines_length')} chars)")
                    st.session_state['data_loaded']['guidelines'] = True
                else:
                    st.error("❌ Failed to load guidelines")
    
    st.divider()
    
    st.subheader("📊 Data Status")
    st.write("Courses:", "✅" if st.session_state['data_loaded']['courses'] else "⚪")
    st.write("Holidays:", "✅" if st.session_state['data_loaded']['holidays'] else "⚪")
    st.write("Guidelines:", "✅" if st.session_state['data_loaded']['guidelines'] else "⚪")
    st.write("Documents:", f"✅ {len(st.session_state['available_documents'])}" if st.session_state['documents_loaded'] else "⚪")

# --- MAIN CONTENT ---
st.title("🤖 AI Agent Toolkit for Tata Strive")

if not st.session_state['detected_location']:
    with st.spinner("Detecting location..."):
        location_data = detect_location()
        if location_data:
            st.session_state['detected_location'] = location_data

location_info = st.session_state.get('detected_location', {})
detected_loc = location_info.get('location', {})
suggested_lang = location_info.get('suggested_language', 'English')

if detected_loc.get('detected'):
    st.info(f"📍 Detected Location: **{detected_loc.get('city', 'Unknown')}, {detected_loc.get('state', 'Unknown')}** | Suggested Language: **{suggested_lang}**")
else:
    st.info("📍 Location not detected. Using defaults.")

tab1, tab2, tab4 = st.tabs([
    "📝 Assessment Creator",
    "🗓️ Lesson Planner",
    "🎯 Personalized Learning"
])

# --- TAB 1: ASSESSMENT CREATOR ---
with tab1:
    st.header("Create a New Assessment")
    
    if not st.session_state['data_loaded']['guidelines']:
        st.warning("⚠️ Upload assessment guidelines in sidebar for enhanced question generation")
    
    # Document Selection
    st.subheader("📚 Select Source Documents")
    st.markdown("*Choose which documents to use for generating the assessment (required)*")
    
    # Search filter
    doc_search = st.text_input("🔍 Search documents:", key="ass_doc_search", placeholder="Type to filter...")
    
    # Filter documents based on search
    filtered_docs = st.session_state['available_documents']
    if doc_search:
        filtered_docs = [d for d in filtered_docs if doc_search.lower() in d.lower()]
    
    # Multi-select with filtered options
    selected_ass_docs = st.multiselect(
        "Select documents:",
        options=filtered_docs,
        key="ass_selected_docs",
        help="Select one or more documents to base the assessment on"
    )
    
    if selected_ass_docs:
        st.success(f"✅ {len(selected_ass_docs)} document(s) selected")
    else:
        st.warning("⚠️ You must select at least one document to proceed")
    
    st.divider()
    
    with st.form("assessment_form"):
        assessment_query = st.text_area("Topic for the assessment:", "Create a quiz about greeting guests at a hotel.", key="ass_query")
        
        col1, col2 = st.columns(2)
        with col1:
            lang_list = ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"]
            default_index = lang_list.index(suggested_lang) if suggested_lang in lang_list else 0
            assessment_lang = st.selectbox("Language:", lang_list, index=default_index, key="ass_lang")
        with col2:
            assessment_format = st.radio("Output Format:", ["json", "docx", "pdf"], key="ass_format", horizontal=True)
        
        if st.form_submit_button("Generate Assessment", use_container_width=True):
            if not selected_ass_docs:
                st.error("❌ Please select at least one source document before generating")
            else:
                st.session_state['download_info'] = None
                with st.spinner("Generating your assessment..."):
                    payload = {
                        "query": assessment_query, 
                        "language": assessment_lang, 
                        "output_format": assessment_format,
                        "selected_documents": selected_ass_docs
                    }
                    result = call_api("/create/assessment", payload)
                    
                    if result:
                        if assessment_format == 'json':
                            st.success("✅ Assessment generated successfully!")
                            st.write("### English Version"); st.markdown(result['english_answer'])
                            if assessment_lang != "English":
                                st.write(f"### {assessment_lang} Version"); st.markdown(result['translated_answer'])
                            st.write("#### Sources Used:"); st.write(result['sources'])
                        else:
                            st.success("✅ Document generated successfully!")
                            st.session_state['download_info'] = {"data": result, "file_name": f"assessment.{assessment_format}", "mime": f"application/{'vnd.openxmlformats-officedocument.wordprocessingml.document' if assessment_format == 'docx' else 'pdf'}"}

    if st.session_state.get('download_info') and 'assessment' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(label=f"📥 Download {info['file_name']}", data=info['data'], file_name=info['file_name'], mime=info['mime'], use_container_width=True)

# --- TAB 2: LESSON PLANNER ---
with tab2:
    st.header("Create a New Lesson Plan")
    
    if not st.session_state['data_loaded']['courses']:
        st.warning("⚠️ Upload course duration data for accurate planning.")
    if not st.session_state['data_loaded']['holidays']:
        st.warning("⚠️ Upload holiday calendar to exclude holidays.")
    
    # Document Selection
    st.subheader("📚 Select Source Documents")
    st.markdown("*Choose which documents to use for generating the lesson plan (required)*")
    
    # Search filter
    lp_doc_search = st.text_input("🔍 Search documents:", key="lp_doc_search", placeholder="Type to filter...")
    
    # Filter documents based on search
    filtered_lp_docs = st.session_state['available_documents']
    if lp_doc_search:
        filtered_lp_docs = [d for d in filtered_lp_docs if lp_doc_search.lower() in d.lower()]
    
    # Multi-select with filtered options
    selected_lp_docs = st.multiselect(
        "Select documents:",
        options=filtered_lp_docs,
        key="lp_selected_docs",
        help="Select one or more documents to base the lesson plan on"
    )
    
    if selected_lp_docs:
        st.success(f"✅ {len(selected_lp_docs)} document(s) selected")
    else:
        st.warning("⚠️ You must select at least one document to proceed")
    
    st.divider()
    
    with st.form("lesson_planner_form"):
        lp_query = st.text_area("Topic for the lesson plan:", "A detailed lesson plan for Front Desk Associate training", key="lp_query")
        
        col1, col2 = st.columns(2)
        with col1:
            lp_course = st.text_input("Course Name (Optional):", "Front Desk Associate", key="lp_course")
            state_list = ["Corporate", "West Bengal", "Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana", "Odisha", "Punjab", "Haryana", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Delhi", "Assam"]
            default_state_index = state_list.index(detected_loc.get('state')) if detected_loc.get('state') in state_list else 0
            lp_state = st.selectbox("State/Location:", state_list, index=default_state_index, key="lp_state")
        
        with col2:
            lp_start_date = st.date_input("Start Date:", value=datetime.now(), key="lp_start_date")
            lang_list = ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"]
            default_lang_index = lang_list.index(suggested_lang) if suggested_lang in lang_list else 0
            lp_lang = st.selectbox("Language:", lang_list, index=default_lang_index, key="lp_lang")
        
        lp_format = st.radio("Output Format:", ["json", "docx", "pdf"], key="lp_format", horizontal=True)
        
        if st.form_submit_button("Generate Lesson Plan", use_container_width=True):
            if not selected_lp_docs:
                st.error("❌ Please select at least one source document before generating")
            else:
                st.session_state['download_info'] = None
                with st.spinner("Generating lesson plan..."):
                    payload = {
                        "query": lp_query, 
                        "course_name": lp_course, 
                        "state": lp_state, 
                        "start_date": lp_start_date.strftime('%Y-%m-%d'), 
                        "language": lp_lang, 
                        "output_format": lp_format,
                        "selected_documents": selected_lp_docs
                    }
                    result = call_api("/create/lesson_plan", payload)
                    
                    if result:
                        if lp_format == 'json':
                            st.success("✅ Lesson plan generated successfully!")
                            st.write("### English Version"); st.markdown(result['english_answer'])
                            if lp_lang != "English":
                                st.write(f"### {lp_lang} Version"); st.markdown(result['translated_answer'])
                            st.write("#### Sources Used:"); st.write(result['sources'])
                            with st.expander("📅 Holidays Considered"): st.text(result['holidays_considered'])
                        else:
                            st.success("✅ Document generated successfully!")
                            st.session_state['download_info'] = {"data": result, "file_name": f"lesson_plan.{lp_format}", "mime": f"application/{'vnd.openxmlformats-officedocument.wordprocessingml.document' if lp_format == 'docx' else 'pdf'}"}

    if st.session_state.get('download_info') and 'lesson_plan' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(label=f"📥 Download {info['file_name']}", data=info['data'], file_name=info['file_name'], mime=info['mime'], use_container_width=True)

# --- TAB 4: PERSONALIZED LEARNING ---
with tab4:
    st.header("🎯 Automated Personalized Learning System")
    st.markdown("Upload student assessment data and the system will automatically analyze performance, generate personalized study guides, and email PDFs to students who need support.")
    
    st.divider()
    
    st.subheader("📤 Upload Assessment Data")
    st.info("Upload a CSV or Excel file with student results. The system will email personalized content to students scoring below 70%.")
    
    uploaded_file = st.file_uploader("Upload Assessment CSV/Excel", type=['csv', 'xlsx', 'xls'], key="assessment_upload")
    
    if uploaded_file:
        if st.button("🚀 Process & Send Emails", use_container_width=True, type="primary"):
            st.session_state['email_results'] = None
            
            with st.spinner("⏳ Processing assessment data and sending emails... This may take a few minutes..."):
                result = upload_file_to_api("/process/assessment_and_email", uploaded_file)
                
                if result and 'error' not in result:
                    st.session_state['email_results'] = result
                    st.success("✅ Processing Complete!")
                else:
                    st.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
    
    if st.session_state.get('email_results'):
        results = st.session_state['email_results']
        st.divider()
        st.subheader("📊 Processing Results")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Students", results.get('total_students', 0))
        col2.metric("Average Score", f"{results.get('average_score', 0):.1f}%")
        col3.metric("Emails Sent", results.get('emails_sent', 0))
        
        st.divider()
        
        st.subheader("📧 Email Delivery Status")
        email_df = pd.DataFrame(results.get('email_results', []))
        if not email_df.empty:
            st.dataframe(email_df.style.applymap(lambda v: 'background-color: #d4edda; color: #155724' if '✅' in str(v) else ('background-color: #f8d7da; color: #721c24' if '❌' in str(v) else ''), subset=['status']), use_container_width=True, hide_index=True)
            st.download_button("📥 Download Email Report (CSV)", email_df.to_csv(index=False), "email_delivery_report.csv", "text/csv")
        else:
            st.info("ℹ️ No emails needed to be sent (all students scored above 70%).")
        
        st.divider()
        
        weak_questions = results.get('weak_questions', [])
        if weak_questions:
            st.subheader("📉 Most Challenging Questions")
            st.markdown("*Questions that less than 60% of students answered correctly.*")
            for i, q in enumerate(weak_questions, 1):
                with st.expander(f"Question {i} - Success Rate: {q['success_rate']:.1f}%"):
                    st.write(q['question'])