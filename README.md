# LeetCode SDE Tracker

## Overview
The LeetCode SDE Tracker is a secure, cloud-hosted web application built with Streamlit. It is designed to help software engineering candidates track their progress through comprehensive problem lists (such as Striver's SDE Sheet). The application categorizes problems, tracks expected versus actual time complexities, calculates completion statistics, and auto-saves progress. 

To ensure data persistence across server restarts and to protect personal progress from unauthorized access, this application utilizes Google Sheets as a real-time cloud database and implements a bank-grade authentication system.

## Key Features
* **Persistent Cloud Storage:** Uses Google Sheets API to store and retrieve user data in real-time, preventing data loss when the hosting server restarts.
* **Cryptographic Authentication:** Implements SHA-256 password hashing to ensure plaintext passwords are never stored in the codebase or environment variables.
* **Anti-Brute Force Measures:** Features a built-in rate limiter that locks the application for 5 minutes after 5 failed login attempts.
* **Timing Attack Prevention:** Utilizes `hmac.compare_digest` for secure password validation.
* **Auto-Save Functionality:** Automatically pushes state changes to the cloud database without requiring manual save actions.

---

# [TODO]

## Part 1: Security Setup (Authentication & Rate Limiting)

Storing plaintext passwords, even in encrypted cloud secrets, is a security vulnerability. This application uses hashing and rate-limiting to create a secure login screen. 

* **Hashing:** You will run your password through a SHA-256 hashing algorithm locally and save the resulting string in your Streamlit Cloud Secrets. When a password is submitted, the app hashes the guess and compares the two hashes.
* **Rate-Limiting:** The app uses Streamlit's `session_state` and Python's `time` module to track failed attempts. Entering the wrong password 5 times locks the interface for 5 minutes.

### Step 1.1: Generate your Password Hash
Open your local terminal or Python shell and run the following code to generate your secure hash. Replace "your_super_secret_password" with your actual password.

```python
import hashlib
print(hashlib.sha256("your_super_secret_password".encode()).hexdigest())
```
Copy the long alphanumeric string that is printed to your console.

### Step 1.2: Add the Gatekeeper Code
Place this security block at the very top of your `app.py` file, immediately after your page configuration.

```python
import streamlit as st
import pandas as pd
import os
import time
import hashlib
import hmac
from streamlit_gsheets import GSheetsConnection

# --- Page Config ---
st.set_page_config(page_title="LeetCode SDE Tracker", layout="wide")

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
```

---

## Part 2: Database Migration (Google Sheets Integration)

To prevent data loss during ephemeral server restarts on cloud hosting platforms, the application state must be separated from the codebase. Google Sheets acts as the database.

### Step 2.1: Create the Sheet
1. Go to Google Sheets and create a new spreadsheet (e.g., `SDE Tracker DB`).
2. Open your local `leetcode_tracker.csv`, copy all contents, and paste them into the new Google Sheet.

### Step 2.2: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Click **Select a project** (top left) and click **New Project**. Name it `Streamlit-Tracker` and click Create.
3. Ensure the new project is selected at the top of the screen.

### Step 2.3: Enable the APIs
1. In the search bar at the top, search for **Google Drive API** and click **Enable**.
2. Search for **Google Sheets API** and click **Enable**.

### Step 2.4: Create the Service Account
1. In the left sidebar, navigate to **IAM & Admin > Service Accounts**.
2. Click **+ Create Service Account** at the top. Name it `streamlit-bot` and click **Done**.
3. Copy the generated email address for this bot (e.g., `streamlit-bot@your-project.iam.gserviceaccount.com`).
4. Open your Google Sheet, click **Share** in the top right, paste this bot email address, and grant it **Editor** access.

### Step 2.5: Get Your JSON Key
1. In the Google Cloud Service Accounts page, click the three dots (`⋮`) next to your bot and select **Manage keys**.
2. Click **Add Key > Create new key**. Choose **JSON** and click Create. 
3. A JSON file will download to your machine. Open it in a text editor for the deployment phase.

---

## Part 3: Code Updates for the Database

Update the data loading and saving mechanisms in your `app.py` to target Google Sheets instead of a local CSV.

### Step 3.1: Replace the Load Data Function
Replace your old CSV `load_data()` function with the following:

```python
# --- Load Data from Google Sheets ---
# Get the connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Replace this URL with the actual URL of your Google Sheet
SHEET_URL = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit"

def load_data():
    # ttl=0 ensures it doesn't cache stale data, it always fetches fresh
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    
    if 'Solved' in df.columns:
        df['Solved'] = df['Solved'].astype(str).str.lower().map({'true': True, 'false': False, '1': True, '0': False})
        df['Solved'] = df['Solved'].fillna(False).astype(bool)
        
    if 'My TC' in df.columns:
        df['My TC'] = df['My TC'].fillna("")
        
    if 'P.No' in df.columns:
        df['P.No'] = df['P.No'].astype(str)
        
    return df

df = load_data()
```

### Step 3.2: Replace the Auto-Save Mechanism
At the bottom of your script, replace the local `df.to_csv(...)` logic with the cloud update command:

```python
# --- Auto-Save Mechanism to Google Sheets ---
if changes_made:
    # Update the Google Sheet
    conn.update(spreadsheet=SHEET_URL, data=df)
    
    st.toast("Progress saved automatically to the Cloud!")
    st.rerun()
```

---

## Part 4: Deployment & Secrets Configuration

### Step 4.1: Repository Setup
Push your `app.py` and a `requirements.txt` file to your GitHub repository. The `requirements.txt` file must contain:

```text
streamlit
pandas
st-gsheets-connection
```

### Step 4.2: Streamlit Community Cloud Setup
1. Go to [share.streamlit.io](https://share.streamlit.io/), log in, and click **New app**. 
2. Select your repository and point it to `app.py`. 
3. **Important:** Before clicking deploy, click **Advanced settings** (or Settings > Secrets).

### Step 4.3: Configure Cloud Secrets
In the "Secrets" text box, paste your password hash from Part 1, followed by the contents of your downloaded JSON key from Part 2 formatted under a TOML block. It must look exactly like this:

```toml
password_hash = "YOUR_SHA256_HASH_GENERATED_LOCALLY"

[connections.gsheets]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_MASSIVE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-bot@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```

Once the secrets are pasted, click **Deploy**. Your application will now be live on the web, fully secured, and backed by a persistent Google Sheets database.