 
 
from celery import shared_task
from django.core.files.storage import default_storage
import fitz  # PyMuPDF
import openai
from django.conf import settings
import json
import logging
import tempfile
import os
import re
from .models import NotesAppendixes
import boto3
from django.conf import settings
from urllib.parse import urlparse, unquote_plus
from openai import OpenAI
from notes.models import Note

logger = logging.getLogger(__name__)

# Initialize DeepSeek client
def get_deepseek_client():
    return OpenAI(
        api_key=settings.DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com",  # DeepSeek endpoint
    )
    
    
@shared_task(bind=True)
def process_existing_pdf_task(self, file_path, note_id=0):
    
    """
    Process PDF with single DeepSeek API call for both summary and MCQs
    """
    
    note = Note.objects.get(id=note_id)
    if note is None:
        raise Exception(f"Note not found for ID: {note_id}")
    try:
        # Configure DeepSeek
        openai.api_base = "https://api.deepseek.com"
        openai.api_key = settings.DEEPSEEK_API_KEY
        client = get_deepseek_client()
        logger.info(f"Reading PDF from B2: {file_path}")
   
        temp_path = getting_file(file_path) # this is the pdf file
        
        try:
                # 3. Extract text from PDF
                pdf_text = extract_text_from_pdf(temp_path)
                
                if not pdf_text.strip():
                    raise Exception("No text could be extracted from PDF (2222222) ")
                
                logger.info(f"Extracted {len(pdf_text)} characters from PDF")
                
                # 4. SINGLE API CALL for both summary and MCQs
                ai_results = generate_summary_and_mcqs(pdf_text , client)
                logger.info("Summary and MCQs generated successfully")
               
                processed_pdf = NotesAppendixes.objects.get_or_create(note_id=note)
                processed_pdf.summary = ai_results['summary']
                processed_pdf.MCQ = ai_results['mcqs']
                processed_pdf.save()
                
                return {
                    'success': True,
                    # 'note_id': note_id.id,
                    'file_path': file_path,
                    'summary_length': len(ai_results['summary']),
                    'MCQ_count': len(ai_results['mcqs'].get('mcqs', []))
                }
                
        except Exception as exc:
         logger.error(f"PDF processing failed for {file_path}: {str(exc)}")
        
         raise Exception(f"PDF processing failed for  {file_path}: {str(exc)}")
    except Exception as exc:
        logger.error(f"PDF processing failed for {file_path}: {str(exc)}")
        raise Exception(f"PDF processing failed for {file_path}: {str(exc)}")
def extract_text_from_pdf(file_path):
    """Extract text from PDF file path"""
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        raise Exception(f"PDF text extraction failed: {str(e)}")

def generate_summary_and_mcqs(text, client : OpenAI):
    """
    Single API call to generate both summary and MCQs
    This reduces costs by 50% and improves speed
    """
    try:
        # Truncate very long texts to fit context window
        if len(text) > 10000:
            text = text[:10000] 
            
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {
                    "role": "system", 
                    "content": """You are teacher. Generate a comprehensive summary in markdown format and up to 30 MCQ from the provided file , your response should be in arabic if the file's language is arabic otherwise the language is english , and always skip the introduction and the conclusion and the author bio. 
                    summary instructions :
                     -Role : You are an expert educational content designer, skilled at transforming dense teacher notes into clear, engaging, and effective student study guides.
                     -Format & Structure: For each major topic or chapter in my notebook, please structure the help book content using the following template:
                     
                     1-Title & Learning Goal: A clear title and one sentence on what the student will learn.

                    2-Key Terms: A bulleted list of the 3-5 most important vocabulary words with simple, clear definitions.

                    3-The Core Idea: A concise paragraph explaining the main concept in simple, direct language.

                    4-Why It Matters: A brief note on how this concept connects to the real world or the broader subject.

                    5-Study Tip: One practical piece of advice on how to remember or understand this topic (e.g., "A good way to remember this sequence is the acronym PEMDAS.").

                    6-Test Yourself: 2-3 key questions that a test might ask about this topic with the correct answer and the explanation            
                    Return ONLY valid JSON with this exact structure:
                    {
                        "summary": "Comprehensive summary of the document in markdown format...",
                        "mcqs": [
                            {
                                "q": "Question text here",
                                "options": ["A", "B", "C", "D"],
                                "ans": 0,
                                "exp": "Brief explanation of correct answer"
                            }
                        ]
                    }"""
                },
                {
                    "role": "user", 
                    "content": f"analyze this document and generate both a comprehensive summary in markdown format and up to 30 MCQ:\n\n{text}"
                }
            ],
            max_tokens=20000,
            temperature=0.5
        
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse the JSON response
        try:
            ai_data = _parse_ai_json(result_text)

            return {
                'summary': ai_data['summary'],
                'mcqs': {'mcqs': ai_data['mcqs']}
            }

        except (json.JSONDecodeError, ValueError) as e:
            logger.error("Failed to parse AI response as JSON. Raw response: %s", result_text)
            raise Exception(f"AI returned invalid JSON: {str(e)}")
        
    except Exception as e:
        raise Exception(f"AI generation failed: {str(e)}")
    
    
    
    

def get_b2_client():
    """Create a direct boto3 client for Backblaze B2"""
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION_NAME
    )

def download_file_from_b2(file_path):
    """Download file from Backblaze B2 using direct boto3 client"""
    client = get_b2_client()
    
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Download file from B2
            client.download_fileobj(
                settings.AWS_BUCKET_NAME,
                file_path,
                temp_file
            )
            temp_path = temp_file.name
        
        return temp_path
        
    except Exception as e:
        raise Exception(f"Failed to download file from B2: {str(e)}")

def file_exists_in_b2(file_path):
    """Check if file exists in Backblaze B2"""
    client = get_b2_client()
    
    try:
        client.head_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=file_path
        )
        return True
    except client.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        else:
            raise Exception(f"Failed to check if file exists in B2: {str(e)}")


def getting_file(file_path):
    """Retrieve file from Backblaze B2 using the S3 SDK and return a local temp path."""
    client = get_b2_client()
    object_key = _normalize_object_key(file_path)
    possible_keys = [object_key]

    if "+" in object_key:
        possible_keys.append(object_key.replace("+", " "))

    if object_key != file_path:
        possible_keys.append(file_path.lstrip("/"))

    seen = set()
    candidates = []
    for key in possible_keys:
        if key and key not in seen:
            seen.add(key)
            candidates.append(key)

    last_error = None
    suffix = os.path.splitext(object_key)[1] or ".pdf"

    for key in candidates:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                client.download_fileobj(
                    settings.AWS_BUCKET_NAME,
                    key,
                    temp_file,
                )
                return temp_file.name
        except client.exceptions.NoSuchKey as exc:
            last_error = exc
            continue
        except Exception as exc:
            raise Exception(f"Failed to retrieve file from B2: {str(exc)}") from exc

    raise FileNotFoundError(
        f"File not found in B2 after trying candidates {candidates}: {file_path}"
    )


def _normalize_object_key(file_path):
    parsed = urlparse(str(file_path))
    key = parsed.path if parsed.scheme and parsed.netloc else str(file_path)
    key = key.lstrip("/")
    return unquote_plus(key)


def _parse_ai_json(raw_text):
    """
    Attempt to extract and parse JSON from the AI response, handling common wrappers like code fences.
    """
    if not raw_text:
        raise ValueError("Empty AI response.")

    text = raw_text.strip()

    if text.startswith("```"):
        text = text.lstrip("`")
        if text.lower().startswith("json"):
            text = text[4:]
        fence_end = text.find("```")
        if fence_end != -1:
            text = text[:fence_end]

    text = text.strip()
    if not text.startswith("{"):
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            text = match.group(0)

    data = json.loads(text)

    summary = data.get("summary")
    mcqs = data.get("mcqs")

    if not isinstance(summary, str) or not isinstance(mcqs, list):
        raise ValueError("Missing or invalid fields in AI response.")

    return {
        "summary": summary,
        "mcqs": mcqs,
    }