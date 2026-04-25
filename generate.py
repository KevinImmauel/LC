import re
import requests
import csv
import os
import time
from google import genai

# --- Configuration ---
GEMINI_API_KEY = ""
client = genai.Client(api_key=GEMINI_API_KEY)
CSV_FILENAME = "leetcode_tracker.csv"
HEADERS = ["P.No", "Title", "URL", "Difficulty", "Category", "Expected TC", "My TC", "Solved"]

# --- Auto-Discover Models ---
print("🔍 Auto-detecting valid AI models for your API key...")
MODELS = []
try:
    # Ask the API directly what models it has available
    for m in client.models.list():
        # Clean up the name string
        name = m.name.replace("models/", "")
        
        # We only want text-generation models (flash and pro)
        if "gemini" in name and ("flash" in name or "pro" in name):
            MODELS.append(name)
            
    # Put gemini-2.0-flash at the front since we know 2.5 is exhausted for you right now
    if "gemini-2.0-flash" in MODELS:
        MODELS.insert(0, MODELS.pop(MODELS.index("gemini-2.0-flash")))
        
    print(f"✅ Found {len(MODELS)} valid models to use for fallbacks!")
except Exception as e:
    print(f"⚠️ Auto-detect failed ({e}). Using hardcoded fallbacks.")
    # Safe bets that almost always exist
    MODELS = ["gemini-2.0-flash", "gemini-2.5-pro", "gemini-1.5-flash"]

current_model_idx = 0

def get_expected_tc(title):
    """Fetches TC using aggressive fallbacks for ANY API error."""
    global current_model_idx
    
    prompt = f"""
    What is the optimal Expected Time Complexity for the LeetCode problem titled "{title}"?
    Respond ONLY with the Big O notation (e.g., O(n), O(n log n), O(n^2)). Do not explain.
    """
    
    attempts = 0
    while attempts < len(MODELS):
        active_model = MODELS[current_model_idx]
        try:
            response = client.models.generate_content(
                model=active_model,
                contents=prompt
            )
            return response.text.strip()
        
        except Exception as e:
            error_msg = str(e).replace('\n', ' ')[:40]
            print(f" [⚠️ {active_model} failed ({error_msg}...). Switching!] ", end="", flush=True)
            
            current_model_idx = (current_model_idx + 1) % len(MODELS)
            attempts += 1
            time.sleep(2) 
                
    print(" [All models exhausted! Waiting 15 seconds...] ", end="", flush=True)
    time.sleep(15)
    return "Error"

def load_existing_progress():
    """Reads the CSV into a dictionary so we don't overwrite or repeat work."""
    existing_data = {}
    if os.path.exists(CSV_FILENAME):
        with open(CSV_FILENAME, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                match = re.search(r"problems/([\w-]+)/", row["URL"])
                if match:
                    slug = match.group(1)
                    existing_data[slug] = row
    return existing_data

def save_progress(data_dict):
    """Writes the current state of the dictionary to the CSV."""
    with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(data_dict.values())

def main():
    print("🚀 Starting robust LeetCode data extraction...\n")
    
    try:
        with open("demo.html", "r") as f:
            html_content = f.read()
    except FileNotFoundError:
        print("❌ Error: demo.html not found!")
        return

    pattern = r"https://leetcode\.com/problems/([\w-]+)/"
    slugs = list(set(re.findall(pattern, html_content)))
    total_slugs = len(slugs)
    print(f"📁 Found {total_slugs} unique problems in demo.html.")
    
    tracking_data = load_existing_progress()
    print(f"📂 Loaded {len(tracking_data)} existing records from {CSV_FILENAME}.\n")

    for i, slug in enumerate(slugs):
        print(f"[{i+1}/{total_slugs}] Processing '{slug}'... ", end="", flush=True)
        
        if slug in tracking_data:
            existing_tc = tracking_data[slug].get("Expected TC", "").strip()
            # If we already have a valid answer, skip to save quotas!
            if existing_tc.startswith("O(") or existing_tc.startswith("O ("):
                print(f"⏭️ Skipped (TC '{existing_tc}' already exists)")
                continue

        try:
            res = requests.get(f"https://leetcode-api-pied.vercel.app/problem/{slug}")
            if res.status_code == 200:
                problem_data = res.json()
                
                q_id = problem_data.get('questionFrontendId', 'N/A')
                title = problem_data.get('title', slug)
                url = problem_data.get('url', f"https://leetcode.com/problems/{slug}/")
                difficulty = problem_data.get('difficulty', 'N/A')
                category = problem_data.get('categoryTitle', 'N/A')
                
                expected_tc = get_expected_tc(title)
                
                tracking_data[slug] = {
                    "P.No": q_id,
                    "Title": title,
                    "URL": url,
                    "Difficulty": difficulty,
                    "Category": category,
                    "Expected TC": expected_tc,
                    "My TC": tracking_data.get(slug, {}).get("My TC", ""),       
                    "Solved": tracking_data.get(slug, {}).get("Solved", "False") 
                }
                
                save_progress(tracking_data)
                
                print(f"✅ Saved! (TC: {expected_tc})")
            else:
                print(f"❌ Failed (API Status: {res.status_code})")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            
        time.sleep(1)

    print("\n🎉 All done! CSV is fully up to date.")

if __name__ == "__main__":
    main()