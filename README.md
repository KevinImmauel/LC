# 🚀 LeetCode SDE Tracker & Scraper

A robust, cloud-synced, and AI-powered educational tracker built with [Streamlit](https://streamlit.io/). This system helps software engineers prepare for technical interviews by efficiently tracking their progress on structured problem lists (like Striver's SDE Sheet). 

It features an intelligent data scraper that uses Google's Gemini models to deduce expected time complexities, and a beautifully designed, secure front-end dashboard that synchronizes your progress in real-time with Google Sheets.

---

## ✨ Key Features

- **Automated Metadata Extraction:** The included `generate.py` script automatically parses LeetCode problems, fetches metadata from an external LeetCode API, and intelligently prompts Google's Gemini LLMs to determine the optimal "Expected Time Complexity" (Big O notation) for each problem.
- **Secure Access Control:** The application logic features a bank-grade, built-in security fortress. It employs SHA-256 password hashing, prevents timing attacks via `hmac.compare_digest`, and limits brute-force attempts by enforcing temporary lockouts.
- **Persistent Cloud Sync:** Your progress isn't tied to your local machine! By utilizing Google Sheets as a low-latency, real-time database, any changes made to your data—like marking a problem as 'Solved' or tracking your own 'Time Complexity'—are automatically saved to the cloud.
- **Live Progress Analytics:** An intuitive and colorful dashboard metrics interface providing overall progress completion %, difficulty split-ups, and category-level progress expansion items.

---

## 📂 Project Structure

```text
├── main.py                # Main Streamlit web application & UI
├── generate.py            # AI-powered script to build tracking data from HTML
├── leetcode_tracker.csv   # Locally generated CSV (Synced to Sheets later)
├── requirements.txt       # Python dependencies 
└── README.md              # Project documentation
```

### Script Breakdown

#### 1. The Streamlit App (`main.py`)
This is the core dashboard visualizing the problems.
* **Authentication:** Mandates a hashed password before accessing the dashboard.
* **Google Sheets Connectivity:** Uses `streamlit-gsheets` to load, display, and auto-update candidate data on the fly.
* **Interactive UI:** Leverages `st.data_editor` to edit the list with responsive data metrics.

#### 2. The Smart Scraper (`generate.py`)
A backend tool designed to initially bootstrap the tracker list or augment new data.
* Parses a `demo.html` file (e.g., the saved webpage of Striver's SDE Guide).
* Resolves problems via an external API to construct titles, IDs, difficulties, and URLs.
* Connects using `google-genai` to automatically probe models (like `gemini-2.0-flash`) and determine Expected T.C!

---

## 🛠⚙️ Getting Started & Setup

### Prerequisites
* Python 3.9+
* A valid **Google Gemini API Key** (for data generation).
* A **Google Cloud Platform (GCP) Service Account** (for Google Sheets real-time syncing).

### 1. Local Setup
1. Clone the repository and configure your virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. *(Optional)* Generate the tracker CSV for the first time:
    - Ensure your `demo.html` problem list exists.
    - Set the `GEMINI_API_KEY` directly inside `generate.py`.
    - Run `python generate.py`.
    - Once completed, open up your target Google Sheet and import `leetcode_tracker.csv`.

### 2. Streamlit Cloud Secrets Configuration
When deploying (or running locally), create a `secrets.toml` file under `.streamlit/secrets.toml` (or configure via Streamlit Advanced Settings in the cloud). The file must match this structure:

```toml
# Local SHA-256 hashed password string
password_hash = "your_sha256_hashed_password"

# Google Sheets Configuration
[connections.gsheets]
type = "service_account"
project_id = "your-gcp-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "bot@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
```
*(Need help getting the hash? Open python and run: `import hashlib; print(hashlib.sha256(b"your_password").hexdigest())`)*

### 3. Launching the App
Run the frontend dashboard using Streamlit:
```bash
streamlit run main.py
```

---

## 🗄️ Database Architecture
The application leverages **Google Sheets** for real-time state. By default, the application writes/reads to the `new` worksheet on the target sheet URL defined in `main.py`. Ensure that the service account defined in `secrets.toml` has **Editor Access** shared directly to the Google Sheet URL!

## 🛡️ Security Acknowledgements
* Secrets, Hashes, and Service Accounts are handled securely and *should never* be committed to version control. Let Streamlit manage secrets externally.
* Rate limits aggressively prevent script-automated brute-force access to your tracker.

## 🤝 Contributing
Feel free to open a Pull Request if you'd like to adjust aesthetics, tweak the Streamlit configuration, or upgrade the AI metadata extractor.