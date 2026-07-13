/*
==========================================================
Aetheraeon AI
Frontend Logic

Handles:

- API communication
- Authentication
- Chat
- Greeting system
- UI state
- User interaction

==========================================================
*/

/*
==========================================================
AETHERAEON JAVASCRIPT INDEX

JS-001 Configuration
JS-002 Global State
JS-003 API Communication
JS-004 Authentication
JS-005 Chat System
JS-006 Message Rendering
JS-007 Greeting System
JS-008 Timers
JS-009 Animations
JS-010 Settings
JS-011 Event Handlers

==========================================================
*/

/*
==========================================================
FUNCTION INDEX

Function: applyTheme()

Purpose:
Applies the selected visual theme and optionally persists the choice.

Section:
JS-010 Settings

Function: loadTheme()

Purpose:
Loads the saved theme and greeting style from application settings.

Section:
JS-010 Settings

Function: setBackendAvailability()

Purpose:
Updates login availability and the server status message.

Section:
JS-003 API Communication

Function: checkBackendAvailability()

Purpose:
Checks backend reachability through the existing status endpoint.

Section:
JS-003 API Communication

Function: startBackendAvailabilityMonitoring()

Purpose:
Starts page-load and recovery checks for backend availability.

Section:
JS-003 API Communication

Function: switchTab()

Purpose:
Supports the existing switch tab frontend behavior.

Section:
JS-004 Authentication

Function: submitAuth()

Purpose:
Submits validated login or registration data to the existing authentication endpoints.

Section:
JS-004 Authentication

Function: checkSession()

Purpose:
Checks whether the browser already has an authenticated server session.

Section:
JS-004 Authentication

Function: logout()

Purpose:
Supports the existing logout frontend behavior.

Section:
JS-004 Authentication

Function: toggleUserMenu()

Purpose:
Toggles user menu without changing its underlying data flow.

Section:
JS-001 Configuration

Function: closeUserMenu()

Purpose:
Closes the user menu interface when requested.

Section:
JS-001 Configuration

Function: openSettings()

Purpose:
Opens and prepares the settings interface.

Section:
JS-010 Settings

Function: switchSettingsTab()

Purpose:
Supports the existing switch settings tab frontend behavior.

Section:
JS-010 Settings

Function: loadSettingsData()

Purpose:
Loads settings data for the current interface state.

Section:
JS-010 Settings

Function: populateModelSelect()

Purpose:
Supports the existing populate model select frontend behavior.

Section:
JS-010 Settings

Function: saveProfile()

Purpose:
Saves profile through its existing UI or API flow.

Section:
JS-010 Settings

Function: saveAccount()

Purpose:
Saves account through its existing UI or API flow.

Section:
JS-010 Settings

Function: deleteAccount()

Purpose:
Removes account through the existing flow.

Section:
JS-010 Settings

Function: saveModelSettings()

Purpose:
Saves model settings through its existing UI or API flow.

Section:
JS-010 Settings

Function: savePersonalitySettings()

Purpose:
Saves personality settings through its existing UI or API flow.

Section:
JS-010 Settings

Function: loadPersonalityTraits()

Purpose:
Loads personality traits for the current interface state.

Section:
JS-010 Settings

Function: renderPersonalityTraits()

Purpose:
Renders personality traits in the current interface.

Section:
JS-010 Settings

Function: openPersonalityManager()

Purpose:
Opens and prepares the personality manager interface.

Section:
JS-010 Settings

Function: addPersonalityTrait()

Purpose:
Adds personality trait to the current UI state.

Section:
JS-010 Settings

Function: removePersonalityTrait()

Purpose:
Removes personality trait through the existing flow.

Section:
JS-010 Settings

Function: saveWebSearchToggle()

Purpose:
Saves web search toggle through its existing UI or API flow.

Section:
JS-010 Settings

Function: loadWebSearchToggle()

Purpose:
Loads web search toggle for the current interface state.

Section:
JS-010 Settings

Function: makeId()

Purpose:
Creates or selects id for the current UI flow.

Section:
JS-001 Configuration

Function: loadConversations()

Purpose:
Loads the current user’s conversations from the backend.

Section:
JS-005 Chat System

Function: newConversation()

Purpose:
Supports the existing new conversation frontend behavior.

Section:
JS-005 Chat System

Function: activateConv()

Purpose:
Supports the existing activate conv frontend behavior.

Section:
JS-005 Chat System

Function: stopGreetingRotation()

Purpose:
Stops greeting rotation.

Section:
JS-007 Greeting System

Function: scheduleGreetingRotation()

Purpose:
Supports the existing schedule greeting rotation frontend behavior.

Section:
JS-007 Greeting System

Function: shuffledCopy()

Purpose:
Supports the existing shuffled copy frontend behavior.

Section:
JS-001 Configuration

Function: drawGreetingUiPool()

Purpose:
Creates or selects greeting ui pool for the current UI flow.

Section:
JS-007 Greeting System

Function: selectGreetingEffect()

Purpose:
Creates or selects greeting effect for the current UI flow.

Section:
JS-007 Greeting System

Function: updateGreetingCountdown()

Purpose:
Updates the interface for update greeting countdown.

Section:
JS-007 Greeting System

Function: startGreetingCountdown()

Purpose:
Starts greeting countdown.

Section:
JS-007 Greeting System

Function: renderTemporaryGreeting()

Purpose:
Displays a temporary greeting without persisting it as a conversation message.

Section:
JS-007 Greeting System

Function: showGreetingLoadingState()

Purpose:
Updates the interface for show greeting loading state.

Section:
JS-007 Greeting System

Function: startGreetingLoadingMessages()

Purpose:
Starts greeting loading messages.

Section:
JS-007 Greeting System

Function: ensureGreetingLoadingState()

Purpose:
Supports the existing ensure greeting loading state frontend behavior.

Section:
JS-007 Greeting System

Function: stopGreetingLoadingMessages()

Purpose:
Stops greeting loading messages.

Section:
JS-007 Greeting System

Function: clearTemporaryGreetingForInteraction()

Purpose:
Supports the existing clear temporary greeting for interaction frontend behavior.

Section:
JS-007 Greeting System

Function: refreshTemporaryGreeting()

Purpose:
Refreshes temporary greeting from its existing source.

Section:
JS-007 Greeting System

Function: prefetchTemporaryGreeting()

Purpose:
Supports the existing prefetch temporary greeting frontend behavior.

Section:
JS-007 Greeting System

Function: swapPrefetchedGreeting()

Purpose:
Supports the existing swap prefetched greeting frontend behavior.

Section:
JS-007 Greeting System

Function: showNoConversationState()

Purpose:
Updates the interface for show no conversation state.

Section:
JS-005 Chat System

Function: toggleConversation()

Purpose:
Toggles conversation without changing its underlying data flow.

Section:
JS-005 Chat System

Function: loadAndRenderMessages()

Purpose:
Loads persisted messages for the active conversation and renders them.

Section:
JS-006 Message Rendering

Function: deleteConv()

Purpose:
Removes conv through the existing flow.

Section:
JS-005 Chat System

Function: renameConv()

Purpose:
Supports the existing rename conv frontend behavior.

Section:
JS-005 Chat System

Function: togglePin()

Purpose:
Toggles pin without changing its underlying data flow.

Section:
JS-001 Configuration

Function: sortedIds()

Purpose:
Updates the interface for sorted ids.

Section:
JS-001 Configuration

Function: renderSidebar()

Purpose:
Renders sidebar in the current interface.

Section:
JS-011 Event Handlers

Function: filterConvList()

Purpose:
Updates the interface for filter conv list.

Section:
JS-005 Chat System

Function: switchSidebarTab()

Purpose:
Supports the existing switch sidebar tab frontend behavior.

Section:
JS-011 Event Handlers

Function: renderPlaybooks()

Purpose:
Renders playbooks in the current interface.

Section:
JS-005 Chat System

Function: openPlaybookModal()

Purpose:
Opens and prepares the playbook modal interface.

Section:
JS-011 Event Handlers

Function: addPlaybookStep()

Purpose:
Adds playbook step to the current UI state.

Section:
JS-005 Chat System

Function: savePlaybook()

Purpose:
Saves playbook through its existing UI or API flow.

Section:
JS-005 Chat System

Function: parseMessageContent()

Purpose:
Separates displayable message text from process metadata.

Section:
JS-006 Message Rendering

Function: addMsgDOM()

Purpose:
Builds and appends one visible message to the chat transcript.

Section:
JS-006 Message Rendering

Function: toolLabel()

Purpose:
Supports the existing tool label frontend behavior.

Section:
JS-006 Message Rendering

Function: addTyping()

Purpose:
Adds typing to the current UI state.

Section:
JS-006 Message Rendering

Function: dumpState()

Purpose:
Supports the existing dump state frontend behavior.

Section:
JS-001 Configuration

Function: sendCmd()

Purpose:
Sends a chat command and renders the response returned by the backend.

Section:
JS-005 Chat System

Function: _pickTTSVoice()

Purpose:
Supports the existing pick ttsvoice frontend behavior.

Section:
JS-011 Event Handlers

Function: speakText()

Purpose:
Supports the existing speak text frontend behavior.

Section:
JS-001 Configuration

Function: _initSpeechRecognition()

Purpose:
Supports the existing init speech recognition frontend behavior.

Section:
JS-001 Configuration

Function: toggleVoice()

Purpose:
Toggles voice without changing its underlying data flow.

Section:
JS-011 Event Handlers

Function: stopVoice()

Purpose:
Stops voice.

Section:
JS-011 Event Handlers

Function: openSearch()

Purpose:
Opens and prepares the search interface.

Section:
JS-011 Event Handlers

Function: closeSearch()

Purpose:
Closes the search interface when requested.

Section:
JS-011 Event Handlers

Function: closeSearchIfOutside()

Purpose:
Closes the search if outside interface when requested.

Section:
JS-011 Event Handlers

Function: debounceSearch()

Purpose:
Supports the existing debounce search frontend behavior.

Section:
JS-011 Event Handlers

Function: doSearch()

Purpose:
Supports the existing do search frontend behavior.

Section:
JS-011 Event Handlers

Function: highlight()

Purpose:
Transforms highlight for safe display or use.

Section:
JS-001 Configuration

Function: _renderAllDotsOffline()

Purpose:
Renders all dots offline in the current interface.

Section:
JS-001 Configuration

Function: refreshStatus()

Purpose:
Refreshes the visible status of backend-managed services.

Section:
JS-008 Timers

Function: convToText()

Purpose:
Supports the existing conv to text frontend behavior.

Section:
JS-005 Chat System

Function: openShareModal()

Purpose:
Opens and prepares the share modal interface.

Section:
JS-011 Event Handlers

Function: doShare()

Purpose:
Supports the existing do share frontend behavior.

Section:
JS-005 Chat System

Function: shareConversation()

Purpose:
Supports the existing share conversation frontend behavior.

Section:
JS-005 Chat System

Function: copyConversation()

Purpose:
Produces or transfers conversation for the user.

Section:
JS-005 Chat System

Function: exportConversation()

Purpose:
Produces or transfers conversation for the user.

Section:
JS-005 Chat System

Function: exportSingleConv()

Purpose:
Produces or transfers single conv for the user.

Section:
JS-005 Chat System

Function: exportAllConversations()

Purpose:
Produces or transfers all conversations for the user.

Section:
JS-005 Chat System

Function: startRename()

Purpose:
Starts rename.

Section:
JS-005 Chat System

Function: finishRename()

Purpose:
Supports the existing finish rename frontend behavior.

Section:
JS-005 Chat System

Function: titleKeydown()

Purpose:
Supports the existing title keydown frontend behavior.

Section:
JS-001 Configuration

Function: _isMobile()

Purpose:
Supports the existing is mobile frontend behavior.

Section:
JS-001 Configuration

Function: toggleSidebar()

Purpose:
Toggles sidebar without changing its underlying data flow.

Section:
JS-011 Event Handlers

Function: closeSidebarDrawer()

Purpose:
Closes the sidebar drawer interface when requested.

Section:
JS-011 Event Handlers

Function: autoResize()

Purpose:
Supports the existing auto resize frontend behavior.

Section:
JS-011 Event Handlers

Function: now()

Purpose:
Supports the existing now frontend behavior.

Section:
JS-001 Configuration

Function: formatTimestamp()

Purpose:
Transforms timestamp for safe display or use.

Section:
JS-001 Configuration

Function: scrollBottom()

Purpose:
Supports the existing scroll bottom frontend behavior.

Section:
JS-001 Configuration

Function: escHtml()

Purpose:
Transforms html for safe display or use.

Section:
JS-001 Configuration

Function: _initEyeButtons()

Purpose:
Supports the existing init eye buttons frontend behavior.

Section:
JS-011 Event Handlers

Function: togglePw()

Purpose:
Toggles pw without changing its underlying data flow.

Section:
JS-011 Event Handlers

Function: copyToClipboard()

Purpose:
Produces or transfers to clipboard for the user.

Section:
JS-001 Configuration

Function: fallbackCopy()

Purpose:
Supports the existing fallback copy frontend behavior.

Section:
JS-001 Configuration

Function: downloadFile()

Purpose:
Produces or transfers file for the user.

Section:
JS-001 Configuration

Function: showToast()

Purpose:
Updates the interface for show toast.

Section:
JS-001 Configuration

Function: openModal()

Purpose:
Opens and prepares the modal interface.

Section:
JS-011 Event Handlers

Function: closeModal()

Purpose:
Closes the modal interface when requested.

Section:
JS-011 Event Handlers

Function: closeModalIfOutside()

Purpose:
Closes the modal if outside interface when requested.

Section:
JS-011 Event Handlers

Function: bootApp()

Purpose:
Initializes the authenticated application shell from the supplied user record.

Section:
JS-001 Configuration

Function: openMemModal()

Purpose:
Opens and prepares the mem modal interface.

Section:
JS-011 Event Handlers

Function: closeMemModal()

Purpose:
Closes the mem modal interface when requested.

Section:
JS-011 Event Handlers

Function: memCloseIfOutside()

Purpose:
Supports the existing mem close if outside frontend behavior.

Section:
JS-005 Chat System

Function: memLoad()

Purpose:
Supports the existing mem load frontend behavior.

Section:
JS-005 Chat System

Function: _memRender()

Purpose:
Supports the existing mem render frontend behavior.

Section:
JS-005 Chat System

Function: memFilterRows()

Purpose:
Supports the existing mem filter rows frontend behavior.

Section:
JS-005 Chat System

Function: memSemanticSearch()

Purpose:
Supports the existing mem semantic search frontend behavior.

Section:
JS-011 Event Handlers

Function: memSearchKeydown()

Purpose:
Supports the existing mem search keydown frontend behavior.

Section:
JS-011 Event Handlers

Function: memSortByCol()

Purpose:
Supports the existing mem sort by col frontend behavior.

Section:
JS-005 Chat System

Function: memApplySort()

Purpose:
Supports the existing mem apply sort frontend behavior.

Section:
JS-005 Chat System

Function: _memApplySort()

Purpose:
Supports the existing mem apply sort frontend behavior.

Section:
JS-005 Chat System

Function: _memApplySortToVisible()

Purpose:
Supports the existing mem apply sort to visible frontend behavior.

Section:
JS-005 Chat System

Function: _memSortArr()

Purpose:
Supports the existing mem sort arr frontend behavior.

Section:
JS-005 Chat System

Function: _memUpdateSortArrows()

Purpose:
Supports the existing mem update sort arrows frontend behavior.

Section:
JS-005 Chat System

Function: _memToggleRow()

Purpose:
Supports the existing mem toggle row frontend behavior.

Section:
JS-005 Chat System

Function: memToggleAll()

Purpose:
Supports the existing mem toggle all frontend behavior.

Section:
JS-005 Chat System

Function: memDeleteOne()

Purpose:
Supports the existing mem delete one frontend behavior.

Section:
JS-005 Chat System

Function: memDeleteSelected()

Purpose:
Supports the existing mem delete selected frontend behavior.

Section:
JS-005 Chat System

Function: openMemEdit()

Purpose:
Opens and prepares the mem edit interface.

Section:
JS-001 Configuration

Function: openMemCreate()

Purpose:
Opens and prepares the mem create interface.

Section:
JS-001 Configuration

Function: closeMemEdit()

Purpose:
Closes the mem edit interface when requested.

Section:
JS-001 Configuration

Function: memEditCloseIfOutside()

Purpose:
Supports the existing mem edit close if outside frontend behavior.

Section:
JS-005 Chat System

Function: memSaveEdit()

Purpose:
Supports the existing mem save edit frontend behavior.

Section:
JS-005 Chat System

Function: memExportSQL()

Purpose:
Exports loaded memory records as SQL text.

Section:
JS-005 Chat System

Function: memExportJSON()

Purpose:
Exports loaded memory records as JSON.

Section:
JS-005 Chat System

Function: memImportFile()

Purpose:
Imports supported memory export data through existing memory API requests.

Section:
JS-005 Chat System

Function: _memSetStatus()

Purpose:
Supports the existing mem set status frontend behavior.

Section:
JS-008 Timers

Function: _memShowError()

Purpose:
Supports the existing mem show error frontend behavior.

Section:
JS-005 Chat System

Function: _memUpdateCounts()

Purpose:
Supports the existing mem update counts frontend behavior.

Section:
JS-005 Chat System

Function: _memDownloadFile()

Purpose:
Supports the existing mem download file frontend behavior.

Section:
JS-005 Chat System

Function: makeGroup()

Purpose:
Creates one labeled conversation group for sidebar rendering.

Section:
JS-005 Chat System

Function: addMenuItem() (occurrence 1 of 2)

Purpose:
Creates an action item for a conversation context menu.

Section:
JS-011 Event Handlers

Function: addMenuItem() (occurrence 2 of 2)

Purpose:
Creates an action item for a playbook context menu.

Section:
JS-011 Event Handlers

==========================================================
*/

// JS-001: Configuration

"use strict";

// ── Global Escape: close any open modal / search / menu ─────
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;
  document.querySelectorAll(".modal-overlay.open").forEach((m) => m.classList.remove("open"));
  if (document.getElementById("mem-edit-modal").classList.contains("open")) {
    closeMemEdit();
    return;
  }
  closeSearch();
  closeUserMenu();
  closeMemModal();
});

// JS-002: Global State

let currentUser = null;
let conversations = {}; // keyed by conversation_id (UUID string)
let activeConvId = null;
let cmdHistory = [];
let historyIdx = -1;
let draftSaved = "";
let sidebarOpen = true;
let _toastTimer = null;
let _editingPbId = null; // null = new playbook, number = editing existing
let _shareContent = "";
let _searchTimer = null;
let _statusTimer = null;
let _backendAvailabilityTimer = null;
let _backendAvailable = false;
let _greetingTimer = null;
let _greetingPrefetchTimer = null;
let _greetingLoadingTimer = null;
let _greetingCountdownTimer = null;
let _greetingRequest = 0;
let _greetingDeadline = 0;
let _nextGreeting = null;
let _activeGreetingText = "";
let _greetingPersonalityStyle = "balanced";
const _greetingUiPools = new Map();

// GREETING_COUNTDOWN_DEVELOPER_TOGGLE — set true to show the optional timer.
const SHOW_GREETING_COUNTDOWN = true;
const BACKEND_AVAILABILITY_INTERVAL_MS = 15000;
let personalityTraits = [];

// DOM shortcuts
const chat = document.getElementById("chat");
const input = document.getElementById("msg-input");
const sendBtn = document.getElementById("send-btn");

// JS-010: Settings

async function applyTheme(theme, persist = true) {
  document.documentElement.setAttribute("data-theme", theme);
  // Update active theme button highlight
  document
    .querySelectorAll(".theme-btn")
    .forEach((b) => b.classList.toggle("active", b.dataset.theme === theme));
  if (persist && currentUser) {
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ui_theme: theme }),
    }).catch(() => {});
  }
}

async function loadTheme() {
  try {
    const r = await fetch("/api/settings");
    const d = await r.json();
    if (d.ok && d.settings) {
      _greetingPersonalityStyle = d.settings.personality_style || "balanced";
    }
    applyTheme(d.ok ? d.settings.ui_theme || "dark" : "dark", false);
  } catch {
    applyTheme("dark", false);
  }
}

// JS-003: API Communication
// API calls remain colocated with their owning UI feature to preserve existing behavior.

// JS-004: Authentication

let currentTab = "login";

// ------------------------------------------------------
// Function: setBackendAvailability()
// Purpose: Updates only the login availability message and submit state.
// Called by: checkBackendAvailability()
// Updates: Backend state, login status text, and login button availability.
// ------------------------------------------------------
function setBackendAvailability(available) {
  _backendAvailable = available;

  const submitButton = document.getElementById("auth-submit-btn");
  const statusElement = document.getElementById("backend-status");

  submitButton.disabled = !available;
  submitButton.setAttribute("aria-disabled", String(!available));

  if (available) {
    submitButton.title = "";
    statusElement.textContent = "";
    statusElement.classList.remove("visible");
    return;
  }

  submitButton.title = "Aetheraeon AI server is unavailable";
  statusElement.textContent = "Aetheraeon AI server is currently offline. Please try again later.";
  statusElement.classList.add("visible");
}

// ------------------------------------------------------
// Function: checkBackendAvailability()
// Purpose: Performs a lightweight reachability check against the existing status endpoint.
// Called by: startBackendAvailabilityMonitoring() and its recovery timer.
// Updates: Login availability through setBackendAvailability().
// ------------------------------------------------------
async function checkBackendAvailability() {
  let available = false;

  try {
    const response = await fetch("/api/status", {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    available = response.ok;
  } catch {
    available = false;
  }

  setBackendAvailability(available);
  return available;
}

// ------------------------------------------------------
// Function: startBackendAvailabilityMonitoring()
// Purpose: Checks the backend on page load and periodically restores login when it returns.
// Called by: Frontend initialization.
// Updates: Backend availability timer.
// ------------------------------------------------------
function startBackendAvailabilityMonitoring() {
  checkBackendAvailability();

  if (!_backendAvailabilityTimer) {
    _backendAvailabilityTimer = setInterval(
      checkBackendAvailability,
      BACKEND_AVAILABILITY_INTERVAL_MS,
    );
  }
}

function switchTab(tab) {
  currentTab = tab;
  const isReg = tab === "register";
  document.getElementById("tab-login").classList.toggle("active", !isReg);
  document.getElementById("tab-register").classList.toggle("active", isReg);
  document.getElementById("reg-fullname-field").style.display = isReg ? "" : "none";
  document.getElementById("reg-username-field").style.display = isReg ? "" : "none";
  document.getElementById("auth-submit-btn").textContent = isReg ? "Create Account" : "Sign In";
  document.getElementById("login-switch-text").innerHTML = isReg
    ? "Have an account? <span onclick=\"switchTab('login')\">Sign in</span>"
    : "No account? <span onclick=\"switchTab('register')\">Create one</span>";
  document.getElementById("auth-err").textContent = "";
}

// ------------------------------------------------------
// Function: submitAuth()
// Purpose: Validates login form input and submits it to the existing authentication endpoints.
// Called by: Login button and authentication Enter-key handlers.
// Updates: Authentication errors or the authenticated application shell.
// ------------------------------------------------------
async function submitAuth() {
  const email = document.getElementById("auth-email").value.trim().toLowerCase();
  const password = document.getElementById("auth-password").value;
  const errEl = document.getElementById("auth-err");
  errEl.textContent = "";

  if (!_backendAvailable) {
    setBackendAvailability(false);
    return;
  }

  if (!email || !password) {
    errEl.textContent = "Email and password required.";
    return;
  }
  if (!/\S+@\S+\.\S+/.test(email)) {
    errEl.textContent = "Enter a valid email.";
    return;
  }
  if (password.length < 4) {
    errEl.textContent = "Password must be 4+ characters.";
    return;
  }

  let endpoint = "/api/login";
  let payload = { email, password };

  if (currentTab === "register") {
    const fullName = document.getElementById("auth-fullname").value.trim();
    const username = document.getElementById("auth-username").value.trim();
    if (!fullName || !username) {
      errEl.textContent = "Full name and username required.";
      return;
    }
    endpoint = "/api/register";
    payload = { full_name: fullName, username, email, password };
  }

  try {
    const resp = await fetch(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    if (!data.ok) {
      errEl.textContent = data.error || "Authentication failed.";
      return;
    }
    bootApp(data.user);
  } catch (e) {
    errEl.textContent = "Connection error: " + e.message;
  }
}

async function checkSession() {
  try {
    const r = await fetch("/api/session");
    const d = await r.json();
    if (d.ok) bootApp(d.user);
  } catch {}
}

async function logout() {
  closeUserMenu();
  await fetch("/api/logout", { method: "POST" }).catch(() => {});
  currentUser = null;
  personalityTraits = [];
  _greetingUiPools.clear();
  conversations = {};
  activeConvId = null;
  if (_statusTimer) {
    clearInterval(_statusTimer);
    _statusTimer = null;
  }
  stopGreetingRotation();
  chat.innerHTML = "";
  document.getElementById("app").style.display = "none";
  document.getElementById("login-screen").style.display = "flex";
  // Clear auth fields
  ["auth-email", "auth-password", "auth-fullname", "auth-username"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.value = "";
  });
  document.getElementById("auth-err").textContent = "";
}

// ── Enter key to submit auth ──────────────────────────────
["auth-email", "auth-password", "auth-fullname", "auth-username"].forEach((id) => {
  const el = document.getElementById(id);
  if (el)
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter") submitAuth();
    });
});

// ────────────────────────────────────────────────────────────
// USER MENU (context menu)
// ────────────────────────────────────────────────────────────

function toggleUserMenu(e) {
  e.stopPropagation();
  const menu = document.getElementById("user-menu");
  const badge = document.querySelector(".user-badge");
  const rect = badge.getBoundingClientRect();
  menu.style.left = rect.left + "px";
  menu.style.bottom = window.innerHeight - rect.top + 6 + "px";
  menu.style.top = "auto";
  menu.classList.toggle("open");
}

function closeUserMenu() {
  document.getElementById("user-menu").classList.remove("open");
}

document.addEventListener("click", (e) => {
  if (!document.getElementById("user-menu").contains(e.target)) closeUserMenu();
});

// ────────────────────────────────────────────────────────────
// SETTINGS MODAL
// ────────────────────────────────────────────────────────────

function openSettings(panel = "themes") {
  closeUserMenu();
  loadSettingsData();
  switchSettingsTab(panel);
  openModal("settings-modal");
  loadWebSearchToggle();
}

function switchSettingsTab(panel) {
  document
    .querySelectorAll(".settings-tab")
    .forEach((b) => b.classList.toggle("active", b.dataset.panel === panel));
  document
    .querySelectorAll(".settings-panel")
    .forEach((p) => p.classList.toggle("active", p.id === "panel-" + panel));
}

async function loadSettingsData() {
  if (currentUser) {
    document.getElementById("new-username-input").value = currentUser.username || "";
    document.getElementById("full-name-input").value = currentUser.full_name || "";
    document.getElementById("account-email-input").value = currentUser.email || "";
  }
  document.getElementById("profile-current-pw-input").value = "";
  document.getElementById("current-pw-input").value = "";
  document.getElementById("new-pw-input").value = "";
  try {
    const [settingsResponse, modelsResponse] = await Promise.all([
      fetch("/api/settings"),
      fetch("/api/models/installed"),
    ]);
    const settingsData = await settingsResponse.json();
    const modelsData = await modelsResponse.json();
    if (!settingsData.ok || !settingsData.settings) return;

    const s = settingsData.settings;
    const models = modelsData.ok ? modelsData.models : [];
    populateModelSelect("pref-router-model", models, s.preferred_router_model);
    populateModelSelect("pref-chat-model", models, s.preferred_chat_model);
    populateModelSelect("pref-code-model", models, s.preferred_code_model);
    document.getElementById("web-search-toggle").checked = !!s.web_search_enabled;
    document.getElementById("personality-style").value = s.personality_style || "balanced";
    document.getElementById("response-tone").value = s.response_tone || "direct";
    document.getElementById("response-detail").value = s.response_detail || "normal";
    document.getElementById("humor-level").value = s.humor_level || "low";
    document.getElementById("greeting-style").value = s.greeting_style || "friendly";
    await loadPersonalityTraits();
  } catch {}
}

function populateModelSelect(id, models, selected) {
  const select = document.getElementById(id);
  select.innerHTML = "";
  const available = [...models];
  if (!available.length) {
    select.add(new Option("No installed models found", ""));
    select.disabled = true;
    return;
  }
  select.disabled = false;
  available.forEach((model) => select.add(new Option(model, model)));
  select.value = selected && available.includes(selected) ? selected : available[0];
}

// ── Profile change ────────────────────────────────────────
async function saveProfile() {
  const errEl = document.getElementById("username-err");
  const okEl = document.getElementById("username-ok");
  const username = document.getElementById("new-username-input").value.trim();
  const fullName = document.getElementById("full-name-input").value.trim();
  const currentPassword = document.getElementById("profile-current-pw-input").value;
  errEl.textContent = "";
  okEl.textContent = "";
  if (!username || !fullName) {
    errEl.textContent = "Username and full name are required.";
    return;
  }
  if (!currentPassword) {
    errEl.textContent = "Enter your current password.";
    return;
  }
  try {
    const r = await fetch("/api/account/username", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username,
        full_name: fullName,
        current_password: currentPassword,
      }),
    });
    const d = await r.json();
    if (!d.ok) {
      errEl.textContent = d.error || "Failed.";
      return;
    }
    currentUser.username = d.username;
    currentUser.full_name = d.full_name;
    okEl.textContent = d.changed ? "✅ Profile updated!" : "No profile changes to save.";
    document.getElementById("user-display-name").textContent = d.full_name;
    document.getElementById("profile-current-pw-input").value = "";
  } catch (e) {
    errEl.textContent = "Error: " + e.message;
  }
}

// ── Account change ────────────────────────────────────────
async function saveAccount() {
  const errEl = document.getElementById("pw-err");
  const okEl = document.getElementById("pw-ok");
  const email = document.getElementById("account-email-input").value.trim().toLowerCase();
  const curPw = document.getElementById("current-pw-input").value;
  const newPw = document.getElementById("new-pw-input").value;
  errEl.textContent = "";
  okEl.textContent = "";
  if (!email || !/\S+@\S+\.\S+/.test(email)) {
    errEl.textContent = "Enter a valid email.";
    return;
  }
  if (!curPw) {
    errEl.textContent = "Enter your current password.";
    return;
  }
  if (newPw && newPw.length < 6) {
    errEl.textContent = "New password must be 6+ characters.";
    return;
  }
  try {
    const r = await fetch("/api/account/password", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, current_password: curPw, new_password: newPw }),
    });
    const d = await r.json();
    if (!d.ok) {
      errEl.textContent = d.error || "Failed.";
      return;
    }
    okEl.textContent =
      d.email_changed || d.password_changed ? "✅ Account updated!" : "No account changes to save.";
    currentUser.email = d.email;
    document.getElementById("user-display-email").textContent = d.email;
    document.getElementById("current-pw-input").value = "";
    document.getElementById("new-pw-input").value = "";
  } catch (e) {
    errEl.textContent = "Error: " + e.message;
  }
}

// ── Delete account ────────────────────────────────────────
async function deleteAccount() {
  const errEl = document.getElementById("delete-err");
  const pw = document.getElementById("delete-account-pw").value;
  errEl.textContent = "";
  if (!pw) {
    errEl.textContent = "Enter your password to confirm.";
    return;
  }
  if (!confirm("This will permanently delete your account and ALL data. Are you absolutely sure?"))
    return;
  try {
    const r = await fetch("/api/account/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: pw }),
    });
    const d = await r.json();
    if (!d.ok) {
      errEl.textContent = d.error || "Failed.";
      return;
    }
    showToast("Account deleted.", "var(--red)");
    setTimeout(logout, 1500);
  } catch (e) {
    errEl.textContent = "Error: " + e.message;
  }
}

// ── Save model settings ───────────────────────────────────
async function saveModelSettings() {
  const okEl = document.getElementById("models-ok");
  okEl.textContent = "";
  const settings = {
    preferred_router_model: document.getElementById("pref-router-model").value,
    preferred_chat_model: document.getElementById("pref-chat-model").value.trim() || null,
    preferred_code_model: document.getElementById("pref-code-model").value.trim() || null,
  };
  if (
    !settings.preferred_router_model ||
    !settings.preferred_chat_model ||
    !settings.preferred_code_model
  ) {
    okEl.textContent = "No installed models are available.";
    return;
  }
  try {
    const r = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    const d = await r.json();
    okEl.textContent = d.ok ? "✅ Models saved!" : d.error || "Failed to save models.";
  } catch (e) {
    okEl.textContent = "Error: " + e.message;
  }
}

async function savePersonalitySettings() {
  const errEl = document.getElementById("personality-err");
  const okEl = document.getElementById("personality-ok");
  errEl.textContent = "";
  okEl.textContent = "";
  const settings = {
    personality_style: document.getElementById("personality-style").value,
    response_tone: document.getElementById("response-tone").value,
    response_detail: document.getElementById("response-detail").value,
    humor_level: document.getElementById("humor-level").value,
    greeting_style: document.getElementById("greeting-style").value,
  };
  try {
    const r = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    const d = await r.json();
    if (!d.ok) {
      errEl.textContent = d.error || "Failed.";
      return;
    }
    okEl.textContent = "Personality saved.";
  } catch (e) {
    errEl.textContent = "Error: " + e.message;
  }
}

async function loadPersonalityTraits() {
  const r = await fetch("/api/personality/traits");
  const d = await r.json();
  personalityTraits = d.ok ? d.traits : [];
  renderPersonalityTraits();
}

function renderPersonalityTraits() {
  const preview = document.getElementById("personality-traits-preview");
  preview.textContent = personalityTraits.length
    ? personalityTraits.map((item) => item.trait).join(", ")
    : "No custom traits.";

  const list = document.getElementById("personality-traits-list");
  list.innerHTML = "";
  if (!personalityTraits.length) {
    list.textContent = "No custom traits yet.";
    return;
  }
  personalityTraits.forEach((item) => {
    const row = document.createElement("div");
    row.style.cssText =
      "display:flex;align-items:center;justify-content:space-between;gap:12px;padding:8px;border:1px solid var(--border);border-radius:6px";
    const text = document.createElement("span");
    text.textContent = item.trait;
    const button = document.createElement("button");
    button.className = "modal-btn danger";
    button.textContent = "Remove";
    button.onclick = () => removePersonalityTrait(item.id);
    row.append(text, button);
    list.appendChild(row);
  });
}

async function openPersonalityManager() {
  await loadPersonalityTraits();
  document.getElementById("trait-manager-err").textContent = "";
  openModal("personality-manager-modal");
}

async function addPersonalityTrait() {
  const input = document.getElementById("new-personality-trait");
  const errEl = document.getElementById("trait-manager-err");
  const trait = input.value.trim();
  errEl.textContent = "";
  if (!trait) {
    errEl.textContent = "Enter a trait.";
    return;
  }
  const r = await fetch("/api/personality/traits", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ trait }),
  });
  const d = await r.json();
  if (!d.ok) {
    errEl.textContent = d.error || "Failed.";
    return;
  }
  input.value = "";
  await loadPersonalityTraits();
}

async function removePersonalityTrait(id) {
  const r = await fetch("/api/personality/traits", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  });
  const d = await r.json();
  if (!d.ok) {
    document.getElementById("trait-manager-err").textContent = d.error || "Failed.";
    return;
  }
  await loadPersonalityTraits();
}

async function saveWebSearchToggle(enabled) {
  // ----------------------------------------------------------
  // Save the web search preference to the server.
  // This writes to user_settings.web_search_enabled in MariaDB.
  // The value is read by api_chat on every request.
  // ----------------------------------------------------------
  try {
    const r = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ web_search_enabled: enabled ? 1 : 0 }),
    });
    const d = await r.json();
    if (!d.ok) throw new Error(d.error || "Save failed");
    showToast(enabled ? "Web search ON" : "Web search OFF");
  } catch (e) {
    showToast("Failed to save web search setting.");
  }
}

async function loadWebSearchToggle() {
  // ----------------------------------------------------------
  // Load the saved web search preference from the server and
  // set the checkbox state to match.  Called inside loadSettingsData.
  // ----------------------------------------------------------
  try {
    const r = await fetch("/api/settings");
    const d = await r.json();
    if (d.ok && d.settings) {
      const el = document.getElementById("web-search-toggle");
      if (el) el.checked = !!d.settings.web_search_enabled;
    }
  } catch {}
}

// JS-005: Chat System

function makeId() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
  });
}

async function loadConversations() {
  try {
    const r = await fetch("/api/conversations");
    const d = await r.json();
    const raw = Array.isArray(d.conversations) ? d.conversations : [];
    const out = {};
    raw.forEach((c) => {
      const cid = c.conversation_id || c.id;
      if (!cid) return;
      out[cid] = {
        conversation_id: cid,
        name: c.name || "New Conversation",
        pinned: !!c.pinned,
        created: c.created_at || Date.now(),
        messages: [],
      };
    });
    return out;
  } catch {
    return {};
  }
}

async function newConversation() {
  const cid = makeId();
  const conv = {
    conversation_id: cid,
    name: "New Conversation",
    pinned: false,
    created: Date.now(),
    messages: [],
  };
  try {
    const response = await fetch("/api/conversations/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: cid, name: "New Conversation" }),
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || "Create failed");
  } catch (error) {
    showToast("Could not create conversation.", "var(--red)");
    return null;
  }
  conversations[cid] = conv;
  await activateConv(cid);
  renderSidebar();
  return cid;
}

async function activateConv(cid) {
  if (!conversations[cid]) return;
  stopGreetingRotation();
  activeConvId = cid;
  document.getElementById("conv-title-display").textContent = conversations[cid].name || "Untitled";
  renderSidebar();
  await loadAndRenderMessages(cid);
}

function stopGreetingRotation() {
  _greetingRequest++;
  _greetingDeadline = 0;
  _nextGreeting = null;
  if (_greetingTimer) {
    clearTimeout(_greetingTimer);
    _greetingTimer = null;
  }
  if (_greetingPrefetchTimer) {
    clearTimeout(_greetingPrefetchTimer);
    _greetingPrefetchTimer = null;
  }
  stopGreetingLoadingMessages();
  if (_greetingCountdownTimer) {
    clearInterval(_greetingCountdownTimer);
    _greetingCountdownTimer = null;
  }
}

function scheduleGreetingRotation(refreshSeconds, prefetchLeadSeconds = 30) {
  if (activeConvId || input.value.trim() || !Number.isFinite(Number(refreshSeconds))) return;
  if (_greetingTimer) clearTimeout(_greetingTimer);
  if (_greetingPrefetchTimer) clearTimeout(_greetingPrefetchTimer);

  const rotationMs = Math.max(1000, Number(refreshSeconds) * 1000);
  const prefetchMs = Math.max(0, rotationMs - Number(prefetchLeadSeconds) * 1000);
  _greetingDeadline = Date.now() + rotationMs;
  _nextGreeting = null;
  _greetingPrefetchTimer = setTimeout(prefetchTemporaryGreeting, prefetchMs);
  _greetingTimer = setTimeout(swapPrefetchedGreeting, rotationMs);
  startGreetingCountdown();
}

function shuffledCopy(items) {
  const values = [...items];
  for (let index = values.length - 1; index > 0; index--) {
    const swapIndex = Math.floor(Math.random() * (index + 1));
    [values[index], values[swapIndex]] = [values[swapIndex], values[index]];
  }
  return values;
}

function drawGreetingUiPool(poolName, items) {
  const userKey = currentUser?.id || "anonymous";
  const key = `${userKey}:${poolName}`;
  const signature = items.join("\u0000");
  let state = _greetingUiPools.get(key);
  if (!state || state.signature !== signature) {
    state = { signature, unused: [], last: null };
    _greetingUiPools.set(key, state);
  }
  if (!state.unused.length) state.unused = shuffledCopy(items);
  let selected = state.unused.pop();
  if (selected === state.last && state.unused.length) {
    const alternative = state.unused.pop();
    state.unused.push(selected);
    selected = alternative;
  }
  state.last = selected;
  return selected;
}

function selectGreetingEffect() {
  return drawGreetingUiPool("effects", [
    "greeting-pulse-glow",
    "greeting-breathe",
    "greeting-border-flow",
    "greeting-shimmer",
    "greeting-float",
    "greeting-cursor",
    "greeting-energy-wave",
    "greeting-focus-ring",
  ]);
}

function updateGreetingCountdown() {
  if (!SHOW_GREETING_COUNTDOWN) return;
  const timer = chat.querySelector(".greeting-countdown");
  if (!timer || !_greetingDeadline) return;
  const remaining = Math.max(0, Math.ceil((_greetingDeadline - Date.now()) / 1000));
  const minutes = String(Math.floor(remaining / 60)).padStart(2, "0");
  const seconds = String(remaining % 60).padStart(2, "0");
  timer.textContent = `Next greeting in: ${minutes}:${seconds}`;
}

function startGreetingCountdown() {
  if (_greetingCountdownTimer) clearInterval(_greetingCountdownTimer);
  if (!SHOW_GREETING_COUNTDOWN) return;
  updateGreetingCountdown();
  _greetingCountdownTimer = setInterval(updateGreetingCountdown, 1000);
}

// JS-007: Greeting System
// ------------------------------------------------------
// Function: renderTemporaryGreeting()
// Purpose: Renders the temporary greeting without storing it as a conversation message.
// Called by: Greeting loading, refresh, and prefetch flows.
// Updates: The temporary greeting node inside the chat container.
// ------------------------------------------------------
function renderTemporaryGreeting(text, loading = false) {
  if (activeConvId || input.value.trim()) return;
  const visibleText = String(text || "").trim() || (loading ? "Aetheraeon is thinking..." : "");
  if (!visibleText) return;
  const panel = document.createElement("div");
  const effect = loading ? "greeting-loading" : selectGreetingEffect();
  panel.className = `msg msg-ai temporary-greeting ${effect}${loading ? " loading" : ""}`;
  panel.dataset.greetingState = loading ? "loading" : "ready";
  const bubble = document.createElement("div");
  bubble.className = "bubble" + (loading ? " typing" : "");
  bubble.textContent = visibleText;
  if (!loading) _activeGreetingText = visibleText;
  if (SHOW_GREETING_COUNTDOWN && !loading) {
    const countdown = document.createElement("div");
    countdown.className = "greeting-countdown";
    panel.appendChild(countdown);
  }
  panel.appendChild(bubble);
  chat.replaceChildren(panel);
  if (!loading) updateGreetingCountdown();
}

function showGreetingLoadingState() {
  const loadingByStyle = {
    professional: [
      "Preparing a useful question...",
      "Looking for a worthwhile topic...",
      "Finding a good place to begin...",
      "Checking what might be useful...",
      "Aetheraeon is thinking...",
      "Almost ready...",
    ],
    casual: [
      "I have an idea forming...",
      "Let me think of something interesting...",
      "Looking for a little inspiration...",
      "Let me think about that...",
      "Searching my thoughts...",
      "Putting something together...",
      "Aetheraeon is thinking...",
      "Almost ready...",
    ],
    friendly: [
      "Finding a good question for you...",
      "Trying to remember what might interest you...",
      "Checking what we should talk about today...",
      "Looking for something interesting...",
      "I have an idea forming...",
      "Searching my thoughts...",
      "Putting something together...",
      "Almost ready...",
    ],
    balanced: [
      "Let me think of something interesting...",
      "Finding a good question for you...",
      "Looking for a little inspiration...",
      "I have an idea forming...",
      "Checking what might be useful...",
      "Aetheraeon is thinking...",
      "Searching my thoughts...",
      "Putting something together...",
      "Let me think...",
      "Almost ready...",
      "Let me think about that...",
    ],
  };
  const loadingMessages = loadingByStyle[_greetingPersonalityStyle] || loadingByStyle.balanced;
  renderTemporaryGreeting(
    drawGreetingUiPool(`loading:${_greetingPersonalityStyle}`, loadingMessages),
    true,
  );
}

function startGreetingLoadingMessages() {
  stopGreetingLoadingMessages();
  showGreetingLoadingState();
  _greetingLoadingTimer = setInterval(showGreetingLoadingState, 2200);
}

function ensureGreetingLoadingState() {
  if (activeConvId || input.value.trim()) return;
  const panel = chat.querySelector(".temporary-greeting.loading");
  const bubble = panel?.querySelector(".bubble");
  if (!panel || !bubble?.textContent.trim()) showGreetingLoadingState();
}

function stopGreetingLoadingMessages() {
  if (_greetingLoadingTimer) {
    clearInterval(_greetingLoadingTimer);
    _greetingLoadingTimer = null;
  }
}

function clearTemporaryGreetingForInteraction() {
  if (!chat.querySelector(".temporary-greeting")) return;
  stopGreetingRotation();
  chat.innerHTML = "";
}

async function refreshTemporaryGreeting() {
  if (activeConvId || input.value.trim()) return;
  const requestId = ++_greetingRequest;
  startGreetingLoadingMessages();

  try {
    const response = await fetch("/api/greeting");
    const data = await response.json();
    if (requestId !== _greetingRequest || activeConvId || input.value.trim()) return;
    if (!response.ok || !data.ok || !data.greeting) {
      ensureGreetingLoadingState();
      _greetingTimer = setTimeout(refreshTemporaryGreeting, 10000);
      return;
    }
    stopGreetingLoadingMessages();
    renderTemporaryGreeting(data.greeting);
    scheduleGreetingRotation(data.refresh_seconds, data.prefetch_lead_seconds);
  } catch {
    if (requestId === _greetingRequest && !activeConvId && !input.value.trim()) {
      ensureGreetingLoadingState();
      _greetingTimer = setTimeout(refreshTemporaryGreeting, 10000);
    }
  }
}

async function prefetchTemporaryGreeting() {
  if (activeConvId || input.value.trim()) return;
  const requestId = _greetingRequest;
  try {
    const response = await fetch("/api/greeting?refresh=1");
    const data = await response.json();
    if (requestId !== _greetingRequest || activeConvId || input.value.trim()) return;
    if (!response.ok || !data.ok || !data.greeting) throw new Error("Greeting unavailable");
    if (data.source === "fallback" && chat.querySelector(".temporary-greeting:not(.loading)")) {
      _greetingPrefetchTimer = setTimeout(prefetchTemporaryGreeting, 5000);
      return;
    }
    _nextGreeting = data;
    if (Date.now() >= _greetingDeadline) swapPrefetchedGreeting();
  } catch {
    if (requestId === _greetingRequest && !activeConvId && !input.value.trim()) {
      _greetingPrefetchTimer = setTimeout(prefetchTemporaryGreeting, 5000);
    }
  }
}

function swapPrefetchedGreeting() {
  if (activeConvId || input.value.trim()) return;
  if (!_nextGreeting) {
    _greetingTimer = setTimeout(swapPrefetchedGreeting, 1000);
    return;
  }
  const next = _nextGreeting;
  renderTemporaryGreeting(next.greeting);
  scheduleGreetingRotation(next.refresh_seconds, next.prefetch_lead_seconds);
}

function showNoConversationState() {
  activeConvId = null;
  document.getElementById("conv-title-display").textContent = "";
  renderSidebar();
  stopGreetingRotation();
  refreshTemporaryGreeting();
}

function toggleConversation(cid) {
  if (activeConvId === cid) {
    showNoConversationState();
    return;
  }
  activateConv(cid);
}

async function loadAndRenderMessages(cid) {
  chat.innerHTML = "";
  try {
    const r = await fetch(`/api/messages?conversation_id=${encodeURIComponent(cid)}`);
    const d = await r.json();
    if (d.ok && d.messages) {
      d.messages.forEach((m) => {
        addMsgDOM(
          m.role === "user" ? "you" : "ai",
          m.content || "",
          m.tool_used || "system",
          m.created_at ? m.created_at.slice(11, 16) : Date.now(),
        );
      });
    }
  } catch {}
  scrollBottom();
}

async function deleteConv(cid) {
  if (!confirm("Delete this conversation? This cannot be undone.")) return;

  const backup = conversations[cid];

  try {
    // ── 1. DELETE ON SERVER FIRST ──
    const r = await fetch("/api/conversations/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: cid }),
    });

    const d = await r.json();
    if (!d.ok) throw new Error("Delete failed");

    // ── 2. ALWAYS RELOAD STATE FROM SERVER ──
    conversations = await loadConversations();
    renderSidebar();

    // ── 3. HANDLE EMPTY STATE ──
    if (activeConvId === cid || !conversations[activeConvId]) {
      showNoConversationState();
    }

    // ── 4. SAFE ACTIVATION ──
  } catch (err) {
    // ── rollback if anything fails ──
    if (backup) {
      conversations[cid] = backup;
      renderSidebar();
    }

    console.error("Delete failed:", err);
  }
}

async function renameConv(cid, newName) {
  if (!conversations[cid]) return;

  const old = conversations[cid].name;

  const clean = (newName || "").trim().slice(0, 80) || "Untitled";

  // ── 1. Optimistic UI update (instant) ──
  conversations[cid].name = clean;

  if (activeConvId === cid) {
    document.getElementById("conv-title-display").textContent = clean;
  }

  renderSidebar();

  try {
    // ── 2. Persist to backend ──
    const res = await fetch("/api/conversations/rename", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: cid, name: clean }),
    });

    const data = await res.json();

    // ── 3. Server rejected → rollback ──
    if (!data.ok) {
      conversations[cid].name = old;
      renderSidebar();
      if (activeConvId === cid) {
        document.getElementById("conv-title-display").textContent = old;
      }
    }
  } catch (err) {
    // ── 4. Network failure rollback ──
    conversations[cid].name = old;
    renderSidebar();
    if (activeConvId === cid) {
      document.getElementById("conv-title-display").textContent = old;
    }
  }
}

async function togglePin(cid) {
  if (!conversations[cid]) return;
  const old = conversations[cid].pinned;
  conversations[cid].pinned = !old;
  renderSidebar();
  try {
    await fetch("/api/conversations/pin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ conversation_id: cid, pinned: conversations[cid].pinned }),
    });
  } catch {
    conversations[cid].pinned = old;
    renderSidebar();
  }
}

function sortedIds() {
  return Object.keys(conversations).sort((a, b) => {
    const A = conversations[a],
      B = conversations[b];
    if (!!A.pinned !== !!B.pinned) return A.pinned ? -1 : 1;
    return new Date(B.created) - new Date(A.created);
  });
}

// ────────────────────────────────────────────────────────────
// SIDEBAR RENDERING
// ────────────────────────────────────────────────────────────

function renderSidebar() {
  const list = document.getElementById("conv-list");
  const filter = (document.getElementById("conv-filter-input").value || "").toLowerCase();

  list.innerHTML = "";

  let ids = sortedIds();

  if (filter) {
    ids = ids.filter((id) => (conversations[id].name || "").toLowerCase().includes(filter));
  }

  const pinned = ids.filter((id) => conversations[id]?.pinned);
  const unpinned = ids.filter((id) => !conversations[id]?.pinned);

  function makeGroup(label, groupIds) {
    if (!groupIds.length) return;

    if (label) {
      const gl = document.createElement("div");
      gl.className = "conv-group-label";
      gl.textContent = label;
      list.appendChild(gl);
    }

    groupIds.forEach((id) => {
      const conv = conversations[id];

      // MAIN ITEM
      const item = document.createElement("div");
      item.className = "conv-item" + (id === activeConvId ? " active" : "");
      item.onclick = () => toggleConversation(id);

      // NAME
      const nm = document.createElement("span");
      nm.className = "conv-name";
      nm.textContent = conv.name || "New Conversation";

      item.appendChild(nm);

      // ACTION AREA
      const acts = document.createElement("div");
      acts.className = "conv-actions";

      acts.addEventListener("click", (e) => {
        e.stopPropagation();
      });

      // MENU BUTTON
      const menuBtn = document.createElement("button");
      menuBtn.className = "conv-menu-btn";
      menuBtn.textContent = "⋮";

      // DROPDOWN MENU
      const menu = document.createElement("div");
      menu.className = "conv-dropdown-menu";
      menu.style.display = "none";

      // HELPER
      function addMenuItem(label, fn) {
        const btn = document.createElement("button");

        btn.className = "conv-dropdown-item";
        btn.textContent = label;

        btn.onclick = (e) => {
          e.stopPropagation();

          menu.style.display = "none";

          fn();
        };

        menu.appendChild(btn);
      }

      // MENU ITEMS
      addMenuItem(conv.pinned ? "Unpin" : "Pin", () => togglePin(id));

      addMenuItem("Rename", () => {
        activateConv(id);
        startRename();
      });

      addMenuItem("Share", () => {
        exportSingleConv(id, true);
      });

      addMenuItem("Export", () => {
        exportSingleConv(id, false);
      });

      // DIVIDER
      const hr = document.createElement("hr");
      hr.className = "conv-menu-divider";
      menu.appendChild(hr);

      addMenuItem("Delete", () => {
        deleteConv(id);
      });

      // TOGGLE MENU
      menuBtn.onclick = (e) => {
        e.stopPropagation();

        const isOpen = menu.style.display === "block";

        // CLOSE ALL MENUS
        document.querySelectorAll(".conv-dropdown-menu").forEach((m) => {
          m.style.display = "none";
        });

        // TOGGLE CURRENT
        menu.style.display = isOpen ? "none" : "block";
      };

      // APPEND
      acts.appendChild(menuBtn);
      acts.appendChild(menu);

      item.appendChild(acts);

      list.appendChild(item);
    });
  }

  makeGroup("Pinned", pinned);
  makeGroup(pinned.length ? "Recent" : "", unpinned);
}

// FILTER
function filterConvList() {
  renderSidebar();
}

// CLOSE MENUS WHEN CLICKING OUTSIDE
document.addEventListener("click", () => {
  document.querySelectorAll(".conv-dropdown-menu").forEach((menu) => {
    menu.style.display = "none";
  });
});

// ────────────────────────────────────────────────────────────
// SIDEBAR TABS (chats vs playbooks)
// ────────────────────────────────────────────────────────────

function switchSidebarTab(tab) {
  document.getElementById("nav-chats").classList.toggle("active", tab === "chats");
  document.getElementById("nav-playbooks").classList.toggle("active", tab === "playbooks");
  document.getElementById("conv-list").classList.toggle("hidden", tab !== "chats");
  document.getElementById("playbook-list").classList.toggle("active", tab === "playbooks");
  if (tab === "playbooks") renderPlaybooks();
}

// ────────────────────────────────────────────────────────────
// PLAYBOOKS
// ────────────────────────────────────────────────────────────

async function renderPlaybooks() {
  const container = document.getElementById("pb-items");
  container.innerHTML =
    '<div style="font-size:0.72em;color:var(--muted);padding:10px 12px">Loading…</div>';
  try {
    const r = await fetch("/api/playbooks");
    const d = await r.json();
    container.innerHTML = "";
    if (!d.ok || !d.playbooks.length) {
      container.innerHTML =
        '<div style="font-size:0.72em;color:var(--muted);padding:10px 12px">(no playbooks yet)</div>';
      return;
    }
    d.playbooks.forEach((pb) => {
      const item = document.createElement("div");
      item.className = "pb-item";
      const nm = document.createElement("span");
      nm.className = "pb-name";
      nm.textContent = pb.name;
      item.appendChild(nm);
      // ACTIONS
      const acts = document.createElement("div");
      acts.className = "pb-actions";

      acts.addEventListener("click", (e) => {
        e.stopPropagation();
      });

      // MENU BUTTON
      const menuBtn = document.createElement("button");
      menuBtn.className = "conv-menu-btn";
      menuBtn.textContent = "⋮";

      // MENU
      const menu = document.createElement("div");
      menu.className = "conv-dropdown-menu";
      menu.style.display = "none";

      // HELPER
      function addMenuItem(label, fn, extraClass = "") {
        const btn = document.createElement("button");

        btn.className = "conv-dropdown-item " + extraClass;
        btn.textContent = label;

        btn.onclick = (e) => {
          e.stopPropagation();

          menu.style.display = "none";

          fn();
        };

        menu.appendChild(btn);
      }

      // ITEMS
      addMenuItem("Run", () => {
        sendCmd("run playbook " + pb.name);
      });

      addMenuItem("Edit", () => {
        openPlaybookModal(pb);
      });

      // DIVIDER
      const hr = document.createElement("hr");
      hr.className = "conv-menu-divider";
      menu.appendChild(hr);

      addMenuItem(
        "Delete",
        () => {
          if (!confirm(`Delete playbook "${pb.name}"?`)) return;

          fetch("/api/playbooks/delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: pb.id }),
          }).then(() => renderPlaybooks());
        },
        "danger",
      );

      // TOGGLE MENU
      menuBtn.onclick = (e) => {
        e.stopPropagation();

        const isOpen = menu.style.display === "block";

        document.querySelectorAll(".conv-dropdown-menu").forEach((m) => {
          m.style.display = "none";
        });

        menu.style.display = isOpen ? "none" : "block";
      };

      acts.appendChild(menuBtn);
      acts.appendChild(menu);

      item.appendChild(acts);
      container.appendChild(item);
    });
  } catch (e) {
    container.innerHTML =
      '<div style="font-size:0.72em;color:var(--red);padding:10px 12px">Failed to load playbooks.</div>';
  }
}

function openPlaybookModal(pb = null) {
  _editingPbId = pb ? pb.id : null;
  document.getElementById("pb-modal-title").textContent = pb
    ? "✏️ Edit Playbook"
    : "📋 New Playbook";
  document.getElementById("pb-name-input").value = pb ? pb.name || "" : "";
  document.getElementById("pb-err").textContent = "";

  // Parse steps from content JSON
  let steps = [];
  if (pb && pb.content) {
    try {
      const parsed = JSON.parse(pb.content);
      steps = parsed.steps || [];
      document.getElementById("pb-desc-input").value = parsed.description || "";
    } catch {
      document.getElementById("pb-desc-input").value = "";
    }
  } else {
    document.getElementById("pb-desc-input").value = "";
  }

  // Render step list
  const stepList = document.getElementById("pb-step-list");
  stepList.innerHTML = "";
  if (!steps.length) {
    addPlaybookStep(); // Start with one empty step
  } else {
    steps.forEach((s) => addPlaybookStep(s));
  }

  openModal("playbook-modal");
}

function addPlaybookStep(step = null) {
  const list = document.getElementById("pb-step-list");
  const row = document.createElement("div");
  row.className = "pb-step";

  const actionIn = document.createElement("input");
  actionIn.placeholder = "action (chat, shell, aider…)";
  actionIn.value = step ? step.action || "" : "";
  const targetIn = document.createElement("input");
  targetIn.placeholder = "target / command / message";
  targetIn.value = step ? step.target || step.message || "" : "";
  const delBtn = document.createElement("button");
  delBtn.className = "pb-step-del";
  delBtn.textContent = "✕";
  delBtn.onclick = () => row.remove();

  row.append(actionIn, targetIn, delBtn);
  list.appendChild(row);
}

async function savePlaybook() {
  const errEl = document.getElementById("pb-err");
  errEl.textContent = "";
  const name = document.getElementById("pb-name-input").value.trim();
  if (!name) {
    errEl.textContent = "Playbook name required.";
    return;
  }

  const desc = document.getElementById("pb-desc-input").value.trim();
  const rows = document.getElementById("pb-step-list").querySelectorAll(".pb-step");
  const steps = [];
  rows.forEach((row) => {
    const inputs = row.querySelectorAll("input");
    const action = inputs[0].value.trim();
    const target = inputs[1].value.trim();
    if (action) steps.push({ action, target, message: target });
  });

  const content = JSON.stringify({ name, description: desc, steps });

  try {
    let url = "/api/playbooks/create";
    let body = { name, content };
    if (_editingPbId) {
      url = "/api/playbooks/update";
      body = { id: _editingPbId, name, content };
    }
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const d = await r.json();
    if (!d.ok) {
      errEl.textContent = d.error || "Save failed.";
      return;
    }
    closeModal("playbook-modal");
    showToast(_editingPbId ? "Playbook updated!" : "Playbook created!");
    renderPlaybooks();
  } catch (e) {
    errEl.textContent = "Error: " + e.message;
  }
}

// JS-006: Message Rendering

/**
 * Parse backtick code blocks and inline code in a message string.
 * Returns an array of DOM nodes.
 */
function parseMessageContent(text) {
  const container = document.createDocumentFragment();

  // Split on triple-backtick code blocks
  const parts = text.split(/(```[\s\S]*?```)/g);
  parts.forEach((part) => {
    if (part.startsWith("```") && part.endsWith("```")) {
      // Extract language hint and code
      const inner = part.slice(3, -3);
      const nlIndex = inner.indexOf("\n");
      const lang = nlIndex > -1 ? inner.slice(0, nlIndex).trim() : "";
      const code = nlIndex > -1 ? inner.slice(nlIndex + 1) : inner;

      const pre = document.createElement("pre");
      const code_el = document.createElement("code");
      code_el.textContent = code;
      pre.appendChild(code_el);

      // Copy button
      const copyBtn = document.createElement("button");
      copyBtn.className = "code-copy-btn";
      copyBtn.textContent = lang ? `📋 ${lang}` : "📋 copy";
      copyBtn.onclick = () => {
        copyToClipboard(code);
        showToast("Code copied!");
      };
      pre.appendChild(copyBtn);
      container.appendChild(pre);
    } else {
      // Handle inline code (`...`)
      const inlineParts = part.split(/(`[^`]+`)/g);
      inlineParts.forEach((ip) => {
        if (ip.startsWith("`") && ip.endsWith("`") && ip.length > 2) {
          const code_el = document.createElement("code");
          code_el.textContent = ip.slice(1, -1);
          container.appendChild(code_el);
        } else if (ip) {
          container.appendChild(document.createTextNode(ip));
        }
      });
    }
  });
  return container;
}

// ------------------------------------------------------
// Function: addMsgDOM()
// Purpose: Builds and appends a visible chat message from server-backed message data.
// Called by: Conversation loading, chat submission, status notices, and greeting flows.
// Updates: The chat message container.
// ------------------------------------------------------
function addMsgDOM(who, text, tool, ts) {
  const wrap = document.createElement("div");
  wrap.className = "msg msg-" + who;

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  let processBlock = null;
  let details = null;

  // ── PROCESS EXTRACTION (AI ONLY) ─────────────────────
  if (who === "ai") {
    const start = text.indexOf("[PROCESS]");
    const end = text.indexOf("AI:");

    if (start !== -1 && end !== -1) {
      processBlock = text.slice(start + 9, end).trim();
      text = text.slice(0, start) + "AI:" + text.slice(end + 3);

      // build collapsible process UI
      details = document.createElement("details");
      details.className = "process-box";

      const summary = document.createElement("summary");
      summary.textContent = "PROCESS";

      const pre = document.createElement("pre");
      pre.textContent = processBlock;

      details.appendChild(summary);
      details.appendChild(pre);
    }
  }

  // ── BUBBLE CONTENT RENDERING ─────────────────────────
  if (who === "ai" && (text.includes("```") || text.includes("`"))) {
    bubble.appendChild(parseMessageContent(text));
  } else {
    bubble.textContent = text;
  }

  // ── APPEND IN CORRECT ORDER ──────────────────────────

  // timestamp first (optional style consistency)
  const meta = document.createElement("div");
  meta.className = "msg-meta";

  const toolBadge =
    tool && tool !== "chat" && tool !== "system"
      ? `<span class="tool-badge tool-${tool}">${toolLabel(tool)}</span>`
      : "";

  meta.innerHTML = formatTimestamp(ts || Date.now()) + toolBadge;
  if (who === "you") meta.style.textAlign = "right";

  wrap.appendChild(meta);

  // bubble ALWAYS comes second
  wrap.appendChild(bubble);

  // process comes AFTER bubble (clean UX)
  if (details) {
    wrap.appendChild(details);
  }

  // ── ACTION BUTTONS ───────────────────────────────────
  const acts = document.createElement("div");
  acts.className = "msg-actions";

  const copyBtn = document.createElement("button");
  copyBtn.className = "msg-act";
  copyBtn.textContent = "📋 copy";

  const shareBtn = document.createElement("button");
  shareBtn.className = "msg-act";
  shareBtn.textContent = "📤 share";

  copyBtn.onclick = () => {
    copyToClipboard(text);
    showToast("Copied!");
  };

  shareBtn.onclick = () => openShareModal(text, false);

  acts.append(copyBtn, shareBtn);
  wrap.appendChild(acts);

  // ── FINAL RENDER ──────────────────────────────────────
  chat.appendChild(wrap);
  scrollBottom();

  return wrap;
}

function toolLabel(t) {
  const map = {
    shell: "⚡ shell",
    aider: "🤖 aider",
    chromadb_store: "🧠 store",
    chromadb_recall: "🔍 recall",
    memory_recall: "🔍 session",
    n8n: "⚙️ n8n",
    web_search: "🌐 web",
    system: "🔧 sys",
  };
  return map[t] || "🔧 " + t;
}

function addTyping() {
  const el = document.createElement("div");
  el.className = "msg msg-ai";
  el.innerHTML = '<div class="bubble typing">Aetheraeon <span>▋</span></div>';
  chat.appendChild(el);
  scrollBottom();
  return el;
}

// SEND MESSAGE
function dumpState(label = "STATE DUMP") {
  console.log(`\n📊 ${label}`, {
    activeConvId,
    currentUser,
    userId: currentUser?.id,
    conversationsCount: conversations ? Object.keys(conversations).length : 0,
    sidebarOpen,
    cmdHistoryLength: cmdHistory?.length,
  });
}
// ------------------------------------------------------
// Function: sendCmd()
// Purpose: Sends a user command to the existing chat endpoint and renders its response.
// Called by: Send button, keyboard handler, and quick-command controls.
// Updates: Command history, input state, messages, and conversation metadata.
// ------------------------------------------------------
async function sendCmd(cmd) {
  dumpState("BEFORE SEND");
  console.log("🔥 SEND FUNCTION HIT");
  cmd = (cmd || "").trim();
  if (!cmd) return;

  if (!currentUser?.id) {
    showToast("Sign in before sending a message.");
    return;
  }

  const startsNewConversation = !activeConvId;
  const greetingContext = startsNewConversation ? _activeGreetingText : "";
  clearTemporaryGreetingForInteraction();
  sendBtn.disabled = true;
  if (!activeConvId) {
    const createdId = await newConversation();
    if (!createdId) {
      sendBtn.disabled = false;
      return;
    }
  }

  const sendingConvId = activeConvId;

  // ── Command history (for ↑↓ navigation) ──────────────────
  if (cmdHistory[0] !== cmd) {
    cmdHistory.unshift(cmd);
    if (cmdHistory.length > 100) cmdHistory.pop();
  }
  historyIdx = -1;
  draftSaved = "";

  // Clear input
  input.value = "";
  autoResize();

  // Show user bubble (optimistic)
  addMsgDOM("you", cmd, "system", Date.now());

  const typing = addTyping();

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: cmd,
        conversation_id: sendingConvId,
        user_id: currentUser?.id,
        greeting_context: greetingContext,
      }),
    });
    _activeGreetingText = "";
    const data = await resp.json();

    if (data.title && conversations[sendingConvId]) {
      conversations[sendingConvId].name = data.title;

      if (activeConvId === sendingConvId) {
        document.getElementById("conv-title-display").textContent = data.title;
      }

      renderSidebar();
    }

    // Remove typing indicator
    if (typing?.parentNode) chat.removeChild(typing);

    const text = data.response || data.error || "(no response)";

    // ── Handle special actions ─────────────────────────────
    if (data.action === "clear_chat") {
      chat.innerHTML = "";
      addMsgDOM("ai", text, data.tool || "system", Date.now());
    } else if (data.action?.type === "aider_approve") {
      const msgEl = addMsgDOM("ai", text, data.tool || "aider", Date.now());
      const bubble = msgEl.querySelector(".bubble");
      if (bubble) {
        const det = document.createElement("details");
        det.className = "proc";
        det.open = true;
        const s = document.createElement("summary");
        s.textContent = "Aider approval required";
        const pre = document.createElement("pre");
        pre.textContent = `File:        ${data.action.file}\nInstruction: ${data.action.instruction}`;
        const btnRow = document.createElement("div");
        btnRow.style.cssText = "margin-top:8px;display:flex;gap:8px";

        const okBtn = document.createElement("button");
        okBtn.className = "qbtn";
        okBtn.textContent = "✅ Approve & Run";
        const canBtn = document.createElement("button");
        canBtn.className = "qbtn";
        canBtn.textContent = "❌ Cancel";

        okBtn.onclick = async () => {
          okBtn.disabled = canBtn.disabled = true;
          const t0 = Date.now();
          const sm = addMsgDOM("ai", "[AIDER] starting…", "aider", Date.now());
          const tmr = setInterval(() => {
            const s2 = Math.floor((Date.now() - t0) / 1000);
            const b2 = sm.querySelector(".bubble");
            if (b2)
              b2.textContent = `[AIDER] running… ${String(Math.floor(s2 / 60)).padStart(2, "0")}:${String(s2 % 60).padStart(2, "0")}`;
          }, 1000);
          try {
            const r2 = await fetch("/api/aider/run", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                file: data.action.file,
                instruction: data.action.instruction,
              }),
            });
            const d2 = await r2.json();
            clearInterval(tmr);
            addMsgDOM(
              "ai",
              d2.response || d2.error || "(no response)",
              d2.tool || "aider",
              Date.now(),
            );
          } catch (e2) {
            clearInterval(tmr);
            addMsgDOM("ai", "⚠️ Aider failed: " + e2.message, "system", Date.now());
          }
        };
        canBtn.onclick = () => {
          det.open = false;
          addMsgDOM("ai", "AI: Aider cancelled.", "system", Date.now());
        };
        btnRow.append(okBtn, canBtn);
        det.append(s, pre, btnRow);
        bubble.appendChild(det);
      }
    } else {
      addMsgDOM("ai", text, data.tool || "system", Date.now());
      // Speak AI response if voice mode is active
      speakText(text);
    }
  } catch (e) {
    if (typing?.parentNode) chat.removeChild(typing);
    addMsgDOM("ai", "⚠️ Connection error: " + e.message, "system", Date.now());
  }

  sendBtn.disabled = false;
  input.focus();
}

// ────────────────────────────────────────────────────────────
// VOICE — Speech-to-Text (mic input) + Text-to-Speech (AI output)
// ────────────────────────────────────────────────────────────

let _ttsVoice = null;

/** Pick the best available TTS voice (called once at load + on voice list change). */
function _pickTTSVoice() {
  if (!window.speechSynthesis) return;
  const voices = speechSynthesis.getVoices();
  _ttsVoice =
    voices.find((v) => v.lang === "en-US" && /natural|neural|google/i.test(v.name)) ||
    voices.find((v) => v.lang === "en-US") ||
    voices.find((v) => v.lang.startsWith("en")) ||
    voices[0] ||
    null;
}
if (window.speechSynthesis) {
  _pickTTSVoice();
  speechSynthesis.onvoiceschanged = _pickTTSVoice;
}

/**
 * Speak an AI response aloud.
 * Only fires when voice mode is active (_voiceActive).
 * Strips code blocks and debug lines before speaking.
 */
function speakText(text) {
  if (!_voiceActive || !window.speechSynthesis || !text) return;
  const clean = text
    .replace(/```[\s\S]*?```/g, "code block")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[PROCESS\][^\n]*/g, "")
    .replace(/\[AI (ERROR|RAW)\][^\n]*/g, "")
    .trim();
  if (!clean) return;
  speechSynthesis.cancel();
  const utt = new SpeechSynthesisUtterance(clean.slice(0, 600));
  utt.voice = _ttsVoice;
  utt.rate = 1.05;
  utt.pitch = 1.0;
  speechSynthesis.speak(utt);
}

function _initSpeechRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const sr = new SR();
  sr.lang = "en-US";
  sr.interimResults = true;
  sr.continuous = false;
  sr.onresult = (e) => {
    const transcript = Array.from(e.results)
      .map((r) => r[0].transcript)
      .join("");
    input.value = transcript;
    autoResize();
    if (input.value.trim()) clearTemporaryGreetingForInteraction();
    if (e.results[e.results.length - 1].isFinal) {
      stopVoice();
      sendCmd(input.value);
    }
  };
  sr.onerror = () => stopVoice();
  sr.onend = () => {
    if (_voiceActive) stopVoice();
  };
  return sr;
}

let _speechRecog = null;
let _voiceActive = false;

function toggleVoice() {
  if (_voiceActive) {
    stopVoice();
    return;
  }

  // Detect iOS — Safari on iOS blocks SpeechRecognition in WKWebView and some contexts
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SR) {
    // ----------------------------------------------------------
    // SpeechRecognition is supported in:
    //   Chrome (desktop + Android): window.webkitSpeechRecognition
    //   Edge (desktop): window.SpeechRecognition
    //   Safari (iOS 14.5+ and macOS): window.webkitSpeechRecognition
    //   Firefox: NOT supported (no implementation)
    //
    // On iOS the page MUST be served over HTTPS or the API is
    // blocked by the browser regardless of iOS version.
    //
    // If you are on HTTP localhost this will fail on iOS.
    // ----------------------------------------------------------
    const isHTTP =
      window.location.protocol === "http:" && !window.location.hostname.includes("localhost");
    if (isHTTP) {
      showToast("Voice requires HTTPS. Access via https:// or localhost.", "var(--orange)");
    } else if (isIOS) {
      showToast(
        "Voice requires Safari iOS 14.5+ or Chrome on iOS. Check your browser.",
        "var(--orange)",
      );
    } else {
      showToast("Voice not supported in this browser. Use Chrome, Edge, or Safari.", "var(--red)");
    }
    return;
  }

  if (!_speechRecog) _speechRecog = _initSpeechRecognition();
  if (!_speechRecog) {
    showToast("Could not start voice recognition. Please allow microphone access.", "var(--red)");
    return;
  }

  _voiceActive = true;
  document.getElementById("voice-btn").classList.add("active");
  document.getElementById("voice-indicator").classList.add("show");
  try {
    _speechRecog.start();
  } catch (e) {
    // Already started or permission denied
    stopVoice();
    showToast("Microphone access denied or already in use.", "var(--red)");
  }
}

function stopVoice() {
  _voiceActive = false;
  document.getElementById("voice-btn").classList.remove("active");
  document.getElementById("voice-indicator").classList.remove("show");
  try {
    _speechRecog?.stop();
  } catch {}
  speechSynthesis?.cancel();
}

// ────────────────────────────────────────────────────────────
// SEARCH
// ────────────────────────────────────────────────────────────

function openSearch() {
  document.getElementById("search-overlay").classList.add("open");
  const inp = document.getElementById("search-input");
  inp.focus();
  // Enter triggers search immediately
  inp.onkeydown = (e) => {
    if (e.key === "Enter") {
      clearTimeout(_searchTimer);
      doSearch();
    }
  };
}

function closeSearch() {
  const el = document.getElementById("search-overlay");
  if (!el) return;
  el.classList.remove("open");
  const ri = document.getElementById("search-results");
  const si = document.getElementById("search-input");
  if (ri) ri.innerHTML = "";
  if (si) si.value = "";
}

function closeSearchIfOutside(e) {
  if (e.target === document.getElementById("search-overlay")) closeSearch();
}

function debounceSearch() {
  clearTimeout(_searchTimer);
  _searchTimer = setTimeout(doSearch, 300);
}

async function doSearch() {
  const q = document.getElementById("search-input").value.trim();
  const resultsEl = document.getElementById("search-results");
  if (!q) {
    resultsEl.innerHTML = "";
    return;
  }
  resultsEl.innerHTML =
    '<div style="font-size:0.78em;color:var(--muted);padding:8px">Searching…</div>';
  try {
    const r = await fetch(`/api/messages/search?query=${encodeURIComponent(q)}`);
    const d = await r.json();
    resultsEl.innerHTML = "";
    if (!d.ok || !d.results.length) {
      resultsEl.innerHTML =
        '<div style="font-size:0.78em;color:var(--muted);padding:8px">No results.</div>';
      return;
    }
    d.results.forEach((res) => {
      const el = document.createElement("div");
      el.className = "search-result";
      el.innerHTML = `
        <div class="search-result-conv">📂 ${escHtml(res.conversation_name || "Unknown")}</div>
        <div class="search-result-text">${highlight(escHtml(res.content || ""), escHtml(q))}</div>
        <div class="search-result-role">${res.role === "user" ? "👤 You" : "🤖 AI"} · ${(res.created_at || "").slice(0, 16)}</div>
      `;
      el.onclick = () => {
        closeSearch();
        if (conversations[res.conversation_id]) activateConv(res.conversation_id);
        else {
          showToast("Conversation not loaded.", "var(--orange)");
        }
      };
      resultsEl.appendChild(el);
    });
  } catch (e) {
    resultsEl.innerHTML =
      '<div style="font-size:0.78em;color:var(--red);padding:8px">Search failed.</div>';
  }
}

function highlight(html, term) {
  if (!term) return html;
  const escapedTerm = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  return html.replace(
    new RegExp(`(${escapedTerm})`, "gi"),
    '<mark style="background:var(--accent);color:#0d1117;border-radius:2px;padding:0 2px">$1</mark>',
  );
}

// JS-008: Timers
// Status polling and backend availability polling use separate existing-purpose timers.

// STATUS DOTS

let _lastStatusOk = true;
let _knownServices = ["ollama", "chromadb", "n8n", "aider"]; // shown even when server is down

/** Render all known service dots as offline (red). Called when server is unreachable. */
function _renderAllDotsOffline() {
  const el = document.getElementById("status-dots");
  if (!el) return;
  el.innerHTML = "";
  _knownServices.forEach((name) => {
    const w = document.createElement("div");
    w.className = "status-dot-wrap";
    w.title = `${name}: OFFLINE (server down)`;
    const dot = document.createElement("div");
    dot.className = "dot fail";
    const lbl = document.createElement("div");
    lbl.className = "dot-label";
    lbl.textContent = name;
    w.append(dot, lbl);
    el.appendChild(w);
  });
}

async function refreshStatus() {
  try {
    const r = await fetch("/api/status", { signal: AbortSignal.timeout(10000) });
    const d = await r.json();

    // Remember service names for offline rendering
    const names = Object.keys(d.status || {});
    if (names.length) _knownServices = names;

    const el = document.getElementById("status-dots");
    el.innerHTML = "";
    let allOk = true;
    for (const [name, state] of Object.entries(d.status || {})) {
      const ok = typeof state === "object" && state !== null ? !!state.status : !!state;
      if (!ok) allOk = false;
      const w = document.createElement("div");
      w.className = "status-dot-wrap";
      w.title = `${name}: ${ok ? "online" : "OFFLINE"}`;
      const dot = document.createElement("div");
      dot.className = "dot" + (ok ? " ok" : " fail");
      const lbl = document.createElement("div");
      lbl.className = "dot-label";
      lbl.textContent = name;
      w.append(dot, lbl);
      el.appendChild(w);
    }
    if (d.version) document.getElementById("app-version").textContent = d.version;
    if (activeConvId && !allOk && _lastStatusOk) {
      const off = Object.entries(d.status || {})
        .filter(
          ([, state]) => !(typeof state === "object" && state !== null ? state.status : state),
        )
        .map(([name]) => name);
      addMsgDOM("ai", "⚠️ SERVICE OFFLINE: " + off.join(", "), "system", Date.now());
    }
    _lastStatusOk = allOk;
  } catch {
    // Server is completely unreachable — turn ALL dots red immediately
    _renderAllDotsOffline();
    if (activeConvId && _lastStatusOk) {
      addMsgDOM(
        "ai",
        "⚠️ Cannot reach Aetheraeon server — ai_orchestrator.py may be stopped.",
        "system",
        Date.now(),
      );
    }
    _lastStatusOk = false;
  }
}

// ────────────────────────────────────────────────────────────
// SHARE / EXPORT
// ────────────────────────────────────────────────────────────

/**
 * Fetch messages from DB and format as plain text transcript.
 * Returns a string.
 */
async function convToText(id) {
  const cid = id || activeConvId;
  const conv = conversations[cid];
  if (!conv) return "";

  const header = [
    `Aetheraeon — ${conv.name}`,
    `Exported: ${new Date().toLocaleString()}`,
    "─".repeat(50),
    "",
  ].join("\n");

  try {
    const r = await fetch(`/api/messages?conversation_id=${encodeURIComponent(cid)}`);
    const d = await r.json();
    if (!d.ok || !d.messages?.length) return header + "\n(no messages)";
    const body = d.messages
      .map((m) => {
        const who = m.role === "user" ? "You" : "AI";
        const time = (m.created_at || "").slice(11, 16);
        return `[${time}] ${who}:\n${m.content || ""}\n`;
      })
      .join("\n");
    return header + "\n" + body;
  } catch {
    return header + "\n(could not load messages)";
  }
}

function openShareModal(content, isWhole = false) {
  _shareContent = content || "";
  document.getElementById("share-sub").textContent = isWhole
    ? "Share full conversation"
    : "Share this message";
  openModal("share-modal");
}

function doShare(method) {
  const content = _shareContent;
  closeModal("share-modal");
  if (!content) return;
  if (method === "copy") {
    copyToClipboard(content);
    showToast("Copied!");
    return;
  }
  if (method === "file") {
    downloadFile(content, `aetheraeon-${Date.now()}.txt`);
    return;
  }
  if (method === "native") {
    // ----------------------------------------------------------
    // navigator.share() is the Web Share API.
    // Supported on: iOS Safari, Chrome on Android, Chrome 89+
    //               desktop (Windows only on Chrome/Edge).
    // On iOS it MUST be triggered by a direct user gesture
    // (a tap/click).  It will silently fail if called from a
    // setTimeout or other async path without a gesture chain.
    //
    // The .catch() suppresses the AbortError that fires when
    // the user dismisses the share sheet without sharing.
    // ----------------------------------------------------------
    if (navigator.canShare && navigator.canShare({ text: content })) {
      navigator.share({ title: "Aetheraeon Chat", text: content }).catch((err) => {
        if (err.name !== "AbortError") {
          copyToClipboard(content);
          showToast("Share failed -- copied to clipboard instead.");
        }
      });
    } else if (navigator.share) {
      navigator.share({ title: "Aetheraeon Chat", text: content }).catch(() => {
        copyToClipboard(content);
        showToast("Copied!");
      });
    } else {
      copyToClipboard(content);
      showToast("Share not available -- copied to clipboard.");
    }
  }
}

async function shareConversation() {
  const text = await convToText(activeConvId);
  openShareModal(text, true);
}

async function copyConversation() {
  const text = await convToText(activeConvId);
  copyToClipboard(text);
  showToast("Conversation copied!");
}

function exportConversation() {
  exportSingleConv(activeConvId, false);
}

async function exportSingleConv(id, shareMode = false) {
  const conv = conversations[id];
  if (!conv) return;
  const text = await convToText(id);
  if (shareMode) {
    openShareModal(text, true);
    return;
  }
  const safe = (conv.name || "chat").replace(/[^a-z0-9]/gi, "_").slice(0, 30);
  downloadFile(text, `aetheraeon_${safe}_${Date.now()}.txt`);
  showToast("Exported!");
}

async function exportAllConversations() {
  showToast("Exporting all conversations…", "var(--orange)");
  const lines = [
    `Aetheraeon — ALL CONVERSATIONS`,
    `User: ${currentUser?.email || ""}`,
    `Exported: ${new Date().toLocaleString()}`,
    "═".repeat(60),
  ];

  for (const id of sortedIds()) {
    const conv = conversations[id];
    if (!conv) continue;
    lines.push(`\n${"═".repeat(60)}`);
    lines.push(`📌 ${conv.name}${conv.pinned ? " [PINNED]" : ""}`);
    lines.push("─".repeat(60));
    try {
      const r = await fetch(`/api/messages?conversation_id=${encodeURIComponent(id)}`);
      const d = await r.json();
      if (d.ok && d.messages?.length) {
        d.messages.forEach((m) => {
          const who = m.role === "user" ? "You" : "AI";
          const time = (m.created_at || "").slice(11, 16);
          lines.push(`[${time}] ${who}: ${m.content || ""}`);
        });
      } else {
        lines.push("(no messages)");
      }
    } catch {
      lines.push("(failed to load)");
    }
  }

  downloadFile(lines.join("\n"), `aetheraeon_all_${Date.now()}.txt`);
  showToast("Export complete!");
}

// ────────────────────────────────────────────────────────────
// RENAME (inline header)
// ────────────────────────────────────────────────────────────

function startRename() {
  const disp = document.getElementById("conv-title-display");
  const field = document.getElementById("conv-title-input");
  if (!activeConvId || !conversations[activeConvId]) return;
  field.value = conversations[activeConvId].name || "";
  disp.style.display = "none";
  field.style.display = "inline-block";
  field.focus();
  field.select();
}

function finishRename() {
  const field = document.getElementById("conv-title-input");
  const disp = document.getElementById("conv-title-display");
  const val = field.value.trim();
  if (val && activeConvId) renameConv(activeConvId, val);
  field.style.display = "none";
  disp.style.display = "";
}

function titleKeydown(e) {
  if (e.key === "Enter") finishRename();
  if (e.key === "Escape") {
    document.getElementById("conv-title-input").style.display = "none";
    document.getElementById("conv-title-display").style.display = "";
  }
}

// ────────────────────────────────────────────────────────────
// SIDEBAR TOGGLE — desktop collapse vs mobile drawer
// ────────────────────────────────────────────────────────────

function _isMobile() {
  return window.innerWidth <= 768;
}

function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");

  if (_isMobile()) {
    // Mobile: slide-in drawer over content
    const isOpen = sidebar.classList.contains("open");

    if (isOpen) {
      sidebar.classList.remove("open");
      backdrop.classList.remove("show");
    } else {
      sidebar.classList.remove("collapsed");
      sidebar.classList.add("open");
      backdrop.classList.add("show");
    }
  } else {
    // Desktop: use REAL DOM state
    const isCollapsed = sidebar.classList.contains("collapsed");

    if (isCollapsed) {
      sidebar.classList.remove("collapsed");
    } else {
      sidebar.classList.add("collapsed");
    }

    sidebar.classList.remove("open");
    backdrop.classList.remove("show");
  }
}

function closeSidebarDrawer() {
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");

  sidebar.classList.remove("open");
  sidebar.classList.add("collapsed");

  backdrop.classList.remove("show");
}

// Close drawer on resize to desktop
window.addEventListener("resize", () => {
  if (!_isMobile()) {
    document.getElementById("sidebar-backdrop").classList.remove("show");
    document.getElementById("sidebar").classList.remove("open");
  }
});

// JS-011: Event Handlers

sendBtn.addEventListener("click", () => sendCmd(input.value));

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendCmd(input.value);
    return;
  }
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (historyIdx === -1) draftSaved = input.value;
    if (historyIdx < cmdHistory.length - 1) {
      historyIdx++;
      input.value = cmdHistory[historyIdx];
    }
    autoResize();
    return;
  }
  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIdx > 0) {
      historyIdx--;
      input.value = cmdHistory[historyIdx];
    } else if (historyIdx === 0) {
      historyIdx = -1;
      input.value = draftSaved;
    }
    autoResize();
    return;
  }
});

input.addEventListener("input", () => {
  autoResize();
  if (input.value.trim()) clearTemporaryGreetingForInteraction();
});

function autoResize() {
  input.style.height = "auto";
  input.style.height = Math.min(input.scrollHeight, 140) + "px";
}

// Quick bar buttons
document.querySelectorAll(".qbtn[data-cmd]").forEach((btn) => {
  btn.addEventListener("click", () => {
    const cmd = btn.getAttribute("data-cmd");
    if (cmd.endsWith(" ")) {
      input.value = cmd;
      input.focus();
      autoResize();
      clearTemporaryGreetingForInteraction();
    } else sendCmd(cmd);
  });
});

// ────────────────────────────────────────────────────────────
// UTILITIES
// ────────────────────────────────────────────────────────────

function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function formatTimestamp(ts) {
  let d;

  // ── SAFE INPUT HANDLING ─────────────────────────────
  if (!ts) {
    d = new Date();
  } else {
    d = new Date(ts);

    // fallback if invalid date
    if (isNaN(d.getTime())) {
      d = new Date();
    }
  }

  // ── PHP-STYLE COMPONENTS ────────────────────────────
  const MM = String(d.getMonth() + 1).padStart(2, "0");
  const DD = String(d.getDate()).padStart(2, "0");
  const YYYY = d.getFullYear();

  let hh = d.getHours();
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ampm = hh >= 12 ? "PM" : "AM";

  hh = hh % 12 || 12;
  hh = String(hh).padStart(2, "0");

  // ── FINAL FORMAT (easy to change like PHP) ───────────
  return `${MM}/${DD}/${YYYY} - ${hh}:${mm} ${ampm}`;
}

function scrollBottom() {
  chat.scrollTop = chat.scrollHeight;
}

function escHtml(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ────────────────────────────────────────────────────────────
// PASSWORD SHOW/HIDE — SVG eye icons
// ────────────────────────────────────────────────────────────

// Eye-open: classic almond lens shape with iris, pupil, and upper lashes
const _EYE_OPEN_SVG = `<svg class="eye-open" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <!-- Upper lashes -->
  <line x1="12" y1="3"  x2="12" y2="5.2"/>
  <line x1="17" y1="4.5" x2="15.8" y2="6.4"/>
  <line x1="7"  y1="4.5" x2="8.2"  y2="6.4"/>
  <!-- Almond / lens outline -->
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/>
  <!-- Iris ring -->
  <circle cx="12" cy="12" r="3.2"/>
  <!-- Pupil -->
  <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none"/>
</svg>`;

// Eye-slash: same eye with a diagonal line slashed through it
const _EYE_SLASH_SVG = `<svg class="eye-slash" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
  <!-- Almond outline (partial — hidden behind slash) -->
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8S1 12 1 12z"/>
  <!-- Iris ring -->
  <circle cx="12" cy="12" r="3.2"/>
  <!-- Pupil -->
  <circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none"/>
  <!-- Slash line -->
  <line x1="3" y1="3" x2="21" y2="21" stroke-width="2"/>
</svg>`;

/** Inject SVG icons into all .pw-eye buttons that are empty. */
function _initEyeButtons() {
  document.querySelectorAll(".pw-eye").forEach((btn) => {
    if (!btn.querySelector("svg")) {
      btn.innerHTML = _EYE_OPEN_SVG + _EYE_SLASH_SVG;
    }
  });
}

/**
 * Toggle a password input between hidden and visible.
 * Swaps the open/slash SVG via the .showing class on the button.
 */
function togglePw(inputId, btn) {
  const el = document.getElementById(inputId);
  if (!el) return;
  const showing = el.type === "text";
  el.type = showing ? "password" : "text";
  btn.classList.toggle("showing", !showing);
  btn.title = showing ? "Show password" : "Hide password";
}

// Run after DOM is ready
document.addEventListener("DOMContentLoaded", _initEyeButtons);

function copyToClipboard(text) {
  if (!text) return;
  if (navigator.clipboard?.writeText) {
    navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
  } else fallbackCopy(text);
}

function fallbackCopy(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.cssText = "position:fixed;opacity:0";
  document.body.appendChild(ta);
  ta.select();
  document.execCommand("copy");
  document.body.removeChild(ta);
}

function downloadFile(content, filename) {
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function showToast(msg, color) {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.style.background = color || "var(--green)";
  el.classList.add("show");
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove("show"), 2400);
}

// ────────────────────────────────────────────────────────────
// MODAL HELPERS
// ────────────────────────────────────────────────────────────

function openModal(id) {
  document.getElementById(id).classList.add("open");
}
function closeModal(id) {
  document.getElementById(id).classList.remove("open");
}

function closeModalIfOutside(e, id) {
  if (e.target === document.getElementById(id)) closeModal(id);
}

// ────────────────────────────────────────────────────────────
// BOOT
// ────────────────────────────────────────────────────────────

// ------------------------------------------------------
// Function: bootApp()
// Purpose: Transitions an authenticated session into the existing application UI.
// Called by: Login/registration success and session restoration.
// Updates: User identity, theme, conversations, service status, and input focus.
// ------------------------------------------------------
async function bootApp(user) {
  currentUser = user;

  // ── 1. Switch UI ──
  document.getElementById("login-screen").style.display = "none";
  document.getElementById("app").style.display = "flex";

  // ── 2. Populate user info ──
  const avatar = (user?.avatar || "?").toUpperCase();
  const fullName = user?.full_name?.trim() || user?.username?.trim() || "User";
  const email = user?.email?.trim() || "";

  document.getElementById("user-avatar").textContent = avatar;
  document.getElementById("user-display-name").textContent = fullName;
  document.getElementById("user-display-email").textContent = email;

  // ── 3. Load theme ──
  await loadTheme();

  // ── 4. Load conversations from DB (source of truth) ──
  conversations = await loadConversations();
  showNoConversationState();

  // ── 5. Handle EMPTY STATE cleanly ──
  // ── 6. Activate most recent / first conversation safely ──

  // ── 7. Render sidebar AFTER activation (keeps UI consistent) ──

  // ── 8. Status polling ──
  await refreshStatus();
  _statusTimer = setInterval(refreshStatus, 15000);

  // ── 9. Focus input ──
  input?.focus();
}

// INIT

startBackendAvailabilityMonitoring();
checkSession();

// JS-009: Animations
/* =======================================================
   CUSTOM CURSOR SYSTEM
   - 1:1 mouse tracking (no lag)
   - Hover state for interactive elements
   - Click / Hold / Double-click animations
   - Background-aware visual styling handled in CSS
   - Designed to plug into AI web UI without conflicts
======================================================= */

const cursor = document.getElementById("cursor");

let lastClick = 0;

/* =======================================================
   FOLLOW MOUSE
======================================================= */

document.addEventListener("mousemove", (e) => {
  cursor.style.left = e.clientX + "px";
  cursor.style.top = e.clientY + "px";
});

/* =======================================================
   BUTTON HOVER
======================================================= */

document.addEventListener("pointerover", (e) => {
  const el = e.target.closest(
    "button, a, input, textarea, select, [onclick], .clickable, .conv-act-btn",
  );

  if (el) {
    cursor.classList.add("hover");
  }
});

document.addEventListener("pointerout", (e) => {
  const el = e.target.closest(
    "button, a, input, textarea, select, [onclick], .clickable, .conv-act-btn",
  );

  if (el) {
    cursor.classList.remove("hover");
  }
});

/* =======================================================
   HOLD + SINGLE CLICK
======================================================= */

document.addEventListener("mousedown", () => {
  cursor.classList.add("holding");
});

document.addEventListener("mouseup", () => {
  cursor.classList.remove("holding");

  cursor.classList.add("clicking");

  setTimeout(() => {
    cursor.classList.remove("clicking");
  }, 180);
});

/* =======================================================
   DOUBLE CLICK
======================================================= */

document.addEventListener("click", () => {
  const now = Date.now();

  if (now - lastClick < 300) {
    cursor.classList.add("double");

    setTimeout(() => {
      cursor.classList.remove("double");
    }, 700);
  }

  lastClick = now;
});

// ============================================================
// CHROMADB MEMORY MANAGER — JavaScript
// ============================================================
// Uses existing server routes:
//   /api/memory/all
//   /api/memory/delete
//   /api/memory/update
//   /api/memory/create
//   /api/memory/search
// ============================================================

// ── State ────────────────────────────────────────────────────

/** Full dataset loaded from ChromaDB — array of row objects. */
let _memAllRows = [];

/** Currently visible rows (after filter/search). */
let _memVisibleRows = [];

/** Set of selected row IDs. */
let _memSelected = new Set();

/** Which column we are currently sorted by. */
let _memSortCol = "timestamp";
let _memSortDir = "desc"; // 'asc' | 'desc'

/** ID of the entry currently being edited (null = new entry). */
let _memEditingId = null;

/** Debounce timer for the filter input. */
let _memFilterTimer = null;

// ── Modal open / close ────────────────────────────────────────

/** Open the Memory Manager and load data. */
function openMemModal() {
  document.getElementById("mem-modal").classList.add("open");
  memLoad();
}

/** Close the Memory Manager. */
function closeMemModal() {
  document.getElementById("mem-modal").classList.remove("open");
}

/** Close if user clicks the dark backdrop (not the panel). */
function memCloseIfOutside(e) {
  if (e.target === document.getElementById("mem-modal")) closeMemModal();
}

// ── Load all memories from server ────────────────────────────

/**
 * Fetch all ChromaDB entries via /api/memory/all.
 * Calls the existing chroma_get_all() function through the new route.
 */
async function memLoad() {
  _memSetStatus("Loading from ChromaDB…");
  document.getElementById("mem-tbody").innerHTML =
    '<tr class="mem-state-row"><td colspan="7">Loading…</td></tr>';
  document.getElementById("mem-count-badge").textContent = "Loading…";

  try {
    const r = await fetch("/api/memory/all");
    const d = await r.json();

    if (!d.ok) {
      _memShowError("Server error: " + (d.error || "unknown"));
      return;
    }

    // Normalise each entry into a flat row object
    _memAllRows = (d.entries || []).map((e) => ({
      id: e.id || "",
      content: e.content || e.document || "",
      type: e.meta?.type || e.type || "general",
      timestamp: e.meta?.timestamp || e.timestamp || "",
      source: e.meta?.source || e.source || "",
      meta: e.meta || {},
    }));

    _memSelected.clear();
    _memApplySort(); // sort then render
    _memSetStatus(`Loaded ${_memAllRows.length} records`);
    document.getElementById("mem-count-badge").textContent = `${_memAllRows.length} memories`;
  } catch (err) {
    _memShowError("Could not reach server: " + err.message);
  }
}

// ── Render table ──────────────────────────────────────────────

/**
 * Render _memVisibleRows into the table body.
 * Respects current sort and filter state.
 */
function _memRender() {
  const tbody = document.getElementById("mem-tbody");
  const selCount = document.getElementById("mem-sel-count");
  tbody.innerHTML = "";

  if (!_memVisibleRows.length) {
    tbody.innerHTML = '<tr class="mem-state-row"><td colspan="7">No memories found.</td></tr>';
    _memUpdateCounts();
    return;
  }

  const frag = document.createDocumentFragment();
  _memVisibleRows.forEach((row, i) => {
    const tr = document.createElement("tr");
    if (_memSelected.has(row.id)) tr.classList.add("selected");

    // ── Checkbox ──────────────────────────────────────────
    const tdChk = document.createElement("td");
    const chk = document.createElement("input");
    chk.type = "checkbox";
    chk.className = "mem-checkbox";
    chk.checked = _memSelected.has(row.id);
    chk.dataset.id = row.id;
    chk.addEventListener("change", (e) => {
      e.stopPropagation();
      _memToggleRow(row.id, chk.checked, tr);
    });
    tdChk.appendChild(chk);

    // ── Type badge ────────────────────────────────────────
    const tdType = document.createElement("td");
    const typeSlug = (row.type || "general").replace(/[^a-z_]/g, "");
    tdType.innerHTML = `<span class="mem-type-badge mem-type-${typeSlug}">${escHtml(row.type || "?")}</span>`;

    // ── Content (truncated, click to expand) ──────────────
    const tdContent = document.createElement("td");
    tdContent.className = "mem-content-cell";
    tdContent.textContent = row.content;
    tdContent.title = "Click to expand/collapse";
    tdContent.addEventListener("click", (e) => {
      e.stopPropagation();
      tdContent.classList.toggle("expanded");
    });

    // ── Timestamp ─────────────────────────────────────────
    const tdTs = document.createElement("td");
    tdTs.style.fontSize = "0.75em";
    tdTs.style.color = "var(--muted)";
    tdTs.textContent = row.timestamp || "—";

    // ── Source ────────────────────────────────────────────
    const tdSrc = document.createElement("td");
    tdSrc.style.fontSize = "0.75em";
    tdSrc.style.color = "var(--muted)";
    tdSrc.textContent = row.source || "—";

    // ── Actions ───────────────────────────────────────────
    const tdAct = document.createElement("td");
    tdAct.style.whiteSpace = "nowrap";

    const editBtn = document.createElement("button");
    editBtn.className = "mem-row-btn";
    editBtn.textContent = "✏️";
    editBtn.title = "Edit this memory";
    editBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      openMemEdit(row);
    });

    const delBtn = document.createElement("button");
    delBtn.className = "mem-row-btn del";
    delBtn.textContent = "🗑";
    delBtn.title = "Delete this memory";
    delBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      memDeleteOne(row.id, tr);
    });

    tdAct.append(editBtn, delBtn);

    // ── ID (truncated, full in title tooltip) ─────────────
    const tdId = document.createElement("td");
    tdId.className = "mem-id-cell";
    tdId.textContent = row.id.slice(0, 8) + "…";
    tdId.title = row.id;

    // ── Row click = select / deselect ─────────────────────
    tr.addEventListener("click", () => {
      const nowSelected = !_memSelected.has(row.id);
      chk.checked = nowSelected;
      _memToggleRow(row.id, nowSelected, tr);
    });

    tr.append(tdChk, tdType, tdContent, tdTs, tdSrc, tdAct, tdId);
    frag.appendChild(tr);
  });

  tbody.appendChild(frag);
  _memUpdateCounts();
}

// ── Filter (client-side text filter) ─────────────────────────

/**
 * Filter _memAllRows by the search input text AND type dropdown.
 * This is a fast client-side filter — no server call.
 * For semantic (embedding) search, user clicks the Semantic button.
 */
function memFilterRows() {
  clearTimeout(_memFilterTimer);

  _memFilterTimer = setTimeout(() => {
    const q = (document.getElementById("mem-search-input").value || "").toLowerCase().trim();

    const type = document.getElementById("mem-type-filter").value;

    const filteredRows = _memAllRows.filter((row) => {
      const matchType = !type || row.type === type;

      const matchText =
        !q ||
        row.content.toLowerCase().includes(q) ||
        row.type.toLowerCase().includes(q) ||
        row.source.toLowerCase().includes(q) ||
        row.id.toLowerCase().includes(q);

      return matchType && matchText;
    });

    // -----------------------------------------------
    // LOCAL MATCH FOUND
    // -----------------------------------------------

    if (filteredRows.length > 0) {
      _memVisibleRows = filteredRows;

      _memApplySortToVisible();
      _memRender();

      return;
    }

    // -----------------------------------------------
    // NO LOCAL MATCH
    // FALL BACK TO SEMANTIC SEARCH
    // -----------------------------------------------

    if (q.length >= 3) {
      memSemanticSearch();
    }
  }, 120);
}

// ── Semantic search (calls /api/memory/search → chroma_recall_with_meta) ──

/**
 * Run a semantic similarity search using ChromaDB embeddings.
 * Maps to your existing chroma_recall_with_meta() function on the server.
 */
async function memSemanticSearch() {
  const q = (document.getElementById("mem-search-input").value || "").trim();
  if (!q) {
    _memSetStatus("Enter a query in the search box first.");
    return;
  }

  _memSetStatus(`Semantic search: "${q}"…`);
  try {
    const r = await fetch("/api/memory/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q, n: 20 }),
    });
    const d = await r.json();
    if (!d.ok) {
      _memSetStatus("Search error: " + (d.error || "?"));
      return;
    }

    _memVisibleRows = (d.results || []).map((e) => ({
      id: e.id || "",
      content: e.content || e.document || "",
      type: e.meta?.type || "general",
      timestamp: e.meta?.timestamp || "",
      source: e.meta?.source || "",
      meta: e.meta || {},
    }));

    _memRender();
    _memSetStatus(`Semantic search returned ${_memVisibleRows.length} results for "${q}"`);
  } catch (err) {
    _memSetStatus("Search failed: " + err.message);
  }
}

// ── Key handler for search input ──────────────────────────────

/** Enter → semantic search. Typing → client filter (handled by oninput). */
function memSearchKeydown(e) {
  if (e.key === "Enter") {
    e.preventDefault();
    memSemanticSearch();
  }
}

// ── Sorting ───────────────────────────────────────────────────

/** Called when user clicks a column header. Toggles asc/desc. */
function memSortByCol(col) {
  if (_memSortCol === col) {
    _memSortDir = _memSortDir === "asc" ? "desc" : "asc";
  } else {
    _memSortCol = col;
    _memSortDir = "asc";
  }
  _memApplySortToVisible();
  _memRender();
  _memUpdateSortArrows();
}

/** Called when the sort dropdown changes. */
function memApplySort() {
  const val = document.getElementById("mem-sort-select").value;
  const [col, dir] = val.split("-");
  _memSortCol = col;
  _memSortDir = dir;
  _memApplySort();
}

/** Sort _memAllRows then reset visible rows. */
function _memApplySort() {
  _memSortArr(_memAllRows);
  // Re-apply filter after sort
  memFilterRows();
}

/** Sort _memVisibleRows in place without touching filter. */
function _memApplySortToVisible() {
  _memSortArr(_memVisibleRows);
}

function _memSortArr(arr) {
  const dir = _memSortDir === "asc" ? 1 : -1;
  arr.sort((a, b) => {
    const av = (a[_memSortCol] || "").toString().toLowerCase();
    const bv = (b[_memSortCol] || "").toString().toLowerCase();
    return av < bv ? -dir : av > bv ? dir : 0;
  });
}

function _memUpdateSortArrows() {
  document.querySelectorAll("#mem-table th .sort-arrow").forEach((el) => {
    el.textContent = "↕";
    el.parentElement.classList.remove("sorted-asc", "sorted-desc");
  });
  // Find the th that matches our sort column (by onclick attribute)
  document.querySelectorAll("#mem-table th[onclick]").forEach((th) => {
    if (th.getAttribute("onclick")?.includes(`'${_memSortCol}'`)) {
      const arrow = th.querySelector(".sort-arrow");
      if (arrow) arrow.textContent = _memSortDir === "asc" ? "↑" : "↓";
      th.classList.add(_memSortDir === "asc" ? "sorted-asc" : "sorted-desc");
    }
  });
}

// ── Select / deselect ────────────────────────────────────────

function _memToggleRow(id, selected, tr) {
  if (selected) {
    _memSelected.add(id);
    tr.classList.add("selected");
  } else {
    _memSelected.delete(id);
    tr.classList.remove("selected");
  }
  _memUpdateCounts();
}

/** Select-all / deselect-all checkbox in header. */
function memToggleAll(chkAll) {
  const checkboxes = document.querySelectorAll("#mem-tbody .mem-checkbox");
  checkboxes.forEach((chk) => {
    chk.checked = chkAll.checked;
    const id = chk.dataset.id;
    const tr = chk.closest("tr");
    if (chkAll.checked) {
      _memSelected.add(id);
      tr.classList.add("selected");
    } else {
      _memSelected.delete(id);
      tr.classList.remove("selected");
    }
  });
  _memUpdateCounts();
}

// ── Delete ────────────────────────────────────────────────────

/**
 * Delete a single memory entry by ID.
 * Calls your existing /api/memory/delete route, which uses
 * your existing handle_memory_command_fn(confirmed=True).
 */
async function memDeleteOne(id, trEl) {
  if (!confirm("Delete this memory entry?")) return;
  try {
    const r = await fetch("/api/memory/delete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id }),
    });
    const d = await r.json();
    if (!d.ok && d.error) {
      _memSetStatus("Delete failed: " + d.error);
      return;
    }
    // Remove from local data & re-render (no need to reload all)
    _memAllRows = _memAllRows.filter((r) => r.id !== id);
    _memVisibleRows = _memVisibleRows.filter((r) => r.id !== id);
    _memSelected.delete(id);
    if (trEl) trEl.style.opacity = "0.3"; // visual feedback
    setTimeout(() => _memRender(), 300);
    _memSetStatus("Deleted 1 memory.");
    document.getElementById("mem-count-badge").textContent = `${_memAllRows.length} memories`;
  } catch (err) {
    _memSetStatus("Delete error: " + err.message);
  }
}

/**
 * Bulk-delete all currently selected rows.
 */
async function memDeleteSelected() {
  const ids = [..._memSelected];
  if (!ids.length) {
    _memSetStatus("No rows selected.");
    return;
  }
  if (!confirm(`Delete ${ids.length} selected memory entries? This cannot be undone.`)) return;

  let deleted = 0;
  for (const id of ids) {
    try {
      const r = await fetch("/api/memory/delete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
      });
      const d = await r.json();
      if (d.ok !== false) {
        deleted++;
        _memAllRows = _memAllRows.filter((r) => r.id !== id);
        _memVisibleRows = _memVisibleRows.filter((r) => r.id !== id);
      }
    } catch {}
  }

  _memSelected.clear();
  _memRender();
  _memSetStatus(`Deleted ${deleted} of ${ids.length} selected entries.`);
  document.getElementById("mem-count-badge").textContent = `${_memAllRows.length} memories`;
}

// ── Edit modal ────────────────────────────────────────────────

/** Open edit modal for an existing row. */
function openMemEdit(row) {
  _memEditingId = row.id;
  document.getElementById("mem-edit-title").textContent = "✏️ Edit Memory";
  document.getElementById("mem-edit-id-disp").textContent = "ID: " + row.id;
  document.getElementById("mem-edit-id-disp").style.display = "";
  document.getElementById("mem-edit-content").value = row.content;
  document.getElementById("mem-edit-type").value = row.type || "general";
  document.getElementById("mem-edit-source").value = row.source || "user";
  document.getElementById("mem-edit-err").textContent = "";
  document.getElementById("mem-save-btn").textContent = "Save Changes";
  document.getElementById("mem-edit-modal").classList.add("open");
  document.getElementById("mem-edit-content").focus();
}

/** Open edit modal as a blank Create form. */
function openMemCreate() {
  _memEditingId = null;
  document.getElementById("mem-edit-title").textContent = "+ New Memory";
  document.getElementById("mem-edit-id-disp").style.display = "none";
  document.getElementById("mem-edit-content").value = "";
  document.getElementById("mem-edit-type").value = "user_fact";
  document.getElementById("mem-edit-source").value = "user";
  document.getElementById("mem-edit-err").textContent = "";
  document.getElementById("mem-save-btn").textContent = "Create Memory";
  document.getElementById("mem-edit-modal").classList.add("open");
  document.getElementById("mem-edit-content").focus();
}

function closeMemEdit() {
  document.getElementById("mem-edit-modal").classList.remove("open");
  _memEditingId = null;
}

function memEditCloseIfOutside(e) {
  if (e.target === document.getElementById("mem-edit-modal")) closeMemEdit();
}

/**
 * Save an update or create a new memory.
 *
 * UPDATE  → calls /api/memory/update  (your existing route)
 *         which calls handle_memory_command_fn("memory edit <id> <text>")
 *         and also updates the type/source via /api/memory/update_meta (NEW)
 *
 * CREATE → calls /api/memory/create
 *          which calls chroma_store(text, {type, source})
 */
async function memSaveEdit() {
  const content = document.getElementById("mem-edit-content").value.trim();
  const type = document.getElementById("mem-edit-type").value;
  const source = document.getElementById("mem-edit-source").value.trim() || "user";
  const errEl = document.getElementById("mem-edit-err");
  errEl.textContent = "";

  if (!content) {
    errEl.textContent = "Content cannot be empty.";
    return;
  }

  try {
    if (_memEditingId) {
      // ── UPDATE existing entry ──────────────────────────
      const r = await fetch("/api/memory/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: _memEditingId, text: content, type, source }),
      });
      const d = await r.json();
      if (!d.ok) {
        errEl.textContent = d.error || "Save failed.";
        return;
      }

      // Update local data immediately — no need to reload all
      const idx = _memAllRows.findIndex((r) => r.id === _memEditingId);
      if (idx > -1) {
        _memAllRows[idx].content = content;
        _memAllRows[idx].type = type;
        _memAllRows[idx].source = source;
        _memAllRows[idx].meta.type = type;
        _memAllRows[idx].meta.source = source;
      }
      _memVisibleRows = _memVisibleRows.map((r) =>
        r.id === _memEditingId ? { ...r, content, type, source } : r,
      );
      _memRender();
      closeMemEdit();
      _memSetStatus("Memory updated.");
    } else {
      // ── CREATE new entry ───────────────────────────────
      const r = await fetch("/api/memory/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: content, type, source }),
      });
      const d = await r.json();
      if (!d.ok) {
        errEl.textContent = d.error || "Create failed.";
        return;
      }

      closeMemEdit();
      // Reload to get the real UUID assigned by ChromaDB
      await memLoad();
      _memSetStatus("New memory created.");
    }
  } catch (err) {
    errEl.textContent = "Error: " + err.message;
  }
}

// ── Export ────────────────────────────────────────────────────

/**
 * Export all (or visible) memories as a MySQL-compatible .sql file.
 * Format: DROP TABLE IF EXISTS + CREATE TABLE + INSERT rows.
 * You can paste this directly into MySQL/MariaDB or import via HeidiSQL/SQLyog.
 */
function memExportSQL() {
  const rows = _memVisibleRows.length ? _memVisibleRows : _memAllRows;
  if (!rows.length) {
    _memSetStatus("No data to export.");
    return;
  }

  const now = new Date().toISOString().replace("T", " ").slice(0, 19);
  const lines = [
    `-- Aetheraeon ChromaDB Memory Export`,
    `-- Generated: ${now}`,
    `-- Rows: ${rows.length}`,
    `--`,
    ``,
    `DROP TABLE IF EXISTS \`aetheraeon_memory_export\`;`,
    ``,
    `CREATE TABLE \`aetheraeon_memory_export\` (`,
    `  \`id\`        VARCHAR(36)  NOT NULL,`,
    `  \`content\`   LONGTEXT,`,
    `  \`type\`      VARCHAR(50),`,
    `  \`source\`    VARCHAR(50),`,
    `  \`timestamp\` VARCHAR(30),`,
    `  PRIMARY KEY (\`id\`)`,
    `) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;`,
    ``,
    `INSERT INTO \`aetheraeon_memory_export\``,
    `  (\`id\`, \`content\`, \`type\`, \`source\`, \`timestamp\`)`,
    `VALUES`,
  ];

  const sqlEsc = (s) => (s || "").replace(/\\/g, "\\\\").replace(/'/g, "\\'").replace(/\n/g, "\\n");

  const valueLines = rows.map((r, i) => {
    const comma = i < rows.length - 1 ? "," : ";";
    return `  ('${sqlEsc(r.id)}', '${sqlEsc(r.content)}', '${sqlEsc(r.type)}', '${sqlEsc(r.source)}', '${sqlEsc(r.timestamp)}')${comma}`;
  });

  lines.push(...valueLines);
  lines.push("");
  lines.push(`-- End of export (${rows.length} rows)`);

  const filename = `aetheraeon_memory_${Date.now()}.sql`;
  _memDownloadFile(lines.join("\n"), filename, "text/plain");
  _memSetStatus(`Exported ${rows.length} rows as ${filename}`);
}

/**
 * Export all (or visible) memories as a .json file.
 */
function memExportJSON() {
  const rows = _memVisibleRows.length ? _memVisibleRows : _memAllRows;
  if (!rows.length) {
    _memSetStatus("No data to export.");
    return;
  }

  const payload = {
    exported_at: new Date().toISOString(),
    count: rows.length,
    entries: rows.map((r) => ({
      id: r.id,
      content: r.content,
      type: r.type,
      source: r.source,
      timestamp: r.timestamp,
    })),
  };

  const filename = `aetheraeon_memory_${Date.now()}.json`;
  _memDownloadFile(JSON.stringify(payload, null, 2), filename, "application/json");
  _memSetStatus(`Exported ${rows.length} rows as ${filename}`);
}

async function memImportFile(event) {
  // ----------------------------------------------------------
  // IMPORT HANDLER
  // Reads a .json or .sql file exported by this same system
  // and calls /api/memory/create for each entry found.
  //
  // JSON FORMAT expected:
  //   { "entries": [ { "content": "...", "type": "...", "source": "..." } ] }
  //
  // SQL FORMAT expected:
  //   Lines that match:  ('uuid', 'content', 'type', 'source', 'timestamp'),
  //   Values are extracted by splitting on the INSERT VALUES pattern.
  //
  // Each entry is sent one at a time with a small delay to avoid
  // hammering the server.  Failures are counted and reported.
  // ----------------------------------------------------------
  const file = event.target.files[0];
  if (!file) return;

  // Reset the input so the same file can be re-imported if needed
  event.target.value = "";

  _memSetStatus("Reading import file...");

  const text = await file.text();
  const ext = file.name.split(".").pop().toLowerCase();

  let entries = [];

  if (ext === "json") {
    // ----------------------------------------------------------
    // JSON IMPORT
    // Parses the standard export format from memExportJSON().
    // ----------------------------------------------------------
    try {
      const parsed = JSON.parse(text);
      const raw = parsed.entries || parsed;
      if (!Array.isArray(raw)) {
        _memSetStatus("Import failed: JSON must contain an entries array.");
        return;
      }
      raw.forEach((e) => {
        const content = (e.content || e.document || "").trim();
        if (content) {
          entries.push({
            text: content,
            type: e.type || "general",
            source: e.source || "import",
          });
        }
      });
    } catch (err) {
      _memSetStatus("Import failed: invalid JSON -- " + err.message);
      return;
    }
  } else if (ext === "sql") {
    // ----------------------------------------------------------
    // SQL IMPORT
    // Parses INSERT VALUES lines from the export format of
    // memExportSQL().  Extracts content, type, source columns.
    // Each VALUES row format: ('id','content','type','source','ts')
    // ----------------------------------------------------------
    const valueRegex =
      /\(\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'\s*\)/g;
    let match;
    while ((match = valueRegex.exec(text)) !== null) {
      // match[1]=id, [2]=content, [3]=type, [4]=source, [5]=timestamp
      const content = match[2]
        .replace(/\\n/g, "\n")
        .replace(/\\'/g, "'")
        .replace(/\\\\/g, "\\")
        .trim();
      if (content) {
        entries.push({
          text: content,
          type: match[3] || "general",
          source: match[4] || "import",
        });
      }
    }
  } else {
    _memSetStatus("Import failed: only .json and .sql files are supported.");
    return;
  }

  if (!entries.length) {
    _memSetStatus("Import failed: no valid entries found in file.");
    return;
  }

  _memSetStatus(`Importing ${entries.length} entries...`);

  let success = 0;
  let failed = 0;

  for (const entry of entries) {
    try {
      const r = await fetch("/api/memory/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(entry),
      });
      const d = await r.json();
      if (d.ok || d.skipped) {
        success++;
      } else {
        failed++;
      }
    } catch {
      failed++;
    }

    // Small delay between requests to avoid server overload
    await new Promise((res) => setTimeout(res, 50));
  }

  _memSetStatus(`Import complete: ${success} added, ${failed} failed.`);

  // Reload table to show new entries
  await memLoad();
}

// ── UI helpers ────────────────────────────────────────────────

function _memSetStatus(msg) {
  const el = document.getElementById("mem-load-msg");
  if (el) el.textContent = msg;
}

function _memShowError(msg) {
  document.getElementById("mem-tbody").innerHTML =
    `<tr class="mem-state-row"><td colspan="7" style="color:var(--red)">${escHtml(msg)}</td></tr>`;
  document.getElementById("mem-count-badge").textContent = "Error";
  _memSetStatus(msg);
}

function _memUpdateCounts() {
  const total = _memAllRows.length;
  const visible = _memVisibleRows.length;
  const sel = _memSelected.size;

  document.getElementById("mem-total-count").textContent = `${total} total`;

  const visEl = document.getElementById("mem-visible-count");
  visEl.textContent = visible < total ? `${visible} shown` : "";

  const selEl = document.getElementById("mem-sel-count");
  const delSelBtn = document.getElementById("mem-del-sel-btn");
  if (sel > 0) {
    selEl.textContent = `${sel} selected`;
    selEl.style.display = "";
    if (delSelBtn) delSelBtn.style.display = "";
  } else {
    selEl.style.display = "none";
    if (delSelBtn) delSelBtn.style.display = "none";
  }

  // Sync select-all checkbox state
  const allChk = document.getElementById("mem-check-all");
  if (allChk) {
    allChk.checked = sel > 0 && sel === visible;
    allChk.indeterminate = sel > 0 && sel < visible;
  }
}

function _memDownloadFile(content, filename, mime) {
  const blob = new Blob([content], { type: mime });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
