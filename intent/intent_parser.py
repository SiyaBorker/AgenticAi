import ollama
import json
import re

# ----------------------------------
# ✅ 1️⃣ Allowed Extensions (Safety Layer)
# ----------------------------------

ALLOWED_EXTENSIONS = [
    ".pdf", ".docx", ".txt",
    ".mp4", ".mov", ".avi", ".mkv",
    ".jpg", ".jpeg", ".png", ".gif"
]

INTENT_SCHEMA = {
    "action": None,
    "extensions": None,
    "source": None,
    "destination": None,
    "filename": None,
    "new_filename": None,
    "size_mb": None,
    "size_operator": None
}

# ----------------------------------
# ✅ 2️⃣ System Prompt
# ----------------------------------
SYSTEM_PROMPT = """
You are a strict intent extraction engine for file operations.

Return ONLY valid JSON.
Do NOT use markdown.
Do NOT explain.
Do NOT add extra text.
Always include ALL fields.
Use null when not applicable.

Schema:

{
  "action": "create | rename | delete | move | null",
  "extensions": ["list of file extensions like .pdf, .mp4"] or null,
  "source": "string or null",
  "destination": "string or null",
  "filename": "string or null",
  "new_filename": "string or null",
  "size_mb": "number or null",
  "size_operator": "> | < | = | null"
}

Rules:
- Always include dot in extensions (.pdf not pdf).
- If file types are mentioned (like pdf, word docs, txt),
  convert them into correct extensions.
  Example:
    "word docs" → ".docx", ".doc"
    "pdfs" → ".pdf"
    "text files" → ".txt"
- Convert GB to MB before returning.
  Example: 0.5GB → 512
- Extract size operator separately.
- Extract source after words like "from".
- Extract destination after words like "to".
- If no extension can be determined, use null.
- Do NOT invent paths.
- Do NOT combine fields.
- Do not try to guess the path just give wherver you think the user is referring to. We will handle the ambiguity later.

Examples:

User: Delete video files larger than 500MB from downloads

Output:
{
  "action": "delete",
  "extensions": [".mp4", ".mov", ".avi", ".mkv"],
  "source": "downloads",
  "destination": null,
  "filename": null,
  "new_filename": null,
  "size_mb": 500,
  "size_operator": ">"
}

User: Rename report.pdf to final.pdf in documents

Output:
{
  "action": "rename",
  "extensions": [".pdf"],
  "source": "documents",
  "destination": null,
  "filename": "report.pdf",
  "new_filename": "final.pdf",
  "size_mb": null,
  "size_operator": null
}
"""

# ----------------------------------
# ✅ 3️⃣ Extract JSON Safely
# ----------------------------------

def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None

# ----------------------------------
# ✅ 4️⃣ Validate & Clean Intent
# ----------------------------------

def validate_intent(intent):

    # Ensure all required fields exist
    for key in INTENT_SCHEMA:
        if key not in intent:
            intent[key] = None

    # Validate action
    allowed_actions = ["create", "rename", "delete", "move", None]
    if intent["action"] not in allowed_actions:
        intent["action"] = None

    # Validate extensions
    if intent["extensions"] is None:
        pass
    elif isinstance(intent["extensions"], str):
        intent["extensions"] = [intent["extensions"]]
    elif not isinstance(intent["extensions"], list):
        intent["extensions"] = None

    if intent["extensions"]:
        cleaned = []
        for ext in intent["extensions"]:
            if not ext.startswith("."):
                ext = "." + ext
            if ext.lower() in ALLOWED_EXTENSIONS:
                cleaned.append(ext.lower())
        intent["extensions"] = cleaned if cleaned else None

    # Validate size
    if intent["size_mb"] is not None:
        try:
            intent["size_mb"] = float(intent["size_mb"])
        except:
            intent["size_mb"] = None

    # Validate operator
    allowed_ops = [">", "<", "=", None]
    if intent["size_operator"] not in allowed_ops:
        intent["size_operator"] = None

    return intent

# ----------------------------------
# ✅ 5️⃣ Main Parser
# ----------------------------------

def parse_intent(user_text, model="phi3"):

    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ],
        options={"temperature": 0}
    )

    raw_output = response["message"]["content"].strip()
    print("\n🔎 LLM Raw Output:\n", raw_output)

    json_text = extract_json(raw_output)

    if not json_text:
        print("❌ No JSON found.")
        return None

    try:
        intent = json.loads(json_text)
    except json.JSONDecodeError:
        print("❌ JSON parsing failed.")
        return None

    return validate_intent(intent)


