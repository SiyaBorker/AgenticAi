import os
import json
from difflib import get_close_matches

# ----------------------------------
# ✅ CONFIGURATION
# ----------------------------------

ROOTS = [
    os.path.expanduser("~"),
]

DRIVES = ["C:\\", "D:\\", "E:\\", "F:\\"]

INDEX_FILE = "folder_index.json"

SKIP_KEYWORDS = [
    "appdata",
    "programdata",
    "site-packages",
    "venv",
    "cache",
    "bin",
    "tests",
    "windows defender",
    "system volume information",
    "$recycle.bin"
]

AMBIGUITY_THRESHOLD = 3


# ----------------------------------
# ✅ BUILD INDEX
# ----------------------------------

def should_skip_path(path):
    path_lower = path.lower()
    return any(keyword in path_lower for keyword in SKIP_KEYWORDS)


def build_index_from_roots(roots):
    folder_index = {}

    for root_path in roots:
        if not os.path.exists(root_path):
            continue

        print(f"Scanning: {root_path}")

        for root, dirs, _ in os.walk(root_path, onerror=lambda e: None):

            if should_skip_path(root):
                continue

            for folder in dirs:
                folder_path = os.path.join(root, folder)
                folder_lower = folder.lower()

                if should_skip_path(folder_path):
                    continue

                if folder_lower not in folder_index:
                    folder_index[folder_lower] = [folder_path]
                else:
                    folder_index[folder_lower].append(folder_path)

    return folder_index


def build_multi_drive_index(drives):
    folder_index = {}

    for drive in drives:
        if not os.path.exists(drive):
            continue

        print(f"Scanning drive: {drive}")

        for root, dirs, _ in os.walk(drive, onerror=lambda e: None):

            if should_skip_path(root):
                continue

            for folder in dirs:
                folder_path = os.path.join(root, folder)
                folder_lower = folder.lower()

                if should_skip_path(folder_path):
                    continue

                if folder_lower not in folder_index:
                    folder_index[folder_lower] = [folder_path]
                else:
                    folder_index[folder_lower].append(folder_path)

    return folder_index


# ----------------------------------
# ✅ PERSISTENCE
# ----------------------------------

def save_index(folder_index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(folder_index, f, indent=2)


def load_index():
    if not os.path.exists(INDEX_FILE):
        return None

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_or_initialize_index():
    existing_index = load_index()

    if existing_index:
        total = len(existing_index)
        print(f"\n📦 Currently storing {total} indexed folder names.")
        choice = input("Use existing index or refresh? (use/refresh): ").lower()

        if choice == "refresh":
            folder_index = build_index_from_roots(ROOTS)
            save_index(folder_index)
            print("✅ Index refreshed.\n")
            return folder_index

        print("✅ Using existing index.\n")
        return existing_index

    print("⚙ No existing index found. Building new index...\n")
    folder_index = build_index_from_roots(ROOTS)
    save_index(folder_index)
    print("✅ Index built and saved.\n")

    return folder_index


# ----------------------------------
# ✅ PATH RANKING WITH SCORES
# ----------------------------------

def score_path(path):
    score = 0
    path_lower = path.lower()
    user_home = os.path.expanduser("~").lower()

    if user_home in path_lower:
        score += 10

    if "\\users\\" in path_lower:
        score += 5

    for keyword in SKIP_KEYWORDS:
        if keyword in path_lower:
            score -= 10

    return score


def rank_paths_with_scores(paths):
    scored = []

    for path in paths:
        score = score_path(path)
        scored.append((score, path))

    scored.sort(reverse=True)
    return scored


# ----------------------------------
# ✅ RESOLUTION WITH AMBIGUITY HANDLING
# ----------------------------------

def resolve_folder(folder_name, folder_index, allow_fuzzy=True):
    if not folder_name:
        return None

    folder_name = folder_name.lower()

    matches = folder_index.get(folder_name)

    if not matches and allow_fuzzy:
        possible = get_close_matches(folder_name, folder_index.keys(), n=1, cutoff=0.6)
        if possible:
            matches = folder_index.get(possible[0])

    if not matches:
        return None

    ranked = rank_paths_with_scores(matches)

    if len(ranked) == 1:
        return ranked[0][1]

    top_score = ranked[0][0]
    second_score = ranked[1][0]

    if abs(top_score - second_score) > AMBIGUITY_THRESHOLD:
        return ranked[0][1]

    print("\nMultiple similar folders found:")
    for i, (score, path) in enumerate(ranked):
        print(f"{i+1}. {path}  (score={score})")

    choice = input("Select folder number: ")

    try:
        return ranked[int(choice) - 1][1]
    except:
        print("Invalid selection.")
        return None


# ----------------------------------
# ✅ TEST MODE
# ----------------------------------

if __name__ == "__main__":

    print("Choose indexing mode:")
    print("1 - Safe Root Scan (Recommended)")
    print("2 - Full Multi-Drive Scan (Slow)")
    choice = input("Enter choice: ")

    if choice == "2":
        folder_index = build_multi_drive_index(DRIVES)
        save_index(folder_index)
    else:
        folder_index = get_or_initialize_index()

    print(f"\nIndexed {len(folder_index)} unique folder names.\n")

    while True:
        query = input("Enter folder name (or 'exit'): ")

        if query.lower() == "exit":
            break

        resolved = resolve_folder(query, folder_index)

        if resolved:
            print(f"\nResolved Path: {resolved}\n")
        else:
            print("\nFolder not found.\n")
