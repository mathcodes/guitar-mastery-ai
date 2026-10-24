/**
 * Guitar Mastery AI — Frontend Application
 *
 * Handles chat interactions, agent selection, theme toggling,
 * message rendering with markdown, and data table display.
 */

// ============================================================
// State
// ============================================================
const state = {
    sessionId: null,
    selectedAgent: "auto",
    isLoading: false,
    messageCount: 0,
};

// ============================================================
// DOM References
// ============================================================
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

const dom = {
    sidebar: $("#sidebar"),
    sidebarToggle: $("#sidebarToggle"),
    menuBtn: $("#menuBtn"),
    chatContainer: $("#chatContainer"),
    messages: $("#messages"),
    welcomeScreen: $("#welcomeScreen"),
    messageInput: $("#messageInput"),
    sendBtn: $("#sendBtn"),
    charCount: $("#charCount"),
    currentAgentLabel: $("#currentAgentLabel"),
    sessionLabel: $("#sessionLabel"),
    themeToggle: $("#themeToggle"),
    newSessionBtn: $("#newSessionBtn"),
    skillLevel: $("#skillLevel"),
    apiKeyBtn: $("#apiKeyBtn"),
    apiKeyBtnText: $("#apiKeyBtnText"),
    apiKeyDialog: $("#apiKeyDialog"),
    apiKeyForm: $("#apiKeyForm"),
    apiKeyInput: $("#apiKeyInput"),
    apiKeyError: $("#apiKeyError"),
    apiKeyRemove: $("#apiKeyRemove"),
    apiKeyCancel: $("#apiKeyCancel"),
};

// ============================================================
// Bring-your-own API key (kept only in this browser)
// ============================================================
const KEY_STORAGE = "gm-anthropic-key";
let memoryKey = ""; // fallback when storage is unavailable (private mode)

function getApiKey() {
    try { return localStorage.getItem(KEY_STORAGE) || memoryKey; } catch { return memoryKey; }
}

function setApiKey(value) {
    memoryKey = value || "";
    try {
        if (value) localStorage.setItem(KEY_STORAGE, value);
        else localStorage.removeItem(KEY_STORAGE);
    } catch { /* storage blocked: keep in memory for this tab */ }
    renderKeyState();
}

function renderKeyState() {
    const has = Boolean(getApiKey());
    dom.apiKeyBtn.classList.toggle("has-key", has);
    dom.apiKeyBtnText.textContent = has ? "API key added" : "Add API key";
    dom.apiKeyRemove.hidden = !has;
}

function openKeyDialog() {
    dom.apiKeyError.textContent = "";
    dom.apiKeyInput.value = getApiKey();
    dom.apiKeyDialog.showModal();
    dom.apiKeyInput.focus();
}

function bindKeyDialog() {
    dom.apiKeyBtn.addEventListener("click", openKeyDialog);
    dom.apiKeyCancel.addEventListener("click", () => dom.apiKeyDialog.close());
    dom.apiKeyRemove.addEventListener("click", () => {
        setApiKey("");
        dom.apiKeyDialog.close();
        dom.apiKeyBtn.focus();
    });
    dom.apiKeyForm.addEventListener("submit", (e) => {
        const value = dom.apiKeyInput.value.trim();
        if (!value.startsWith("sk-ant-")) {
            e.preventDefault();
            dom.apiKeyError.textContent = "Anthropic API keys start with sk-ant-. Check the key and try again.";
            dom.apiKeyInput.setAttribute("aria-invalid", "true");
            dom.apiKeyInput.focus();
            return;
        }
        dom.apiKeyInput.removeAttribute("aria-invalid");
        setApiKey(value);
    });
    dom.apiKeyDialog.addEventListener("close", () => dom.apiKeyBtn.focus());
    renderKeyState();
}

// ============================================================
// Agent Metadata
// ============================================================
const AGENT_META = {
    auto:               { icon: "🤖", name: "Auto-Route",          color: "var(--accent)" },
    jazz_teacher:       { icon: "🎵", name: "Jazz Teacher",        color: "var(--green)" },
    luthier_historian:  { icon: "🪵", name: "Luthier & Historian", color: "var(--amber)" },
    sql_expert:         { icon: "🔍", name: "Data Explorer",       color: "var(--blue)" },
    dev_pm:             { icon: "⚙️", name: "Dev & PM",            color: "var(--text-tertiary)" },
};

// ============================================================
// Initialization
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    bindEvents();
    bindKeyDialog();
});

function bindEvents() {
    // Sidebar
    dom.sidebarToggle.addEventListener("click", toggleSidebar);
    dom.menuBtn.addEventListener("click", () => {
        if (window.innerWidth > 768) {
            toggleSidebar();
            return;
        }
        const open = dom.sidebar.classList.toggle("open");
        dom.menuBtn.setAttribute("aria-expanded", String(open));
        dom.menuBtn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
        if (open) dom.sidebar.querySelector("button")?.focus();
    });
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && dom.sidebar.classList.contains("open")) {
            closeMobileSidebar();
            dom.menuBtn.focus();
        }
    });
    // Suggestion chips (event delegation; no inline handlers)
    dom.messages.addEventListener("click", (e) => {
        const btn = e.target.closest(".suggestion-btn");
        if (btn) sendMessage(btn.dataset.prompt);
    });

    // Theme
    dom.themeToggle.addEventListener("click", toggleTheme);

    // Agent selection
    $$(".agent-card").forEach((card) => {
        card.addEventListener("click", () => selectAgent(card.dataset.agent));
    });

    // Quick actions
    $$(".quick-btn").forEach((btn) => {
        btn.addEventListener("click", () => sendMessage(btn.dataset.prompt));
    });

    // Welcome cards
    $$(".welcome-card").forEach((card) => {
        card.addEventListener("click", () => sendMessage(card.dataset.prompt));
    });

    // Input
    dom.messageInput.addEventListener("input", onInputChange);
    dom.messageInput.addEventListener("keydown", onInputKeydown);
    dom.sendBtn.addEventListener("click", () => sendMessage());

    // New session
    dom.newSessionBtn.addEventListener("click", newSession);

    // Close sidebar on outside click (mobile)
    document.addEventListener("click", (e) => {
        if (
            window.innerWidth <= 768 &&
            dom.sidebar.classList.contains("open") &&
            !dom.sidebar.contains(e.target) &&
            e.target !== dom.menuBtn
        ) {
            closeMobileSidebar();
        }
    });
}

function closeMobileSidebar() {
    dom.sidebar.classList.remove("open");
    dom.menuBtn.setAttribute("aria-expanded", "false");
    dom.menuBtn.setAttribute("aria-label", "Open menu");
}

// ============================================================
// Theme
// ============================================================
function initTheme() {
    const saved = localStorage.getItem("gm-theme") || "dark";
    document.documentElement.setAttribute("data-theme", saved);
}

function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme");
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("gm-theme", next);
}

// ============================================================
// Sidebar
// ============================================================
function toggleSidebar() {
    const collapsed = dom.sidebar.classList.toggle("collapsed");
    document.body.classList.toggle("sidebar-collapsed", collapsed);
    dom.sidebarToggle.setAttribute("aria-expanded", String(!collapsed));
    dom.menuBtn.setAttribute("aria-expanded", String(!collapsed));
    if (collapsed) dom.menuBtn.focus();
    else dom.sidebarToggle.focus();
}

function selectAgent(agentName) {
    state.selectedAgent = agentName;

    $$(".agent-card").forEach((card) => {
        const active = card.dataset.agent === agentName;
        card.classList.toggle("active", active);
        card.setAttribute("aria-pressed", String(active));
    });

    const meta = AGENT_META[agentName] || AGENT_META.auto;
    dom.currentAgentLabel.textContent = meta.name;

    // Close mobile sidebar
    if (window.innerWidth <= 768) {
        closeMobileSidebar();
    }
}

// ============================================================
// Session
// ============================================================
function newSession() {
    state.sessionId = null;
    state.messageCount = 0;
    dom.messages.innerHTML = "";
    dom.welcomeScreen.classList.remove("hidden");
    dom.sessionLabel.textContent = "New Session";
    dom.messageInput.focus();
}

// ============================================================
// Input Handling
// ============================================================
function onInputChange() {
    const len = dom.messageInput.value.length;
    dom.charCount.textContent = `${len} / 5000`;
    dom.sendBtn.disabled = len === 0 || state.isLoading;

    // Auto-resize textarea
    dom.messageInput.style.height = "auto";
    dom.messageInput.style.height = Math.min(dom.messageInput.scrollHeight, 200) + "px";
}

function onInputKeydown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (!dom.sendBtn.disabled) {
            sendMessage();
        }
    }
}

// ============================================================
// Send Message
// ============================================================
async function sendMessage(overrideText) {
    const text = overrideText || dom.messageInput.value.trim();
    if (!text || state.isLoading) return;

    // Hide welcome, show messages
    dom.welcomeScreen.classList.add("hidden");

    // Clear input
    if (!overrideText) {
        dom.messageInput.value = "";
        onInputChange();
    }

    // Add user message
    addMessage("user", text);

    // Show typing indicator
    const typingEl = showTyping();

    state.isLoading = true;
    dom.sendBtn.disabled = true;

    try {
        const payload = {
            message: text,
            skill_level: dom.skillLevel.value,
        };

        if (state.sessionId) {
            payload.session_id = state.sessionId;
        }

        if (state.selectedAgent !== "auto") {
            payload.preferred_agent = state.selectedAgent;
        }

        const response = await fetch("/api/v1/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Request failed");
        }

        const data = await response.json();

        // Update session
        state.sessionId = data.session_id;
        dom.sessionLabel.textContent = `Session ${data.session_id.slice(0, 8)}...`;

        // Remove typing indicator
        typingEl.remove();

        // Add agent response
        addAgentMessage(data);

    } catch (err) {
        typingEl.remove();
        addMessage("error", `Error: ${err.message}`);
    } finally {
        state.isLoading = false;
        dom.sendBtn.disabled = dom.messageInput.value.length === 0;
        dom.messageInput.focus();
    }
}

// ============================================================
// Message Rendering
// ============================================================
function addMessage(type, text) {
    state.messageCount++;

    const el = document.createElement("div");
    el.className = `message ${type}-msg`;

    const isUser = type === "user";

    el.innerHTML = `
        <div class="message-avatar" aria-hidden="true">${isUser ? "👤" : "❌"}</div>
        <div class="message-body">
            <div class="message-header">
                <span class="message-sender">${isUser ? "You" : "System"}</span>
                <span class="message-time">${formatTime()}</span>
            </div>
            <div class="message-content">${escapeHtml(text)}</div>
        </div>
    `;

    dom.messages.appendChild(el);
    scrollToBottom();
}

function addAgentMessage(data) {
    state.messageCount++;

    const agent = data.agent_used || "unknown";
    const meta = AGENT_META[agent] || AGENT_META.auto;
    const routing = data.routing_info || {};
    const metadata = data.metadata || {};

    const el = document.createElement("div");
    el.className = "message agent-msg";

    // Build metadata chips
    let metaChips = "";
    if (routing.agent) {
        metaChips += `<span class="meta-chip"><b>Agent:</b> ${meta.name}</span>`;
    }
    if (routing.confidence) {
        const conf = Math.round(routing.confidence * 100);
        metaChips += `<span class="meta-chip confidence">Confidence: ${conf}%</span>`;
    }
    if (metadata.latency_ms) {
        metaChips += `<span class="meta-chip latency">⚡ ${metadata.latency_ms}ms</span>`;
    }
    if (metadata.tokens_input || metadata.tokens_output) {
        const t = (metadata.tokens_input || 0) + (metadata.tokens_output || 0);
        metaChips += `<span class="meta-chip tokens">🔤 ${t} tokens</span>`;
    }

    // Build suggestions
    let suggestionsHtml = "";
    if (data.suggestions && data.suggestions.length > 0) {
        suggestionsHtml = `<div class="message-suggestions">
            ${data.suggestions.map((s) => `<button type="button" class="suggestion-btn" data-prompt="${escapeAttr(s)}">${escapeHtml(s)}</button>`).join("")}
        </div>`;
    }

    // Build data tables (for SQL results)
    let dataHtml = "";
    if (data.data) {
        dataHtml = renderDataTables(data.data);
    }

    el.innerHTML = `
        <div class="message-avatar" aria-hidden="true">${meta.icon}</div>
        <div class="message-body">
            <div class="message-header">
                <span class="message-sender">${meta.name}</span>
                <span class="message-badge badge-agent">${agent}</span>
                <span class="message-time">${formatTime()}</span>
            </div>
            <div class="message-content">${renderMarkdown(data.message)}</div>
            ${dataHtml}
            <div class="message-meta">${metaChips}</div>
            ${suggestionsHtml}
        </div>
    `;

    dom.messages.appendChild(el);
    scrollToBottom();
}

// ============================================================
// Data Table Rendering
// ============================================================
function renderDataTables(data) {
    let html = "";

    for (const [toolName, toolData] of Object.entries(data)) {
        if (!toolData) continue;

        // If it has a "results" array with objects, render as a table
        if (toolData.results && Array.isArray(toolData.results) && toolData.results.length > 0) {
            const results = toolData.results;

            // Only render table if results are objects
            if (typeof results[0] === "object" && results[0] !== null) {
                const keys = Object.keys(results[0]).filter(
                    (k) => !["voicings", "intervals", "exercises", "tips", "chord_compatibility"].includes(k)
                );

                if (keys.length === 0) continue;

                html += `<div class="data-table-wrapper">
                    <table class="data-table">
                        <thead><tr>${keys.map((k) => `<th>${escapeHtml(formatKey(k))}</th>`).join("")}</tr></thead>
                        <tbody>
                            ${results.map((row) => `<tr>${keys.map((k) => {
                                let val = row[k];
                                if (val === null || val === undefined) val = "—";
                                else if (typeof val === "object") val = JSON.stringify(val).slice(0, 80);
                                else val = String(val);
                                return `<td title="${escapeAttr(val)}">${escapeHtml(val.length > 60 ? val.slice(0, 60) + "…" : val)}</td>`;
                            }).join("")}</tr>`).join("")}
                        </tbody>
                    </table>
                </div>`;
            }
        }

        // Show SQL query if present
        if (toolData.sql) {
            html += `<div class="message-content"><pre><code>${escapeHtml(toolData.sql)}</code></pre></div>`;
        }
    }

    return html;
}

// ============================================================
// Typing Indicator
// ============================================================
function showTyping() {
    const el = document.createElement("div");
    el.className = "message agent-msg typing-indicator";

    const agent = state.selectedAgent !== "auto" ? state.selectedAgent : "auto";
    const meta = AGENT_META[agent];

    el.innerHTML = `
        <div class="message-avatar" aria-hidden="true">${meta.icon}</div>
        <div class="message-body">
            <span class="sr-only">${meta.name} is thinking…</span>
            <div class="typing-dots" aria-hidden="true">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;

    dom.messages.appendChild(el);
    scrollToBottom();
    return el;
}

// ============================================================
// Markdown Renderer (lightweight)
// ============================================================
function renderMarkdown(text) {
    if (!text) return "";

    let html = escapeHtml(text);

    // Code blocks (```...```)
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
        return `<pre><code>${code.trim()}</code></pre>`;
    });

    // Inline code
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

    // Bold
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");

    // Italic
    html = html.replace(/(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)/g, "<em>$1</em>");

    // Headers
    html = html.replace(/^#### (.+)$/gm, "<h4>$1</h4>");
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");

    // Horizontal rule
    html = html.replace(/^---$/gm, "<hr>");

    // Unordered lists
    html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => `<ul>${match}</ul>`);

    // Ordered lists
    html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

    // Blockquotes
    html = html.replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>");

    // Paragraphs (double newline)
    html = html.replace(/\n\n/g, "</p><p>");
    html = `<p>${html}</p>`;

    // Single newlines within paragraphs
    html = html.replace(/\n/g, "<br>");

    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, "");
    html = html.replace(/<p>(<h[234]>)/g, "$1");
    html = html.replace(/(<\/h[234]>)<\/p>/g, "$1");
    html = html.replace(/<p>(<ul>)/g, "$1");
    html = html.replace(/(<\/ul>)<\/p>/g, "$1");
    html = html.replace(/<p>(<pre>)/g, "$1");
    html = html.replace(/(<\/pre>)<\/p>/g, "$1");
    html = html.replace(/<p>(<hr>)<\/p>/g, "$1");
    html = html.replace(/<p>(<blockquote>)/g, "$1");
    html = html.replace(/(<\/blockquote>)<\/p>/g, "$1");

    return html;
}

// ============================================================
// Utilities
// ============================================================
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function escapeAttr(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function formatKey(key) {
    return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatTime() {
    return new Date().toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
    });
}

function scrollToBottom() {
    requestAnimationFrame(() => {
        dom.chatContainer.scrollTop = dom.chatContainer.scrollHeight;
    });
}
