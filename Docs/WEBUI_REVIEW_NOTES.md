# Aetheraeon WebUI Review Notes

This file contains recommendations that were intentionally **not implemented** during the cleanup pass. They require functional, structural, compatibility, deployment, or legal decisions beyond the approved scope.

## Duplicate memory-toolbar ID

**File:** `WebUI/index.html`

**Line/function:** Lines 259 and 308; memory manager toolbar markup

**Current behavior:** Two separate toolbar containers both use `id="mem-toolbar"`. Browsers render both, but `document.getElementById("mem-toolbar")` can return only the first element and the document does not have unique IDs.

**Why improvement may help:** Unique IDs improve HTML validity, accessibility relationships, test reliability, and future DOM targeting.

**Recommended modification:** Give the second toolbar a distinct semantic ID such as `mem-actions-toolbar`, then update any associated selectors or tests in the same change.

**Risk level:** Medium. Changing an ID was explicitly prohibited for this pass and could break unknown external selectors or automation.

## Inline event handlers

**File:** `WebUI/index.html`

**Line/function:** Lines 106–936; 91 `onclick`, `onchange`, `oninput`, `onkeydown`, and related attributes

**Current behavior:** HTML directly invokes global JavaScript functions through inline event attributes.

**Why improvement may help:** Central event registration would separate structure from behavior and permit a stricter Content Security Policy without `'unsafe-inline'` script handling.

**Recommended modification:** In a dedicated future change, attach equivalent listeners from `aetheraeon.js` after DOM readiness. Preserve handler ordering, arguments, event propagation, and every current function call.

**Risk level:** High. There are many interaction paths, and a missed or reordered listener could break authentication, chat, settings, memory, playbooks, or modal behavior.

## Keyboard access for clickable non-button elements

**File:** `WebUI/index.html`

**Line/function:** Lines 179–184 (`user-menu-item`), 856 (`pb-new-btn`), 862 (`user-badge`), and 895–896 (`conv-title-display`)

**Current behavior:** Several interactive controls are `<div>` or `<span>` elements activated only through pointer click handlers.

**Why improvement may help:** Native buttons or complete keyboard semantics would make these controls reachable and operable for keyboard and assistive-technology users.

**Recommended modification:** Prefer semantic `<button>` elements. If markup must remain unchanged, add an appropriate role, `tabindex="0"`, visible focus styling, and Enter/Space keyboard handlers that call the same existing functions.

**Risk level:** Medium. Element substitutions can affect inherited styling, focus order, click propagation, and context-menu placement.

## Global custom cursor behavior

**File:** `WebUI/css/aetheraeon.css`

**Line/function:** Lines 125, 133, and 1923; base controls and responsive cursor rules

**Current behavior:** The native cursor is hidden with `cursor: none` and replaced by the custom cursor system.

**Why improvement may help:** A native cursor is more predictable for accessibility tools, remote desktop, high-contrast settings, touch/hybrid devices, and users who prefer reduced motion.

**Recommended modification:** Enable the custom cursor only inside `@media (hover: hover) and (pointer: fine)`, retain the native cursor elsewhere, and provide a `prefers-reduced-motion` fallback.

**Risk level:** Medium. Cursor behavior is a visible product choice and changing media conditions may alter the intended experience on some devices.

## Backend health endpoint and duplicate authenticated polling

**File:** `WebUI/js/aetheraeon.js`

**Line/function:** `checkBackendAvailability()` near line 1304, `startBackendAvailabilityMonitoring()` near line 1327, and `bootApp()` status interval near line 3804

**Current behavior:** Pre-authentication availability and authenticated service status both call `/api/status`. The availability interval continues after login, so authenticated pages can perform two status requests on related schedules.

**Why improvement may help:** A dedicated minimal health endpoint and lifecycle-aware polling could reduce work and distinguish “HTTP backend reachable” from “all managed services healthy.”

**Recommended modification:** Add a read-only `/api/health` route that performs no session snapshot or service orchestration. Stop the pre-authentication timer after successful boot, restart it when returning to login, and keep the authenticated status timer unchanged.

**Risk level:** Medium. This requires a new backend contract and timer lifecycle changes, both prohibited during this pass.

## `AbortSignal.timeout` compatibility

**File:** `WebUI/js/aetheraeon.js`

**Line/function:** Lines 1310 and 3261; `checkBackendAvailability()` and `refreshStatus()`

**Current behavior:** Status fetches use `AbortSignal.timeout(10000)`.

**Why improvement may help:** Older browsers and some embedded WebViews do not implement `AbortSignal.timeout`, which can cause the status check itself to throw before `fetch()` begins.

**Recommended modification:** Feature-detect `AbortSignal.timeout` and use a small `AbortController` fallback when it is unavailable.

**Risk level:** Low to medium. A fallback adds timer and cancellation logic that must be cleaned up correctly.

## Generated inline presentation markup

**File:** `WebUI/js/aetheraeon.js`

**Line/function:** `addMsgDOM()` near line 2776 and `doSearch()` near lines 3186–3220

**Current behavior:** A small number of dynamically generated elements still receive inline presentation through `element.style` or HTML strings. Static CSS has been fully removed from `index.html`, but these existing JavaScript rendering paths retain their original output.

**Why improvement may help:** Named CSS classes would centralize presentation and make generated states easier to theme and maintain.

**Recommended modification:** Introduce documented state classes for message alignment, search loading/empty/error messages, and highlighted text; update the renderers to assign those classes without changing their content or data flow.

**Risk level:** Medium. These strings are part of active rendering logic, and class migration could change message/search appearance or sanitization behavior.

## Canonical URL and social preview assets

**File:** `WebUI/index.html`

**Line/function:** Lines 34–89; SEO metadata

**Current behavior:** Accurate title, description, Open Graph, Twitter summary, and JSON-LD metadata are present. Canonical URL, `og:url`, and social preview image fields are intentionally omitted because no stable public URLs or approved images were provided.

**Why improvement may help:** Canonical and preview metadata improves search consolidation and link presentation after public hosting is established.

**Recommended modification:** After choosing the production origin, add one canonical URL, matching `og:url`, and sanitized absolute image URLs with correct dimensions and alt text. Do not use placeholders in production.

**Risk level:** Low if the final URLs are correct; medium if incorrect URLs cause indexing or sharing problems.

## Screenshots

**File:** `readme.md`

**Line/function:** Line 124; Screenshots section

**Current behavior:** The README explains that no screenshots are bundled.

**Why improvement may help:** Sanitized screenshots improve GitHub discoverability and help users understand the interface before installation.

**Recommended modification:** Add desktop and mobile screenshots after removing usernames, emails, conversations, memory entries, local paths, service credentials, and other private data.

**Risk level:** Medium. Unsanitized screenshots can disclose personal or security-sensitive information.

## Repository license

**File:** `readme.md`

**Line/function:** Line 147; License section

**Current behavior:** No license file is present, and the README states that normal copyright restrictions apply.

**Why improvement may help:** Public users need explicit terms before they can confidently use, modify, or redistribute the project. It also determines whether “open source” is an accurate project description.

**Recommended modification:** The repository owner should choose an appropriate license, add it as a root `LICENSE` file, and then update the README and public metadata to match.

**Risk level:** High (legal/project-governance decision). Do not select a license without owner approval.
