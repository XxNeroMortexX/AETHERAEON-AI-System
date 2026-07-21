"""Deterministic support for creative intent, novelty, and hard constraints.

This module is deliberately limited to creative-response cognition.  It does
not access memory, personality, tools, persistence, or deployment state.
"""

from __future__ import annotations

from dataclasses import dataclass
import re


_CREATIVE_ACTION = (
    r"(?:invent|create|design|build|brainstorm|imagine|envision|dream|"
    r"describe|write|draft|generate|compose|develop|conceive)"
)
_WORLD_BUILDING_SUBJECT = (
    r"(?:fiction|science[ -]?fiction|sci[ -]?fi|story|novel|narrative|scene|"
    r"poem|lyrics|fantasy(?:\s+city)?|imaginary\s+world|world(?:building)?|"
    r"world[ -]building|city|species|civilization|society|"
    r"language|culture|history|myth|character|creature|magic\s+system|"
    r"future\s+society)"
)
_IDEATION_SUBJECT = (
    r"(?:ideas?|concepts?|names?|sports?|games?|materials?|artifacts?|"
    r"companies|company|societies|mechanics|social\s+structures?|"
    r"behavio[u]?rs?|slogans?|art|artwork|art\s+forms?|creative\s+medium|"
    r"creative\s+media|logos?|illustrations?|paintings?|music)"
)

_WORLD_BUILDING_REQUEST = re.compile(
    rf"\b{_CREATIVE_ACTION}\b[^\n]{{0,140}}\b{_WORLD_BUILDING_SUBJECT}\b|"
    rf"\b{_WORLD_BUILDING_SUBJECT}\b[^\n]{{0,80}}\b(?:invent|create|design|"
    r"write|develop)\b",
    re.IGNORECASE,
)
_CREATIVE_IDEATION_REQUEST = re.compile(
    rf"\b{_CREATIVE_ACTION}\b[^\n]{{0,140}}\b{_IDEATION_SUBJECT}\b|"
    r"\b(?:invent|brainstorm|conceive)\b",
    re.IGNORECASE,
)
_ROLEPLAY_REQUEST = re.compile(r"\b(?:roleplay|role-play)\b", re.IGNORECASE)
_EXPLICIT_WORLDBUILDING_REQUEST = re.compile(
    r"\b(?:world[ -]?building|imaginary\s+world|fictional\s+society|"
    r"original\s+(?:fantasy|science[ -]?fiction|sci[ -]?fi)\s+creation)\b",
    re.IGNORECASE,
)
_PURE_IMAGINATION_REQUEST = re.compile(
    r"(?:"
    r"^\s*(?:imagine|envision|dream(?:\s+up)?)\b"
    r"|\b(?:describe|create|imagine|envision|dream(?:\s+up)?)\b"
    r"[^\n]{0,160}\b(?:"
    r"place\s+that\s+(?:can|could)\s+not\s+exist|"
    r"impossible\s+(?:place|world|environment|location)|"
    r"fictional\s+(?:place|world|environment|location|scene)|"
    r"unreal\s+(?:place|world|environment|location)|"
    r"imaginary\s+experience|experience\s+in\s+(?:an?\s+)?fictional\s+place|"
    r"beyond\s+(?:normal\s+)?reality|outside\s+normal\s+reality"
    r")\b"
    r")",
    re.IGNORECASE,
)
_EXPLICIT_ART_INVENTION = re.compile(
    r"\b(?:original\s+(?:form\s+of\s+)?art|new\s+art\s+form|"
    r"invent\s+(?:an?\s+)?art|new\s+creative\s+medium)\b",
    re.IGNORECASE,
)
_ABSTRACT_INVENTION_REQUEST = re.compile(
    rf"\b{_CREATIVE_ACTION}\b[^\n]{{0,180}}\b(?:"
    r"something\s+that\s+has\s+never\s+existed(?:\s+before)?|"
    r"(?:completely\s+)?original\s+(?:method|form|system)\s+of\s+"
    r"communication|imaginary\s+experience|unreal\s+location|"
    r"impossible\s+(?:concept|place)|beyond\s+(?:normal\s+)?reality"
    r")\b",
    re.IGNORECASE,
)
_NEVER_EXISTED_CREATION = re.compile(
    rf"\b{_CREATIVE_ACTION}\b[^\n]{{0,180}}\bnever\s+existed(?:\s+before)?\b|"
    r"\b(?:concept|idea|creation|experience|art\s+form)\b"
    r"[^\n]{0,80}\bnever\s+existed(?:\s+before)?\b",
    re.IGNORECASE,
)

_CONSTRAINT_MARKER = re.compile(
    r"\b(?:"
    r"(?:do\s+not|don't|never|must\s+not|should\s+not|cannot|can't)\s+"
    r"(?:base\s+(?:it|them|this|that|the\s+\w+)\s+on|be\s+based\s+on|"
    r"use|include|mention|feature|contain|involve|rely\s+on)"
    r"|(?:cannot|can't)\s+be"
    r"|not\s+based\s+on"
    r"|avoid(?:\s+using)?"
    r"|without"
    r")\b\s*:?[ \t]*(.*)$",
    re.IGNORECASE,
)
_LIST_SEPARATOR = re.compile(r"\s*(?:,|;|\bor\b|\band\b)\s*", re.IGNORECASE)
_LEADING_LIST_MARKER = re.compile(r"^\s*(?:[-*\u2022]+|\d+[.)])\s*")
_WORD = re.compile(r"[a-z0-9]+(?:['-][a-z0-9]+)?", re.IGNORECASE)
_INLINE_NO_CONSTRAINT = re.compile(
    r"(?:^|\(|,)\s*(?:[-*\u2022]+\s*)?no\s+"
    r"([a-z][a-z -]{0,40}?)(?=\s*(?:,|\)|$))",
    re.IGNORECASE,
)

_FORBIDDEN_SEMANTIC_CATEGORIES = (
    (
        ("technology",),
        (
            "mechanism", "device", "machine", "system", "computer",
            "digital", "software", "ai", "hardware", "electronics",
            "electronic system", "embedded device", "automated equipment",
        ),
    ),
    (
        ("consciousness", "conscious"),
        (
            "awareness", "perception", "thought", "thinking", "mind",
            "mental", "feeling", "emotion", "sentience", "presence",
            "shared consciousness", "subjective experience",
            "inner experience", "experience internally",
            "participants experience", "participants feel",
        ),
    ),
    (
        ("biology", "biological"),
        (
            "organism", "living process", "living being", "lifeform",
            "instinct", "sense", "sensory", "nervous system", "neural",
            "organic life",
        ),
    ),
    (
        ("matter", "material"),
        (
            "particle", "field", "radiation", "force", "wave", "mass",
            "atom", "molecule", "substance", "physical material",
        ),
    ),
    (
        ("energy",),
        (
            "particle", "field", "radiation", "force", "wave",
            "electricity", "power", "charge", "current", "light", "heat",
        ),
    ),
    (
        ("sound",),
        (
            "whisper", "voice", "noise", "audible", "acoustic", "sonic",
            "echo", "hearing", "listening",
        ),
    ),
    (
        ("light",),
        (
            "glow", "luminous", "illumination", "radiance", "brightness",
            "beam", "radiation", "visible spectrum",
        ),
    ),
    (
        ("space", "spatial"),
        (
            "location", "distance", "dimension", "direction", "volume",
            "position", "place", "depth", "expanse", "spatial extent",
        ),
    ),
    (
        ("time", "temporal"),
        (
            "duration", "sequence", "chronology", "moment", "interval",
            "before", "after", "cycle", "temporal order",
        ),
    ),
    (("creature",), ("entity", "being")),
)

# These wider associations are intentionally enabled only when a request names
# multiple exclusions. In ordinary creative prose the terms remain available.
_MULTI_RESTRICTION_SEMANTIC_EXTENSIONS = (
    (("energy",), ("charged", "resonance", "field", "force")),
    (("light",), ("glow", "shimmer", "luminous")),
    (("sound",), ("harmony", "melody", "sonic", "wave")),
    (
        ("consciousness", "awareness", "perception", "thought"),
        ("psyche", "mental clarity", "emotional influence"),
    ),
    (("place",), ("realm", "environment", "domain")),
)

_GENERIC_ABSTRACTION_PATTERNS = (
    ("equilibrium", re.compile(r"\bequilibrium\b", re.IGNORECASE), 1),
    ("hidden rules", re.compile(r"\bhidden\s+rules?\b", re.IGNORECASE), 2),
    ("unknown origin", re.compile(r"\b(?:an?\s+)?unknown\s+origin\b", re.IGNORECASE), 2),
    ("mysterious purpose", re.compile(r"\bmysterious\s+purpose\b", re.IGNORECASE), 2),
    ("resonance", re.compile(r"\breson(?:ance|ant|ates?|ating)\b", re.IGNORECASE), 1),
    ("infinite depth", re.compile(r"\binfinite\s+depth\b", re.IGNORECASE), 2),
    (
        "observers cannot explain",
        re.compile(
            r"\b(?:observers?|visitors?|participants?)\b[^.!?\n]{0,48}"
            r"\b(?:cannot|can't|could\s+not|are\s+unable\s+to)\s+explain\b",
            re.IGNORECASE,
        ),
        2,
    ),
    ("presence", re.compile(r"\bpresence\b", re.IGNORECASE), 1),
    ("balance", re.compile(r"\bbalance(?:d|s|ing)?\b", re.IGNORECASE), 1),
    ("hidden force", re.compile(r"\bhidden\s+force\b", re.IGNORECASE), 2),
)
_ORIGINALITY_THRESHOLD = 0.65

_DESCRIPTIVE_ONLY_REQUEST = re.compile(
    r"\b(?:do\s+not|don't|never)\s+explain\s+(?:how|why)\b|"
    r"\b(?:describe|show|present)\s+only\b|"
    r"\bonly\s+describe\b|\bno\s+explanation\b",
    re.IGNORECASE,
)
_EXPLANATORY_PATTERNS = (
    ("acting as", re.compile(r"\bact(?:s|ed|ing)?\s+as\b", re.IGNORECASE)),
    ("because", re.compile(r"\bbecause\b", re.IGNORECASE)),
    ("this allows", re.compile(r"\bthis\s+allows\b", re.IGNORECASE)),
    ("which enables", re.compile(r"\bwhich\s+enables\b", re.IGNORECASE)),
    ("it functions by", re.compile(r"\bit\s+functions\s+by\b", re.IGNORECASE)),
    ("it operates through", re.compile(r"\bit\s+operates\s+through\b", re.IGNORECASE)),
)
_SENTENCE = re.compile(r"[^.!?\n]+(?:[.!?]+|$)")

_STRUCTURE_REQUEST_MARKER = re.compile(
    r"\b(?:describe\s+only|output|return|include|provide|list|present)\b"
    r"[^\n:]{0,48}\b(?:fields?|sections?|items?|details?)\b\s*:?[ \t]*|"
    r"\b(?:required|requested)\s+(?:fields?|sections?|items?|details?)\b\s*:?[ \t]*|"
    r"\b(?:describe\s+only|output|return|include|provide|list|present)\b\s*:\s*",
    re.IGNORECASE,
)
_NUMBERED_SECTION = re.compile(r"^\s*(\d{1,2})[.)]\s*(.+?)\s*$")
_BULLETED_SECTION = re.compile(r"^\s*[-*\u2022]\s*(.+?)\s*$")
_NON_OUTPUT_HEADING = re.compile(
    r"^\s*(?:rules?|constraints?|restrictions?|exclusions?|requirements?)\s*:\s*$",
    re.IGNORECASE,
)
_CONSTRAINT_LIKE_ITEM = re.compile(
    r"^(?:do\s+not|don't|cannot|can't|must\s+not|should\s+not|"
    r"never|no\s+|avoid\b|without\b)",
    re.IGNORECASE,
)

_CREATIVE_INVENTION_REQUEST = re.compile(
    r"\b(?:invent|create|design|conceive|imagine|envision)\b"
    r"[^\n]{0,180}\b(?:method|phenomenon|organization|organisation|system|"
    r"concept|society|communication|material|place|world|experience|form)\b|"
    r"\b(?:original|impossible|abstract)\s+(?:invention|phenomenon|concept|"
    r"organization|organisation|system|method|experience)\b",
    re.IGNORECASE,
)
_ABSTRACT_SUBSTITUTION_PATTERNS = (
    ("asymmetry", re.compile(r"\basymmetr(?:y|ic|ical|ically)\b", re.IGNORECASE)),
    ("correspondence", re.compile(r"\bcorrespondence\b", re.IGNORECASE)),
    ("admissible", re.compile(r"\badmissib(?:le|ility)\b", re.IGNORECASE)),
    ("terms", re.compile(r"\bterms?\b", re.IGNORECASE)),
    ("clauses", re.compile(r"\bclauses?\b", re.IGNORECASE)),
    ("definitions", re.compile(r"\bdefinitions?\b|\bdefined\s+(?:as|by)\b", re.IGNORECASE)),
    ("relations", re.compile(r"\brelations?\b|\brelational\b", re.IGNORECASE)),
    ("structures", re.compile(r"\bstructures?\b|\bstructural\b", re.IGNORECASE)),
    ("states", re.compile(r"\bstates?\b", re.IGNORECASE)),
    ("conditions", re.compile(r"\bconditions?\b|\bconditional\b", re.IGNORECASE)),
    ("axioms", re.compile(r"\b(?:axioms?|axiomatic)\b", re.IGNORECASE)),
    ("equations", re.compile(r"\bequations?\b", re.IGNORECASE)),
    ("variables", re.compile(r"\bvariables?\b", re.IGNORECASE)),
    ("mappings", re.compile(r"\bmappings?\b", re.IGNORECASE)),
    ("functions", re.compile(r"\bfunctions?\b", re.IGNORECASE)),
    ("propositions", re.compile(r"\bpropositions?\b", re.IGNORECASE)),
    ("equivalence", re.compile(r"\bequivalen(?:ce|t)\b", re.IGNORECASE)),
    ("ontology", re.compile(r"\bontolog(?:y|ical)\b", re.IGNORECASE)),
    ("metaphysical", re.compile(r"\bmetaphysic(?:s|al)\b", re.IGNORECASE)),
)
_DEFINITION_SUBSTITUTE = re.compile(
    r"\b(?:is|becomes?)\s+(?:merely|simply|only|nothing\s+more\s+than)?\s*"
    r"(?:an?\s+)?(?:abstract\s+)?(?:definition|relation|structure|state|condition)\b|"
    r"\bdefined\s+(?:as|by)\b",
    re.IGNORECASE,
)
_CONCRETE_CREATION_TERMS = re.compile(
    r"\b(?:doorways?|doors?|routes?|roads?|paths?|rooms?|thresholds?|"
    r"members?|strangers?|objects?|surfaces?|garments?|vessels?|gardens?|"
    r"houses?|courts?|trails?|destinations?|duties|debts?|gifts?|creators?|"
    r"artists?|performers?|gestures?|works?|performances?|"
    r"opens?|closes?|arrives?|leaves?|enters?|carries|exchanges?|inherits?|"
    r"gathers?|returns?|crosses?|builds?|breaks?|joins?|performs?|removes?|"
    r"passes?|alters?)\b",
    re.IGNORECASE,
)

_ART_PROCESS_TERMS = re.compile(
    r"\b(?:creators?|artists?|performers?|make|makes|made|create|creates|"
    r"arrange|arranges|compose|composes|layer|layers|fold|folds|cut|cuts|"
    r"paint|paints|perform|performs|repeat|repeats|stage|stages|assemble|"
    r"alter|alters|remove|removes|pass|passes)\b",
    re.IGNORECASE,
)
_ART_FORM_TERMS = re.compile(
    r"\b(?:art|medium|work|performance|composition|ritual|installation|"
    r"practice|piece|gesture|movement)\b",
    re.IGNORECASE,
)
_COMMUNICATION_METHOD_TERMS = re.compile(
    r"\b(?:participants?|sender|receiver|offer|offers|accept|accepts|reply|"
    r"answer|answers|convey|conveys|message|exchange|exchanges|transfer|"
    r"signal|delivery|confirm|confirms|acknowledge|completion)\b",
    re.IGNORECASE,
)
_COMMUNICATION_RECOGNITION_TERMS = re.compile(
    r"\b(?:confirm|confirms|confirmation|acknowledge|acknowledgement|receipt|"
    r"delivery|answer|reply|completion|completed|matched|both\s+participants)\b",
    re.IGNORECASE,
)
_COMMUNICATION_ACTION_TERMS = re.compile(
    r"\b(?:offer|offers|accept|accepts|reply|answer|convey|conveys|message|"
    r"exchange|exchanges|transfer|signal|delivery|confirm|confirms|"
    r"acknowledge|completion)\b",
    re.IGNORECASE,
)
_PHENOMENON_TERMS = re.compile(
    r"\b(?:phenomenon|occurs?|occurrence|event|anomaly|appears?|vanishes?|"
    r"changes?|reverses?|repeats?|transforms?|transformation|opens?|closes?|impossible|"
    r"suddenly|always)\b",
    re.IGNORECASE,
)
_ORGANIZATION_TERMS = re.compile(
    r"\b(?:members?|membership|duties|roles?|rules?|groups?|joins?|leaves?|"
    r"inherits?|obligations?|council|house)\b",
    re.IGNORECASE,
)
_LOCATION_DOMINANT_TERMS = re.compile(
    r"\b(?:realm|environment|domain|place|city|room|landscape|world|chamber)\b",
    re.IGNORECASE,
)
_MEANINGFUL_PLACEHOLDER = re.compile(
    r"^\s*(?:unknown|none|not\s+applicable|same\s+as\s+above|unspecified|"
    r"something\s+happens?|it\s+occurs?)\.?\s*$",
    re.IGNORECASE,
)

_CONSTRAINT_REFUSAL = re.compile(
    r"\b(?:could not|cannot|can't|unable to)\s+(?:complete|create|generate|"
    r"satisfy|fulfill)|\bimpossible to satisfy\b",
    re.IGNORECASE,
)

_GENUINE_CONTRADICTION = re.compile(
    r"\btriangle\b[^.\n]{0,80}\b(?:four|4)\s+sides?\b|"
    r"\bboth\s+exists?\s+and\s+(?:does\s+not|cannot|can't)\s+exist"
    r"(?:\s+simultaneously)?\b",
    re.IGNORECASE,
)


def detect_creative_intent(user_input: str) -> str | None:
    """Return the strongest creative route supported by the request text."""

    text = str(user_input or "").strip()
    if not text:
        return None
    if (
        _ROLEPLAY_REQUEST.search(text)
        or _EXPLICIT_WORLDBUILDING_REQUEST.search(text)
        or _PURE_IMAGINATION_REQUEST.search(text)
        or _ABSTRACT_INVENTION_REQUEST.search(text)
        or _WORLD_BUILDING_REQUEST.search(text)
    ):
        return "creative_writing"
    if _CREATIVE_IDEATION_REQUEST.search(text):
        return "creative_ideation"
    if _EXPLICIT_ART_INVENTION.search(text) or _NEVER_EXISTED_CREATION.search(text):
        return "creative_ideation"
    return None


def creative_generation_guidance(has_forbidden_concepts: bool = False) -> str:
    """Build compact generation guidance from general novelty principles."""

    guidance = (
        "CREATIVE CALIBRATION: Build originality from a non-obvious governing "
        "mechanism and its consequences, not from familiar labels with cosmetic "
        "changes. Develop interacting relationships, systems, social structures, "
        "materials, or behaviors as relevant. Preserve internal consistency: each "
        "major feature needs understandable cause and effect, and all parts must "
        "remain compatible with the premise."
    )
    if has_forbidden_concepts:
        guidance += (
            " Treat every explicit exclusion in the request as a hard constraint. "
            "Do not use, rename, negate, or reframe an excluded concept as part of "
            "the answer. Exclusions are generative boundaries, not a reason to "
            "refuse: when familiar categories are removed, increase abstraction "
            "through unfamiliar structures, nonphysical concepts, environments, "
            "or experiences. Silently check the completed answer against the "
            "excluded categories before responding."
        )
    return guidance


def _clean_constraint_item(value: str) -> str:
    item = _LEADING_LIST_MARKER.sub("", str(value or "").strip())
    item = re.sub(r"^(?:any\s+of\s+|any\s+|the\s+following\s*:?[ \t]*)", "", item, flags=re.IGNORECASE)
    item = item.strip(" \t\r\n.:,;()[]{}\"'")
    return re.sub(r"\s+", " ", item)


def _constraint_items(value: str) -> list[str]:
    cleaned = _clean_constraint_item(value)
    if not cleaned:
        return []
    parts = [_clean_constraint_item(part) for part in _LIST_SEPARATOR.split(cleaned)]
    return [part for part in parts if part and len(_WORD.findall(part)) <= 5]


def extract_forbidden_concepts(user_input: str) -> tuple[str, ...]:
    """Extract explicit negative concepts, including newline-delimited lists."""

    lines = str(user_input or "").replace("\r\n", "\n").split("\n")
    concepts: list[str] = []
    collecting_list = False

    for raw_line in lines:
        line = raw_line.strip()
        no_items = [
            match.group(1)
            for match in _INLINE_NO_CONSTRAINT.finditer(line)
        ]
        if no_items:
            for item in no_items:
                concepts.extend(_constraint_items(item))
            continue

        marker = _CONSTRAINT_MARKER.search(line)
        if marker:
            tail = marker.group(1).strip()
            concepts.extend(_constraint_items(tail))
            collecting_list = not tail
            continue

        if not collecting_list:
            continue
        if not line:
            continue

        candidate = _clean_constraint_item(line)
        word_count = len(_WORD.findall(candidate))
        looks_like_item = bool(candidate) and word_count <= 5
        if not looks_like_item:
            collecting_list = False
            continue
        concepts.extend(_constraint_items(candidate))

    return tuple(dict.fromkeys(concept.casefold() for concept in concepts))


def _clean_section_label(value: str) -> str:
    label = re.sub(r"[*_`#]+", "", str(value or "")).strip()
    label = label.strip(" \t\r\n.:;,-\u2013\u2014()[]{}\"'")
    return re.sub(r"\s+", " ", label)


def _inline_numbered_sections(value: str) -> list[tuple[int, str]]:
    pattern = re.compile(
        r"(?:^|\s)(\d{1,2})[.)]\s*(.+?)(?=\s+\d{1,2}[.)]\s|$)"
    )
    return [
        (int(match.group(1)), _clean_section_label(match.group(2)))
        for match in pattern.finditer(str(value or ""))
        if _clean_section_label(match.group(2))
    ]


def extract_required_creative_sections(
    user_input: str,
) -> tuple[tuple[int, str], ...]:
    """Extract an explicitly requested multi-field creative response shape."""

    lines = str(user_input or "").replace("\r\n", "\n").split("\n")
    sections: list[tuple[int, str]] = []
    active = False

    for raw_line in lines:
        line = raw_line.strip()
        marker = _STRUCTURE_REQUEST_MARKER.search(line)
        if marker:
            active = True
            tail = line[marker.end():].strip()
            sections.extend(_inline_numbered_sections(tail))
            continue
        if not active:
            continue
        if _NON_OUTPUT_HEADING.match(line):
            break
        if not line:
            continue

        numbered = _NUMBERED_SECTION.match(line)
        if numbered:
            label = _clean_section_label(numbered.group(2))
            if label and not _CONSTRAINT_LIKE_ITEM.match(label):
                sections.append((int(numbered.group(1)), label))
            continue

        bulleted = _BULLETED_SECTION.match(line)
        if bulleted:
            label = _clean_section_label(bulleted.group(1))
            if label and not _CONSTRAINT_LIKE_ITEM.match(label):
                sections.append((len(sections) + 1, label))
            continue

        if sections:
            break

    if len(sections) >= 2:
        return tuple(dict.fromkeys(sections))

    # Also support a bare numbered field request without a "provide/include"
    # marker. Runs introduced by Rules/Constraints headings are intentionally
    # ignored so numbered exclusions cannot become output requirements.
    candidate_runs: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    previous_nonblank = ""
    blocked_run = False
    for raw_line in lines:
        line = raw_line.strip()
        match = _NUMBERED_SECTION.match(line)
        if match:
            if not current:
                blocked_run = bool(_NON_OUTPUT_HEADING.match(previous_nonblank))
            label = _clean_section_label(match.group(2))
            if not blocked_run and label and not _CONSTRAINT_LIKE_ITEM.match(label):
                current.append((int(match.group(1)), label))
            continue
        if current:
            candidate_runs.append(current)
            current = []
        blocked_run = False
        if line:
            previous_nonblank = line
    if current:
        candidate_runs.append(current)

    for candidate in candidate_runs:
        if len(candidate) >= 2:
            return tuple(dict.fromkeys(candidate))
    return ()


def _semantic_root(word: str) -> str:
    normalized = word.casefold()
    if len(normalized) > 4 and normalized.endswith("ies"):
        normalized = normalized[:-3] + "y"
    elif len(normalized) > 4 and normalized.endswith("s"):
        normalized = normalized[:-1]
    if len(normalized) > 4 and normalized.endswith(("e", "y")):
        normalized = normalized[:-1]
    return normalized


def _concept_occurs(concept: str, response_text: str) -> bool:
    concept_words = _WORD.findall(concept.casefold())
    response_words = _WORD.findall(str(response_text or "").casefold())
    if not concept_words or not response_words:
        return False

    roots = [_semantic_root(word) for word in concept_words]
    for start in range(0, len(response_words) - len(roots) + 1):
        matches = True
        for offset, root in enumerate(roots):
            candidate = _semantic_root(response_words[start + offset])
            if len(root) >= 4:
                matches = len(candidate) >= 4 and (
                    candidate.startswith(root) or root.startswith(candidate)
                )
            else:
                matches = candidate == root
            if not matches:
                break
        if matches:
            return True
    return False


def _related_forbidden_terms(concept: str) -> tuple[str, ...]:
    """Return the compact semantic group for an explicitly banned category."""

    matches: list[str] = []
    for category_names, related_terms in _FORBIDDEN_SEMANTIC_CATEGORIES:
        category_terms = category_names + related_terms
        if any(_concept_occurs(term, concept) for term in category_terms):
            matches.extend(category_terms)
    return tuple(dict.fromkeys(matches))


def _multi_restriction_related_terms(concept: str) -> tuple[str, ...]:
    matches: list[str] = []
    for category_names, related_terms in _MULTI_RESTRICTION_SEMANTIC_EXTENSIONS:
        category_terms = category_names + related_terms
        if any(_concept_occurs(term, concept) for term in category_terms):
            matches.extend(category_terms)
    return tuple(dict.fromkeys(matches))


def _semantic_equivalent_occurs(term: str, response_text: str) -> bool:
    # "Being" is also a common verb, so only treat it as a creature synonym
    # when it is used as a noun. Other terms in these compact groups are not
    # meaningfully ambiguous in the creative-constraint cases they cover.
    if term == "being":
        return bool(
            re.search(
                r"\b(?:a|an|the|another|living|sentient)\s+beings?\b|"
                r"\bbeings\b",
                str(response_text or ""),
                re.IGNORECASE,
            )
        )
    return _concept_occurs(term, response_text)


def creative_constraints_are_impossible(user_input: str) -> bool:
    """Identify explicit logical contradictions, not merely many exclusions."""

    return bool(_GENUINE_CONTRADICTION.search(str(user_input or "")))


def is_creative_constraint_refusal(response_text: str) -> bool:
    """Recognize a model refusal caused by restrictive creative exclusions."""

    return bool(_CONSTRAINT_REFUSAL.search(str(response_text or "")))


@dataclass(frozen=True)
class CreativeConstraintValidation:
    """Result of a transient, deterministic forbidden-concept check."""

    forbidden_concepts: tuple[str, ...]
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations


@dataclass(frozen=True)
class CreativeOriginalityValidation:
    """Result of a small lexical heuristic for generic abstraction reliance."""

    score: float
    threshold: float
    generic_tropes: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return self.score >= self.threshold


@dataclass(frozen=True)
class DescriptiveOnlyValidation:
    """Result of checking an explicit description-only output requirement."""

    requested: bool
    explanatory_phrases: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.explanatory_phrases


@dataclass(frozen=True)
class CreativeStructureValidation:
    """Result of checking explicitly requested creative response sections."""

    required_sections: tuple[tuple[int, str], ...]
    missing_sections: tuple[str, ...]

    @property
    def requested(self) -> bool:
        return bool(self.required_sections)

    @property
    def passed(self) -> bool:
        return not self.missing_sections


@dataclass(frozen=True)
class CreativeInventionQualityValidation:
    """Contextual check that an invention is more than abstract terminology."""

    evaluated: bool
    issues: tuple[str, ...]
    abstract_terms: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.issues


@dataclass(frozen=True)
class CreativeCategoryValidation:
    """Checks that a highly constrained invention remains the requested kind."""

    requested_category: str | None
    evaluated: bool
    issues: tuple[str, ...]
    duplicate_sections: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.issues


def validate_creative_constraints(
    user_input: str,
    response_text: str,
) -> CreativeConstraintValidation:
    """Check output for explicit exclusions with lightweight word semantics."""

    forbidden = extract_forbidden_concepts(user_input)
    expanded_semantics = len(forbidden) >= 2
    violations = tuple(
        concept
        for concept in forbidden
        if _concept_occurs(concept, response_text)
        or any(
            _semantic_equivalent_occurs(related_term, response_text)
            for related_term in _related_forbidden_terms(concept)
        )
        or (
            expanded_semantics
            and any(
                _semantic_equivalent_occurs(related_term, response_text)
                for related_term in _multi_restriction_related_terms(concept)
            )
        )
    )
    return CreativeConstraintValidation(forbidden, violations)


def validate_creative_originality(
    response_text: str,
) -> CreativeOriginalityValidation:
    """Score repeated stock abstractions without invoking another model."""

    text = str(response_text or "")
    reliance = 0
    matches: list[str] = []
    for label, pattern, weight in _GENERIC_ABSTRACTION_PATTERNS:
        occurrences = min(2, len(pattern.findall(text)))
        if occurrences:
            matches.append(label)
            reliance += weight * occurrences

    # Three low-weight tropes, a strong trope plus another trope, or repeated
    # strong phrasing crosses the threshold. A single incidental use does not.
    score = round(max(0.0, 1.0 - (reliance / 8.0)), 3)
    return CreativeOriginalityValidation(
        score=score,
        threshold=_ORIGINALITY_THRESHOLD,
        generic_tropes=tuple(matches),
    )


def validate_descriptive_only(
    user_input: str,
    response_text: str,
) -> DescriptiveOnlyValidation:
    """Detect explanation markers only when the request explicitly forbids them."""

    requested = bool(_DESCRIPTIVE_ONLY_REQUEST.search(str(user_input or "")))
    if not requested:
        return DescriptiveOnlyValidation(False, ())
    violations = tuple(
        label
        for label, pattern in _EXPLANATORY_PATTERNS
        if pattern.search(str(response_text or ""))
    )
    return DescriptiveOnlyValidation(True, violations)


def _normalized_section_label(value: str) -> str:
    return " ".join(_WORD.findall(_clean_section_label(value).casefold()))


def _response_contains_section(
    response_text: str,
    number: int,
    label: str,
) -> bool:
    required = _normalized_section_label(label)
    if not required:
        return False

    for raw_line in str(response_text or "").replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        numbered = _NUMBERED_SECTION.match(line)
        if numbered and int(numbered.group(1)) == number:
            actual = _normalized_section_label(numbered.group(2))
            if actual == required or actual.startswith(required + " "):
                return True

        # Named Markdown headings and label/value lines also preserve separate
        # sections even when the model omits the requested list numbering.
        plain = re.sub(r"^[#*`_\-\u2022\s]+", "", line)
        label_match = re.match(r"^(.+?)(?:\s*[:\-\u2013\u2014]\s*|$)", plain)
        if label_match:
            actual = _normalized_section_label(label_match.group(1))
            if actual == required:
                return True
    return False


def validate_creative_structure(
    user_input: str,
    response_text: str,
) -> CreativeStructureValidation:
    """Require every requested field to occupy its own labeled section."""

    required = extract_required_creative_sections(user_input)
    missing = tuple(
        label
        for number, label in required
        if not _response_contains_section(response_text, number, label)
    )
    return CreativeStructureValidation(required, missing)


def _abstract_substitution_terms(response_text: str) -> tuple[str, ...]:
    return tuple(
        label
        for label, pattern in _ABSTRACT_SUBSTITUTION_PATTERNS
        if pattern.search(str(response_text or ""))
    )


def _section_value(
    response_text: str,
    number: int,
    label: str,
) -> str:
    lines = str(response_text or "").replace("\r\n", "\n").split("\n")
    required = _normalized_section_label(label)
    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        numbered = _NUMBERED_SECTION.match(line)
        content = numbered.group(2).strip() if numbered else line
        if numbered and int(numbered.group(1)) != number:
            continue
        plain = re.sub(r"^[#*`_\-\u2022\s]+", "", content)
        parts = re.split(r"\s*[:\u2013\u2014]\s*", plain, maxsplit=1)
        if _normalized_section_label(parts[0]) != required:
            continue
        if len(parts) == 2 and parts[1].strip():
            return parts[1].strip()
        for following in lines[index + 1:]:
            if following.strip():
                return following.strip()
    return ""


def _meaningful_invented_name(value: str) -> bool:
    normalized = _normalized_section_label(value)
    if not normalized or normalized in {
        "unnamed", "unknown", "none", "the concept", "the phenomenon",
        "the system", "the organization", "the organisation", "the method",
    }:
        return False
    return bool(re.search(r"[a-z]{3,}", normalized, re.IGNORECASE))


def validate_creative_invention_quality(
    user_input: str,
    response_text: str,
) -> CreativeInventionQualityValidation:
    """Reject abstract substitution only when it displaces an invention."""

    request = str(user_input or "")
    response = str(response_text or "")
    if not _CREATIVE_INVENTION_REQUEST.search(request):
        return CreativeInventionQualityValidation(False, (), ())

    abstract_terms = _abstract_substitution_terms(response)
    concrete_count = len(_CONCRETE_CREATION_TERMS.findall(response))
    issues: list[str] = []
    abstract_substitution = len(abstract_terms) >= 3 and concrete_count < 2
    if abstract_substitution:
        issues.append("abstract terminology replaced the requested invention")
    if (
        _DEFINITION_SUBSTITUTE.search(response)
        and len(abstract_terms) >= 2
        and concrete_count < 2
    ):
        issues.append("the response defined an abstraction instead of creating one")

    required = extract_required_creative_sections(request)
    forbidden_count = len(extract_forbidden_concepts(request))
    strict_completion = bool(required) and (
        forbidden_count >= 4 or abstract_substitution
    )
    if strict_completion:
        values = {
            _normalized_section_label(label): _section_value(
                response, number, label
            )
            for number, label in required
        }
        substantive_words = sum(len(_WORD.findall(value)) for value in values.values())
        if substantive_words < max(18, len(required) * 4):
            issues.append("the invention lacks descriptive substance")

        for label, value in values.items():
            value_words = len(_WORD.findall(value))
            value_concrete = len(_CONCRETE_CREATION_TERMS.findall(value))
            value_abstract = len(_abstract_substitution_terms(value))
            if any(token in label for token in ("name", "title", "identity")):
                if not _meaningful_invented_name(value):
                    issues.append("the invention lacks a distinct identity or name")
            elif any(token in label for token in ("experience", "encounter", "manifestation")):
                if value_words < 7 or (value_abstract >= 2 and not value_concrete):
                    issues.append("the encounter experience is not concrete enough")
            elif any(token in label for token in ("limitation", "limit", "weakness")):
                if value_words < 6 or not value_concrete:
                    issues.append("the limitation is not meaningful")
            elif any(token in label for token in ("mystery", "unresolved", "question")):
                if value_words < 7 or not value_concrete:
                    issues.append("the mystery is not meaningfully described")

    return CreativeInventionQualityValidation(
        True,
        tuple(dict.fromkeys(issues)),
        abstract_terms,
    )


def _requested_invention_category(user_input: str) -> str | None:
    request = str(user_input or "")
    if re.search(
        r"\b(?:art\s+form|artistic\s+medium|creative\s+medium)\b",
        request,
        re.IGNORECASE,
    ):
        return "art_form"
    if re.search(
        r"\b(?:method|form|mode|system)\s+of\s+communication\b|"
        r"\bcommunication\s+(?:method|form|mode|system)\b",
        request,
        re.IGNORECASE,
    ):
        return "communication_method"
    if re.search(r"\bphenomenon\b", request, re.IGNORECASE):
        return "phenomenon"
    if re.search(
        r"\b(?:organization|organisation|society|institution)\b",
        request,
        re.IGNORECASE,
    ):
        return "organization"
    if re.search(r"\b(?:place|world|realm|environment)\b", request, re.IGNORECASE):
        return "place"
    return None


def _section_signature(value: str) -> set[str]:
    stopwords = {
        "a", "an", "and", "as", "at", "by", "each", "for", "from",
        "in", "is", "it", "of", "on", "one", "only", "or", "the",
        "their", "to", "with",
    }
    return {
        word.casefold()
        for word in _WORD.findall(str(value or ""))
        if word.casefold() not in stopwords
    }


def validate_creative_category(
    user_input: str,
    response_text: str,
) -> CreativeCategoryValidation:
    """Validate category fidelity and section distinctness contextually."""

    request = str(user_input or "")
    category = _requested_invention_category(request)
    # These checks target the highly constrained failure mode. Ordinary prose
    # is not subjected to a global creative-category vocabulary requirement.
    if category is None or len(extract_forbidden_concepts(request)) < 2:
        return CreativeCategoryValidation(category, False, (), ())

    required = extract_required_creative_sections(request)
    section_values = [
        (label, _section_value(response_text, number, label))
        for number, label in required
    ]
    body = "\n".join(value for _, value in section_values) if required else str(response_text or "")
    issues: list[str] = []
    duplicates: list[str] = []

    for label, value in section_values:
        normalized_label = _normalized_section_label(label)
        words = _WORD.findall(value)
        is_name = any(
            token in normalized_label for token in ("name", "title", "identity")
        )
        if (
            not value.strip()
            or _MEANINGFUL_PLACEHOLDER.match(value)
            or (not is_name and len(words) < 4)
        ):
            issues.append(f"required field lacks meaningful content: {label}")

    signatures = [
        (label, _section_signature(value))
        for label, value in section_values
        if value.strip()
    ]
    for index, (label, signature) in enumerate(signatures):
        for previous_label, previous_signature in signatures[:index]:
            union = signature | previous_signature
            similarity = len(signature & previous_signature) / len(union) if union else 1.0
            if signature == previous_signature or (
                min(len(signature), len(previous_signature)) >= 4
                and similarity >= 0.8
            ):
                duplicates.append(f"{previous_label} / {label}")
    if duplicates:
        issues.append("numbered sections repeat the same information")

    if category == "art_form":
        if len(_ART_PROCESS_TERMS.findall(body)) < 2 or not _ART_FORM_TERMS.search(body):
            issues.append("the response is a scene or event, not a repeatable art form")
    elif category == "communication_method":
        if (
            len(_COMMUNICATION_METHOD_TERMS.findall(body)) < 2
            or not _COMMUNICATION_ACTION_TERMS.search(body)
        ):
            issues.append("the response is an occurrence, not a communication method")
    elif category == "phenomenon":
        if len(_PHENOMENON_TERMS.findall(body)) < 2:
            issues.append("the response describes a place or object, not a phenomenon")
    elif category == "organization":
        if len(_ORGANIZATION_TERMS.findall(body)) < 2:
            issues.append("the response does not describe an organization")

    for label, value in section_values:
        normalized_label = _normalized_section_label(label)
        if (
            category == "art_form"
            and "creator" in normalized_label
            and any(token in normalized_label for token in ("make", "create", "process"))
            and len(_ART_PROCESS_TERMS.findall(value)) < 2
        ):
            issues.append("How creators make it lacks a creation process")
        if (
            category == "communication_method"
            and (
                "communication occurred" in normalized_label
                or "participants know" in normalized_label
                or "recognition" in normalized_label
            )
            and (
                not _COMMUNICATION_RECOGNITION_TERMS.search(value)
                or not _COMMUNICATION_ACTION_TERMS.search(value)
            )
        ):
            issues.append(
                "communication recognition field describes only an occurrence"
            )
        if any(token in normalized_label for token in ("experience", "encounter")):
            location_count = len(_LOCATION_DOMINANT_TERMS.findall(value))
            action_count = (
                len(_ART_PROCESS_TERMS.findall(value))
                + len(_COMMUNICATION_METHOD_TERMS.findall(value))
                + len(_PHENOMENON_TERMS.findall(value))
            )
            if category != "place" and location_count and not action_count:
                issues.append("encounter field became a location instead of the invention")

    return CreativeCategoryValidation(
        category,
        True,
        tuple(dict.fromkeys(issues)),
        tuple(dict.fromkeys(duplicates)),
    )


def remove_explanatory_sentences(response_text: str) -> str:
    """Remove marked explanatory sentences after the sole model revision is spent."""

    retained_lines = []
    for raw_line in str(response_text or "").replace("\r\n", "\n").split("\n"):
        retained_sentences = []
        for match in _SENTENCE.finditer(raw_line):
            sentence = match.group(0).strip()
            if sentence and not any(
                pattern.search(sentence) for _, pattern in _EXPLANATORY_PATTERNS
            ):
                retained_sentences.append(sentence)
        if retained_sentences:
            retained_lines.append(" ".join(retained_sentences))
    return "\n".join(retained_lines).strip()


def _fallback_profile(user_input: str) -> str:
    request = str(user_input or "")
    if re.search(
        r"\b(?:art\s+form|artistic\s+medium|creative\s+medium)\b",
        request,
        re.IGNORECASE,
    ):
        return "art_form"
    if re.search(r"\bcommunicat(?:e|es|ed|ing|ion)\b", request, re.IGNORECASE):
        return "communication"
    if re.search(
        r"\b(?:organization|organisation|society|civic|membership)\b",
        request,
        re.IGNORECASE,
    ):
        return "organization"
    return "phenomenon"


def _structured_fallback_value(label: str, profile: str) -> str:
    normalized = _normalized_section_label(label)
    if any(word in normalized for word in ("name", "title")):
        return {
            "art_form": "The Borrowed Gesture.",
            "communication": "The Borrowed Crossing.",
            "organization": "The Unfinished House.",
            "phenomenon": "The Elsewake.",
        }[profile]
    if "constant" in normalized:
        return {
            "art_form": "Every version keeps one gesture inherited from its first creator.",
            "communication": "The exchanged routes always end at the same sealed doorway.",
            "organization": "No member completes the duty first received.",
            "phenomenon": "The doorway always returns to the room behind it.",
        }[profile]
    if any(word in normalized for word in ("changing", "variable", "variation")):
        return {
            "art_form": "Each creator removes one inherited gesture and contributes another.",
            "communication": "The destination behind the doorway differs for every pair.",
            "organization": "The membership groups change with the duties left unfinished.",
            "phenomenon": "A different object changes owners whenever the door opens.",
        }[profile]
    if any(word in normalized for word in ("limitation", "limit", "weakness")):
        return {
            "art_form": "A creator may alter only one gesture in the work.",
            "communication": "Each exchange distinguishes only departure from return.",
            "organization": "A member may carry only one inherited duty.",
            "phenomenon": "The doorway appears only in rooms containing something borrowed.",
        }[profile]
    if any(word in normalized for word in ("mystery", "unresolved", "question")):
        return {
            "art_form": (
                "Some finished works contain a gesture that no participating "
                "creator contributed."
            ),
            "communication": (
                "A third doorway sometimes arrives, opening toward a destination "
                "claimed by neither route."
            ),
            "organization": (
                "Some duties return bearing the names of strangers who never "
                "entered the House."
            ),
            "phenomenon": (
                "One returned object always belongs to a stranger who never "
                "entered the room."
            ),
        }[profile]
    if (
        profile == "art_form"
        and "creator" in normalized
        and any(token in normalized for token in ("make", "create", "process"))
    ):
        return (
            "Each creator performs one inherited gesture, removes another, and "
            "passes the unfinished work to the next creator."
        )
    if (
        "communication occurred" in normalized
        or "participants know" in normalized
        or "confirmation" in normalized
    ):
        return (
            "Both participants confirm completion when the offered route closes "
            "and the accepting route opens at its former destination."
        )
    if any(word in normalized for word in ("experience", "encounter", "encountered")):
        return {
            "art_form": (
                "The audience encounters a performance of altered gestures, each "
                "retaining one movement from an earlier work."
            ),
            "communication": (
                "One participant offers a destination by leaving a route; the "
                "other accepts when a different route inherits that destination."
            ),
            "organization": (
                "A newcomer receives a half-completed duty from a stranger and "
                "leaves a different duty behind."
            ),
            "phenomenon": (
                "A locked doorway opens into the room it has just left, with one "
                "object now belonging to a stranger."
            ),
        }[profile]
    if any(word in normalized for word in ("member", "membership", "organization")):
        return "Each member inherits one unfinished duty and leaves another behind."
    return {
        "art_form": "Creators exchange altered gestures as a repeatable performance.",
        "communication": "Two routes exchange their destinations at a sealed doorway.",
        "organization": "Members exchange unfinished duties with strangers.",
        "phenomenon": "A returned object belongs to someone who never entered the room.",
    }[profile]


def _build_structured_fallback(
    required_sections: tuple[tuple[int, str], ...],
    profile: str,
) -> str:
    return "\n".join(
        f"{number}. {label}: {_structured_fallback_value(label, profile)}"
        for number, label in required_sections
    )


def build_abstract_constraint_fallback(user_input: str) -> str:
    """Return a constraint-safe abstract concept after one failed model revision."""

    required_sections = extract_required_creative_sections(user_input)
    if required_sections:
        structured = _build_structured_fallback(
            required_sections,
            _fallback_profile(user_input),
        )
        if validate_creative_constraints(user_input, structured).passed:
            return structured

        # Structure is a hard output requirement. Keep it even in the unusual
        # contradictory case where a requested heading itself names an excluded
        # concept; collapsing to one sentence would compound the failure.
        return "\n".join(
            f"{number}. {label}: Aruveth."
            for number, label in required_sections
        )

    profile = _fallback_profile(user_input)
    concrete_candidate = {
        "art_form": (
            "The Borrowed Gesture is a repeatable performance passed between "
            "creators. Each creator performs one inherited gesture, removes "
            "another, and passes the unfinished work onward. A finished piece may "
            "contain a gesture that none of its creators contributed."
        ),
        "communication": (
            "The Borrowed Crossing begins when one participant offers a destination "
            "by leaving a route and the other accepts through a different route. "
            "Both participants confirm completion when the first route closes and "
            "the accepting route opens at its former destination. Each exchange "
            "distinguishes only departure from return."
        ),
        "organization": (
            "The Unfinished House gives each member a half-completed duty inherited "
            "from a stranger. No member completes the duty first received, and "
            "membership groups change around the duties left behind. Some duties "
            "return bearing names from strangers who never entered the House."
        ),
        "phenomenon": (
            "The Elsewake begins when a locked doorway opens into the room it has "
            "just left and one object has changed owners. It appears only in rooms "
            "containing something borrowed. One returned object always belongs to "
            "a stranger who never entered the room."
        ),
    }[profile]

    candidates = (
        concrete_candidate,
        (
            "Velu is asymmetric mutual definition rendered as seven incompatible "
            "clauses. No clause stands alone; every pairing yields a distinct "
            "reading without resolving the contradiction."
        ),
        (
            "The result is a recurring agreement among locations. Each location "
            "changes which paths remain possible, and the resulting sequence "
            "distributes needs, settles disputes, and preserves shared customs. "
            "Participation in the sequence replaces membership in any familiar "
            "category, while relationships renew the whole whenever the "
            "arrangement changes."
        ),
        (
            "It is an abstract arrangement of intervals and relationships. A "
            "change in one interval alters the choices available in the next, "
            "creating coherent customs, exchanges, and consequences without "
            "relying on any excluded category."
        ),
        (
            "Oru is a self-consistent pattern of differences: each difference "
            "reorders the next, so continuity emerges from sequence alone."
        ),
    )
    for candidate in candidates:
        if validate_creative_constraints(user_input, candidate).passed:
            return candidate
    # A coined minimal concept remains generative while avoiding a blanket
    # refusal even when the request excludes unusually broad vocabulary.
    return "Oru: a self-consistent relation whose next state follows from its last."


def build_constraint_revision_prompt(
    user_input: str,
    draft_response: str,
    violations: tuple[str, ...],
    generic_tropes: tuple[str, ...] = (),
    explanatory_phrases: tuple[str, ...] = (),
    required_sections: tuple[tuple[int, str], ...] = (),
    missing_sections: tuple[str, ...] = (),
    invention_quality_issues: tuple[str, ...] = (),
    category_quality_issues: tuple[str, ...] = (),
    restrictive_refusal: bool = False,
) -> str:
    """Build one bounded corrective request; callers must not retry in a loop."""

    findings = []
    if violations:
        findings.append(
            "The draft used explicitly excluded concepts: "
            + ", ".join(violations)
        )
    if generic_tropes:
        findings.append(
            "The draft relied too heavily on generic abstract-fiction tropes: "
            + ", ".join(generic_tropes)
        )
    if explanatory_phrases:
        findings.append(
            "The draft violated the description-only instruction with explanatory "
            "phrasing: " + ", ".join(explanatory_phrases)
        )
    if missing_sections:
        findings.append(
            "The draft omitted or collapsed required output sections: "
            + ", ".join(missing_sections)
        )
    if invention_quality_issues:
        findings.append(
            "The draft did not feel like a completed invention: "
            + "; ".join(invention_quality_issues)
        )
    if category_quality_issues:
        findings.append(
            "The draft did not match the requested invention category: "
            + "; ".join(category_quality_issues)
        )
    if restrictive_refusal:
        findings.append(
            "The draft refused a restrictive but achievable creative request."
        )
    correction = "\n".join(findings) or "The draft needs one creative-quality revision."
    constraint_guidance = ""
    if violations or restrictive_refusal:
        constraint_guidance = """
Replace the underlying mechanics, not merely the forbidden words. The revised
answer must not mention, rename, negate, or imply those excluded concepts.
Treat the exclusions as an invitation to increase abstraction through an
unfamiliar structure, nonphysical concept, environment, or experience; do not
refuse merely because common categories have been removed.
""".strip()
    structure_guidance = ""
    if required_sections:
        template = "\n".join(
            f"{number}. {label}: <description>"
            for number, label in required_sections
        )
        structure_guidance = f"""
Preserve the requested response structure exactly. Return every field as its
own numbered section, in this order, with no omitted or merged fields:
{template}
""".strip()
    category_guidance = ""
    if category_quality_issues:
        category_guidance = """
Keep the invention in the requested category. An art form needs a repeatable
creative process; a communication method needs an exchange and recognizable
completion; a phenomenon needs a recurring occurrence or change rather than a
setting, object, or creature. Give every numbered section distinct, meaningful
information and do not repeat one description under multiple headings.
""".strip()
    return f"""
Revise the draft once so it fully answers the original creative request.

ORIGINAL REQUEST:
{user_input}

DRAFT TO REVISE:
{draft_response}

{correction}

{constraint_guidance}
{structure_guidance}
{category_guidance}
Avoid generic abstract-fiction clichés, including equilibrium, hidden rules,
unknown origins, mysterious purposes, resonance, infinite depth, inexplicable
observers, presence, balance, and hidden forces. Build a genuinely novel
conceptual structure with specific relationships and consequences. Do not use
philosophical, mathematical, definitional, or logical terminology as a
substitute for the requested creation. Give the invention a distinct identity,
a clear encounter, a meaningful limitation, and a specific unresolved mystery
where those fields are requested. If the
request says not to explain how it works or asks for description only, use only
descriptive statements and omit causal or functional explanation. Preserve
internal consistency and all other requested constraints. Return only the
complete revised answer.
""".strip()
