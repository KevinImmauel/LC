# GOOGLE SHEETS UPDATE [TODO]

### Phase 1: Set up the Google Sheet & Get Your Keys

To let your Streamlit app "talk" to your private Google Sheet, you need to create a secure robot account (a Service Account) in Google.

**1. Create the Sheet**
* Go to Google Sheets and create a new spreadsheet. Name it something like `SDE Tracker DB`.
* Open your local `leetcode_tracker.csv`, copy everything, and paste it into this new Google Sheet.

**2. Create a Google Cloud Project**
* Go to the [Google Cloud Console](https://console.cloud.google.com/).
* Click **Select a project** (top left) and click **New Project**. Name it `Streamlit-Tracker` and click Create.
* Once created, make sure that project is selected at the top of the screen.

**3. Enable the APIs**
* In the search bar at the top, search for **Google Drive API** and click **Enable**.
* Search for **Google Sheets API** and click **Enable**.

**4. Create the "Robot" Account (Service Account)**
* In the left sidebar, go to **IAM & Admin > Service Accounts**.
* Click **+ Create Service Account** at the top. Name it `streamlit-bot` and click **Done** (you can skip the optional steps).
* You will now see an email address for this bot (e.g., `streamlit-bot@your-project.iam.gserviceaccount.com`). **Copy this email address.**
* Go back to your Google Sheet, click **Share** in the top right, paste this bot email address, and give it **Editor** access. (This is how your app gets permission to edit the sheet).

**5. Get Your JSON Key**
* Back in the Google Cloud Service Accounts page, click the three dots (`⋮`) next to your bot and select **Manage keys**.
* Click **Add Key > Create new key**. Choose **JSON** and click Create. 
* A file will download to your computer. Open it in Notepad/TextEdit—you will need the text inside it shortly.

---

### Phase 2: Host It & Update the Code

Now we move everything to the cloud.

**1. GitHub & Streamlit Setup**
* Push your `app.py` and a new `requirements.txt` file to a public or private GitHub repository. 
* Your `requirements.txt` file MUST contain these lines:
  ```text
  streamlit
  pandas
  st-gsheets-connection
  ```
* Go to [share.streamlit.io](https://share.streamlit.io/), log in with GitHub, and click **New app**. Select your repository and `app.py`. 
* **Stop before you click deploy!** Click **Advanced settings** (or Settings > Secrets).

**2. Add the Secrets**
In the "Secrets" text box, you need to paste the contents of your JSON file inside a specific block. It must look exactly like this:

```toml
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
*(Just paste the entire contents of your downloaded JSON file under `[connections.gsheets]` and format it like the above).*

Now click **Deploy**.

---

### Phase 3: The Code Update

Replace the "Load Data" and "Auto-Save" sections of your `app.py` to use the new Google Sheets connection.

**1. Update your Imports**
Add this to the top of your `app.py`:
```python
from streamlit_gsheets import GSheetsConnection
```

**2. Replace the `load_data()` function**
Replace your current CSV load function with this:

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

**3. Replace the Auto-Save Mechanism**
At the very bottom of your script, replace the `df.to_csv(...)` logic with this:

```python
# --- Auto-Save Mechanism to Google Sheets ---
if changes_made:
    # Update the Google Sheet
    conn.update(spreadsheet=SHEET_URL, data=df)
    
    st.toast("✅ Progress saved automatically to the Cloud!")
    st.rerun()
```

That's it! Now, when you check a box on your live Streamlit website, it will instantly update your Google Sheet. If the server goes to sleep and restarts, it will just read the fresh data straight from your Google Sheet.