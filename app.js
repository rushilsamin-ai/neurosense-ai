const API_BASE = "https://neurosense-ai-ox4b.onrender.com";

async function checkBackend() {
    const dot = document.getElementById("backend-status-dot");
    const text = document.getElementById("backend-status-text");
    try {
        const res = await fetch(`${API_BASE}/`);
        if (res.ok) {
            dot.className = "w-2.5 h-2.5 rounded-full bg-emerald-500";
            text.innerText = "FastAPI Online";
            text.className = "text-emerald-400 font-mono";
        }
    } catch {
        dot.className = "w-2.5 h-2.5 rounded-full bg-red-500";
        text.innerText = "FastAPI Offline";
        text.className = "text-red-400 font-mono";
    }
}

function switchTab(tabId) {
    document.querySelectorAll(".panel").forEach(p => p.classList.add("hidden"));
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    document.getElementById(`panel-${tabId}`).classList.remove("hidden");
    document.getElementById(`tab-btn-${tabId}`).classList.add("active");
}

async function runSummarizer() {
    const text = document.getElementById("sum-input").value;
    if (!text.trim()) return alert("Please enter text.");
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
    }
}

async function runSentiment() {
    const text = document.getElementById("sent-input").value;
    if (!text.trim()) return alert("Please enter text.");
    const res = await fetch(`${API_BASE}/api/v1/sentiment`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text })
    });
    const data = await res.json();
    if (res.ok) {
        document.getElementById("sent-verdict").innerText = data.classification;
        document.getElementById("sent-verdict").style.color = data.accent_color;
        document.getElementById("sent-confidence").innerText = `Confidence: ${data.metrics.confidence_ratio}`;
        document.getElementById("sent-polarity").innerText = data.metrics.polarity_score;
        document.getElementById("sent-result").classList.remove("hidden");
    }
}

async function runCodeReview() {
    const code = document.getElementById("code-input").value;
    if (!code.trim()) return alert("Please enter code.");
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
    }
}

window.onload = checkBackend;