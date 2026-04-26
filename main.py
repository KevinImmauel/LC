import streamlit as st
import pandas as pd
import os
import time
import hashlib
import hmac
from streamlit_gsheets import GSheetsConnection

# --- Page Config ---
st.set_page_config(page_title="LeetCode SDE Tracker", page_icon="🚀", layout="wide")

# --- Security Fortress (Hash & Rate Limit) ---
MAX_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes in seconds

def check_password():
    """Returns True if the user had the correct password."""
    
    # Initialize session state variables for rate limiting
    if "failed_attempts" not in st.session_state:
        st.session_state["failed_attempts"] = 0
    if "lockout_time" not in st.session_state:
        st.session_state["lockout_time"] = 0

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Calculate how much time is left in the lockout
        time_left = st.session_state["lockout_time"] - time.time()
        
        if time_left > 0:
            st.error(f"[LOCKED] Too many failed attempts. Locked out for {int(time_left // 60)}m {int(time_left % 60)}s.")
            return

        # Hash the user's input
        entered_password = st.session_state["password"]
        entered_hash = hashlib.sha256(entered_password.encode()).hexdigest()
        
        # hmac.compare_digest prevents "timing attacks"
        if hmac.compare_digest(entered_hash, st.secrets["password_hash"]):
            st.session_state["password_correct"] = True
            st.session_state["failed_attempts"] = 0  # Reset attempts on success
            del st.session_state["password"]  # Clear the password from memory
        else:
            st.session_state["password_correct"] = False
            st.session_state["failed_attempts"] += 1
            
            # Trigger lockout if they hit the max
            if st.session_state["failed_attempts"] >= MAX_ATTEMPTS:
                st.session_state["lockout_time"] = time.time() + LOCKOUT_DURATION

    # --- UI Logic ---
    if "password_correct" not in st.session_state:
        st.title("Access Restricted")
        st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
        return False
        
    elif not st.session_state["password_correct"]:
        st.title("Access Restricted")
        time_left = st.session_state["lockout_time"] - time.time()
        
        # Disable the input box entirely if they are locked out
        if time_left > 0:
            st.error(f"[SYSTEM LOCKED] Please wait {int(time_left // 60)}m {int(time_left % 60)}s before trying again.")
        else:
            st.text_input("Enter password:", type="password", on_change=password_entered, key="password")
            st.error(f"Incorrect password. Attempt {st.session_state['failed_attempts']}/{MAX_ATTEMPTS}")
        return False
        
    else:
        return True

# Stop the script entirely if the password is not correct
if not check_password():
    st.stop()

# ==========================================
# --- THE REST OF YOUR APP STARTS HERE ---
# ==========================================

STRIVERS_SDE_CATEGORIES = [
    "Arrays",
    "Arrays Part-II",
    "Arrays Part-III",
    "Arrays Part-IV",
    "Linked List",
    "Linked List Part-II",
    "Linked List and Arrays",
    "Greedy Algorithm",
    "Recursion",
    "Recursion and Backtracking",
    "Binary Search",
    "Heaps",
    "Stack and Queue",
    "Stack and Queue Part-II",
    "String",
    "String Part-II",
    "Binary Tree",
    "Binary Tree part-II",
    "Binary Tree part-III",
    "Binary Search Tree",
    "Binary Search Tree Part-II",
    "Binary Trees[Miscellaneous]",
    "Graph",
    "Graph Part-II",
    "Dynamic Programming",
    "Dynamic Programming Part-II",
    "Trie"
]

# --- Load Data from Google Sheets ---
# Get the connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Replace this URL with the actual URL of your Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/1zRyVIa84LTOxBewmiQIcPqKFRUk-eg9sEV2EVN0Sj9o/edit"

def fetch_data():
    """Fetches data from Google Sheets. Cached for 10 minutes to save API quotas."""
    df = conn.read(spreadsheet=SHEET_URL,worksheet="new", ttl="10m")
    
    # 1. Strip accidental spaces from Google Sheet column names (e.g., "Solved " -> "Solved")
    df.columns = df.columns.str.strip()
    
    # 2. Bulletproof the 'Solved' column
    if 'Solved' not in df.columns:
        df['Solved'] = False  # Create it if it's missing entirely
    else:
        df['Solved'] = df['Solved'].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        df['Solved'] = df['Solved'].fillna(False).astype(bool)
        
    # 3. Bulletproof the 'My TC' column
    if 'My TC' not in df.columns:
        df['My TC'] = ""
    else:
        df['My TC'] = df['My TC'].fillna("")
        
    # 4. Bulletproof the 'P.No' column
    if 'P.No' in df.columns:
        df['P.No'] = df['P.No'].astype(str)
        
    return df

# Initialize session state so we ONLY read from the Google API once per visit
if "tracker_data" not in st.session_state:
    st.session_state["tracker_data"] = fetch_data()

# For the rest of the script, we use the local memory copy, not the Google API
df = st.session_state["tracker_data"]

st.title("🚀 Striver's SDE Sheet Tracker")

total_q = len(df)
total_solved = df['Solved'].sum()
overall_progress = (total_solved / total_q) * 100 if total_q > 0 else 0

st.markdown(f"### Overall Progress: **{overall_progress:.1f}%**")
st.progress(overall_progress / 100)

def get_diff_stats(diff):
    diff_df = df[df['Difficulty'] == diff]
    return diff_df['Solved'].sum(), len(diff_df)

easy_sol, easy_tot = get_diff_stats("Easy")
med_sol, med_tot = get_diff_stats("Medium")
hard_sol, hard_tot = get_diff_stats("Hard")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🏆 Total Solved", value=f"{total_solved} / {total_q}")
with col2:
    st.metric(label="🟢 Easy", value=f"{easy_sol} / {easy_tot}")
with col3:
    st.metric(label="🟡 Medium", value=f"{med_sol} / {med_tot}")
with col4:
    st.metric(label="🔴 Hard", value=f"{hard_sol} / {hard_tot}")

st.divider()

def color_difficulty(val):
    if val == 'Easy':
        return 'background-color: rgba(0, 200, 83, 0.15); color: #00e676; font-weight: bold;'
    elif val == 'Medium':
        return 'background-color: rgba(255, 171, 0, 0.15); color: #ffd600; font-weight: bold;'
    elif val == 'Hard':
        return 'background-color: rgba(255, 23, 68, 0.15); color: #ff5252; font-weight: bold;'
    return ''

column_config = {
    "P.No": st.column_config.TextColumn("ID", width="small"),
    "URL": st.column_config.LinkColumn("Link", display_text="Open in LC"),
    "Difficulty": st.column_config.TextColumn("Difficulty", width="small"),
    "Category": None, 
    "Expected TC": st.column_config.TextColumn("Expected TC"),
    "My TC": st.column_config.TextColumn("My Time Complexity"),
    "Solved": st.column_config.CheckboxColumn("Solved?", default=False)
}

changes_made = False

for cat in STRIVERS_SDE_CATEGORIES:
    cat_df = df[df['Category'] == cat]
    
    if cat_df.empty:
        continue
        
    cat_total = len(cat_df)
    cat_solved = cat_df['Solved'].sum()
    
    if cat_solved == cat_total:
        status_icon = "✅"
    elif cat_solved > 0:
        status_icon = "⏳"
    else:
        status_icon = "📓"
        
    expander_title = f"{status_icon} **{cat}** — {cat_solved} / {cat_total} Solved"
    
    with st.expander(expander_title, expanded=False):
        styled_cat_df = cat_df.style.map(color_difficulty, subset=['Difficulty'])
        
        edited_cat_df = st.data_editor(
            styled_cat_df,
            column_config=column_config,
            disabled=["P.No", "Title", "URL", "Difficulty", "Category", "Expected TC"], 
            hide_index=True,
            use_container_width=True,
            key=f"editor_{cat}" 
        )
        
        if not edited_cat_df.equals(cat_df):
            for col in ['My TC', 'Solved']:
                df.loc[cat_df.index, col] = edited_cat_df[col]
            changes_made = True

# --- Auto-Save Mechanism to Google Sheets ---
# --- Auto-Save Mechanism to Google Sheets ---
if changes_made:
    # 1. Update our local session state so the UI stays lightning fast
    st.session_state["tracker_data"] = df
    
    # 2. Push the update specifically to the "new" tab
    conn.update(spreadsheet=SHEET_URL, worksheet="new", data=df)
    
    # 3. Clear the connection cache so the NEXT time you hard-refresh, it gets the latest data
    st.cache_data.clear()
    
    st.toast("✅ Progress saved automatically to the Cloud!")
    st.rerun()

st.divider()
st.download_button(
    label="💾 Download Backup CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='leetcode_tracker_backup.csv',
    mime='text/csv',
)