# 🌱 ESG Copilot

**AI-Powered Sustainability Assistant for Small Businesses**

ESG Copilot helps small businesses understand and improve their sustainability
performance through a simple, AI-powered platform. It assesses business practices,
generates a **Sustainability Score**, benchmarks against industry averages, and
provides practical, AI-powered recommendations for improvement.

## Features

- **Guided ESG questionnaire** across Environmental, Social, and Governance pillars
- **Sustainability Score** (overall + per-pillar) with a letter rating
- **AI-powered recommendations** via the OpenAI API (with a rule-based fallback)
- **Industry benchmark comparison**
- **Progress tracking** to monitor improvement over time (session-based)

## Tech stack

- [Streamlit](https://streamlit.io/) — UI
- [OpenAI API](https://platform.openai.com/) — recommendations
- [Plotly](https://plotly.com/python/) — charts & gauges
- [pandas](https://pandas.pydata.org/) — data handling

---

## Run it on GitHub + Streamlit Community Cloud (no local hosting)

### 1. Push this project to GitHub

Create a new GitHub repository and upload all the files from this ZIP (you can
drag-and-drop them into GitHub's web uploader, or use Git/Codespaces).

> Make sure `.streamlit/secrets.toml` is **NOT** committed — it's already in
> `.gitignore`. Your API key goes into Streamlit Cloud secrets instead (step 3).

### 2. Deploy on Streamlit Community Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. Click **"Create app"** → **"Deploy a public app from GitHub"**.
3. Select your repository, branch (`main`), and set **Main file path** to `app.py`.
4. Click **Deploy**.

### 3. Add your OpenAI API key (enables AI recommendations)

In your deployed app: **Manage app → Settings → Secrets**, then paste:

```toml
OPENAI_API_KEY = "sk-your-openai-api-key-here"
OPENAI_MODEL = "gpt-4o-mini"
```

Save — the app restarts automatically. Without a key, the app still works using
built-in rule-based recommendations.

---

## Develop in GitHub Codespaces (optional)

1. On your GitHub repo, click **Code → Codespaces → Create codespace on main**.
2. In the Codespace terminal:

   ```bash
   pip install -r requirements.txt
   # optional: enable AI locally
   mkdir -p .streamlit
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   # then edit .streamlit/secrets.toml and add your key
   streamlit run app.py
   ```

3. Codespaces will offer to open the forwarded port in your browser.

---

## Project structure

```
.
├── app.py                       # Main Streamlit app (UI + tabs)
├── esg_copilot/
│   ├── __init__.py
│   ├── questions.py             # Guided ESG questionnaire
│   ├── scoring.py               # Scoring engine + industry benchmarks
│   └── recommendations.py       # OpenAI recommendations + fallback
├── .streamlit/
│   ├── config.toml              # Eco theme
│   └── secrets.toml.example     # Template for your API key
├── requirements.txt
└── README.md
```

## Notes

- This is a **mock-up / demo** platform. The Sustainability Score and industry
  benchmarks use illustrative, representative logic — not certified ESG audits.
- Progress tracking is session-based (resets when the app restarts). For
  persistent history, connect a database.
