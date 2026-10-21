import ast
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from textblob import TextBlob

app = FastAPI(
    title="NeuroSense AI Engine",
    version="2.4.0",
    docs_url="/docs",
    redoc_url=None
)

# Enable CORS for external access (Vercel, local testing, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
class SummarizeRequest(BaseModel):
    text: str
    ratio: float = 0.5

class SentimentRequest(BaseModel):
    text: str

class CodeAuditRequest(BaseModel):
    code: str
    language: str = "python"


# --- API Routes ---
@app.get("/")
def health_check():
    return {
        "system": "NeuroSense AI Operational Engine",
        "status": "ONLINE",
        "engine_version": "2.4.0-Release"
    }

@app.post("/api/v1/summarize")
def summarize_text(req: SummarizeRequest):
    content = req.text.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
    
    sentences = re.split(r'(?<=[.!?])\s+', content)
    original_count = len(content.split())
    
    if len(sentences) <= 2:
        summary = content
    else:
        keep_count = max(1, int(len(sentences) * req.ratio))
        summary = " ".join(sentences[:keep_count])
        
    condensed_count = len(summary.split())
    reduction = round(((original_count - condensed_count) / max(original_count, 1)) * 100, 1)

    return {
        "original_word_count": original_count,
        "condensed_word_count": condensed_count,
        "compression_efficiency": f"{reduction}% Reduction",
        "executive_summary": summary
    }

@app.post("/api/v1/sentiment")
def analyze_sentiment(req: SentimentRequest):
    content = req.text.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Text payload cannot be empty.")
    
    blob = TextBlob(content)
    polarity = round(blob.sentiment.polarity, 2)
    subjectivity = round(blob.sentiment.subjectivity, 2)

    if polarity > 0.15:
        verdict = "POSITIVE"
        color = "#10b981"
    elif polarity < -0.15:
        verdict = "NEGATIVE"
        color = "#ef4444"
    else:
        verdict = "NEUTRAL"
        color = "#94a3b8"

    confidence = round((abs(polarity) * 0.7 + subjectivity * 0.3) * 100, 1)

    return {
        "classification": verdict,
        "accent_color": color,
        "metrics": {
            "polarity_score": polarity,
            "subjectivity_score": subjectivity,
            "confidence_ratio": f"{confidence}%"
        }
    }

@app.post("/api/v1/code-audit")
def audit_code(req: CodeAuditRequest):
    source = req.code.strip()
    if not source:
        raise HTTPException(status_code=400, detail="Source code cannot be empty.")

    vulnerabilities = []
    
    # 1. AST Structural Analysis
    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec"]:
                    vulnerabilities.append({
                        "message": f"Critical dynamic code execution via {node.func.id}()",
                        "level": "CRITICAL"
                    })
    except SyntaxError as e:
        return {
            "audit_grade": "SYNTAX_ERROR",
            "vulnerabilities": [{
                "message": f"Syntax parsing failed: {e.msg} at line {e.lineno}",
                "level": "CRITICAL"
            }]
        }

    # 2. Heuristic Pattern Detection
    dangerous_patterns = [
        (r"os\.system\(", "Unsanitized system shell invocation (os.system)", "CRITICAL"),
        (r"subprocess\.Popen\(", "Direct process spawn risk (subprocess.Popen)", "WARNING"),
        (r"(password|secret|token)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded credential detected in plain text", "WARNING"),
        (r"except\s*:\s*(pass)?", "Bare generic except clause suppressing errors", "NOTICE")
    ]

    for pattern, label, severity in dangerous_patterns:
        if re.search(pattern, source, re.IGNORECASE):
            vulnerabilities.append({"message": label, "level": severity})

    if not vulnerabilities:
        vulnerabilities.append({"message": "Clean compilation: No immediate critical risks detected.", "level": "PASSED"})
        grade = "A+"
    elif any(v["level"] == "CRITICAL" for v in vulnerabilities):
        grade = "FAIL"
    else:
        grade = "B"

    return {
        "audit_grade": grade,
        "vulnerabilities": vulnerabilities
    }