"""Optional presentation metadata for ordinary chat responses."""


def build_choice_response_metadata(response_text: str) -> dict | None:
    """Attach buttons only to the known structured action-choice response."""

    text = str(response_text or "")
    expected_choices = (
        "1. Open project folder",
        "2. Show files",
        "3. Search project",
        "4. Explain manually",
    )
    if (
        "Please choose an action:" not in text
        or not all(choice in text for choice in expected_choices)
    ):
        return None

    return {
        "type": "choice_buttons",
        "options": [
            {"label": "Open Project Folder", "value": "Open project folder"},
            {"label": "Show Files", "value": "Show files"},
            {"label": "Search Project", "value": "Search project"},
            {"label": "Explain Manually", "value": "Explain manually"},
            {
                "label": "Other",
                "value": "",
                "behavior": "custom_input",
            },
        ],
    }
