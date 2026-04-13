import json
from fastapi import APIRouter, File, UploadFile, HTTPException
import pypdf

from backend.core.config import settings

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    pass

router = APIRouter(tags=["Profile"])

SKILL_TAGS = [
    "Python", "JavaScript", "TypeScript", "React", "Vue.js", "Angular",
    "Node.js", "FastAPI", "Django", "Flask", "Express",
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "Machine Learning", "Data Science", "NLP", "Computer Vision",
    "GraphQL", "REST API", "WebSockets",
    "React Native", "Flutter", "Swift", "Kotlin",
    "Go", "Rust", "Java", "PHP", "Ruby on Rails",
    "DevOps", "CI/CD", "Git", "Linux", "Terraform",
    "UI/UX", "Figma", "WordPress", "Shopify", "SEO",
    "Content Writing", "Copywriting", "Video Editing", "3D Modeling",
]

@router.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        pdf_reader = pypdf.PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        
        # Use API key from settings (loaded from .env)
        api_key = settings.GOOGLE_API_KEY
            
        if not api_key:
            raise HTTPException(status_code=500, detail="Google API Key is not configured. Set GOOGLE_API_KEY in your .env file.")
            
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
        
        prompt = f"""
        You are an expert technical recruiter matching resumes to a specific predefined list of skills.
        
        Predefined Skills List:
        {', '.join(SKILL_TAGS)}
        
        Review the following resume text and extract ONLY the skills from the predefined list that the candidate possesses.
        
        Return exactly a valid JSON array of strings containing the exact matching skills.
        Example output: ["Python", "Docker", "FastAPI"]
        Do not return markdown blocks, only the raw JSON array.
        
        Resume text:
        {text[:5000]}  # Limiting length in case of massive pdfs
        """
        
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
            
        content = content.strip()
        skills_matched = json.loads(content)
        
        valid_skills = [s for s in skills_matched if s in SKILL_TAGS]
        
        return {"skills": list(set(valid_skills))}
        
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "RESOURCE_EXHAUSTED" in error_msg or "429" in error_msg:
            raise HTTPException(status_code=429, detail="Gemini API rate limit reached. Please wait a minute and try again.")
        elif "NOT_FOUND" in error_msg:
            raise HTTPException(status_code=500, detail="Gemini model not available. Please contact the admin.")
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {error_msg}")
