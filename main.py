import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="LeetCode SDE Tracker", page_icon="🚀", layout="wide")
CSV_FILENAME = "new.csv"

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

def load_data():
    if not os.path.exists(CSV_FILENAME):
        st.error(f"❌ '{CSV_FILENAME}' not found. Please ensure the CSV is in the same folder.")
        st.stop()
        
    df = pd.read_csv(CSV_FILENAME)
    
    if 'Solved' in df.columns:
        df['Solved'] = df['Solved'].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        df['Solved'] = df['Solved'].fillna(False).astype(bool)
        
    if 'My TC' in df.columns:
        df['My TC'] = df['My TC'].fillna("")
        
    if 'P.No' in df.columns:
        df['P.No'] = df['P.No'].astype(str)
        
    return df

df = load_data()

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

if changes_made:
    df.to_csv(CSV_FILENAME, index=False)
    st.toast("✅ Progress saved automatically!")
    st.rerun()

st.divider()
st.download_button(
    label="💾 Download Backup CSV",
    data=df.to_csv(index=False).encode('utf-8'),
    file_name='leetcode_tracker_backup.csv',
    mime='text/csv',
)