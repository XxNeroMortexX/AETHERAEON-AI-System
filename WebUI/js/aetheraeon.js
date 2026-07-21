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

function setConversationMenuOpen(menu, open) {
  if (!menu) return;
  menu.style.display = open ? "block" : "none";
  const actions = menu.closest(".conv-actions, .pb-actions");
  actions?.classList.toggle("menu-open", open);
  actions?.querySelector(".conv-menu-btn")?.setAttribute(
    "aria-expanded",
    open ? "true" : "false",
  );
}

function closeConversationMenus(selector = ".conv-dropdown-menu") {
  let closed = false;
  document.querySelectorAll(selector).forEach((menu) => {
    if (menu.style.display === "block") closed = true;
    setConversationMenuOpen(menu, false);
  });
  return closed;
}

// ── Global Escape: close any open modal / search / menu ─────
document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape") return;

  const memoryEditor = document.getElementById("mem-edit-modal");
  if (memoryEditor?.classList.contains("open")) {
    e.preventDefault();
    e.stopPropagation();
    closeMemEdit();
    return;
  }
  const topModal = getTopOpenModal();
  if (topModal) {
    e.preventDefault();
    e.stopPropagation();
    if (topModal.id === "search-overlay") closeSearch();
    else closeModal(topModal.id);
    return;
  }
  const memoryManager = document.getElementById("mem-modal");
  if (memoryManager?.classList.contains("open")) {
    e.preventDefault();
    e.stopPropagation();
    closeMemModal();
    return;
  }

  const userMenu = document.getElementById("user-menu");
  if (userMenu?.classList.contains("open")) {
    e.preventDefault();
    e.stopPropagation();
    closeUserMenu();
    return;
  }

  if (slashCommandMenu && !slashCommandMenu.hidden) {
    e.preventDefault();
    e.stopPropagation();
    closeSlashCommandMenu();
    return;
  }

  if (closeConversationMenus(".pb-actions .conv-dropdown-menu")) {
    e.preventDefault();
    e.stopPropagation();
    return;
  }

  if (closeConversationMenus("#conv-list .conv-dropdown-menu")) {
    e.preventDefault();
    e.stopPropagation();
    return;
  }

  const sidebar = document.getElementById("sidebar");
  const sidebarVisible = sidebar && (
    sidebar.classList.contains("open") ||
    !sidebar.classList.contains("collapsed")
  );
  if (sidebarVisible) {
    e.preventDefault();
    e.stopPropagation();
    closeSidebarDrawer();
    return;
  }
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
let _searchCursor = null;
let _searchQuery = "";
let _searchRequestId = 0;
let _statusTimer = null;
let _sessionMonitorTimer = null;
let _backendAvailable = false;
let _greetingTimer = null;
let _greetingPrefetchTimer = null;
let _greetingLoadingTimer = null;
let _greetingCountdownTimer = null;
let _greetingRequest = 0;
let _greetingDeadline = 0;
let _greetingAbortController = null;
let _greetingOwnerConversationId = null;
let _nextGreeting = null;
let _activeGreetingText = "";
let _greetingPersonalityStyle = "balanced";
const _greetingUiPools = new Map();

// GREETING_COUNTDOWN_DEVELOPER_TOGGLE — set true to show the optional timer.
const SHOW_GREETING_COUNTDOWN = true;
const BACKEND_AVAILABILITY_INTERVAL_MS = 15000;
const _inFlightJsonGets = new Map();
let personalityTraits = [];
let personalityTraitHistory = [];
let personalityTraitCandidates = [];
let activeCandidateSubTab = "active";
let traitEditorState = null;
const modalNavigationStack = [];
let displayPreferences = {
  show_processing_details: true,
  processing_details_expanded: false,
  processing_details_mode: "compact",
  font_family: "mono",
  font_size: 18,
  chat_text_size: 16,
  button_size: 16,
  menu_size: 16,
  header_size: 18,
  code_size: 15,
  text_style: "normal",
  custom_text_color: "",
  custom_chat_color: "",
  custom_ui_color: "",
  custom_accent_color: "",
  custom_theme: {},
};

async function fetchJsonOnce(url, options = {}) {
  const method = String(options.method || "GET").toUpperCase();
  if (method !== "GET") {
    const response = await fetch(url, options);
    return { response, data: await response.json() };
  }

  const key = String(url);
  if (!_inFlightJsonGets.has(key)) {
    const request = (async () => {
      const response = await fetch(url, options);
      return { response, data: await response.json() };
    })();
    _inFlightJsonGets.set(key, request);
    request.finally(() => {
      if (_inFlightJsonGets.get(key) === request) _inFlightJsonGets.delete(key);
    }).catch(() => {});
  }
  return _inFlightJsonGets.get(key);
}

const FONT_SIZE_OPTIONS = [12, 13, 14, 15, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36, 40];
const THEME_COLOR_SECTIONS = {
  General: [["background", "Background", "--bg"], ["surface", "Surface / Panels", "--surface"], ["border", "Borders", "--border"], ["text", "Primary Text", "--text"], ["muted", "Secondary Text", "--muted"]],
  Chat: [["chat_background", "Chat Background", "--chat-bg"], ["user_message", "User Message", "--you-bubble"], ["ai_message", "AI Message", "--ai-bubble"], ["code_background", "Code Background", "--code-bg"]],
  Input: [["input_background", "Input Background", "--input-bg"], ["input_border", "Input Border", "--input-border"], ["placeholder", "Placeholder", "--placeholder"]],
  Buttons: [["button", "Button", "--button-bg"], ["button_hover", "Hover", "--button-hover"], ["button_active", "Active", "--button-active"], ["button_disabled", "Disabled", "--button-disabled"]],
  Navigation: [["sidebar", "Sidebar", "--sidebar-bg"], ["sidebar_hover", "Sidebar Hover", "--sidebar-hover"], ["menu", "Menu", "--menu-bg"], ["menu_hover", "Menu Hover", "--menu-hover"]],
  Accent: [["accent", "Accent", "--accent"], ["success", "Success", "--green"], ["warning", "Warning", "--orange"], ["error", "Error", "--red"], ["info", "Info", "--info"]],
  "Router Badge Colors": [["router_chat", "Chat", "--router-chat"], ["router_memory", "Memory", "--router-memory"], ["router_code", "Code", "--router-code"], ["router_personality", "Personality", "--router-personality"], ["router_web", "Web", "--router-web"], ["router_system", "System", "--router-system"]],
};
const THEME_COLOR_VARIABLES = Object.values(THEME_COLOR_SECTIONS).flat().map(([, , cssVar]) => cssVar);
let customThemeDirty = false;

// DOM shortcuts
const chat = document.getElementById("chat");
const input = document.getElementById("msg-input");
const sendBtn = document.getElementById("send-btn");
const slashCommandMenu = document.getElementById("slash-command-menu");
const choiceComposerNotice = document.getElementById("choice-composer-notice");
const choiceComposerCancel = document.getElementById("choice-composer-cancel");

const SLASH_COMMAND_CATALOG = Object.freeze([
  { command: "/help", description: "Show available commands" },
  { command: "/status", description: "Show system health" },
  { command: "/memory", description: "Manage memories" },
  { command: "/model", description: "Manage AI models" },
  { command: "/personality", description: "Manage AI traits" },
  { command: "/memory list", description: "Show stored memories", parent: "/memory" },
  {
    command: "/memory search",
    description: "Search memories",
    parent: "/memory",
    parameterHint: "Search text required",
    example: "/memory search project notes",
  },
  {
    command: "/memory delete",
    description: "Delete a memory entry",
    parent: "/memory",
    parameterHint: "Memory ID required",
    example: "/memory delete abc123",
  },
  { command: "/model show", description: "Show active AI models", parent: "/model" },
  { command: "/model list", description: "List installed AI models", parent: "/model" },
]);
let slashCommandSelection = -1;

// JS-010: Settings

async function applyTheme(theme, persist = true) {
  if (theme === "custom" && !Object.keys(displayPreferences.custom_theme || {}).length) {
    displayPreferences.custom_theme = currentThemePalette();
    renderCustomThemeEditor(displayPreferences.custom_theme);
  }
  document.documentElement.setAttribute("data-theme", theme);
  if (theme !== "custom") {
    THEME_COLOR_VARIABLES.forEach((name) =>
      document.documentElement.style.removeProperty(name),
    );
  } else {
    applyCustomPalette(displayPreferences.custom_theme || {});
  }
  // Update active theme button highlight
  document
    .querySelectorAll(".theme-btn")
    .forEach((b) => b.classList.toggle("active", b.dataset.theme === theme));
  if (persist && currentUser) {
    await fetch(apiUrl("settings"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ui_theme: theme }),
    }).catch(() => {});
  }
}

function applyDisplayPreferences(settings = {}) {
  displayPreferences = { ...displayPreferences, ...settings };
  const root = document.documentElement;
  const fonts = {
    system: "system-ui, sans-serif",
    sans: "Arial, Helvetica, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    mono: "Consolas, 'Courier New', monospace",
  };
  root.style.setProperty("--app-font-family", fonts[displayPreferences.font_family] || fonts.system);
  root.style.setProperty("--base-font-size", `${displayPreferences.font_size}px`);
  root.style.setProperty("--chat-text-size", `${displayPreferences.chat_text_size}px`);
  root.style.setProperty("--button-text-size", `${displayPreferences.button_size}px`);
  root.style.setProperty("--menu-text-size", `${displayPreferences.menu_size}px`);
  root.style.setProperty("--header-text-size", `${displayPreferences.header_size}px`);
  root.style.setProperty("--code-text-size", `${displayPreferences.code_size}px`);
  document.body.dataset.textStyle = displayPreferences.text_style || "normal";
  if (settings.ui_theme === "custom") {
    if (displayPreferences.custom_text_color) root.style.setProperty("--text", displayPreferences.custom_text_color);
    if (displayPreferences.custom_chat_color) root.style.setProperty("--you-bubble", displayPreferences.custom_chat_color);
    if (displayPreferences.custom_ui_color) root.style.setProperty("--surface", displayPreferences.custom_ui_color);
    if (displayPreferences.custom_accent_color) root.style.setProperty("--accent", displayPreferences.custom_accent_color);
    applyCustomPalette(displayPreferences.custom_theme || {});
  }
}

function applyCustomPalette(palette = {}) {
  Object.values(THEME_COLOR_SECTIONS).flat().forEach(([key, , cssVar]) => {
    if (/^#[0-9a-f]{6}$/i.test(palette[key] || "")) document.documentElement.style.setProperty(cssVar, palette[key]);
  });
}

function rgbToHex(color) {
  const values = String(color).match(/\d+/g);
  return values?.length >= 3 ? `#${values.slice(0, 3).map((n) => Number(n).toString(16).padStart(2, "0")).join("")}` : "#000000";
}

function resolvedThemeColor(cssVar) {
  const probe = document.createElement("span");
  probe.style.color = `var(${cssVar})`;
  probe.style.display = "none";
  document.body.appendChild(probe);
  const value = rgbToHex(getComputedStyle(probe).color);
  probe.remove();
  return value;
}

function currentThemePalette() {
  const palette = {};
  Object.values(THEME_COLOR_SECTIONS).flat().forEach(([key, , cssVar]) => { palette[key] = resolvedThemeColor(cssVar); });
  return palette;
}

function renderCustomThemeEditor(palette = {}) {
  const editor = document.getElementById("custom-theme-editor");
  if (!editor) return;
  editor.replaceChildren();
  const values = Object.keys(palette).length ? palette : currentThemePalette();
  Object.entries(THEME_COLOR_SECTIONS).forEach(([sectionName, fields]) => {
    const section = document.createElement("section");
    section.className = "theme-color-section";
    const heading = document.createElement("h4");
    heading.textContent = sectionName;
    const grid = document.createElement("div");
    grid.className = "theme-color-grid";
    fields.forEach(([key, label, cssVar]) => {
      const field = document.createElement("label");
      field.className = "theme-color-field";
      const name = document.createElement("span");
      name.textContent = label;
      const picker = document.createElement("input");
      picker.type = "color";
      picker.dataset.themeColor = key;
      picker.value = values[key] || resolvedThemeColor(cssVar);
      const output = document.createElement("output");
      output.className = "theme-color-value";
      output.value = picker.value;
      output.textContent = picker.value;
      picker.addEventListener("input", () => {
        output.value = picker.value;
        output.textContent = picker.value;
        displayPreferences.custom_theme = { ...currentThemePalette(), ...(displayPreferences.custom_theme || {}), [key]: picker.value };
        customThemeDirty = true;
        applyTheme("custom", false);
      });
      field.append(name, picker, output);
      grid.appendChild(field);
    });
    section.append(heading, grid);
    editor.appendChild(section);
  });
}

function initializeFontSelects() {
  document.querySelectorAll(".font-size-select").forEach((select) => {
    if (!select.options.length) FONT_SIZE_OPTIONS.forEach((size) => select.add(new Option(`${size} px`, size)));
  });
}

function resetFontSettings() {
  const defaults = { "display-font-size": 18, "display-chat-size": 16, "display-menu-size": 16, "display-header-size": 18, "display-code-size": 15 };
  Object.entries(defaults).forEach(([id, value]) => { document.getElementById(id).value = String(value); });
  applyDisplayPreferences({ font_size: 18, chat_text_size: 16, button_size: 16, menu_size: 16, header_size: 18, code_size: 15 });
}

function syncProcessingSettingsState() {
  const enabled = !!document.getElementById("show-processing-details")?.checked;
  const group = document.getElementById("processing-dependent-settings");
  if (group) group.disabled = !enabled;
}

async function loadTheme() {
  try {
    const { data: d } = await fetchJsonOnce(apiUrl("settings"));
    if (d.ok && d.settings) {
      _greetingPersonalityStyle = d.settings.personality_style || "balanced";
      await applyTheme(d.settings.ui_theme || "dark", false);
      applyDisplayPreferences(d.settings);
      renderCustomThemeEditor(d.settings.custom_theme || {});
    } else {
      await applyTheme("dark", false);
    }
  } catch {
    applyTheme("dark", false);
  }
}

// JS-003: API Communication
// API calls remain colocated with their owning UI feature to preserve existing behavior.

// JS-004: Authentication

let currentTab = "login";
let passwordResetToken = "";

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

  submitButton.title = "Aetheraeon Core is unavailable";
  statusElement.textContent = "Aetheraeon Core Offline. The frontend remains available.";
  statusElement.classList.add("visible");
}

function setDeploymentHealth({ aiCore = false, database = null } = {}) {
  const setState = (id, label, state) => {
    const element = document.getElementById(id);
    if (!element) return;
    element.textContent = label;
    element.classList.remove("online", "offline", "checking", "unknown");
    element.classList.add(state);
  };
  setState("health-frontend", "Frontend Online", "online");
  setState(
    "health-ai-core",
    aiCore ? "Aetheraeon Core Online" : "Aetheraeon Core Offline",
    aiCore ? "online" : "offline",
  );
  setState(
    "health-database",
    database === true ? "Database Online" : database === false ? "Database Offline" : "Database Unknown",
    database === true ? "online" : database === false ? "offline" : "unknown",
  );
}

async function checkProductionDatabaseHealth() {
  try {
    const { response, data } = await fetchJsonOnce(apiUrl("db_health.php"), {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    if (
      !response.ok ||
      !data ||
      Object.keys(data).length !== 1 ||
      (data.database !== "Online" && data.database !== "Offline")
    ) {
      return { production: false, database: null };
    }
    return { production: true, database: data.database === "Online" };
  } catch {
    return { production: false, database: null };
  }
}

function deploymentBasePath() {
  const match = String(window.location.pathname || "").match(/^\/Aetheraeon(?=\/|$)/i);
  return match ? match[0] : "";
}

function isProductionDeployment() {
  return deploymentBasePath() !== "";
}

function apiUrl(path = "") {
  let normalized = String(path).trim().replace(/^\/+/, "");
  if (normalized === "api") normalized = "";
  if (normalized.startsWith("api/")) normalized = normalized.slice(4);
  const apiBase = `${deploymentBasePath()}/api`;
  return normalized ? `${apiBase}/${normalized}` : apiBase;
}

// ------------------------------------------------------
// Function: checkBackendAvailability()
// Purpose: Performs the deployment-appropriate lightweight reachability check.
// Called by: startBackendAvailabilityMonitoring() and its recovery timer.
// Updates: Login availability through setBackendAvailability().
// ------------------------------------------------------
async function checkBackendAvailability() {
  return refreshStatus();
}

// ------------------------------------------------------
// Function: startBackendAvailabilityMonitoring()
// Purpose: Checks the backend on page load and periodically restores login when it returns.
// Called by: Frontend initialization.
// Updates: Backend availability timer.
// ------------------------------------------------------
function startBackendAvailabilityMonitoring() {
  refreshStatus();

  if (!_statusTimer) {
    _statusTimer = setInterval(
      refreshStatus,
      BACKEND_AVAILABILITY_INTERVAL_MS,
    );
  }
}

function switchTab(tab) {
  currentTab = tab;
  const isReg = tab === "register";
  document.getElementById("tab-login").classList.toggle("active", !isReg);
  document.getElementById("tab-register").classList.toggle("active", isReg);
  document.getElementById("reg-fullname-field").style.display = isReg ? "flex" : "none";
  document.getElementById("reg-username-field").style.display = isReg ? "flex" : "none";
  const identifierInput = document.getElementById("auth-email");
  document.querySelector('label[for="auth-email"]').textContent = isReg ? "EMAIL" : "USERNAME OR EMAIL";
  identifierInput.type = isReg ? "email" : "text";
  identifierInput.placeholder = isReg ? "user@example.com" : "username or user@example.com";
  identifierInput.autocomplete = isReg ? "email" : "username";
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
  const identifier = document.getElementById("auth-email").value.trim();
  const password = document.getElementById("auth-password").value;
  const errEl = document.getElementById("auth-err");
  errEl.textContent = "";

  if (!_backendAvailable) {
    setBackendAvailability(false);
    return;
  }

  if (!identifier || !password) {
    errEl.textContent = "Username/email and password required.";
    return;
  }
  if (password.length < 4) {
    errEl.textContent = "Password must be 4+ characters.";
    return;
  }

  let endpoint = apiUrl("login");
  let payload = { identifier, password };

  if (currentTab === "register") {
    const email = identifier.toLowerCase();
    const fullName = document.getElementById("auth-fullname").value.trim();
    const username = document.getElementById("auth-username").value.trim();
    if (!fullName || !username) {
      errEl.textContent = "Full name and username required.";
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
      errEl.textContent = "Enter a valid email.";
      return;
    }
    endpoint = apiUrl("register");
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
    bootApp(data.user, data);
  } catch (e) {
    errEl.textContent = "Connection error: " + e.message;
  }
}

async function checkSession() {
  try {
    const r = await fetch(apiUrl("session"));
    const d = await r.json();
    if (d.ok) bootApp(d.user, d);
    else if (d.code === "forced_logout") showForcedLogout(d.error);
  } catch {}
}

function openForgotPassword() {
  passwordResetToken = "";
  document.getElementById("password-reset-title").textContent = "Forgot Password";
  document.getElementById("password-reset-description").textContent = "Enter your email to request a reset link.";
  document.getElementById("reset-email-field").style.display = "flex";
  document.getElementById("reset-password-field").style.display = "none";
  document.getElementById("password-reset-submit").textContent = "Send Reset Link";
  document.getElementById("password-reset-submit").onclick = requestPasswordReset;
  document.getElementById("password-reset-error").textContent = "";
  document.getElementById("password-reset-ok").textContent = "";
  openModal("password-reset-modal");
}

async function requestPasswordReset() {
  const email = document.getElementById("reset-email").value.trim().toLowerCase();
  const errorElement = document.getElementById("password-reset-error");
  const output = document.getElementById("password-reset-ok");
  errorElement.textContent = "";
  output.textContent = "";
  try {
    const response = await fetch(apiUrl("password/forgot"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    });
    const data = await response.json();
    output.textContent = data.message || "If an account exists, a reset email has been sent.";
  } catch (error) {
    errorElement.textContent = "Unable to submit the request.";
  }
}

function openResetPassword(token) {
  passwordResetToken = token;
  document.getElementById("password-reset-title").textContent = "Create New Password";
  document.getElementById("password-reset-description").textContent = "Choose a new password of at least 8 characters.";
  document.getElementById("reset-email-field").style.display = "none";
  document.getElementById("reset-password-field").style.display = "flex";
  document.getElementById("password-reset-submit").textContent = "Update Password";
  document.getElementById("password-reset-submit").onclick = completePasswordReset;
  openModal("password-reset-modal");
}

async function completePasswordReset() {
  const password = document.getElementById("reset-new-password").value;
  const errorElement = document.getElementById("password-reset-error");
  const output = document.getElementById("password-reset-ok");
  errorElement.textContent = "";
  output.textContent = "";
  if (password.length < 8) {
    errorElement.textContent = "Password must be at least 8 characters.";
    return;
  }
  const response = await fetch(apiUrl("password/reset"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token: passwordResetToken, password }),
  });
  const data = await response.json();
  if (!data.ok) {
    errorElement.textContent = data.error || "Reset failed.";
    return;
  }
  output.textContent = data.message;
  history.replaceState({}, "", location.pathname);
  passwordResetToken = "";
}

function closePasswordReset() {
  closeModal("password-reset-modal");
  if (passwordResetToken) history.replaceState({}, "", location.pathname);
  passwordResetToken = "";
}

async function logout() {
  closeUserMenu();
  await fetch(apiUrl("logout"), { method: "POST" }).catch(() => {});
  currentUser = null;
  personalityTraits = [];
  personalityTraitCandidates = [];
  personalityTraitHistory = [];
  traitEditorState = null;
  modalNavigationStack.length = 0;
  _greetingUiPools.clear();
  conversations = {};
  activeConvId = null;
  if (_sessionMonitorTimer) {
    clearInterval(_sessionMonitorTimer);
    _sessionMonitorTimer = null;
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

function showForcedLogout(message = "You have been signed out by an administrator.") {
  currentUser = null;
  conversations = {};
  activeConvId = null;
  if (_sessionMonitorTimer) clearInterval(_sessionMonitorTimer);
  _sessionMonitorTimer = null;
  stopGreetingRotation();
  chat.innerHTML = "";
  document.getElementById("app").style.display = "none";
  document.getElementById("login-screen").style.display = "flex";
  document.getElementById("auth-password").value = "";
  document.getElementById("auth-err").textContent = message;
}

async function monitorSession() {
  try {
    const response = await fetch(apiUrl("session"), { cache: "no-store" });
    const data = await response.json();
    if (data.code === "forced_logout") showForcedLogout(data.error);
    else if (data.ok) updateMaintenanceBanner(!!data.maintenance_mode, data);
  } catch {}
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

function hasAdministrativeRole(role) {
  return role === "owner" || role === "admin";
}

async function openAdminCenter() {
  closeUserMenu();
  if (!hasAdministrativeRole(currentUser?.role)) return;
  openModal("admin-center-modal");
  document.getElementById("admin-center-error").textContent = "";
  await Promise.all([
    loadAdminUsers(), loadAdminAudit(), loadAdminDiagnostics(), loadDeploymentSettings(),
  ]);
}

async function loadAdminUsers() {
  const response = await fetch(apiUrl("admin/users"));
  const data = await response.json();
  if (!data.ok) throw new Error(data.error || "Unable to load users");
  const body = document.getElementById("admin-users-body");
  body.replaceChildren();
  data.users.forEach((user) => body.appendChild(buildAdminUserRow(user)));
}

function buildAdminUserRow(user) {
  const row = document.createElement("tr");
  row.dataset.userId = user.id;

  const identity = document.createElement("td");
  const username = document.createElement("input");
  username.className = "admin-username";
  username.value = user.username || "";
  const fullName = document.createElement("input");
  fullName.className = "admin-full-name";
  fullName.value = user.full_name || "";
  identity.append(username, fullName);

  const emailCell = document.createElement("td");
  const email = document.createElement("input");
  email.className = "admin-email";
  email.type = "email";
  email.value = user.email || "";
  emailCell.appendChild(email);

  const roleCell = document.createElement("td");
  const role = document.createElement("select");
  role.className = "admin-role";
  role.add(new Option("User", "user"));
  role.add(new Option("Admin", "admin"));
  if (user.role === "owner") {
    role.add(new Option("Owner", "owner"));
    role.disabled = true;
  }
  role.value = user.role || "user";
  roleCell.appendChild(role);

  const status = document.createElement("td");
  status.className = user.is_active ? (user.is_online ? "status-online" : "status-offline") : "status-disabled";
  status.textContent = user.is_active ? (user.is_online ? "Online" : "Offline") : "Disabled";

  const activity = document.createElement("td");
  activity.textContent = user.last_activity || user.last_login || "Never";
  const created = document.createElement("td");
  created.textContent = user.created_at || "—";

  const actionsCell = document.createElement("td");
  const actions = document.createElement("div");
  actions.className = "admin-actions";
  const actionDefinitions = [
    ["Save", () => adminSaveUser(user.id, row)],
    ["View", () => enterAdminView(user.id)],
    ["Reset Password", () => adminUserAction(user.id, "reset_password")],
    [user.is_active ? "Disable" : "Enable", () => adminSetActive(user.id, !user.is_active)],
    ["Delete", () => adminDeleteUser(user.id, user.username)],
  ];
  actionDefinitions.forEach(([label, handler]) => {
    const button = document.createElement("button");
    button.textContent = label;
    button.onclick = handler;
    actions.appendChild(button);
  });
  actionsCell.appendChild(actions);
  row.append(identity, emailCell, roleCell, status, activity, created, actionsCell);
  return row;
}

async function adminSaveUser(userId, row) {
  const changes = {
    username: row.querySelector(".admin-username").value.trim(),
    full_name: row.querySelector(".admin-full-name").value.trim(),
    email: row.querySelector(".admin-email").value.trim(),
  };
  const selectedRole = row.querySelector(".admin-role").value;
  if (selectedRole !== "owner") changes.role = selectedRole;
  await adminUserAction(userId, "update", changes);
}

async function adminSetActive(userId, enabled) {
  if (!confirm(`${enabled ? "Enable" : "Disable"} this account?`)) return;
  await adminUserAction(userId, "update", { is_active: enabled });
}

async function adminDeleteUser(userId, username) {
  await adminUserAction(userId, "delete");
}

async function adminUserAction(userId, action, changes = {}) {
  const errorElement = document.getElementById("admin-center-error");
  errorElement.textContent = "";
  try {
    const response = await fetch(apiUrl(`admin/users/${userId}`), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action, ...changes }),
    });
    const data = await response.json();
    if (!data.ok) throw new Error(data.error || "Admin action failed");
    showToast(data.message || "Admin action completed");
    await Promise.all([loadAdminUsers(), loadAdminAudit()]);
  } catch (error) {
    errorElement.textContent = error.message;
  }
}

async function loadAdminAudit() {
  const response = await fetch(apiUrl("admin/audit?limit=100"));
  const data = await response.json();
  const list = document.getElementById("admin-audit-list");
  if (!data.ok) {
    list.textContent = data.error || "Audit log unavailable";
    return;
  }
  list.textContent = data.logs.map((entry) =>
    `${entry.created_at} — ${entry.admin_username || "deleted admin"} ${entry.action} ${entry.target_username || ""}${entry.details ? ` — ${entry.details}` : ""}`,
  ).join("\n") || "No audit entries.";
}

async function loadAdminDiagnostics() {
  const response = await fetch(apiUrl("admin/diagnostics"));
  const data = await response.json();
  document.getElementById("admin-diagnostics").textContent = data.ok
    ? `Version ${data.version} · ${data.active_admins} active admin(s) · Services: ${Object.keys(data.services || {}).join(", ") || "none"}`
    : data.error || "Diagnostics unavailable";
  if (data.ok) {
    document.getElementById("maintenance-mode-toggle").checked = !!data.maintenance_mode;
    updateMaintenanceBanner(!!data.maintenance_mode, { administrator: currentUser });
  }
}

function renderDeploymentSettings(data) {
  if (!data?.ok) return;
  const current = document.getElementById("deployment-current-mode");
  const configured = document.getElementById("deployment-configured-mode");
  const select = document.getElementById("deployment-mode-select");
  const notice = document.getElementById("deployment-restart-notice");
  if (current) current.textContent = titleCaseProcessingValue(data.current_mode);
  if (configured) configured.textContent = titleCaseProcessingValue(data.configured_mode);
  if (select) select.value = data.configured_mode || "development";
  if (notice) notice.hidden = !data.restart_required;
}

async function loadDeploymentSettings() {
  const response = await fetch(apiUrl("admin/deployment"), { cache: "no-store" });
  const data = await response.json();
  if (!data.ok) throw new Error(data.error || "Deployment settings unavailable");
  renderDeploymentSettings(data);
}

async function saveDeploymentMode() {
  if (!hasAdministrativeRole(currentUser?.role)) return;
  const select = document.getElementById("deployment-mode-select");
  const button = document.getElementById("deployment-mode-save");
  const mode = select?.value;
  const confirmed = confirm(
    `Configure ${titleCaseProcessingValue(mode)} deployment mode? Runtime behavior will not change until Aetheraeon is restarted.`,
  );
  if (!confirmed) return;
  button.disabled = true;
  try {
    const response = await fetch(apiUrl("admin/deployment"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode, confirmed: true }),
    });
    const data = await response.json();
    if (!data.ok) throw new Error(data.error || "Unable to save deployment mode");
    renderDeploymentSettings(data);
    showToast(data.message || "Deployment configuration saved. Restart required.");
    await loadAdminAudit();
  } catch (error) {
    document.getElementById("admin-center-error").textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

function updateMaintenanceBanner(enabled, sessionData = {}) {
  const actorIsAdmin = hasAdministrativeRole(currentUser?.role) ||
    hasAdministrativeRole(sessionData.administrator?.role);
  document.getElementById("maintenance-banner")?.classList.toggle("visible", !!enabled && actorIsAdmin);
}

async function setMaintenanceMode(enabled) {
  const toggle = document.getElementById("maintenance-mode-toggle");
  toggle.disabled = true;
  try {
    const response = await fetch(apiUrl("admin/system-settings"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ maintenance_mode: enabled }),
    });
    const data = await response.json();
    if (!data.ok) throw new Error(data.error || "Unable to update Maintenance Mode");
    toggle.checked = !!data.maintenance_mode;
    updateMaintenanceBanner(!!data.maintenance_mode, { administrator: currentUser });
    showToast(`Maintenance Mode ${data.maintenance_mode ? "enabled" : "disabled"}`);
    await loadAdminAudit();
  } catch (error) {
    toggle.checked = !enabled;
    document.getElementById("admin-center-error").textContent = error.message;
  } finally {
    toggle.disabled = false;
  }
}

async function forceLogoutAllUsers() {
  if (!confirm("This will immediately sign out all connected users.")) return;
  const keepCurrent = document.getElementById("keep-admin-session").checked;
  const response = await fetch(apiUrl("admin/sessions/force-logout"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keep_current_session: keepCurrent }),
  });
  const data = await response.json();
  if (!data.ok) {
    document.getElementById("admin-center-error").textContent = data.error || "Unable to invalidate sessions";
    return;
  }
  if (!keepCurrent) {
    showForcedLogout();
    return;
  }
  showToast(data.message || "All active sessions have been invalidated.");
  await loadAdminAudit();
}

async function enterAdminView(userId) {
  const response = await fetch(apiUrl("admin/view-user"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId }),
  });
  const data = await response.json();
  if (!data.ok) {
    document.getElementById("admin-center-error").textContent = data.error || "Unable to enter view";
    return;
  }
  window.location.reload();
}

async function exitAdminView() {
  const response = await fetch(apiUrl("admin/view-user/exit"), { method: "POST" });
  const data = await response.json();
  if (data.ok) window.location.reload();
  else showToast(data.error || "Unable to exit administrator view", "var(--red)");
}

document.addEventListener("click", (e) => {
  if (!document.getElementById("user-menu").contains(e.target)) closeUserMenu();
});

// ────────────────────────────────────────────────────────────
// SETTINGS MODAL
// ────────────────────────────────────────────────────────────

function openSettings(panel = "themes") {
  closeUserMenu();
  initializeFontSelects();
  loadSettingsData();
  switchSettingsTab(panel);
  openModal("settings-modal");
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
    const [settingsResult, modelsResult] = await Promise.all([
      fetchJsonOnce(apiUrl("settings")),
      fetchJsonOnce(apiUrl("models/installed")),
    ]);
    const settingsData = settingsResult.data;
    const modelsData = modelsResult.data;
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
    document.getElementById("display-font-family").value = s.font_family || "mono";
    document.getElementById("display-text-style").value = s.text_style || "normal";
    document.getElementById("display-font-size").value = s.font_size || 18;
    document.getElementById("display-chat-size").value = s.chat_text_size || 16;
    document.getElementById("display-menu-size").value = s.menu_size || 16;
    document.getElementById("display-header-size").value = s.header_size || 18;
    document.getElementById("display-code-size").value = s.code_size || 15;
    document.getElementById("show-processing-details").checked = !!s.show_processing_details;
    document.getElementById("processing-expanded").checked = !!s.processing_details_expanded;
    document.getElementById("processing-mode").value = s.processing_details_mode || "compact";
    syncProcessingSettingsState();
    renderCustomThemeEditor(s.custom_theme || {});
    customThemeDirty = false;
    applyDisplayPreferences(s);
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
    const r = await fetch(apiUrl("account/username"), {
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
    const r = await fetch(apiUrl("account/password"), {
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
  try {
    const r = await fetch(apiUrl("account/delete"), {
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
    const r = await fetch(apiUrl("settings"), {
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

async function saveDisplaySettings() {
  const output = document.getElementById("display-settings-ok");
  output.textContent = "";
  const customTheme = {};
  document.querySelectorAll("[data-theme-color]").forEach((picker) => { customTheme[picker.dataset.themeColor] = picker.value; });
  const selectedTheme = document.documentElement.getAttribute("data-theme") || "dark";
  const settings = {
    ui_theme: customThemeDirty ? "custom" : selectedTheme,
    font_family: document.getElementById("display-font-family").value,
    text_style: document.getElementById("display-text-style").value,
    font_size: Number(document.getElementById("display-font-size").value),
    chat_text_size: Number(document.getElementById("display-chat-size").value),
    button_size: Number(document.getElementById("display-menu-size").value),
    menu_size: Number(document.getElementById("display-menu-size").value),
    header_size: Number(document.getElementById("display-header-size").value),
    code_size: Number(document.getElementById("display-code-size").value),
    custom_theme: customTheme,
    show_processing_details: document.getElementById("show-processing-details").checked ? 1 : 0,
    processing_details_expanded: document.getElementById("processing-expanded").checked ? 1 : 0,
    processing_details_mode: document.getElementById("processing-mode").value,
  };
  try {
    const response = await fetch(apiUrl("settings"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    const data = await response.json();
    if (!data.ok) throw new Error(data.error || "Save failed");
    applyTheme(data.settings.ui_theme || settings.ui_theme, false);
    applyDisplayPreferences(data.settings);
    customThemeDirty = false;
    output.textContent = "Theme and display settings saved.";
  } catch (error) {
    output.textContent = error.message;
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
    const r = await fetch(apiUrl("settings"), {
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
  const { data: d } = await fetchJsonOnce(apiUrl("personality/traits"));
  personalityTraits = d.ok ? d.traits : [];
  personalityTraitCandidates = d.ok ? (d.aetheraeon_trait_candidates || []) : [];
  renderPersonalityTraits();
}

const traitStrengthLabels = {
  1: "Very Weak", 2: "Weak", 3: "Mild", 4: "Moderate", 5: "Balanced",
  6: "Noticeable", 7: "Strong", 8: "Very Strong", 9: "Dominant",
  10: "Core Trait",
};

const traitCategoryOptions = [
  "communication", "conversation", "teaching", "reasoning", "humor",
  "greeting", "technical", "creativity", "personality", "memory",
];

function traitStrengthLevel(item) {
  const level = Number(item?.strength_level || Math.round(Number(item?.strength || 0) / 10));
  return Math.max(1, Math.min(10, level || 1));
}

function traitStrengthDisplay(item) {
  const level = traitStrengthLevel(item);
  return `${level} - ${item?.strength_label || traitStrengthLabels[level]}`;
}

function traitDetail(label, value) {
  const line = document.createElement("div");
  const key = document.createElement("strong");
  key.textContent = label + ": ";
  line.append(key, document.createTextNode(value ?? "Not provided"));
  return line;
}

function traitCreatedDisplay(item) {
  return item?.created_at ? new Date(item.created_at).toLocaleString() : "Unknown";
}

function traitSourceDisplay(item) {
  if (item?.owner === "aetheraeon") {
    return item.created_by === "system" ? "System Default" : "Aetheraeon Evolution";
  }
  return item?.created_by === "aetheraeon" ? "AI suggestion approved by user" : "User";
}

function traitConfidenceBar(value) {
  const confidence = Math.max(0, Math.min(100, Number(value) || 0));
  const wrapper = document.createElement("div");
  wrapper.className = "trait-confidence";
  const track = document.createElement("div");
  track.className = "trait-confidence-track";
  track.setAttribute("role", "progressbar");
  track.setAttribute("aria-label", "Candidate confidence");
  track.setAttribute("aria-valuemin", "0");
  track.setAttribute("aria-valuemax", "100");
  track.setAttribute("aria-valuenow", String(confidence));
  const fill = document.createElement("div");
  fill.className = "trait-confidence-fill";
  fill.style.width = `${confidence}%`;
  const output = document.createElement("span");
  output.className = "trait-confidence-value";
  output.textContent = `${confidence}%`;
  track.appendChild(fill);
  wrapper.append(track, output);
  return wrapper;
}

function traitAction(label, handler, danger = false) {
  const button = document.createElement("button");
  button.className = `modal-btn${danger ? " danger" : ""}`;
  button.textContent = label;
  button.onclick = handler;
  return button;
}

function renderPersonalityTraits() {
  const preview = document.getElementById("personality-traits-preview");
  preview.textContent = personalityTraits.length
    ? personalityTraits.map((item) => item.name || item.trait).join(", ")
    : "No structured traits.";

  const userList = document.getElementById("user-personality-traits-list");
  const aiList = document.getElementById("aetheraeon-personality-traits-list");
  const candidateList = document.getElementById("aetheraeon-trait-candidates-list");
  const promotedCandidateList = document.getElementById("aetheraeon-promoted-candidates-list");
  if (!userList || !aiList || !candidateList || !promotedCandidateList) return;
  userList.replaceChildren();
  aiList.replaceChildren();
  candidateList.replaceChildren();
  promotedCandidateList.replaceChildren();

  const userTraits = personalityTraits.filter((item) => item.owner === "user");
  const aiTraits = personalityTraits.filter((item) => item.owner === "aetheraeon");
  if (!userTraits.length) userList.textContent = "No user traits yet.";
  if (!aiTraits.length) aiList.textContent = "No Aetheraeon traits yet.";

  userTraits.forEach((item) => {
    const card = document.createElement("article");
    card.className = "trait-card";
    const title = document.createElement("h4");
    title.textContent = item.name || item.trait;
    const details = document.createElement("div");
    details.className = "trait-card-details";
    details.append(
      traitDetail("Description", item.description),
      traitDetail("Category", item.category),
      traitDetail("Strength", traitStrengthDisplay(item)),
      traitDetail("Created", traitCreatedDisplay(item)),
      traitDetail("Source", traitSourceDisplay(item)),
    );
    const actions = document.createElement("div");
    actions.className = "trait-card-actions";
    actions.append(
      traitAction("Edit", () => editPersonalityTrait(item)),
      traitAction("Delete", () => removePersonalityTrait(item.id), true),
    );
    card.append(title, details, actions);
    userList.appendChild(card);
  });

  aiTraits.forEach((item) => {
    const card = document.createElement("article");
    card.className = "trait-card";
    const title = document.createElement("h4");
    title.textContent = item.name || item.trait;
    const details = document.createElement("div");
    details.className = "trait-card-details";
    details.append(
      traitDetail("Description", item.description),
      traitDetail("Category", item.category),
      traitDetail("Strength", traitStrengthDisplay(item)),
      traitDetail("Created", item.created_at ? new Date(item.created_at).toLocaleString() : "Unknown"),
      traitDetail("Why it exists", item.reason_created),
      traitDetail("Influenced by", item.influence_summary),
    );
    const latestFeedback = String(item.latest_feedback?.correction || "").trim();
    if (latestFeedback) {
      details.append(traitDetail("Latest User Feedback", `“${latestFeedback}”`));
    }
    const actions = document.createElement("div");
    actions.className = "trait-card-actions";
    actions.append(
      traitAction("Correct this trait", () => correctPersonalityTrait(item)),
      traitAction("Remove", () => removePersonalityTrait(item.id), true),
    );
    card.append(title, details, actions);
    aiList.appendChild(card);
  });

  const activeCandidates = personalityTraitCandidates.filter(
    (item) => item.status !== "promoted",
  );
  const promotedCandidates = personalityTraitCandidates.filter(
    (item) => item.status === "promoted",
  );
  if (!activeCandidates.length) candidateList.textContent = "No active candidates.";
  if (!promotedCandidates.length) {
    promotedCandidateList.textContent = "No candidates have been promoted yet.";
  }

  const renderCandidateCard = (item, promoted = false) => {
      const card = document.createElement("article");
      card.className = `trait-card trait-candidate-card${promoted ? " trait-candidate-card-promoted" : ""}`;
      const title = document.createElement("h4");
      title.textContent = item.name;
      const events = Array.isArray(item.influencing_events) ? item.influencing_events : [];
      card.append(
        title,
        traitDetail("Description", item.description),
        traitDetail("Category", item.category),
        traitConfidenceBar(promoted ? 100 : item.confidence_score),
        traitDetail("Evidence", `${Number(item.evidence_count || 0)} interactions`),
        traitDetail("First detected", item.first_detected_at ? new Date(item.first_detected_at).toLocaleString() : "Unknown"),
        traitDetail("Last detected", item.last_detected_at ? new Date(item.last_detected_at).toLocaleString() : "Unknown"),
        traitDetail("Reason", item.reason_detected),
        traitDetail("Status", promoted ? "Promoted to Aetheraeon Trait" : "Observing"),
        ...(promoted
          ? [
              traitDetail("Created trait", item.promoted_trait_name || "Unknown"),
              traitDetail("Promotion date", item.promoted_at ? new Date(item.promoted_at).toLocaleString() : "Unknown"),
            ]
          : []),
        traitDetail("Influencing events", events.map((event) => event.summary).join("; ") || "Not provided"),
      );
      return card;
  };

  activeCandidates.forEach((item) => candidateList.appendChild(renderCandidateCard(item)));
  promotedCandidates.forEach((item) => {
    promotedCandidateList.appendChild(renderCandidateCard(item, true));
  });
  showCandidateSubTab(activeCandidateSubTab);
}

function showCandidateSubTab(tab = "active") {
  const selectedTab = tab === "promoted" ? "promoted" : "active";
  activeCandidateSubTab = selectedTab;
  ["active", "promoted"].forEach((name) => {
    const selected = name === selectedTab;
    const panel = document.getElementById(`${name}-candidates-panel`);
    const button = document.getElementById(`${name}-candidates-tab`);
    panel?.classList.toggle("hidden", !selected);
    if (panel) {
      panel.hidden = !selected;
      panel.setAttribute("aria-hidden", selected ? "false" : "true");
    }
    button?.classList.toggle("active", selected);
    button?.setAttribute("aria-selected", selected ? "true" : "false");
  });
}

async function openPersonalityManager() {
  await loadPersonalityTraits();
  document.getElementById("trait-manager-err").textContent = "";
  showTraitTab("user");
  openModal("personality-manager-modal");
}

async function showTraitTab(tab) {
  ["user", "aetheraeon", "candidates", "history"].forEach((name) => {
    const panelId = name === "history"
      ? "trait-history-panel"
      : name === "candidates" ? "trait-candidates-panel" : `${name}-traits-panel`;
    const tabId = name === "history"
      ? "trait-history-tab"
      : name === "candidates" ? "trait-candidates-tab" : `${name}-traits-tab`;
    const panel = document.getElementById(panelId);
    panel?.classList.toggle("hidden", name !== tab);
    if (panel) {
      panel.hidden = name !== tab;
      panel.setAttribute("aria-hidden", name === tab ? "false" : "true");
    }
    document.getElementById(tabId)?.classList.toggle("active", name === tab);
  });
  if (tab === "candidates") showCandidateSubTab(activeCandidateSubTab);
  if (tab === "history") await loadPersonalityTraitHistory();
}

function openTraitEditor(mode, item = null) {
  const feedbackMode = mode === "feedback";
  const rawCategory = String(item?.category || "communication").trim();
  const category = rawCategory.toLowerCase();
  const standardCategory = traitCategoryOptions.includes(category);
  traitEditorState = {
    mode,
    item,
    initial: feedbackMode ? {
      correction: String(item?.latest_feedback?.correction || ""),
    } : {
      name: item?.name || item?.trait || "",
      description: item?.description || "",
      category: standardCategory ? category : "other",
      customCategory: standardCategory ? "" : rawCategory,
      strength: item ? traitStrengthLevel(item) : 5,
    },
  };
  document.getElementById("trait-editor-title").textContent = feedbackMode
    ? "Correct Aetheraeon Trait"
    : mode === "edit" ? "Edit User Trait" : "Add User Trait";
  document.getElementById("trait-editor-fields").hidden = feedbackMode;
  document.getElementById("trait-editor-fields").classList.toggle("hidden", feedbackMode);
  document.getElementById("trait-feedback-fields").hidden = !feedbackMode;
  document.getElementById("trait-feedback-fields").classList.toggle("hidden", !feedbackMode);
  document.getElementById("trait-feedback-target").textContent = feedbackMode
    ? `${item?.name || item?.trait}: ${item?.description || "No description provided."}`
    : "";
  document.getElementById("trait-editor-error").textContent = "";
  resetTraitEditorModal();
  openModal("trait-editor-modal");
  setTimeout(() => document.getElementById(
    feedbackMode ? "trait-feedback-correction" : "trait-editor-name",
  )?.focus(), 0);
}

function resetTraitEditorModal() {
  if (!traitEditorState) return;
  const initial = traitEditorState.initial;
  document.getElementById("trait-editor-error").textContent = "";
  if (traitEditorState.mode === "feedback") {
    document.getElementById("trait-feedback-correction").value = initial.correction;
    return;
  }
  document.getElementById("trait-editor-name").value = initial.name;
  document.getElementById("trait-editor-description").value = initial.description;
  document.getElementById("trait-editor-category").value = initial.category;
  document.getElementById("trait-editor-custom-category").value = initial.customCategory;
  document.getElementById("trait-editor-strength").value = String(initial.strength);
  syncTraitCategoryCustom();
}

function syncTraitCategoryCustom() {
  const custom = document.getElementById("trait-editor-category").value === "other";
  const wrapper = document.getElementById("trait-editor-custom-category-wrap");
  wrapper.hidden = !custom;
  wrapper.classList.toggle("hidden", !custom);
}

async function saveTraitEditorModal() {
  if (!traitEditorState) return;
  const err = document.getElementById("trait-editor-error");
  err.textContent = "";
  let endpoint = apiUrl("personality/traits");
  let method = traitEditorState.mode === "edit" ? "PUT" : "POST";
  let payload;
  if (traitEditorState.mode === "feedback") {
    const correction = document.getElementById("trait-feedback-correction").value.trim();
    if (!correction) {
      err.textContent = "Enter correction feedback.";
      return;
    }
    endpoint = apiUrl("personality/traits/correct");
    payload = { id: traitEditorState.item.id, correction };
  } else {
    const name = document.getElementById("trait-editor-name").value.trim();
    const selectedCategory = document.getElementById("trait-editor-category").value;
    const category = selectedCategory === "other"
      ? document.getElementById("trait-editor-custom-category").value.trim()
      : selectedCategory;
    if (!name) {
      err.textContent = "Enter a trait name.";
      return;
    }
    if (!category) {
      err.textContent = "Enter a custom category.";
      return;
    }
    payload = {
      ...(traitEditorState.mode === "edit" ? { id: traitEditorState.item.id } : {}),
      name,
      description: document.getElementById("trait-editor-description").value.trim(),
      category,
      strength_level: Number(document.getElementById("trait-editor-strength").value),
    };
  }
  try {
    const response = await fetch(endpoint, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!data.ok) {
      err.textContent = data.error || "Unable to save trait.";
      return;
    }
    closeModal("trait-editor-modal");
    await loadPersonalityTraits();
    if (traitEditorState.mode === "feedback") showToast("Trait correction saved.");
    traitEditorState = null;
  } catch (error) {
    err.textContent = `Error: ${error.message}`;
  }
}

function addPersonalityTrait() { openTraitEditor("create"); }
function editPersonalityTrait(item) { openTraitEditor("edit", item); }
function correctPersonalityTrait(item) { openTraitEditor("feedback", item); }

async function loadPersonalityTraitHistory() {
  const { data: d } = await fetchJsonOnce(apiUrl("personality/traits/history"));
  personalityTraitHistory = d.ok ? d.history : [];
  const list = document.getElementById("personality-trait-history");
  list.replaceChildren();
  if (!personalityTraitHistory.length) {
    list.textContent = "No trait history yet.";
    return;
  }
  personalityTraitHistory.forEach((item) => {
    const card = document.createElement("article");
    card.className = "trait-card trait-history-card";
    const title = document.createElement("h4");
    const ownerLabel = item.owner === "candidate"
      ? "CANDIDATE"
      : item.owner === "aetheraeon" ? "AETHERAEON" : "USER";
    title.textContent = `${ownerLabel} ${String(item.action || "updated").toUpperCase()}`;
    card.append(
      title,
      traitDetail("Name", item.trait_name),
      traitDetail("Ownership", ownerLabel),
      traitDetail("Date", item.created_at ? new Date(item.created_at).toLocaleString() : "Unknown"),
      traitDetail("Action", item.action),
      traitDetail("Reason", item.reason),
      traitDetail("Source", item.source_label || item.source),
    );
    card.setAttribute("role", "button");
    card.tabIndex = 0;
    const openRelated = () => openTraitHistoryItem(item);
    card.onclick = openRelated;
    card.onkeydown = (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        openRelated();
      }
    };
    list.appendChild(card);
  });
}

function openTraitHistoryItem(item) {
  if (item.owner === "candidate") {
    showTraitTab("candidates");
    return;
  }
  const trait = personalityTraits.find((entry) => entry.id === item.trait_id);
  if (!trait) {
    showToast("This trait is no longer active.");
    return;
  }
  if (item.owner === "aetheraeon") correctPersonalityTrait(trait);
  else editPersonalityTrait(trait);
}

async function removePersonalityTrait(id) {
  const promotedCandidateIds = new Set(
    personalityTraitCandidates
      .filter((item) => Number(item.promoted_trait_id) === Number(id))
      .map((item) => String(item.id)),
  );
  const r = await fetch(apiUrl("personality/traits"), {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  });
  const d = await r.json();
  if (!d.ok) {
    document.getElementById("trait-manager-err").textContent = d.error || "Failed.";
    return;
  }

  personalityTraits = personalityTraits.filter((item) => Number(item.id) !== Number(id));
  personalityTraitCandidates = personalityTraitCandidates.filter(
    (item) => !promotedCandidateIds.has(String(item.id)),
  );
  personalityTraitHistory = personalityTraitHistory.filter((item) => (
    !promotedCandidateIds.has(String(item.candidate_id))
    && !(Number(item.trait_id) === Number(id) && item.source === "aetheraeon_evolution")
  ));
  renderPersonalityTraits();

  await Promise.all([loadPersonalityTraits(), loadPersonalityTraitHistory()]);
  showToast("Trait removed");
}

async function saveWebSearchToggle(enabled) {
  // ----------------------------------------------------------
  // Save the web search preference to the server.
  // This writes to user_settings.web_search_enabled in MariaDB.
  // The value is read by api_chat on every request.
  // ----------------------------------------------------------
  try {
    const r = await fetch(apiUrl("settings"), {
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
    const { data: d } = await fetchJsonOnce(apiUrl("settings"));
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
    const { data: d } = await fetchJsonOnce(apiUrl("conversations"));
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
    const response = await fetch(apiUrl("conversations/create"), {
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
  clearChoiceComposerNotice();
  stopGreetingRotation();
  activeConvId = cid;
  document.getElementById("conv-title-display").textContent = conversations[cid].name || "Untitled";
  renderSidebar();
  await loadAndRenderMessages(cid);
}

function stopGreetingRotation() {
  _greetingRequest++;
  const controller = _greetingAbortController;
  _greetingAbortController = null;
  _greetingOwnerConversationId = null;
  if (controller && !controller.signal.aborted) controller.abort();
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

function beginGreetingRequest() {
  const previousController = _greetingAbortController;
  if (previousController && !previousController.signal.aborted) previousController.abort();

  const request = {
    controller: new AbortController(),
    conversationId: activeConvId,
    requestId: ++_greetingRequest,
  };
  _greetingAbortController = request.controller;
  _greetingOwnerConversationId = request.conversationId;
  return request;
}

function isCurrentGreetingRequest(request) {
  return request.requestId === _greetingRequest
    && request.controller === _greetingAbortController
    && request.conversationId === _greetingOwnerConversationId
    && request.conversationId === activeConvId;
}

function finishGreetingRequest(request) {
  if (request.controller !== _greetingAbortController) return;
  _greetingAbortController = null;
  _greetingOwnerConversationId = null;
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
function renderTemporaryGreeting(text, loading = false, processing = null) {
  if (activeConvId || input.value.trim()) return;
  const visibleText = String(text || "").trim() || (loading ? "Aetheraeon is thinking..." : "");
  if (!visibleText) return;
  const panel = document.createElement("div");
  const effect = loading ? "greeting-loading" : selectGreetingEffect();
  const renderedAt = Date.now();
  panel.className = `msg msg-ai temporary-greeting${loading ? " loading" : ""}`;
  panel.dataset.greetingState = loading ? "loading" : "ready";
  setMessageExportData(panel, "ai", visibleText, "chat", renderedAt, !loading);
  const bubble = document.createElement("div");
  bubble.className = `bubble greeting-body ${effect}${loading ? " typing" : ""}`;
  bubble.textContent = visibleText;
  if (!loading) _activeGreetingText = visibleText;
  panel.appendChild(createMessageMeta("ai", "chat", renderedAt));
  panel.appendChild(bubble);
  const processingDetails = !loading && processing
    ? buildProcessingDetails(processing, "greeting")
    : null;
  if (processingDetails) panel.appendChild(processingDetails);
  if (SHOW_GREETING_COUNTDOWN && !loading) {
    const countdown = document.createElement("div");
    countdown.className = "greeting-countdown";
    panel.appendChild(countdown);
  }
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
  _greetingLoadingTimer = setInterval(showGreetingLoadingState, 7700);
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
  stopGreetingRotation();
  if (!chat.querySelector(".temporary-greeting")) return;
  chat.innerHTML = "";
}

async function refreshTemporaryGreeting() {
  if (activeConvId || input.value.trim()) return;
  const request = beginGreetingRequest();
  startGreetingLoadingMessages();

  try {
    const response = await fetch(apiUrl("greeting"), { signal: request.controller.signal });
    const data = await response.json().catch(() => ({}));
    if (!isCurrentGreetingRequest(request) || activeConvId || input.value.trim()) return;
    if (!response.ok || !data.ok || !data.greeting) {
      ensureGreetingLoadingState();
      _greetingTimer = setTimeout(refreshTemporaryGreeting, 10000);
      return;
    }
    stopGreetingLoadingMessages();
    renderTemporaryGreeting(data.greeting, false, data.processing);
    scheduleGreetingRotation(data.refresh_seconds, data.prefetch_lead_seconds);
  } catch (error) {
    if (error?.name === "AbortError") return;
    if (isCurrentGreetingRequest(request) && !activeConvId && !input.value.trim()) {
      ensureGreetingLoadingState();
      _greetingTimer = setTimeout(refreshTemporaryGreeting, 10000);
    }
  } finally {
    finishGreetingRequest(request);
  }
}

async function prefetchTemporaryGreeting() {
  if (activeConvId || input.value.trim()) return;
  const request = beginGreetingRequest();
  try {
    const response = await fetch(apiUrl("greeting?refresh=1"), { signal: request.controller.signal });
    const data = await response.json().catch(() => ({}));
    if (!isCurrentGreetingRequest(request) || activeConvId || input.value.trim()) return;
    if (!response.ok || !data.ok || !data.greeting) throw new Error("Greeting unavailable");
    if (data.source === "fallback" && chat.querySelector(".temporary-greeting:not(.loading)")) {
      _greetingPrefetchTimer = setTimeout(prefetchTemporaryGreeting, 5000);
      return;
    }
    _nextGreeting = data;
    if (Date.now() >= _greetingDeadline) swapPrefetchedGreeting();
  } catch (error) {
    if (error?.name === "AbortError") return;
    if (isCurrentGreetingRequest(request) && !activeConvId && !input.value.trim()) {
      _greetingPrefetchTimer = setTimeout(prefetchTemporaryGreeting, 5000);
    }
  } finally {
    finishGreetingRequest(request);
  }
}

function swapPrefetchedGreeting() {
  if (activeConvId || input.value.trim()) return;
  if (!_nextGreeting) {
    _greetingTimer = setTimeout(swapPrefetchedGreeting, 1000);
    return;
  }
  const next = _nextGreeting;
  renderTemporaryGreeting(next.greeting, false, next.processing);
  scheduleGreetingRotation(next.refresh_seconds, next.prefetch_lead_seconds);
}

function showNoConversationState() {
  clearChoiceComposerNotice();
  activeConvId = null;
  document.getElementById("conv-title-display").textContent = "";
  renderSidebar();
  stopGreetingRotation();
  void refreshTemporaryGreeting();
}

function toggleConversation(cid) {
  if (activeConvId === cid) {
    showNoConversationState();
    return;
  }
  activateConv(cid);
}

async function loadAndRenderMessages(cid) {
  clearChoiceComposerNotice();
  chat.innerHTML = "";
  try {
    const { data: d } = await fetchJsonOnce(apiUrl(`messages?conversation_id=${encodeURIComponent(cid)}`));
    if (activeConvId !== cid) return;
    if (d.ok && d.messages) {
      d.messages.forEach((m) => {
        addMsgDOM(
          m.role === "user" ? "you" : "ai",
          m.content || "",
          m.tool_used || "chat",
          m.created_at || Date.now(),
          m.processing || null,
          m.message_id || null,
          m.response_metadata || null,
        );
      });
    }
  } catch {}
  scrollBottom();
}

async function deleteConv(cid) {
  const backup = conversations[cid];

  try {
    // ── 1. DELETE ON SERVER FIRST ──
    const r = await fetch(apiUrl("conversations/delete"), {
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

    showToast("Conversation deleted");

    // ── 4. SAFE ACTIVATION ──
  } catch (err) {
    // ── rollback if anything fails ──
    if (backup) {
      conversations[cid] = backup;
      renderSidebar();
    }

    console.error("Delete failed:", err);
    showToast(err.message || "Unable to delete conversation.", "var(--red)");
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
    const res = await fetch(apiUrl("conversations/rename"), {
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
    await fetch(apiUrl("conversations/pin"), {
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
      menuBtn.setAttribute("aria-haspopup", "menu");
      menuBtn.setAttribute("aria-expanded", "false");
      menuBtn.textContent = "⋮";

      // DROPDOWN MENU
      const menu = document.createElement("div");
      menu.className = "conv-dropdown-menu";
      menu.style.display = "none";
      menu.setAttribute("role", "menu");

      // HELPER
      function addMenuItem(label, fn) {
        const btn = document.createElement("button");

        btn.className = "conv-dropdown-item";
        btn.textContent = label;

        btn.onclick = (e) => {
          e.stopPropagation();

          setConversationMenuOpen(menu, false);

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
        closeConversationMenus();

        // TOGGLE CURRENT
        setConversationMenuOpen(menu, !isOpen);
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
  closeConversationMenus();
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
    const r = await fetch(apiUrl("playbooks"));
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
      menuBtn.setAttribute("aria-haspopup", "menu");
      menuBtn.setAttribute("aria-expanded", "false");
      menuBtn.textContent = "⋮";

      // MENU
      const menu = document.createElement("div");
      menu.className = "conv-dropdown-menu";
      menu.style.display = "none";
      menu.setAttribute("role", "menu");

      // HELPER
      function addMenuItem(label, fn, extraClass = "") {
        const btn = document.createElement("button");

        btn.className = "conv-dropdown-item " + extraClass;
        btn.textContent = label;

        btn.onclick = (e) => {
          e.stopPropagation();

          setConversationMenuOpen(menu, false);

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
          fetch(apiUrl("playbooks/delete"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: pb.id }),
          })
            .then((response) => {
              if (!response.ok) throw new Error("Unable to delete playbook.");
              showToast("Playbook deleted");
              return renderPlaybooks();
            })
            .catch((error) => showToast(error.message, "var(--red)"));
        },
        "danger",
      );

      // TOGGLE MENU
      menuBtn.onclick = (e) => {
        e.stopPropagation();

        const isOpen = menu.style.display === "block";

        closeConversationMenus();

        setConversationMenuOpen(menu, !isOpen);
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
    let url = apiUrl("playbooks/create");
    let body = { name, content };
    if (_editingPbId) {
      url = apiUrl("playbooks/update");
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
      const langHint = nlIndex > -1 ? inner.slice(0, nlIndex).trim() : "";
      const rawCode = nlIndex > -1 ? inner.slice(nlIndex + 1) : inner;
      // The newline immediately before a closing Markdown fence is structural,
      // not part of the snippet users expect to copy or download.
      const code = rawCode.replace(/\r\n/g, "\n").replace(/\n$/, "");
      const lang = detectCodeLanguage(code, langHint);

      const pre = document.createElement("pre");
      pre.className = "code-block";
      pre.dataset.language = lang;
      const toolbar = document.createElement("div");
      toolbar.className = "code-toolbar";
      const languageLabel = document.createElement("span");
      languageLabel.className = "code-language";
      languageLabel.textContent = lang;
      const code_el = document.createElement("code");
      code_el.className = `language-${lang}`;
      code.split("\n").forEach((line, index) => {
        const row = document.createElement("span");
        row.className = "code-line";
        const number = document.createElement("span");
        number.className = "code-line-number";
        number.setAttribute("aria-hidden", "true");
        number.textContent = String(index + 1);
        const content = document.createElement("span");
        content.className = "code-line-content";
        content.appendChild(highlightCodeLine(line, lang));
        row.append(number, content);
        code_el.appendChild(row);
      });

      const copyBtn = document.createElement("button");
      copyBtn.className = "code-copy-btn";
      copyBtn.textContent = "📋 Copy Code";
      copyBtn.onclick = () => {
        copyToClipboard(code);
        showToast("Code copied!");
      };
      const downloadBtn = document.createElement("button");
      downloadBtn.className = "code-download-btn";
      downloadBtn.textContent = "⬇ Download";
      downloadBtn.onclick = () => downloadFile(code, `aetheraeon-code.${codeExtension(lang)}`);
      toolbar.append(languageLabel, copyBtn, downloadBtn);
      pre.append(toolbar, code_el);
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

function buildProcessingDetails(processing, route) {
  if (!displayPreferences.show_processing_details) return null;
  const data = processing || {};
  // Older persisted messages may contain heuristic percentages from the
  // retired processing implementation. Never present those as telemetry.
  const legacyEstimated = data.estimated_influence === true;
  const details = document.createElement("details");
  details.className = `processing-details processing-${displayPreferences.processing_details_mode}`;
  details.open = !!displayPreferences.processing_details_expanded;
  const summary = document.createElement("summary");
  summary.textContent = "AI processing details";
  details.appendChild(summary);

  const fields = [
    ["Intent classification", titleCaseProcessingValue(data.intent || route || "None")],
    ["Routing confidence", percentOrZero(legacyEstimated ? 0 : data.routing_confidence)],
    ["Sources / Tools Used", Array.isArray(data.sources_tools) && data.sources_tools.length ? data.sources_tools.map(titleCaseProcessingValue).join(", ") : (route ? titleCaseProcessingValue(route) : "None")],
  ];
  if (displayPreferences.processing_details_mode === "detailed") {
    fields.splice(0, 0,
      ["Analytical reasoning influence", percentOrZero(legacyEstimated ? 0 : data.analytical_influence)],
      ["Creative reasoning influence", percentOrZero(legacyEstimated ? 0 : data.creative_influence)],
      ["Short-term memory usage", percentOrZero(legacyEstimated ? 0 : data.short_term_memory_usage)],
      ["Long-term memory influence", percentOrZero(legacyEstimated ? 0 : data.long_term_memory_usage)],
      ["Long-term memory search", legacyEstimated ? "Not Used" : (data.memory_search_status || "Not Used")],
      ["Memory results found", legacyEstimated ? 0 : (Number(data.memories_found) || 0)],
      ["Memories injected", legacyEstimated ? 0 : (Number(data.memories_injected) || 0)],
    );
    if (!legacyEstimated && data.memory_retrieval_attempted) {
      fields.push(
        ["Long-term memory retrieval", data.memory_retrieval_completed ? "Completed" : "Failed"],
        ["Memory retrieval method", data.memory_retrieval_method || "Unspecified"],
      );
    }
    fields.push(["Personality influence", titleCaseProcessingValue(
      legacyEstimated ? "Not Used" : (data.personality_influence || "Not Used")
    )]);
    if (!legacyEstimated && data.cognition_bypassed) {
      fields.push([
        "Cognition pipeline",
        data.cognition_bypass_reason || "Intentionally bypassed",
      ]);
    }
    if (!legacyEstimated && data.conversation_history_searched) {
      fields.push(
        ["Conversation history search", "Completed"],
        ["Conversation history items found", Number(data.conversation_history_items_found) || 0],
        ["Conversation history references injected", Number(data.conversation_history_items_injected) || 0],
      );
    }
    if (!legacyEstimated && data.greeting_source) {
      fields.push([
        "Greeting generation",
        data.generation_cached
          ? `Cached ${titleCaseProcessingValue(data.greeting_source)}`
          : titleCaseProcessingValue(data.greeting_source),
      ]);
    }
    const personalityDebug = !legacyEstimated && data.personality_debug;
    if (personalityDebug && typeof personalityDebug === "object") {
      fields.push(
        ["Base Settings", formatPersonalityDebugSettings(personalityDebug.base_settings)],
        ["Trait Modifiers", formatPersonalityTraitModifiers(personalityDebug.trait_modifiers)],
        ["Effective Personality", formatPersonalityDebugSettings(personalityDebug.effective_personality)],
      );
    }
    if (!legacyEstimated && data.memory_operation && data.memory_operation !== "Not Used") {
      fields.push(
        ["Memory operation", data.memory_operation],
        ["Destination", data.memory_destination || "Not Used"],
        ["Write attempted", data.memory_write_attempted ? "Yes" : "No"],
        ["Write result", data.memory_write_result || "Not Used"],
      );
    }
    const semanticShadow = !legacyEstimated && data.semantic_memory_shadow;
    if (semanticShadow && semanticShadow.mode === "shadow") {
      const semantic = semanticShadow.semantic || {};
      const legacy = semanticShadow.legacy || {};
      const candidates = semantic.candidate_counts || {};
      const selected = semantic.selected_counts || {};
      const compression = semantic.compression || {};
      fields.push(
        ["Semantic shadow retrieval", semantic.retrieval_method || "Not Used"],
        ["Legacy retrieval method", legacy.retrieval_method || "Not Used"],
        ["Shadow candidates found", `Chroma: ${Number(candidates.chromadb) || 0}; Conversations: ${Number(candidates.conversation_history) || 0}`],
        ["Shadow candidates selected", `Chroma: ${Number(selected.chromadb) || 0}; Conversations: ${Number(selected.conversation_history) || 0}`],
        ["Shadow compressed items", Number(compression.compressed_item_count) || 0],
        ["Shadow injected items", Number(selected.injected_context) || 0],
      );
    }
    const semanticProduction = !legacyEstimated && data.semantic_memory_production;
    if (semanticProduction && semanticProduction.mode === "production") {
      const candidates = semanticProduction.candidate_counts || {};
      const selected = semanticProduction.selected_counts || {};
      const rotation = semanticProduction.rotation_cycles || {};
      const compression = semanticProduction.compression || {};
      fields.push(
        ["Memory Retrieval Mode", semanticProduction.retrieval_method || "Production Semantic Memory Coordinator"],
        ["Semantic candidates found", `Chroma: ${Number(candidates.chromadb) || 0}; Conversations: ${Number(candidates.conversation_history) || 0}`],
        ["Semantic candidates selected", `Chroma: ${Number(selected.chromadb) || 0}; Conversations: ${Number(selected.conversation_history) || 0}`],
        ["Memory rotation cycle", `Chroma: ${Number(rotation.chromadb) || 0}; Conversations: ${Number(rotation.conversation_history) || 0}`],
        ["Compressed context items", Number(compression.compressed_item_count) || 0],
        ["Injected context items", Number(selected.injected_context) || 0],
      );
      if (semanticProduction.fallback_used) {
        fields.push(["Semantic memory fallback", "Legacy retrieval used"]);
      }
    }
  }
  const grid = document.createElement("div");
  grid.className = "processing-grid";
  fields.forEach(([label, value]) => {
    const row = document.createElement("div");
    row.className = "processing-row";
    const key = document.createElement("span");
    key.textContent = label;
    const output = document.createElement("span");
    output.textContent = String(value);
    row.append(key, output);
    grid.appendChild(row);
  });
  details.appendChild(grid);
  return details;
}

function formatPersonalityDebugSettings(settings) {
  if (!settings || typeof settings !== "object") return "Not Used";
  const labels = {
    style: "Style", tone: "Tone", verbosity: "Verbosity",
    humor: "Humor", greeting_style: "Greeting",
  };
  const values = Object.entries(labels)
    .filter(([key]) => settings[key] !== undefined && settings[key] !== null)
    .map(([key, label]) => `${label}: ${titleCaseProcessingValue(settings[key])}`);
  return values.join("; ") || "Not Used";
}

function formatPersonalityTraitModifiers(modifiers) {
  if (!Array.isArray(modifiers) || !modifiers.length) return "None";
  return modifiers
    .map((item) => `${item.trait || "Trait"} ${item.modifier || ""}`.trim())
    .join("; ");
}

function percentOrZero(value) {
  const number = Number(value);
  return Number.isFinite(number) ? `${Math.max(0, Math.min(100, Math.round(number)))}%` : "0%";
}

function titleCaseProcessingValue(value) {
  return String(value || "None").replace(/[_-]+/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function detectCodeLanguage(code, hint = "") {
  const aliases = { py: "python", js: "javascript", ts: "typescript", sh: "shell", ps1: "powershell" };
  const normalizedHint = String(hint).trim().toLowerCase();
  if (normalizedHint) return aliases[normalizedHint] || normalizedHint.replace(/[^a-z0-9+#-]/g, "") || "text";
  if (/^\s*(from\s+\w+\s+import|import\s+\w+|def\s+\w+|class\s+\w+)/m.test(code)) return "python";
  if (/\b(interface|type)\s+\w+|:\s*(string|number|boolean)\b/.test(code)) return "typescript";
  if (/\b(const|let|var|function|document\.|console\.)\b/.test(code)) return "javascript";
  if (/<[a-z][\s\S]*>/i.test(code)) return "html";
  if (/^\s*[.#]?[\w-]+\s*\{[\s\S]*:[^;]+;/m.test(code)) return "css";
  if (/^\s*(SELECT|INSERT|UPDATE|DELETE|CREATE)\b/im.test(code)) return "sql";
  if (/^\s*(Get-|Set-|New-|\$[A-Za-z_])/m.test(code)) return "powershell";
  return "text";
}

function highlightCodeLine(line, language) {
  const fragment = document.createDocumentFragment();
  const keywords = {
    python: "and|as|assert|async|await|break|class|continue|def|del|elif|else|except|False|finally|for|from|if|import|in|is|lambda|None|not|or|pass|raise|return|True|try|while|with|yield",
    javascript: "async|await|break|case|catch|class|const|continue|default|delete|else|export|extends|false|finally|for|from|function|if|import|in|instanceof|let|new|null|of|return|static|switch|this|throw|true|try|typeof|undefined|var|while",
    typescript: "async|await|boolean|class|const|enum|export|extends|false|from|function|if|implements|import|interface|let|namespace|never|new|null|number|private|protected|public|readonly|return|static|string|true|type|undefined|unknown|void",
    sql: "ALTER|AND|AS|BY|CREATE|DELETE|DROP|FROM|GROUP|HAVING|INSERT|INTO|JOIN|LIMIT|NOT|NULL|ON|OR|ORDER|SELECT|SET|TABLE|UPDATE|VALUES|WHERE",
  };
  const keywordPattern = keywords[language] || "";
  const tokenPattern = new RegExp(`("(?:\\\\.|[^"\\\\])*"|'(?:\\\\.|[^'\\\\])*'|\\b(?:${keywordPattern || "(?!)"})\\b|\\b\\d+(?:\\.\\d+)?\\b|(?:#|//).*$)`, language === "sql" ? "gi" : "g");
  let lastIndex = 0;
  for (const match of line.matchAll(tokenPattern)) {
    fragment.appendChild(document.createTextNode(line.slice(lastIndex, match.index)));
    const span = document.createElement("span");
    const token = match[0];
    span.className = token.startsWith("#") || token.startsWith("//")
      ? "syntax-comment"
      : token.startsWith('"') || token.startsWith("'")
        ? "syntax-string"
        : /^\d/.test(token)
          ? "syntax-number"
          : "syntax-keyword";
    span.textContent = token;
    fragment.appendChild(span);
    lastIndex = match.index + token.length;
  }
  fragment.appendChild(document.createTextNode(line.slice(lastIndex)));
  return fragment;
}

function codeExtension(language) {
  return ({ python: "py", javascript: "js", typescript: "ts", html: "html", css: "css", sql: "sql", powershell: "ps1", shell: "sh" })[language] || "txt";
}

function showChoiceComposerNotice() {
  choiceComposerNotice.hidden = false;
  input.focus();
}

function clearChoiceComposerNotice() {
  choiceComposerNotice.hidden = true;
}

function choiceMetadataSignature(responseMetadata) {
  if (responseMetadata?.type !== "choice_buttons" ||
      !Array.isArray(responseMetadata.options)) {
    return "";
  }
  return JSON.stringify(responseMetadata.options.map((option) => [
    String(option?.label || "").trim(),
    String(option?.value || "").trim(),
    String(option?.behavior || "").trim(),
  ]));
}

function stripDuplicateChoiceList(text, responseMetadata, removePrompt = false) {
  if (responseMetadata?.type !== "choice_buttons") return String(text || "");
  const options = Array.isArray(responseMetadata?.options)
    ? responseMetadata.options
    : [];
  const optionText = new Set();
  const normalizeOptionText = (value) => String(value || "")
    .trim()
    .replace(/^\[|\]$/g, "")
    .replace(/[*_`]/g, "")
    .replace(/\s+/g, " ")
    .toLowerCase();
  options.forEach((option) => {
    const label = normalizeOptionText(option?.label);
    const value = normalizeOptionText(option?.value);
    if (label) optionText.add(label);
    if (value) optionText.add(value);
  });

  let insideCodeFence = false;
  const remainingLines = String(text || "").split(/\r?\n/).filter((line) => {
    const trimmed = line.trim();
    if (/^(?:```|~~~)/.test(trimmed)) {
      insideCodeFence = !insideCodeFence;
      return true;
    }
    if (insideCodeFence) return true;
    if (removePrompt && /^please choose an action[:.]?$/i.test(trimmed)) {
      return false;
    }
    const numberedChoice = trimmed.match(/^\d+[.)]\s+(.+)$/);
    return !numberedChoice ||
      !optionText.has(normalizeOptionText(numberedChoice[1]));
  });
  const stripped = remainingLines.join("\n").replace(/\n{3,}/g, "\n\n").trim();
  return stripped || String(text || "");
}

function stripRepeatedChoicePrompt(text, responseMetadata) {
  return stripDuplicateChoiceList(text, responseMetadata, true);
}

// ------------------------------------------------------
// Function: createChoiceButtonGroup()
// Purpose: Renders optional response choices without creating a separate action path.
// Called by: addMsgDOM() for AI messages carrying choice_buttons metadata.
// Updates: Existing message input through sendCmd() or focuses it for a custom response.
// ------------------------------------------------------
function createChoiceButtonGroup(responseMetadata) {
  if (responseMetadata?.type !== "choice_buttons" ||
      !Array.isArray(responseMetadata.options)) {
    return null;
  }

  const options = responseMetadata.options
    .filter((option) => option && typeof option.label === "string")
    .map((option) => ({
      label: option.label.trim(),
      value: typeof option.value === "string" ? option.value.trim() : "",
      behavior: String(option.behavior || "").trim(),
    }))
    .filter((option) => option.label &&
      (option.value || option.behavior === "custom_input"))
    .slice(0, 24);

  if (!options.length) return null;

  const group = document.createElement("div");
  group.className = "chat-choice-actions";
  if (options.length > 5) group.classList.add("chat-choice-grid");
  group.setAttribute("role", "group");
  group.setAttribute("aria-label", "Response choices");

  options.forEach((option) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chat-choice-button";
    button.textContent = option.label;
    button.setAttribute("aria-pressed", "false");

    button.onclick = async () => {
      if (option.behavior === "custom_input") {
        showChoiceComposerNotice();
        return;
      }

      group.querySelectorAll(".chat-choice-button").forEach((choice) => {
        choice.disabled = true;
      });
      button.classList.add("selected");
      button.setAttribute("aria-pressed", "true");
      await sendCmd(option.value, {
        choiceSignature: choiceMetadataSignature(responseMetadata),
      });
    };

    group.appendChild(button);
  });

  return group;
}

// ------------------------------------------------------
// Function: addMsgDOM()
// Purpose: Builds and appends a visible chat message from server-backed message data.
// Called by: Conversation loading, chat submission, status notices, and greeting flows.
// Updates: The chat message container.
// ------------------------------------------------------
function addMsgDOM(
  who,
  text,
  tool,
  ts,
  processing = null,
  messageId = null,
  responseMetadata = null,
) {
  const wrap = document.createElement("div");
  wrap.className = "msg msg-" + who;
  if (messageId !== null && messageId !== undefined) {
    wrap.dataset.messageId = String(messageId);
  }
  const renderedAt = ts || Date.now();
  const route = who === "ai" ? normalizeTool(tool) : "";
  setMessageExportData(wrap, who, text, route, renderedAt);

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  let details = who === "ai" ? buildProcessingDetails(processing, route) : null;

  // ── PROCESS EXTRACTION (AI ONLY) ─────────────────────
  if (who === "ai") {
    const start = text.indexOf("[PROCESS]");
    const end = text.indexOf("AI:");

    if (start !== -1 && end !== -1) {
      text = text.slice(0, start) + "AI:" + text.slice(end + 3);
    }
    text = stripDuplicateChoiceList(text, responseMetadata);
  }

  // ── BUBBLE CONTENT RENDERING ─────────────────────────
  if (who === "ai" && (text.includes("```") || text.includes("`"))) {
    bubble.appendChild(parseMessageContent(text));
  } else {
    bubble.textContent = text;
  }

  // ── APPEND IN CORRECT ORDER ──────────────────────────

  // Keep metadata independent from body effects. Every AI message gets a
  // router badge, with Chat as the display fallback for an unassigned route.
  wrap.appendChild(createMessageMeta(who, route, renderedAt));

  // bubble ALWAYS comes second
  wrap.appendChild(bubble);

  const choiceButtons = who === "ai"
    ? createChoiceButtonGroup(responseMetadata)
    : null;
  if (choiceButtons) {
    wrap.appendChild(choiceButtons);
  }

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

function normalizeTool(tool) {
  const normalized = String(tool || "")
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_-]+/g, "-");
  return normalized || "chat";
}

function toolLabel(tool) {
  const route = normalizeTool(tool);
  const labels = {
    chat: "🧠 Chat",
    shell: "⚡ Shell",
    aider: "💻 Code",
    code: "💻 Code",
    chromadb_store: "💾 Memory",
    chromadb_recall: "💾 Memory",
    memory: "💾 Memory",
    memory_recall: "💾 Memory",
    memory_search: "💾 Memory",
    n8n: "⚙️ N8n",
    web: "🌐 Web",
    web_search: "🌐 Web",
    personality: "🎭 Personality",
    playbook: "▶️ Playbook",
    help: "❓ Help",
    status: "📊 Status",
    system: "🔧 System",
  };
  if (labels[route]) return labels[route];
  const readable = route.replace(/[-_]+/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
  return `🔧 ${readable}`;
}

function createMessageMeta(who, tool, ts) {
  const meta = document.createElement("div");
  meta.className = "msg-meta";

  const timestamp = document.createElement("span");
  timestamp.className = "msg-timestamp";
  timestamp.textContent = formatTimestamp(ts);
  meta.appendChild(timestamp);

  if (who === "ai") {
    const route = normalizeTool(tool);
    const badge = document.createElement("span");
    badge.className = `tool-badge tool-${route}`;
    badge.dataset.router = route;
    badge.textContent = toolLabel(route);
    meta.appendChild(badge);
  }

  return meta;
}

function setMessageExportData(wrap, who, text, tool, ts, exportable = true) {
  wrap.dataset.messageRole = who === "you" ? "user" : "ai";
  wrap.dataset.messageContent = String(text || "");
  wrap.dataset.messageTool = who === "ai" ? normalizeTool(tool) : "";
  wrap.dataset.messageTimestamp = timestampDate(ts).toISOString();
  wrap.dataset.exportable = exportable ? "true" : "false";
}

function addTyping() {
  const el = document.createElement("div");
  el.className = "msg msg-ai";
  el.innerHTML = '<div class="bubble typing">Aetheraeon <span>▋</span></div>';
  el.dataset.exportable = "false";
  el.prepend(createMessageMeta("ai", "chat", Date.now()));
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
async function sendCmd(cmd, uiContext = null) {
  dumpState("BEFORE SEND");
  console.log("🔥 SEND FUNCTION HIT");
  cmd = (cmd || "").trim();
  if (!cmd) return;
  closeSlashCommandMenu();

  if (!currentUser?.id) {
    showToast("Sign in before sending a message.");
    return;
  }
  clearChoiceComposerNotice();

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
    const resp = await fetch(apiUrl("chat"), {
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

    const rawText = data.response || data.error || "(no response)";
    const repeatedChoiceResponse = Boolean(
      uiContext?.choiceSignature &&
      choiceMetadataSignature(data.response_metadata) === uiContext.choiceSignature
    );
    const responseMetadata = repeatedChoiceResponse ? null : data.response_metadata;
    const text = repeatedChoiceResponse
      ? stripRepeatedChoicePrompt(rawText, data.response_metadata)
      : rawText;

    // ── Handle special actions ─────────────────────────────
    if (data.action === "clear_chat") {
      chat.innerHTML = "";
      addMsgDOM(
        "ai",
        text,
        data.tool || "chat",
        Date.now(),
        data.processing,
        null,
        responseMetadata,
      );
    } else if (data.action?.type === "aider_approve") {
      const msgEl = addMsgDOM("ai", text, data.tool || "aider", Date.now(), data.processing);
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
            if (b2) {
              b2.textContent = `[AIDER] running… ${String(Math.floor(s2 / 60)).padStart(2, "0")}:${String(s2 % 60).padStart(2, "0")}`;
              sm.dataset.messageContent = b2.textContent;
            }
          }, 1000);
          try {
            const r2 = await fetch(apiUrl("aider/run"), {
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
      addMsgDOM(
        "ai",
        text,
        data.tool || "chat",
        Date.now(),
        data.processing,
        null,
        responseMetadata,
      );
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
    // Browser secure-context policy determines availability.
    // ----------------------------------------------------------
    if (!window.isSecureContext) {
      showToast("Voice requires a secure HTTPS connection.", "var(--orange)");
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
      doSearch(false);
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
  _searchCursor = null;
  _searchQuery = "";
  _searchRequestId += 1;
}

function closeSearchIfOutside(e) {
  if (e.target === document.getElementById("search-overlay")) closeSearch();
}

function debounceSearch() {
  clearTimeout(_searchTimer);
  _searchTimer = setTimeout(() => doSearch(false), 300);
}

async function doSearch(loadMore = false) {
  const q = document.getElementById("search-input").value.trim();
  const resultsEl = document.getElementById("search-results");
  if (!q) {
    resultsEl.innerHTML = "";
    _searchCursor = null;
    _searchQuery = "";
    return;
  }
  if (!loadMore || q !== _searchQuery) {
    loadMore = false;
    _searchQuery = q;
    _searchCursor = null;
  }
  if (loadMore && !_searchCursor) return;

  const requestId = ++_searchRequestId;
  if (!loadMore) resultsEl.innerHTML =
    '<div style="font-size:0.78em;color:var(--muted);padding:8px">Searching…</div>';
  try {
    const params = new URLSearchParams({ query: q });
    if (loadMore) params.set("cursor", _searchCursor);
    const r = await fetch(apiUrl("messages/search") + "?" + params.toString());
    const d = await r.json();
    if (requestId !== _searchRequestId) return;
    if (!loadMore) resultsEl.innerHTML = "";
    if (!d.ok || !d.results.length) {
      if (!loadMore) {
        resultsEl.innerHTML =
          '<div style="font-size:0.78em;color:var(--muted);padding:8px">No results.</div>';
      }
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
      el.onclick = () => { void openSearchResult(res); };
      resultsEl.appendChild(el);
    });
    _searchCursor = d.next_cursor || null;
    if (d.has_more && _searchCursor) {
      const more = document.createElement("button");
      more.type = "button";
      more.className = "search-load-more";
      more.textContent = "Load more";
      more.onclick = () => { void doSearch(true); };
      resultsEl.appendChild(more);
    }
  } catch (e) {
    if (requestId !== _searchRequestId) return;
    resultsEl.innerHTML =
      '<div style="font-size:0.78em;color:var(--red);padding:8px">Search failed.</div>';
  }
}

async function openSearchResult(result) {
  const conversationId = result && result.conversation_id;
  if (!conversationId) {
    showToast("Conversation unavailable.", "var(--orange)");
    return;
  }
  closeSearch();
  if (!conversations[conversationId]) {
    conversations = await loadConversations();
    renderSidebar();
  }
  if (!conversations[conversationId]) {
    showToast("Conversation unavailable.", "var(--orange)");
    return;
  }
  await activateConv(conversationId);
  jumpToSearchMessage(result.message_id);
}

function jumpToSearchMessage(messageId) {
  const target = [...chat.querySelectorAll(".msg")].find(
    (element) => element.dataset.messageId === String(messageId),
  );
  if (!target) {
    showToast("Message is no longer available.", "var(--orange)");
    return;
  }
  target.scrollIntoView({ behavior: "smooth", block: "center" });
  target.classList.add("search-message-target");
  setTimeout(() => target.classList.remove("search-message-target"), 1800);
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
const _knownServices = ["Aetheraeon", "aider", "chromadb", "n8n", "ollama"];

function _serviceIsOnline(state) {
  return typeof state === "object" && state !== null ? !!state.status : !!state;
}

function _renderStatusDots(aiCore, serviceStatus = {}) {
  const el = document.getElementById("status-dots");
  if (!el) return { allOk: false, offline: [..._knownServices] };
  const states = [
    ["Aetheraeon", !!aiCore],
    ..._knownServices.slice(1).map((name) => [name, _serviceIsOnline(serviceStatus[name])]),
  ];
  const offline = [];
  el.innerHTML = "";
  states.forEach(([name, ok]) => {
    if (!ok) offline.push(name);
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
  });
  return { allOk: offline.length === 0, offline };
}

/** Render all known service dots as offline (red). Called when server is unreachable. */
function _renderAllDotsOffline() {
  return _renderStatusDots(false, {});
}

async function checkCachedServiceStatus() {
  try {
    const { response, data } = await fetchJsonOnce(apiUrl("services"), {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    if (!response.ok || data?.aetheraeon !== true || !data?.status) return null;
    return data.status;
  } catch {
    return null;
  }
}

async function refreshStatus() {
  const apacheHosted = isProductionDeployment();
  const localDatabasePromise = apacheHosted
    ? checkProductionDatabaseHealth()
    : Promise.resolve({ production: false, database: null });
  const cachedServicesPromise = apacheHosted
    ? checkCachedServiceStatus()
    : Promise.resolve(null);
  const healthEndpoint = apiUrl(apacheHosted ? "health" : "status");
  try {
    const { response, data: d } = await fetchJsonOnce(healthEndpoint, {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
    });
    const available = apacheHosted
      ? response.ok && d?.ok === true && d?.ai_core === true
      : response.ok && d?.health?.ai_core === true;
    const [localDatabase, cachedServices] = await Promise.all([
      localDatabasePromise,
      cachedServicesPromise,
    ]);
    setBackendAvailability(available);
    setDeploymentHealth({
      aiCore: available,
      database: apacheHosted
        ? (localDatabase.production ? localDatabase.database : false)
        : d?.health?.database,
    });
    if (!available) throw new Error("Health endpoint unavailable");

    const rendered = _renderStatusDots(
      available,
      apacheHosted ? cachedServices || {} : d.status || {},
    );
    if (d.version) document.getElementById("app-version").textContent = d.version;
    if (activeConvId && !rendered.allOk && _lastStatusOk) {
      addMsgDOM("ai", "⚠️ SERVICE OFFLINE: " + rendered.offline.join(", "), "system", Date.now());
    }
    _lastStatusOk = rendered.allOk;
    return true;
  } catch {
    const [localDatabase, cachedServices] = await Promise.all([
      localDatabasePromise,
      cachedServicesPromise,
    ]);
    setBackendAvailability(false);
    setDeploymentHealth({
      aiCore: false,
      database: apacheHosted
        ? (localDatabase.production ? localDatabase.database : false)
        : null,
    });
    _renderStatusDots(false, apacheHosted ? cachedServices || {} : {});
    if (activeConvId && _lastStatusOk) {
      addMsgDOM(
        "ai",
        "⚠️ Cannot reach Aetheraeon server — ai_orchestrator.py may be stopped.",
        "system",
        Date.now(),
      );
    }
    _lastStatusOk = false;
    return false;
  }
}

// ────────────────────────────────────────────────────────────
// SHARE / EXPORT
// ────────────────────────────────────────────────────────────

/**
 * Format the active rendered conversation, or fetch an inactive one from DB.
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

  // The rendered message list is authoritative for the active conversation.
  // This also includes any just-rendered reply before a persistence refresh.
  if (cid === activeConvId) {
    const visibleMessages = collectVisibleConversationMessages();
    if (visibleMessages.length) {
      const body = visibleMessages
        .map(({ role, content, tool, timestamp }) => {
          const who = role === "user" ? "You" : "AI";
          const router = role === "ai" ? `   ${toolLabel(tool)}` : "";
          return `${formatTimestamp(timestamp)}${router}   ${who}:\n${content}\n`;
        })
        .join("\n");
      return header + "\n" + body;
    }
  }

  try {
    const r = await fetch(apiUrl(`messages?conversation_id=${encodeURIComponent(cid)}`));
    const d = await r.json();
    if (!d.ok || !d.messages?.length) return header + "\n(no messages)";
    const body = d.messages
      .map((m) => {
        const who = m.role === "user" ? "You" : "AI";
        const time = (m.created_at || "").slice(11, 16);
        const router = m.role === "user" ? "" : `   ${toolLabel(m.tool_used || "chat")}`;
        return `[${time}]${router}   ${who}:\n${m.content || ""}\n`;
      })
      .join("\n");
    return header + "\n" + body;
  } catch {
    return header + "\n(could not load messages)";
  }
}

function collectVisibleConversationMessages() {
  return Array.from(chat.querySelectorAll(".msg[data-message-role]"))
    .filter((message) => message.dataset.exportable !== "false")
    .map((message) => ({
      role: message.dataset.messageRole,
      content: message.dataset.messageContent || "",
      tool: message.dataset.messageTool || "chat",
      timestamp: message.dataset.messageTimestamp || Date.now(),
    }));
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
      const r = await fetch(apiUrl(`messages?conversation_id=${encodeURIComponent(id)}`));
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

// Slash command autocomplete foundation. This is input assistance only; the
// backend remains authoritative for command parsing and authorization.
function slashCommandMatches(value) {
  const rawText = String(value || "");
  const text = rawText.trimStart().toLowerCase();
  if (!text.startsWith("/") || /\n/.test(text)) return [];

  const rootCommands = SLASH_COMMAND_CATALOG.filter((item) => !item.parent);
  if (text === "/") return rootCommands;

  const exactRoot = rootCommands.find((item) => item.command === text.trimEnd());
  if (exactRoot && (text === exactRoot.command || text === `${exactRoot.command} `)) {
    const children = SLASH_COMMAND_CATALOG.filter(
      (item) => item.parent === exactRoot.command,
    );
    return children.length ? children : [exactRoot];
  }

  if (!text.includes(" ")) {
    return rootCommands.filter((item) => item.command.startsWith(text));
  }

  const parent = rootCommands.find((item) => text.startsWith(`${item.command} `));
  if (!parent) return [];
  const children = SLASH_COMMAND_CATALOG.filter((item) => item.parent === parent.command);
  const matches = children.filter((item) => item.command.startsWith(text.trimEnd()));
  const exactChild = children.find((item) => item.command === text.trimEnd());
  if (exactChild && (text === exactChild.command || text === `${exactChild.command} `)) {
    return [exactChild];
  }
  return matches;
}

function closeSlashCommandMenu() {
  slashCommandSelection = -1;
  slashCommandMenu.hidden = true;
  slashCommandMenu.replaceChildren();
  input.removeAttribute("aria-activedescendant");
}

function chooseSlashCommand(item) {
  if (!item) return;
  input.value = item.parameterHint ? `${item.command} ` : item.command;
  autoResize();
  input.focus();
  const hasChildren = SLASH_COMMAND_CATALOG.some(
    (candidate) => candidate.parent === item.command,
  );
  if (hasChildren || item.parameterHint) renderSlashCommandMenu();
  else closeSlashCommandMenu();
}

function updateSlashCommandSelection() {
  const buttons = [...slashCommandMenu.querySelectorAll(".slash-command-item")];
  buttons.forEach((button, index) => {
    const active = index === slashCommandSelection;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
  const activeButton = buttons[slashCommandSelection];
  if (activeButton) {
    input.setAttribute("aria-activedescendant", activeButton.id);
    activeButton.scrollIntoView?.({ block: "nearest" });
  } else {
    input.removeAttribute("aria-activedescendant");
  }
}

function renderSlashCommandMenu() {
  const items = slashCommandMatches(input.value);
  if (!items.length) {
    closeSlashCommandMenu();
    return [];
  }

  slashCommandSelection = -1;
  slashCommandMenu.replaceChildren();
  items.forEach((item, index) => {
    const button = document.createElement("button");
    button.type = "button";
    button.id = `slash-command-option-${index}`;
    button.className = "slash-command-item";
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", "false");

    const name = document.createElement("span");
    name.className = "slash-command-name";
    name.textContent = item.command;
    const description = document.createElement("span");
    description.className = "slash-command-description";
    description.textContent = item.description;
    button.append(name, description);
    if (item.parameterHint) {
      const hint = document.createElement("span");
      hint.className = "slash-command-parameter-hint";
      hint.textContent = item.example
        ? `${item.parameterHint} · Example: ${item.example}`
        : item.parameterHint;
      button.appendChild(hint);
    }
    button.addEventListener("mousedown", (event) => {
      event.preventDefault();
      chooseSlashCommand(item);
    });
    slashCommandMenu.appendChild(button);
  });
  slashCommandMenu.hidden = false;
  return items;
}

// JS-011: Event Handlers

sendBtn.addEventListener("click", () => sendCmd(input.value));
choiceComposerCancel.addEventListener("click", () => {
  clearChoiceComposerNotice();
  input.focus();
});

input.addEventListener("keydown", (e) => {
  const slashItems = slashCommandMatches(input.value);
  const slashMenuOpen = !slashCommandMenu.hidden && slashItems.length > 0;
  if (slashMenuOpen && (e.key === "ArrowDown" || e.key === "ArrowUp")) {
    e.preventDefault();
    const offset = e.key === "ArrowDown" ? 1 : -1;
    slashCommandSelection = (
      slashCommandSelection + offset + slashItems.length
    ) % slashItems.length;
    updateSlashCommandSelection();
    return;
  }
  if (slashMenuOpen && e.key === "Escape") {
    e.preventDefault();
    closeSlashCommandMenu();
    return;
  }
  const exactSlashCommand = slashItems.some(
    (item) => item.command === input.value.toLowerCase(),
  );
  if (
    slashMenuOpen &&
    (e.key === "Tab" || (e.key === "Enter" && !exactSlashCommand))
  ) {
    e.preventDefault();
    chooseSlashCommand(slashItems[Math.max(0, slashCommandSelection)]);
    return;
  }
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
  renderSlashCommandMenu();
  if (input.value.trim()) clearTemporaryGreetingForInteraction();
});

document.addEventListener("mousedown", (event) => {
  if (!event.target.closest("#composer-input-wrap")) closeSlashCommandMenu();
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

function timestampDate(ts) {
  if (!ts) return new Date();
  if (ts instanceof Date && !isNaN(ts.getTime())) return new Date(ts.getTime());

  // Database timestamps are local SQL datetimes. The ISO-style separator is
  // consistently parsed by browsers while preserving the intended timezone.
  const value = typeof ts === "string" ? ts.trim() : ts;
  const normalized =
    typeof value === "string" && /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}/.test(value)
      ? value.replace(" ", "T")
      : value;
  const parsed = new Date(normalized);
  return isNaN(parsed.getTime()) ? new Date() : parsed;
}

function formatTimestamp(ts) {
  const d = timestampDate(ts);
  const MM = String(d.getMonth() + 1).padStart(2, "0");
  const DD = String(d.getDate()).padStart(2, "0");
  const YYYY = d.getFullYear();
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ampm = d.getHours() >= 12 ? "PM" : "AM";
  const hh = String(d.getHours() % 12 || 12).padStart(2, "0");
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
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.add("open");
  const existing = modalNavigationStack.indexOf(id);
  if (existing >= 0) modalNavigationStack.splice(existing, 1);
  modalNavigationStack.push(id);
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove("open");
  let index = modalNavigationStack.indexOf(id);
  while (index >= 0) {
    modalNavigationStack.splice(index, 1);
    index = modalNavigationStack.indexOf(id);
  }
}

function getTopOpenModal() {
  for (let index = modalNavigationStack.length - 1; index >= 0; index--) {
    const modal = document.getElementById(modalNavigationStack[index]);
    if (modal?.classList.contains("open")) return modal;
    modalNavigationStack.splice(index, 1);
  }
  const openModals = [...document.querySelectorAll(".modal-overlay.open")];
  return openModals.at(-1) || null;
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
async function bootApp(user, sessionData = {}) {
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
  document.querySelectorAll(".admin-only").forEach((element) =>
    element.classList.toggle("visible", hasAdministrativeRole(user?.role)),
  );
  const adminViewBanner = document.getElementById("admin-view-banner");
  adminViewBanner.classList.toggle("visible", !!sessionData.administrator_view);
  document.getElementById("admin-view-user").textContent = fullName;
  updateMaintenanceBanner(!!sessionData.maintenance_mode, sessionData);

  // ── 3. Load theme ──
  const dashboardResources = Promise.all([
    loadTheme(),
    loadConversations(),
    refreshStatus(),
  ]);

  // ── 4. Load conversations from DB (source of truth) ──
  conversations = (await dashboardResources)[1];
  showNoConversationState();

  // ── 5. Handle EMPTY STATE cleanly ──
  // ── 6. Activate most recent / first conversation safely ──

  // ── 7. Render sidebar AFTER activation (keeps UI consistent) ──

  // ── 8. Status polling ──
  if (_sessionMonitorTimer) clearInterval(_sessionMonitorTimer);
  _sessionMonitorTimer = setInterval(monitorSession, 5000);

  // ── 9. Focus input ──
  input?.focus();
}

// INIT

initializeFontSelects();
renderCustomThemeEditor();
document.getElementById("show-processing-details")?.addEventListener("change", syncProcessingSettingsState);
syncProcessingSettingsState();
startBackendAvailabilityMonitoring();
checkSession();
const initialResetToken = new URLSearchParams(window.location.search).get("reset_token");
if (initialResetToken) openResetPassword(initialResetToken);

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
    const { data: d } = await fetchJsonOnce(apiUrl("memory/all"));

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

    // ── Full ID (selectable and explicitly copyable) ─────
    const tdId = document.createElement("td");
    tdId.className = "mem-id-cell";
    const idText = document.createElement("code");
    idText.className = "mem-id-text";
    idText.textContent = row.id;
    idText.title = row.id;
    const copyIdBtn = document.createElement("button");
    copyIdBtn.className = "mem-id-copy-btn";
    copyIdBtn.type = "button";
    copyIdBtn.textContent = "Copy";
    copyIdBtn.title = "Copy full memory ID";
    copyIdBtn.addEventListener("click", async (e) => {
      e.stopPropagation();
      try {
        await navigator.clipboard.writeText(row.id);
        _memSetStatus("Copied full memory ID");
      } catch {
        _memShowError("Could not copy memory ID");
      }
    });
    tdId.append(idText, copyIdBtn);

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
    const r = await fetch(apiUrl("memory/search"), {
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
  try {
    const r = await fetch(apiUrl("memory/delete"), {
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
    showToast("Memory entry deleted");
    document.getElementById("mem-count-badge").textContent = `${_memAllRows.length} memories`;
  } catch (err) {
    _memSetStatus("Delete error: " + err.message);
    showToast(err.message || "Unable to delete memory entry.", "var(--red)");
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
  let deleted = 0;
  for (const id of ids) {
    try {
      const r = await fetch(apiUrl("memory/delete"), {
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
  showToast(`${deleted} memory ${deleted === 1 ? "entry" : "entries"} deleted`);
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
      const r = await fetch(apiUrl("memory/update"), {
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
      const r = await fetch(apiUrl("memory/create"), {
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
      const r = await fetch(apiUrl("memory/create"), {
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
