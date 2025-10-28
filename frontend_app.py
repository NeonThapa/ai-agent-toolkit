import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
API_BASE_URL = "http://localhost:8081"
LANGUAGE_OPTIONS = ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"]
STATE_OPTIONS = [
    "Corporate", "West Bengal", "Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka",
    "Kerala", "Andhra Pradesh", "Telangana", "Odisha", "Punjab", "Haryana",
    "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Delhi", "Assam"
]
CONTENT_TYPE_OPTIONS = [
    "Learning Guide",
    "Facilitator Notes",
    "Workshop Outline",
    "Learner Handout",
    "Quick Reference Sheet"
]
TONE_OPTIONS = ["Professional", "Friendly", "Motivational", "Coaching", "Inspirational"]
LENGTH_OPTIONS = ["Brief", "Standard", "In-depth"]

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

def render_document_selector(section_key: str, description: str):
    st.subheader("📚 Select Source Documents")
    st.markdown(description)
    
    docs = st.session_state.get('available_documents', [])
    search_value = st.text_input(
        "🔍 Search documents:",
        key=f"{section_key}_doc_search",
        placeholder="Type to filter..."
    )
    
    filtered_docs = docs
    if search_value:
        filtered_docs = [d for d in docs if search_value.lower() in d.lower()]
        if not filtered_docs:
            st.info("No documents matched your search. Clear the filter to see all items.")
    
    selected = st.multiselect(
        "Select documents:",
        options=filtered_docs,
        key=f"{section_key}_selected_docs",
        help="Select one or more documents to ground the AI generation"
    )
    
    if selected:
        st.success(f"✅ {len(selected)} document(s) selected")
    else:
        st.warning("⚠️ Select at least one document to proceed")
    
    st.caption("Tip: Use the search box to quickly narrow down long document lists.")
    st.divider()
    return selected

# --- STREAMLIT APP LAYOUT ---
st.set_page_config(page_title="AI Agent Toolkit", layout="wide")
st.markdown(
    """
    <style>
        .stApp {background-color: #f5f7fb;}
        .stTabs [role="tab"] {padding: 0.75rem 1.5rem; font-weight: 600;}
        .stTabs [role="tab"][aria-selected="true"] {background-color: #ffffff; border-bottom: 3px solid #2c7be5;}
        .status-pill {padding: 0.35rem 0.75rem; border-radius: 999px; background-color: #edf2ff; color: #1d4ed8; font-size: 0.8rem; display: inline-block;}
        .info-card {background: #ffffff; border-radius: 12px; padding: 1.2rem; box-shadow: 0 10px 20px rgba(15, 23, 42, 0.06);}
    </style>
    """,
    unsafe_allow_html=True
)

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
                    region_count = result.get('states_loaded') or result.get('regions_loaded') or 0
                    label = "region" if region_count == 1 else "regions"
                    st.success(f"✅ Loaded holidays for {region_count} {label}")
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
    st.markdown(
        f"<span class='status-pill'>{'✅' if st.session_state['data_loaded']['courses'] else '⚪'} Courses</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<span class='status-pill'>{'✅' if st.session_state['data_loaded']['holidays'] else '⚪'} Holidays</span>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<span class='status-pill'>{'✅' if st.session_state['data_loaded']['guidelines'] else '⚪'} Guidelines</span>",
        unsafe_allow_html=True
    )
    document_status = f"✅ {len(st.session_state['available_documents'])}" if st.session_state['documents_loaded'] else "⚪"
    st.markdown(
        f"<span class='status-pill'>{document_status} Documents</span>",
        unsafe_allow_html=True
    )

# --- MAIN CONTENT ---
st.title("🤖 AI Agent Toolkit for Tata Strive")
st.caption("Design assessments, lesson plans, and tailored learning content in minutes.")

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

with st.container():
    col1, col2, col3 = st.columns(3)
    col1.metric("Knowledge Base Docs", len(st.session_state.get('available_documents', [])))
    col2.metric("Courses Loaded", "Yes" if st.session_state['data_loaded']['courses'] else "No")
    col3.metric("Guidelines Loaded", "Yes" if st.session_state['data_loaded']['guidelines'] else "No")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Assessment Creator",
    "🗓️ Lesson Planner",
    "📘 Content Generator",
    "🎯 Personalized Learning"
])

# --- TAB 1: ASSESSMENT CREATOR ---
with tab1:
    st.header("Create a New Assessment")
    
    if not st.session_state['data_loaded']['guidelines']:
        st.warning("⚠️ Upload assessment guidelines in sidebar for enhanced question generation")
    
    selected_ass_docs = render_document_selector(
        "assessment",
        "*Choose which documents to use for generating the assessment (required)*"
    )
    
    with st.form("assessment_form"):
        assessment_query = st.text_area("Topic for the assessment:", "Create a quiz about greeting guests at a hotel.", key="ass_query")
        
        col1, col2 = st.columns(2)
        with col1:
            default_index = LANGUAGE_OPTIONS.index(suggested_lang) if suggested_lang in LANGUAGE_OPTIONS else 0
            assessment_lang = st.selectbox("Language:", LANGUAGE_OPTIONS, index=default_index, key="ass_lang")
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
    
    selected_lp_docs = render_document_selector(
        "lesson_plan",
        "*Choose which documents to use for generating the lesson plan (required)*"
    )
    
    with st.form("lesson_planner_form"):
        lp_query = st.text_area("Topic for the lesson plan:", "A detailed lesson plan for Front Desk Associate training", key="lp_query")
        
        col1, col2 = st.columns(2)
        with col1:
            lp_course = st.text_input("Course Name (Optional):", "Front Desk Associate", key="lp_course")
            default_state_index = STATE_OPTIONS.index(detected_loc.get('state')) if detected_loc.get('state') in STATE_OPTIONS else 0
            lp_state = st.selectbox("State/Location:", STATE_OPTIONS, index=default_state_index, key="lp_state")
        
        with col2:
            lp_start_date = st.date_input("Start Date:", value=datetime.now(), key="lp_start_date")
            default_lang_index = LANGUAGE_OPTIONS.index(suggested_lang) if suggested_lang in LANGUAGE_OPTIONS else 0
            lp_lang = st.selectbox("Language:", LANGUAGE_OPTIONS, index=default_lang_index, key="lp_lang")
        
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

# --- TAB 3: CONTENT GENERATOR ---
with tab3:
    st.header("🏗️ Build New Learning Content")
    st.markdown("Create facilitator-ready guides, notes, and learner handouts grounded in Tata Strive knowledge.")
    
    selected_content_docs = render_document_selector(
        "content",
        "*Ground the content in the most relevant source documents for factual accuracy (required)*"
    )
    
    with st.form("content_generator_form"):
        content_topic = st.text_area(
            "Primary topic or brief:",
            "Create a learner handout on effective body language for front desk associates.",
            key="content_topic"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            content_type = st.selectbox("Content Type:", CONTENT_TYPE_OPTIONS, key="content_type")
            tone = st.selectbox("Tone:", TONE_OPTIONS, index=0, key="content_tone")
            include_practice = st.checkbox("Add a practical activity or checklist", value=True, key="content_include_practice")
        with col2:
            audience = st.text_input("Target Audience:", "Front Desk Associate trainees", key="content_audience")
            length_choice = st.selectbox("Depth:", LENGTH_OPTIONS, index=1, key="content_length")
            default_lang_index = LANGUAGE_OPTIONS.index(suggested_lang) if suggested_lang in LANGUAGE_OPTIONS else 0
            content_lang = st.selectbox("Language:", LANGUAGE_OPTIONS, index=default_lang_index, key="content_lang")
        
        content_format = st.radio("Output Format:", ["json", "docx", "pdf"], key="content_format", horizontal=True)
        
        if st.form_submit_button("Generate Content", use_container_width=True):
            if not selected_content_docs:
                st.error("❌ Please select at least one source document before generating")
            elif not content_topic.strip():
                st.error("❌ Topic cannot be empty")
            else:
                st.session_state['download_info'] = None
                with st.spinner("Assembling your content package..."):
                    payload = {
                        "query": content_topic.strip(),
                        "content_type": content_type,
                        "audience": audience.strip() or "Front Desk Associate trainees",
                        "tone": tone,
                        "length": length_choice,
                        "include_practice": include_practice,
                        "language": content_lang,
                        "output_format": content_format,
                        "selected_documents": selected_content_docs
                    }
                    result = call_api("/create/content", payload)
                    
                    if result:
                        if content_format == 'json':
                            st.success("✅ Content generated successfully!")
                            st.write("### English Version"); st.markdown(result['english_answer'])
                            if content_lang != "English":
                                st.write(f"### {content_lang} Version"); st.markdown(result['translated_answer'])
                            st.write("#### Sources Used:"); st.write(result['sources'])
                            metadata = result.get('metadata', {})
                            if metadata:
                                st.write("#### Generation Settings:")
                                st.json(metadata)
                        else:
                            st.success("✅ Document generated successfully!")
                            file_extension = 'docx' if content_format == 'docx' else 'pdf'
                            mime_type = (
                                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                if file_extension == 'docx' else "application/pdf"
                            )
                            st.session_state['download_info'] = {
                                "data": result,
                                "file_name": f"content.{file_extension}",
                                "mime": mime_type
                            }
    
    if st.session_state.get('download_info') and 'content' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(
            label=f"📥 Download {info['file_name']}",
            data=info['data'],
            file_name=info['file_name'],
            mime=info['mime'],
            use_container_width=True
        )

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
