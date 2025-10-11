import os
import io
import json
import re
import traceback
from dotenv import load_dotenv
from pinecone import Pinecone
from flask import Flask, request, jsonify, send_file
from google.cloud import storage
import vertexai
from vertexai.language_models import TextEmbeddingModel
import requests
from docx import Document
from fpdf import FPDF

# --- CONFIGURATION ---
load_dotenv()
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")
LOCATION = "asia-south1"
BUCKET_NAME = "rag-source-documents"
METADATA_FILE_PATH = "vector-search-inputs/metadata_lookup.json"
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "tata-strive-rag"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"
EMBEDDING_MODEL = "text-embedding-005"
RAG_MODEL = "tngtech/deepseek-r1t2-chimera:free"
TRANSLATION_MODEL = "deepseek/deepseek-chat-v3.1:free"

# --- CLIENT INITIALIZATION ---
vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client()
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
app = Flask(__name__)

print("Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index(PINECONE_INDEX_NAME)
print("✅ Pinecone index connection established.")

print(f"Loading metadata from gs://{BUCKET_NAME}/{METADATA_FILE_PATH}...")
try:
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(METADATA_FILE_PATH)
    metadata_lookup = json.loads(blob.download_as_string())
    print("✅ Metadata loaded successfully.")
except Exception as e:
    print(f"❌ FATAL: Could not load metadata file. Error: {e}")
    metadata_lookup = {}

# --- CORE LOGIC ---
def perform_rag(query: str, num_neighbors: int = 5) -> tuple[str, list]:
    """Perform RAG search using Pinecone"""
    # Generate embedding for the query
    query_embedding = embedding_model.get_embeddings([query])[0].values
    
    try:
        # Query Pinecone
        query_results = pinecone_index.query(
            vector=query_embedding,
            top_k=num_neighbors,
            include_metadata=True
        )
        matches = query_results.get("matches", [])
    except Exception as e:
        print(f"❌ ERROR querying Pinecone: {e}")
        return "ERROR: Could not query the vector database.", []
    
    # Extract context and sources
    context = ""
    sources = []
    for match in matches:
        if 'metadata' in match:
            context += match['metadata'].get('text', '') + "\n---\n"
            sources.append(match['metadata'].get('title', 'Unknown'))
            
    return context, list(set(sources))

def call_openrouter(system_prompt: str, user_query: str, model: str = RAG_MODEL) -> str:
    """Call OpenRouter API for text generation"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://your-app-url.com",
        "X-Title": "Tata Strive RAG"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "temperature": 0.2,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(
            f"{OPENROUTER_API_BASE}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        return f"Error generating response: {str(e)}"

def translate_text(text: str, target_language: str) -> str:
    """Translate text to target language using OpenRouter"""
    if target_language == "English":
        return text
        
    system_prompt = f"Translate the following text to {target_language}. Maintain the original formatting and structure. Only provide the translation, no explanations."
    return call_openrouter(system_prompt, text, TRANSLATION_MODEL)

# --- PROMPTS ---
ASSESSMENT_PROMPT = """You are an expert educational assessment creator for Tata Strive programs. 
Create assessments based on the following context and user requirements.

Context from knowledge base:
{context}

Create an assessment that:
1. Aligns with Tata Strive's educational objectives
2. Tests practical understanding
3. Includes a mix of question types
4. Provides clear marking criteria

Format the output clearly with numbered questions and marking schemes."""

LESSON_PLAN_PROMPT = """You are an expert curriculum designer for Tata Strive programs.
Create a detailed lesson plan based on the following context and requirements.

Context from knowledge base:
{context}

Create a lesson plan that includes:
1. Learning objectives
2. Pre-requisites
3. Materials needed
4. Detailed time-wise activities
5. Assessment strategies
6. Key takeaways

Make it practical and aligned with Tata Strive's teaching methodology."""

CONTENT_PROMPT = """You are an expert content creator for Tata Strive educational programs.
Create comprehensive educational content based on the following context and topic.

Context from knowledge base:
{context}

Create content that:
1. Is engaging and easy to understand
2. Includes relevant examples
3. Aligns with Tata Strive's educational standards
4. Provides practical applications
5. Is well-structured with clear sections

Make the content informative yet accessible to the target audience."""

# --- DOCUMENT GENERATION ---
def generate_docx(content: str, title: str) -> io.BytesIO:
    """Generate a DOCX document from content"""
    doc = Document()
    doc.add_heading(title, 0)
    
    # Split content into paragraphs
    paragraphs = content.split('\n')
    for para in paragraphs:
        if para.strip():
            doc.add_paragraph(para)
    
    # Save to BytesIO
    docx_buffer = io.BytesIO()
    doc.save(docx_buffer)
    docx_buffer.seek(0)
    return docx_buffer

def generate_pdf(content: str, title: str) -> io.BytesIO:
    """Generate a PDF document from content"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=11)
    # Handle content encoding
    lines = content.split('\n')
    for line in lines:
        if line.strip():
            # Clean the line for PDF compatibility
            clean_line = line.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 5, clean_line)
            pdf.ln(2)
    
    # Save to BytesIO
    pdf_buffer = io.BytesIO()
    pdf_content = pdf.output(dest='S').encode('latin-1')
    pdf_buffer.write(pdf_content)
    pdf_buffer.seek(0)
    return pdf_buffer

# --- ENDPOINTS ---
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "Tata Strive RAG API"}), 200

@app.route('/create/assessment', methods=['POST'])
def create_assessment():
    """Create an assessment based on a topic"""
    try:
        data = request.json
        print(f"DEBUG: Received data: {data}")  # Debug line
        
        # CHANGE THESE LINES:
        topic = data.get('query', '')  # Frontend sends 'query', not 'topic'
        requirements = data.get('requirements', '')
        language = data.get('language', 'English')
        format_type = data.get('output_format', 'json')  # Frontend sends 'output_format', not 'format'
        
        if not topic:
            return jsonify({"error": "Query/topic is required"}), 400
        
        # Perform RAG search
        context, sources = perform_rag(topic)
        
        # Generate assessment
        full_query = f"Topic: {topic}\nRequirements: {requirements}"
        prompt = ASSESSMENT_PROMPT.format(context=context)
        assessment = call_openrouter(prompt, full_query)
        
        # Translate if needed
        translated_assessment = translate_text(assessment, language)
        
        # Generate document if requested
        if format_type == 'docx':
            doc_buffer = generate_docx(translated_assessment, f"Assessment: {topic}")
            return send_file(doc_buffer, as_attachment=True, 
                           download_name=f"assessment_{topic.replace(' ', '_')}.docx",
                           mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        elif format_type == 'pdf':
            pdf_buffer = generate_pdf(translated_assessment, f"Assessment: {topic}")
            return send_file(pdf_buffer, as_attachment=True,
                           download_name=f"assessment_{topic.replace(' ', '_')}.pdf",
                           mimetype='application/pdf')
        
        # For JSON format, return both English and translated
        return jsonify({
            "english_answer": assessment,
            "translated_answer": translated_assessment,
            "language": language,
            "sources": sources
        }), 200
        
    except Exception as e:
        print(f"Error in create_assessment: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/create/lesson_plan', methods=['POST'])
def create_lesson_plan():
    """Create a lesson plan based on a topic"""
    try:
        data = request.json
        topic = data.get('query', '')  # Changed from 'topic'
        duration = data.get('duration', '60 minutes')
        level = data.get('level', 'Intermediate')
        language = data.get('language', 'English')
        format_type = data.get('output_format', 'json')  # Changed from 'format'
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Perform RAG search
        context, sources = perform_rag(topic)
        
        # Generate lesson plan
        full_query = f"Topic: {topic}\nDuration: {duration}\nLevel: {level}"
        prompt = LESSON_PLAN_PROMPT.format(context=context)
        lesson_plan = call_openrouter(prompt, full_query)
        
        # Translate if needed
        lesson_plan = translate_text(lesson_plan, language)
        
        # Generate document if requested
        if format_type == 'docx':
            doc_buffer = generate_docx(lesson_plan, f"Lesson Plan: {topic}")
            return send_file(doc_buffer, as_attachment=True,
                           download_name=f"lesson_plan_{topic.replace(' ', '_')}.docx",
                           mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        elif format_type == 'pdf':
            pdf_buffer = generate_pdf(lesson_plan, f"Lesson Plan: {topic}")
            return send_file(pdf_buffer, as_attachment=True,
                           download_name=f"lesson_plan_{topic.replace(' ', '_')}.pdf",
                           mimetype='application/pdf')
        
        return jsonify({
            "english_answer": lesson_plan,
            "translated_answer": translated_lesson_plan,
            "language": language,
            "sources": sources
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/create/content', methods=['POST'])
def generate_content():
    """Generate educational content based on a topic"""
    try:
        data = request.json
        topic = data.get('topic', '')
        content_type = data.get('content_type', 'article')
        language = data.get('language', 'English')
        format_type = data.get('format', 'text')
        
        if not topic:
            return jsonify({"error": "Topic is required"}), 400
        
        # Perform RAG search
        context, sources = perform_rag(topic)
        
        # Generate content
        full_query = f"Topic: {topic}\nContent Type: {content_type}"
        prompt = CONTENT_PROMPT.format(context=context)
        content = call_openrouter(prompt, full_query)
        
        # Translate if needed
        content = translate_text(content, language)
        
        # Generate document if requested
        if format_type == 'docx':
            doc_buffer = generate_docx(content, f"Content: {topic}")
            return send_file(doc_buffer, as_attachment=True,
                           download_name=f"content_{topic.replace(' ', '_')}.docx",
                           mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        elif format_type == 'pdf':
            pdf_buffer = generate_pdf(content, f"Content: {topic}")
            return send_file(pdf_buffer, as_attachment=True,
                           download_name=f"content_{topic.replace(' ', '_')}.pdf",
                           mimetype='application/pdf')
        
        return jsonify({
            "content": content,
            "sources": sources
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Direct search endpoint for testing"""
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        context, sources = perform_rag(query)
        
        return jsonify({
            "context": context,
            "sources": sources
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting Tata Strive RAG API Server...")
    app.run(host='0.0.0.0', port=8081, debug=True)