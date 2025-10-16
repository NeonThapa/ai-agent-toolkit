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

# --- SIDEBAR FOR DATA UPLOADS ---
with st.sidebar:
    st.header("⚙️ System Configuration")
    
    st.subheader("📊 Upload Reference Data")
    st.markdown("*Upload these files once to enable enhanced features*")
    
    # Course Duration Upload
    with st.expander("📚 Course Duration Data"):
        course_file = st.file_uploader("Upload Course CSV", type=['csv', 'xlsx'], key="course_upload")
        if course_file and st.button("Load Courses"):
            with st.spinner("Loading course data..."):
                result = upload_file_to_api("/upload/course_data", course_file)
                if result and result.get('success'):
                    st.success(f"✅ Loaded {result.get('courses_loaded')} courses")
                    st.session_state['data_loaded']['courses'] = True
                else:
                    st.error("❌ Failed to load courses")
    
    # Holiday Data Upload
    with st.expander("🗓️ Holiday Calendar"):
        holiday_file = st.file_uploader("Upload Holidays CSV", type=['csv', 'xlsx'], key="holiday_upload")
        if holiday_file and st.button("Load Holidays"):
            with st.spinner("Loading holiday data..."):
                result = upload_file_to_api("/upload/holidays", holiday_file)
                if result and result.get('success'):
                    st.success(f"✅ Loaded holidays for {result.get('states_loaded')} states")
                    st.session_state['data_loaded']['holidays'] = True
                else:
                    st.error("❌ Failed to load holidays")
    
    # Assessment Guidelines Upload
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
    
    # Data Status
    st.subheader("📊 Data Status")
    st.write("Courses:", "✅" if st.session_state['data_loaded']['courses'] else "⚪")
    st.write("Holidays:", "✅" if st.session_state['data_loaded']['holidays'] else "⚪")
    st.write("Guidelines:", "✅" if st.session_state['data_loaded']['guidelines'] else "⚪")

# --- MAIN CONTENT ---
st.title("🤖 AI Agent Toolkit for Tata Strive")

# Location Detection
if not st.session_state['detected_location']:
    with st.spinner("Detecting location..."):
        location_data = detect_location()
        if location_data:
            st.session_state['detected_location'] = location_data

location_info = st.session_state.get('detected_location', {})
detected_loc = location_info.get('location', {})
suggested_lang = location_info.get('suggested_language', 'English')

# Location selector
col1, col2 = st.columns([3, 1])
with col1:
    if detected_loc.get('detected'):
        st.info(f"📍 Detected Location: **{detected_loc.get('city', 'Unknown')}, {detected_loc.get('state', 'Unknown')}** | Suggested Language: **{suggested_lang}**")
    else:
        st.info("📍 Location: **India** (Enable location for better experience)")

tab1, tab2, tab3, tab4 = st.tabs([
    "📝 Assessment Creator",
    "🗓️ Lesson Planner",
    "📚 Content Generator",
    "🎯 Personalized Learning"
])

# --- TAB 1: ASSESSMENT CREATOR ---
with tab1:
    st.header("Create a New Assessment")
    
    if not st.session_state['data_loaded']['guidelines']:
        st.warning("⚠️ Upload assessment guidelines in sidebar for enhanced question generation")
    
    with st.form("assessment_form"):
        assessment_query = st.text_area(
            "Topic for the assessment:", 
            "Create a quiz about greeting guests at a hotel.",
            key="ass_query",
            help="Describe what topics the assessment should cover"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            assessment_lang = st.selectbox(
                "Language:", 
                ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"],
                index=0 if suggested_lang == "English" else ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"].index(suggested_lang) if suggested_lang in ["Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"] else 0,
                key="ass_lang"
            )
        with col2:
            assessment_format = st.radio(
                "Output Format:", 
                ["json", "docx", "pdf"],
                key="ass_format",
                horizontal=True
            )
        
        submitted = st.form_submit_button("Generate Assessment", use_container_width=True)
        if submitted:
            st.session_state['download_info'] = None
            with st.spinner("Generating your assessment..."):
                payload = {
                    "query": assessment_query,
                    "language": assessment_lang,
                    "output_format": assessment_format
                }
                result = call_api("/create/assessment", payload)
                
                if result:
                    if assessment_format == 'json':
                        st.success("✅ Assessment generated successfully!")
                        st.write("### English Version")
                        st.markdown(result['english_answer'])
                        if assessment_lang != "English":
                            st.write("---")
                            st.write(f"### {assessment_lang} Version")
                            st.markdown(result['translated_answer'])
                        st.write("---")
                        st.write("#### Sources:")
                        st.write(result['sources'])
                    else:
                        st.success("✅ Document generated successfully!")
                        mime_types = {
                            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "pdf": "application/pdf"
                        }
                        st.session_state['download_info'] = {
                            "data": result,
                            "file_name": f"assessment.{assessment_format}",
                            "mime": mime_types[assessment_format]
                        }

    if st.session_state.get('download_info') and 'assessment' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(
            label=f"📥 Download {info['file_name']}",
            data=info['data'],
            file_name=info['file_name'],
            mime=info['mime'],
            use_container_width=True
        )

# --- TAB 2: LESSON PLANNER ---
with tab2:
    st.header("Create a New Lesson Plan")
    
    if not st.session_state['data_loaded']['courses']:
        st.warning("⚠️ Upload course duration data in sidebar for enhanced lesson planning")
    if not st.session_state['data_loaded']['holidays']:
        st.warning("⚠️ Upload holiday calendar in sidebar to exclude holidays from lesson plans")
    
    with st.form("lesson_planner_form"):
        lp_query = st.text_area(
            "Topic for the lesson plan:",
            "A detailed lesson plan for Front Desk Associate training",
            key="lp_query",
            help="Describe the subject and scope of the lesson plan"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            lp_course = st.text_input(
                "Course Name (Optional):",
                "Front Desk Associate",
                key="lp_course",
                help="Must match exact course name from uploaded course data"
            )
            lp_state = st.selectbox(
                "State/Location:",
                ["Corporate", "West Bengal", "Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka",
                 "Kerala", "Andhra Pradesh", "Telangana", "Odisha", "Punjab", "Haryana",
                 "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Delhi", "Assam"],
                index=0 if not detected_loc.get('state') else (["Corporate", "West Bengal", "Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana", "Odisha", "Punjab", "Haryana", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Delhi", "Assam"].index(detected_loc.get('state')) if detected_loc.get('state') in ["West Bengal", "Maharashtra", "Gujarat", "Tamil Nadu", "Karnataka", "Kerala", "Andhra Pradesh", "Telangana", "Odisha", "Punjab", "Haryana", "Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Delhi", "Assam"] else 0),
                key="lp_state"
            )
        
        with col2:
            lp_start_date = st.date_input(
                "Start Date:",
                value=datetime.now(),
                key="lp_start_date",
                help="Plan will exclude weekends and holidays after this date"
            )
            lp_lang = st.selectbox(
                "Language:",
                ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"],
                index=0 if suggested_lang == "English" else ["English", "Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"].index(suggested_lang) if suggested_lang in ["Bengali", "Hindi", "Marathi", "Tamil", "Telugu", "Gujarati", "Kannada"] else 0,
                key="lp_lang"
            )
        
        lp_format = st.radio(
            "Output Format:",
            ["json", "docx", "pdf"],
            key="lp_format",
            horizontal=True
        )
        
        submitted = st.form_submit_button("Generate Lesson Plan", use_container_width=True)
        if submitted:
            st.session_state['download_info'] = None
            with st.spinner("Generating your lesson plan (considering holidays and course duration)..."):
                payload = {
                    "query": lp_query,
                    "course_name": lp_course,
                    "state": lp_state,
                    "start_date": lp_start_date.strftime('%Y-%m-%d'),
                    "language": lp_lang,
                    "output_format": lp_format
                }
                result = call_api("/create/lesson_plan", payload)
                
                if result:
                    if lp_format == 'json':
                        st.success("✅ Lesson plan generated successfully!")
                        st.write("### English Version")
                        st.markdown(result['english_answer'])
                        if lp_lang != "English":
                            st.write("---")
                            st.write(f"### {lp_lang} Version")
                            st.markdown(result['translated_answer'])
                        st.write("---")
                        st.write("#### Sources:")
                        st.write(result['sources'])
                        if 'holidays_considered' in result:
                            with st.expander("📅 Holidays Considered"):
                                st.text(result['holidays_considered'])
                    else:
                        st.success("✅ Document generated successfully!")
                        mime_types = {
                            "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            "pdf": "application/pdf"
                        }
                        st.session_state['download_info'] = {
                            "data": result,
                            "file_name": f"lesson_plan.{lp_format}",
                            "mime": mime_types[lp_format]
                        }

    if st.session_state.get('download_info') and 'lesson_plan' in st.session_state['download_info']['file_name']:
        info = st.session_state['download_info']
        st.download_button(
            label=f"📥 Download {info['file_name']}",
            data=info['data'],
            file_name=info['file_name'],
            mime=info['mime'],
            use_container_width=True
        )

# --- TAB 3: CONTENT GENERATOR ---
with tab3:
    st.header("Generate Supplementary Content")
    st.info("Coming soon: Generate study materials, practice exercises, and more!")

# --- TAB 4: PERSONALIZED LEARNING ---
with tab4:
    st.header("🎯 Automated Personalized Learning System")
    st.markdown("""
    Upload student assessment data and the system will automatically:
    - ✅ Analyze performance
    - ✅ Generate personalized study guides
    - ✅ Email PDFs to students who need support
    """)
    
    st.divider()
    
    st.subheader("📤 Upload Assessment Data")
    st.info("💡 Upload your CSV/Excel file containing student assessment results. The system will process it and email personalized content to students scoring below 70%.")
    
    uploaded_file = st.file_uploader(
        "Upload Assessment CSV/Excel",
        type=['csv', 'xlsx', 'xls'],
        key="assessment_upload",
        help="File should contain columns: Login ID, Question Text, Answer Status, Obtained Marks"
    )
    
    if uploaded_file:
        with st.expander("📋 Preview Uploaded Data"):
            try:
                if uploaded_file.name.endswith('.csv'):
                    preview_df = pd.read_csv(uploaded_file)
                else:
                    preview_df = pd.read_excel(uploaded_file)
                st.dataframe(preview_df.head(10), use_container_width=True)
                uploaded_file.seek(0)
            except Exception as e:
                st.error(f"Error previewing file: {e}")
        
        st.divider()
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Process & Send Emails", use_container_width=True, type="primary"):
                st.session_state['email_results'] = None
                
                with st.spinner("⏳ Processing assessment data and sending emails... This may take 2-3 minutes..."):
                    progress_text = st.empty()
                    progress_text.write("📊 Analyzing student performance...")
                    
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
        
        with col1:
            st.metric(
                "Total Students",
                results.get('total_students', 0),
                help="Total number of students in the assessment"
            )
        
        with col2:
            st.metric(
                "Average Score",
                f"{results.get('average_score', 0):.1f}%",
                help="Average score across all students"
            )
        
        with col3:
            st.metric(
                "Emails Sent",
                results.get('emails_sent', 0),
                help="Number of personalized emails sent to students"
            )
        
        st.divider()
        
        st.subheader("📧 Email Delivery Status")
        
        email_results = results.get('email_results', [])
        if email_results:
            email_df = pd.DataFrame(email_results)
            
            def highlight_status(val):
                if '✅' in str(val):
                    return 'background-color: #d4edda; color: #155724'
                elif '❌' in str(val):
                    return 'background-color: #f8d7da; color: #721c24'
                return ''
            
            styled_df = email_df.style.applymap(highlight_status, subset=['status'])
            st.dataframe(styled_df, use_container_width=True, hide_index=True)
            
            csv = email_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Email Report (CSV)",
                data=csv,
                file_name="email_delivery_report.csv",
                mime="text/csv"
            )
        else:
            st.info("ℹ️ No emails needed to be sent (all students scored above 70%)")
        
        st.divider()
        
        weak_questions = results.get('weak_questions', [])
        if weak_questions:
            st.subheader("📉 Most Challenging Questions")
            st.markdown("*Questions that less than 60% of students answered correctly*")
            
            for i, q in enumerate(weak_questions, 1):
                with st.expander(f"Question {i} - Success Rate: {q['success_rate']:.1f}%"):
                    st.write(q['question'])
        
        st.divider()
        
        st.success(f"""
        ✅ **Processing Complete!**
        
        - {results.get('emails_sent', 0)} students received personalized study guides
        - Each email contains a PDF with targeted learning materials
        - Students can review the content and improve their understanding
        
        📬 Students should check their email inbox for their personalized study guides.
        """)
    
    st.divider()
    with st.expander("ℹ️ How It Works"):
        st.markdown("""
        ### Automated Personalized Learning System
        
        **Step 1: Upload Assessment Data**
        - Upload CSV/Excel file with student assessment results
        - Required columns: Login ID (email), Question Text, Answer Status, Obtained Marks
        
        **Step 2: Automatic Processing**
        - System analyzes each student's performance
        - Identifies students scoring below 70%
        - Extracts topics they struggled with
        
        **Step 3: Content Generation**
        - For each struggling student:
          - Searches knowledge base for relevant content
          - Generates personalized study guide using AI
          - Creates professional PDF with their name
        
        **Step 4: Email Delivery**
        - Automatically emails PDF to each student
        - Email includes their score and focus areas
        - Delivered within 2-3 minutes of upload
        """)