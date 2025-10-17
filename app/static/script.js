// app/static/script.js
const getBtn = document.getElementById("getBtn");
const userIdInput = document.getElementById("userId");
const status = document.getElementById("status");
const results = document.getElementById("results");

// When frontend is served from FastAPI root, BASE_URL can be empty.
// If you host frontend separately, set BASE_URL = "http://127.0.0.1:8000"
const BASE_URL = "";

function setStatus(text, isError = false){
  status.textContent = text;
  status.style.color = isError ? "crimson" : "";
}

function renderRecommendations(data){
  results.innerHTML = "";
  if(!data || !data.recommendations || data.recommendations.length === 0){
    results.innerHTML = `<p style="text-align:center;color:#666">No recommendations found.</p>`;
    return;
  }
  data.recommendations.forEach(rec => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h3>${escapeHtml(rec.product)}</h3>
      <div class="meta">${escapeHtml(rec.category)}</div>
      <div class="price">₹ ${rec.price ?? "—"}</div>
      <div class="explain">${escapeHtml(rec.explanation)}</div>
    `;
    results.appendChild(card);
  });
}

function escapeHtml(s){
  if(!s && s !== 0) return "";
  return String(s)
    .replaceAll("&","&amp;")
    .replaceAll("<","&lt;")
    .replaceAll(">","&gt;")
    .replaceAll('"',"&quot;")
    .replaceAll("'","&#39;");
}

async function fetchRecommendations(){
  const id = Number(userIdInput.value) || 1;
  setStatus("Loading...");
  results.innerHTML = "";
  try{
    const resp = await fetch(`${BASE_URL}/recommendations/${id}`);
    if(!resp.ok){
      const err = await resp.json().catch(()=>({detail: resp.statusText}));
      setStatus(`Error: ${err.detail || resp.statusText}`, true);
      return;
    }
    const data = await resp.json();
    setStatus("Loaded");
    renderRecommendations(data);
  }catch(err){
    setStatus("Network or CORS error. See console.", true);
    console.error(err);
  }
}

getBtn.addEventListener("click", fetchRecommendations);

window.addEventListener("DOMContentLoaded", () => {
  fetchRecommendations();
});
