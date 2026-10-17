import os
import re
import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from textblob import TextBlob

app = FastAPI(
    title="NeuroSense AI Platform API",
    description="Multi-Modal Machine Learning & Natural Language Telemetry Microservice",
    version="2.4.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentimentRequest(BaseModel):
    text: str

class SummarizeRequest(BaseModel):
    text: str
    ratio: float = 0.5

class CodeAuditRequest(BaseModel):
    code: str
    language: str = "python"

@app.get("/")
def system_health():
    return {
        "system": "NeuroSense AI Operational Engine",
        "status": "ONLINE",
        "engine_version": "2.4.0-Release"
    }

@app.post("/api/v1/sentiment")
def analyze_sentiment(payload: SentimentRequest):
    start_time = time.time()
    clean_text = payload.text.strip()
    if not clean_text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    blob = TextBlob(clean_text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.15:
        verdict = "Positive Sentiment"
        color = "#10b981"
    elif polarity < -0.15:
        verdict = "Negative Sentiment"
        color = "#ef4444"
    else:
        verdict = "Neutral Sentiment"
        color = "#94a3b8"

    return {
        "classification": verdict,
        "accent_color": color,
        "metrics": {
            "polarity_score": round(polarity, 3),
            "confidence_ratio": f"{int(min(98.5, max(60.0, (1 - subjectivity) * 45 + abs(polarity) * 55)))}%"
        }
    }

@app.post("/api/v1/summarize")
def summarize_document(payload: SummarizeRequest):
    text = payload.text.strip()
    words_list = text.split()
    if len(words_list) < 10:
        raise HTTPException(status_code=400, detail="Enter at least 10 words.")

    sentences = re.split(r'(?<=[.!?]) +', text)
    if len(sentences) <= 2:
        return {
            "original_word_count": len(words_list),
            "condensed_word_count": len(words_list),
            "compression_efficiency": "0%",
            "executive_summary": text
        }

    tokens = re.findall(r'\w+', text.lower())
    stopwords = {"the", "a", "an", "in", "on", "of", "at", "by", "for", "with", "is", "was", "are", "and", "or", "to"}
    freq = {}
    for tok in tokens:
        if tok not in stopwords:
            freq[tok] = freq.get(tok, 0) + 1

    max_val = max(freq.values()) if freq else 1
    for k in freq:
        freq[k] /= max_val

    scored_sentences = {}
    for s in sentences:
        s_tokens = re.findall(r'\w+', s.lower())
        score = sum(freq.get(t, 0) for t in s_tokens)
        scored_sentences[s] = score / (len(s_tokens) + 1)

    cutoff = max(1, int(len(sentences) * payload.ratio))
    top_ranked = sorted(scored_sentences.items(), key=lambda x: x[1], reverse=True)[:cutoff]
    summary_ordered = [s for s in sentences if s in dict(top_ranked)]

    condensed = " ".join(summary_ordered)
    orig_count = len(words_list)
    summ_count = len(condensed.split())
    efficiency = round(((orig_count - summ_count) / orig_count) * 100, 1)

    return {
        "original_word_count": orig_count,
        "condensed_word_count": summ_count,
        "compression_efficiency": f"{efficiency}%",
        "executive_summary": condensed
    }

@app.post("/api/v1/code-audit")
def audit_code_security(payload: CodeAuditRequest):
    code = payload.code.strip()
    findings = []

    if re.search(r'except\s*:', code):
        findings.append({"level": "HIGH", "message": "Bare except: block catches system interrupts and masks bugs."})
    if re.search(r'\b(eval|exec)\s*\(', code):
        findings.append({"level": "CRITICAL", "message": "Dynamic code execution (eval/exec) detected. Risk of RCE."})

    grade = "Grade A (Secure)" if len(findings) == 0 else "Grade D (Vulnerable)"

    return {
        "audit_grade": grade,
        "vulnerabilities": findings if findings else [{"level": "INFO", "message": "No static security issues detected."}]
    }