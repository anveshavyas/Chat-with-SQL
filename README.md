# 🗄️ SQL Mind — Chat With Your Database

A Streamlit app that lets you ask plain-English questions about a SQL database and get real answers — no SQL knowledge required. Powered by a LangChain SQL agent running on Groq's Llama models.

---

## ✨ Features

### 💬 Natural Language → SQL
- Ask questions like *"Show all students with marks above 80"* and get a real answer, not just generated SQL
- Built on LangChain's `create_sql_agent` with a `SQLDatabaseToolkit` — the agent inspects your schema, writes the query, runs it, and explains the result
- **Agent reasoning view** — expand to see the step-by-step thought process behind every answer

### 🔌 Multiple Data Sources
- **SQLite (demo)** — point at any local `.db` file
- **Upload CSV/Excel** — drop in a `.csv`, `.xlsx`, or `.xls` file and it's instantly loaded into a fresh SQLite table, column names auto-cleaned to be SQL-safe
- **MySQL** — connect directly to a live MySQL database with host/user/password/database fields

### 🧠 Model Selection
- Pick your model right from the sidebar:
  ```
  llama-3.1-8b-instant
  llama-3.3-70b-versatile
  openai/gpt-oss-120b
  ```
- Swap models per session without restarting the app — useful for trading off speed vs. accuracy on harder queries

### 🛡️ Reliability Safeguards
- `handle_parsing_errors=True` keeps the agent from crashing on malformed reasoning steps
- `max_iterations` cap prevents runaway loops while still giving the agent room to reason through multi-step queries
- Schema explorer in the sidebar shows table names and structure after every successful connection

---

## 🗂️ Project Structure

```
chat with sql/
├── main.py            # Streamlit UI — chat interface, sidebar, connection flow
├── agent.py           # Builds the LangChain SQL agent (Groq LLM + toolkit)
├── database.py        # SQLite / MySQL connectors + CSV/Excel-to-SQLite loader
├── sqlite.py           # One-off script to seed a sample student.db
├── requirements.txt    # Python dependencies
├── streamlit/
│   └── secrets.toml    # Streamlit secrets (optional, for deployment)
└── .env                 # Local environment variables (not committed)
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- A [Groq API key](https://console.groq.com) (free tier available)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/sql-mind.git
cd "chat with sql"

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the App

```bash
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser (or the port Streamlit assigns).

---

## 🔌 Usage

### Option 1 — SQLite demo
1. Select **SQLite (demo)** in the sidebar
2. Enter the path to a `.db` file (defaults to `student.db` — run `python sqlite.py` first to generate sample data)
3. Click **Connect**

### Option 2 — Upload your own data
1. Select **Upload CSV/Excel**
2. Choose a `.csv`, `.xlsx`, or `.xls` file
3. (Optional) Rename the destination table
4. Click **Connect** — your file is loaded into a local SQLite database and is immediately queryable

### Option 3 — MySQL
1. Select **MySQL**
2. Enter host, username, password, and database name
3. Click **Connect**

Once connected, type any question into the chat box — for example:
```
Show all students with marks above 80
What is the average score by class?
List the top 5 records by [your column]
```

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| AI / LLM | LangChain + Groq API (Llama 3.1 / 3.3, GPT-OSS) |
| Database | SQLAlchemy (SQLite, MySQL) |
| File Parsing | Pandas + openpyxl |
| Agent Framework | LangChain `create_sql_agent` (ReAct-style SQL toolkit) |

---

## 📦 Key Dependencies

```
streamlit
langchain
langchain-community
langchain-groq
sqlalchemy
python-dotenv
mysql-connector-python
pandas
openpyxl
```

---

## ⚙️ Configuration

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Groq API authentication key | **Required** |

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Add these to your `.gitignore`:
```
venv/
__pycache__/
*.pyc
.env
```

---

## ⚠️ Notes

- **Local-first** — SQLite and uploaded-file databases live entirely on your machine
- **Groq API** — only your natural-language questions and schema metadata are sent to Groq for inference; no raw database files are uploaded externally
- **Re-uploading files** overwrites the previous table of the same name in the local SQLite store, so use distinct table names if you want multiple uploaded datasets to coexist

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

> **Disclaimer:** SQL Mind is a developer tool for exploring databases conversationally. Always review generated queries before running them against production data.
