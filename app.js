const API_BASE = "https://neurosense-ai-ox4b.onrender.com";

async function checkBackend() {
    const dot = document.getElementById("backend-status-dot");
    const text = document.getElementById("backend-status-text");
    try {
        const res = await fetch(`${API_BASE}/`, { method: "GET" });
        if (res.ok) {
            if (dot) dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]";
            if (text) {
                text.innerText = "FastAPI Online";
                text.className = "text-emerald-400 font-mono text-xs";
            }
        } else {
            throw new Error();
        }
    } catch {
        if (dot) dot.className = "w-2.5 h-2.5 rounded-full bg-red-500 shadow-[0_0_8px_#ef4444]";
        if (text) {
            text.innerText = "FastAPI Offline";
            text.className = "text-red-400 font-mono text-xs";
        }
    }
}

function switchTab(tabId) {
    document.querySelectorAll(".panel").forEach(p => p.classList.add("hidden"));
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    
    const targetPanel = document.getElementById(`panel-${tabId}`);
    const targetBtn = document.getElementById(`tab-btn-${tabId}`);
    
    if (targetPanel) targetPanel.classList.remove("hidden");
    if (targetBtn) targetBtn.classList.add("active");
}

async function runSummarizer() {
    const text = document.getElementById("sum-input").value;
    if (!text.trim()) return alert("Please enter text.");
    
    try {
        const res = await fetch(`${API_BASE}/api/v1/summarize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text, ratio: 0.5 })
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById("sum-orig-words").innerText = data.original_word_count;
            document.getElementById("sum-words").innerText = data.condensed_word_count;
            document.getElementById("sum-comp").innerText = data.compression_efficiency;
            document.getElementById("sum-output-text").innerText = data.executive_summary;
            document.getElementById("sum-result").classList.remove("hidden");
        } else {
            alert(data.detail || "Error running summarizer");
        }
    } catch (err) {
        alert("Failed to connect to backend server.");
    }
}

async function runSentiment() {
    const text = document.getElementById("sent-input").value;
    if (!text.trim()) return alert("Please enter text.");
    
    try {
        const res = await fetch(`${API_BASE}/api/v1/sentiment`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: text })
        });
        const data = await res.json();
        if (res.ok) {
            const verdictElem = document.getElementById("sent-verdict");
            verdictElem.innerText = data.classification;
            verdictElem.style.color = data.accent_color;
            document.getElementById("sent-confidence").innerText = `Confidence: ${data.metrics.confidence_ratio}`;
            document.getElementById("sent-polarity").innerText = data.metrics.polarity_score;
            document.getElementById("sent-result").classList.remove("hidden");
        } else {
            alert(data.detail || "Error running sentiment analysis");
        }
    } catch (err) {
        alert("Failed to connect to backend server.");
    }
}

async function runCodeReview() {
    const code = document.getElementById("code-input").value;
    if (!code.trim()) return alert("Please enter code.");
    
    try {
        const res = await fetch(`${API_BASE}/api/v1/code-audit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ code: code, language: "python" })
        });
        const data = await res.json();
        if (res.ok) {
            const list = document.getElementById("code-issues-list");
            list.innerHTML = "";
            document.getElementById("code-rating").innerText = data.audit_grade;
            data.vulnerabilities.forEach(item => {
                list.innerHTML += `
                    <div class="p-3 bg-slate-950 border border-slate-800 rounded-xl text-xs flex items-center justify-between">
                        <span class="text-slate-300 font-mono">${item.message}</span>
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${item.level === 'CRITICAL' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 'bg-slate-800 text-slate-300'}">${item.level}</span>
                    </div>`;
            });
            document.getElementById("code-result").classList.remove("hidden");
        } else {
            alert(data.detail || "Error running code audit");
        }
    } catch (err) {
        alert("Failed to connect to backend server.");
    }
}

window.onload = checkBackend;