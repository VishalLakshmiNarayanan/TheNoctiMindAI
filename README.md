
# 🧠 NoctiMind (Streamlit)

NoctiMind helps you log, analyze, and reflect on your dreams.  
It turns raw dream text into motifs, archetypes, and emotions, then shows correlations with your sleep quality — complete with visual storytelling.

---

## 🚀 Features
- **AI-Powered Dream Analysis**  
  - Extracts motifs, archetypes, and emotions from your dream text.  
  - Provides therapeutic reframing for calmer reflection.  
- **Dream History**  
  - View logs, emotion arcs, motif clouds, and similarity clusters.  
- **Insights**  
  - Correlates dream negativity with sleep hours & quality.  
  - Personalized feedback based on your recent dream trends.  
- **Visuals**  
  - Emotion arc plots, motif word clouds, archetype/cluster grouping.  

---

## 🛠 Tech Stack
- **Frontend/UI**: Streamlit  
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2`  
- **Clustering**: scikit-learn (KMeans)  
- **Visualization**: Plotly, WordCloud  
- **Database**: SQLite (via SQLAlchemy)  
- **LLM Analysis**: Groq API (`llama-3.3-70b-versatile`)  

---

## 📦 Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/noctimind.git
cd noctimind
````

### 2. Create a virtual environment & install dependencies

```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a file called **`.env`** in the project root:

```bash
GROQ_API_KEY=your_real_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

⚠️ **Do not commit `.env`** — keep your keys private.
(If deploying to Streamlit Cloud, use `.streamlit/secrets.toml` instead.)

### 4. Run the app

```bash
streamlit run app.py
```

The app will open in your browser at [http://localhost:8501](http://localhost:8501).

---

## 📂 Project Structure

```
noctimind/
│── app.py                  # Main entrypoint
│── requirements.txt         # Dependencies
│── .env                     # API keys (local only, do not commit)
│── modules/
│   ├── llm.py               # Groq API integration
│   ├── nlp.py               # Embeddings + helpers
│   ├── storage.py           # SQLite storage
│   └── visuals.py           # Charts & visualizations
│── pages/
│   ├── 1_📘_Log_a_Dream.py
│   ├── 2_📊_History.py
│   ├── 3_🧭_Insights.py
│   └── 4_⚙️_Settings.py
```

---

## 📝 Notes

* First run will download the MiniLM embedding model.
* Dreams are stored locally in `noctimind.db`.
* To reset all data, use **Settings → Danger zone**.
* The Groq API is OpenAI-compatible: [docs](https://console.groq.com/docs/overview).

---

## 🌐 Deployment

* **Streamlit Cloud** → put your API key in `.streamlit/secrets.toml`.
* **Other platforms** → set `GROQ_API_KEY` as an environment variable.

---

## 📑 .gitignore

Add this to `.gitignore` so you don’t leak secrets or local files:

```
.env
*.db
__pycache__/
.venv/
venv/
.streamlit/secrets.toml
```

---

## ⚖️ License

MIT — feel free to fork & build on top of NoctiMind.

```

---

Do you want me to also prepare a **sample screenshot section** in the README (so when you run it, you can drop visuals like “dream log table,” “emotion arcs,” etc.)? That will make it look more polished if you push it to GitHub.
```
