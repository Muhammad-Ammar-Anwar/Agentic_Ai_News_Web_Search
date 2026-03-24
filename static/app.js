/* ─────────────────────────────────────────────────────────────────────────────
   AgenticAI — app.js
   Full frontend logic: config loading, sidebar, chat, API interaction
───────────────────────────────────────────────────────────────────────────── */

const API_BASE = "";          // same origin (Flask serves both)

/* ── DOM refs ────────────────────────────────────────────────────────────── */
const sidebar         = document.getElementById("sidebar");
const sidebarToggle   = document.getElementById("sidebarToggle");
const topbarMenu      = document.getElementById("topbarMenu");
const topbarTitle     = document.getElementById("topbarTitle");

const modelSelect     = document.getElementById("modelSelect");
const usecaseSelect   = document.getElementById("usecaseSelect");
const timeframeSelect = document.getElementById("timeframeSelect");
const timeframeGroup  = document.getElementById("timeframeGroup");
const fetchNewsBtn    = document.getElementById("fetchNewsBtn");

const welcomeScreen   = document.getElementById("welcomeScreen");
const messagesEl      = document.getElementById("messages");
const userInput       = document.getElementById("userInput");
const sendBtn         = document.getElementById("sendBtn");
const clearChatBtn    = document.getElementById("clearChatBtn");

const statusDot       = document.getElementById("statusDot");
const statusLabel     = document.getElementById("statusLabel");
const usecasePill     = document.getElementById("usecasePill");
const modelBadge      = document.getElementById("modelBadge");
const toast           = document.getElementById("toast");

/* ── State ───────────────────────────────────────────────────────────────── */
let isLoading = false;

/* ── Init ────────────────────────────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", async () => {
  await loadConfig();
  setupEventListeners();
  updateUI();
});

/* ── Load config from backend ────────────────────────────────────────────── */
async function loadConfig() {
  try {
    const res  = await fetch(`${API_BASE}/api/config`);
    const data = await res.json();

    populateSelect(modelSelect,    data.groq_model_options);
    populateSelect(usecaseSelect,  data.usecase_options);

    document.title = data.page_title || "LangGraph AgenticAI";
  } catch (err) {
    showToast("Could not reach the backend server.", "error");
  }
}

function populateSelect(el, options = []) {
  el.innerHTML = "";
  options.forEach(opt => {
    const o    = document.createElement("option");
    o.value    = opt;
    o.textContent = opt;
    el.appendChild(o);
  });
}

/* ── Event listeners ─────────────────────────────────────────────────────── */
function setupEventListeners() {

  /* Sidebar toggle (desktop collapse) */
  sidebarToggle.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
      sidebar.classList.remove("open");
    } else {
      sidebar.classList.toggle("collapsed");
      sidebarToggle.textContent = sidebar.classList.contains("collapsed") ? "›" : "‹";
    }
  });

  /* Topbar hamburger (mobile open) */
  topbarMenu.addEventListener("click", () => sidebar.classList.toggle("open"));

  /* Click outside sidebar on mobile */
  document.addEventListener("click", e => {
    if (window.innerWidth <= 768 &&
        sidebar.classList.contains("open") &&
        !sidebar.contains(e.target) &&
        e.target !== topbarMenu) {
      sidebar.classList.remove("open");
    }
  });

  /* Use case changes */
  usecaseSelect.addEventListener("change", updateUI);

  /* Send message */
  sendBtn.addEventListener("click", handleSend);
  userInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  });

  /* Auto-grow textarea */
  userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 200) + "px";
  });

  /* Fetch News button */
  fetchNewsBtn.addEventListener("click", handleFetchNews);

  /* Clear chat */
  clearChatBtn.addEventListener("click", clearChat);

  /* Welcome cards */
  document.querySelectorAll(".welcome-card").forEach(card => {
    card.addEventListener("click", () => {
      const msg = card.dataset.msg;
      if (msg) {
        userInput.value = msg;
        userInput.dispatchEvent(new Event("input"));
        handleSend();
      }
    });
  });

  /* Model badge live update */
  modelSelect.addEventListener("change", updateUI);
}

/* ── Update conditional UI ───────────────────────────────────────────────── */
function updateUI() {
  const usecase = usecaseSelect.value;
  const isNews = usecase === "AI News";

  timeframeGroup.classList.toggle("hidden", !isNews);
  fetchNewsBtn.classList.toggle("hidden", !isNews);

  topbarTitle.textContent = usecase;

  // Pill
  usecasePill.innerHTML = `<span class="use-case-pill">⚡ ${usecase}</span>`;

  // Model badge
  modelBadge.textContent = modelSelect.value || "";
}

/* ── Build request payload ───────────────────────────────────────────────── */
function buildPayload(message) {
  return {
    selected_groq_model: modelSelect.value,
    selected_usecase:   usecaseSelect.value,
    user_message:       message,
  };
}

/* ── Send chat message ───────────────────────────────────────────────────── */
async function handleSend() {
  const msg = userInput.value.trim();
  if (!msg || isLoading) return;

  hideWelcome();
  appendUserMessage(msg);
  userInput.value = "";
  userInput.style.height = "auto";

  const typingId = showTyping();
  setLoading(true);

  try {
    const res  = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify(buildPayload(msg)),
    });
    const data = await res.json();
    removeTyping(typingId);

    if (!res.ok) {
      appendErrorMessage(data.error || "An error occurred.");
    } else {
      renderResponse(data);
    }
  } catch (err) {
    removeTyping(typingId);
    appendErrorMessage("Network error – is the server running?");
  } finally {
    setLoading(false);
  }
}

/* ── Fetch AI News ───────────────────────────────────────────────────────── */
async function handleFetchNews() {
  if (isLoading) return;

  const freq = timeframeSelect.value;   // e.g. "Daily"

  hideWelcome();
  appendUserMessage(`📰 Fetch ${freq} AI News`);

  const typingId = showTyping();
  setLoading(true);

  try {
    const res  = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(buildPayload(freq)),
    });
    const data = await res.json();
    removeTyping(typingId);

    if (!res.ok) {
      appendErrorMessage(data.error || "Failed to fetch news.");
    } else {
      renderResponse(data);
    }
  } catch (err) {
    removeTyping(typingId);
    appendErrorMessage("Network error – is the server running?");
  } finally {
    setLoading(false);
  }
}

/* ── Render response from API ────────────────────────────────────────────── */
function renderResponse(data) {
  if (data.usecase === "AI News") {
    appendNewsBlock(data.frequency, data.markdown);
    return;
  }

  const msgs = data.messages || [];
  msgs.forEach(m => {
    if (m.role === "assistant") appendAssistantMessage(m.content);
    else if (m.role === "tool") appendToolMessage(m.content);
  });
}

/* ── DOM helpers ─────────────────────────────────────────────────────────── */
function hideWelcome() {
  welcomeScreen.classList.add("hidden");
}

function appendUserMessage(text) {
  const el = document.createElement("div");
  el.className = "message user";
  el.innerHTML = `
    <div class="avatar">U</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
}

function appendAssistantMessage(text) {
  const el = document.createElement("div");
  el.className = "message assistant";
  el.innerHTML = `
    <div class="avatar">⬡</div>
    <div class="bubble">${renderMarkdown(text)}</div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
}

function appendToolMessage(text) {
  const el = document.createElement("div");
  el.className = "message tool";
  el.innerHTML = `
    <div class="avatar">🔧</div>
    <div class="bubble">${escapeHtml(text)}</div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
}

function appendErrorMessage(text) {
  const el = document.createElement("div");
  el.className = "message assistant";
  el.innerHTML = `
    <div class="avatar">⬡</div>
    <div class="bubble" style="border-color:rgba(239,68,68,.3);color:#fca5a5;">
      ⚠️ ${escapeHtml(text)}
    </div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
}

function appendNewsBlock(frequency, markdown) {
  const el = document.createElement("div");
  el.className = "news-block";
  el.innerHTML = renderMarkdown(markdown);
  messagesEl.appendChild(el);
  scrollToBottom();
}

function showTyping() {
  const id = "typing-" + Date.now();
  const el = document.createElement("div");
  el.className = "typing-indicator";
  el.id = id;
  el.innerHTML = `
    <div class="avatar" style="background:linear-gradient(135deg,#1a1e2a,#252d3f);border:1px solid var(--border);color:var(--accent-light);font-size:.9rem;">⬡</div>
    <div class="typing-dots"><span></span><span></span><span></span></div>
  `;
  messagesEl.appendChild(el);
  scrollToBottom();
  return id;
}

function removeTyping(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function clearChat() {
  messagesEl.innerHTML = "";
  welcomeScreen.classList.remove("hidden");
}

function scrollToBottom() {
  const cw = document.getElementById("chatWindow");
  cw.scrollTop = cw.scrollHeight;
}

/* ── Loading state ───────────────────────────────────────────────────────── */
function setLoading(state) {
  isLoading = state;
  sendBtn.disabled     = state;
  fetchNewsBtn.disabled = state;

  statusDot.className   = state ? "status-dot loading" : "status-dot";
  statusLabel.textContent = state ? "Processing…" : "Ready";
}

/* ── Toast notification ──────────────────────────────────────────────────── */
let toastTimer;
function showToast(msg, type = "info") {
  clearTimeout(toastTimer);
  toast.textContent = msg;
  toast.className   = `toast ${type} show`;
  toastTimer = setTimeout(() => toast.classList.remove("show"), 3500);
}

/* ── Markdown rendering ──────────────────────────────────────────────────── */
function renderMarkdown(text) {
  if (typeof marked === "undefined") return escapeHtml(text);
  marked.setOptions({ breaks: true, gfm: true });
  return marked.parse(text);
}

/* ── Escape HTML ─────────────────────────────────────────────────────────── */
function escapeHtml(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
