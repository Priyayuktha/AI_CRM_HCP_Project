# 🏥 AI CRM Project

An **AI-powered Healthcare Professional (HCP) Customer Relationship Management (CRM)** system that allows pharmaceutical representatives to log, edit, search, and manage HCP interactions using **natural language**. The AI Assistant automatically extracts key information from user conversations and updates the CRM form without manual data entry.

> **Assignment:** AI-First CRM – HCP Interaction Module  
> **Tech Stack:** React • Redux • FastAPI • LangGraph • Groq LLM • PostgreSQL

---

## 🚀 Features

- 🤖 AI-powered interaction logging using natural language
- 📝 Automatic CRM form population
- ✏️ Edit interactions using conversational prompts
- 🔍 Search Healthcare Professional (HCP) records
- 📜 View previous interaction history
- 📅 AI-assisted follow-up planning
- 🧠 LangGraph agent with multiple AI tools
- 💾 PostgreSQL database integration
- 🎨 Responsive and professional React UI

---

## 🏗️ Tech Stack

### Frontend
- React.js
- Redux Toolkit
- Axios
- CSS
- Google Inter Font

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL

### AI
- LangGraph
- Groq API (Gemma2-9B-IT)
- LLM-based Entity Extraction & Intent Detection

---

## 🤖 LangGraph AI Workflow

```text
User Input
     │
     ▼
LLM Entity Extraction
     │
     ▼
Intent Detection
     │
     ▼
Tool Selection
     │
     ▼
Tool Execution
     │
     ▼
Database Update
     │
     ▼
CRM Form Auto Update
     │
     ▼
AI Confirmation
```

---

## 🛠️ AI Tools

### 1. Log Interaction
Logs a new HCP interaction from natural language.

Example:
> Today I met Dr. John at KMC Hospital. We discussed diabetes medicines and I shared a brochure.

---

### 2. Edit Interaction
Updates only the requested fields.

Example:
> Actually the doctor's name is Dr. Janet.

---

### 3. Search HCP
Finds an HCP profile and displays the doctor's information.

Example:
> Find Dr. John.

---

### 4. Interaction History
Displays previous interactions in timeline format.

Example:
> Show Dr. John's interaction history.

---

### 5. Follow-up Planner
Creates or updates follow-up actions.

Example:
> Schedule a follow-up after 15 days.

---

# 📂 Project Structure

```text
AI_CRM_Project/
│
├── backend/
│   ├── app/
│   │   ├── langgraph/
│   │   ├── models/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tools/
│   │   ├── database.py
│   │   └── main.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── redux/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

---

# ⚙️ Setup Instructions

## 1️⃣ Clone Repository

```bash
git clone https://github.com/Priyayuktha/AI_CRM_Project.git
cd AI_CRM_Project
```

---

## 2️⃣ Backend Setup

Navigate to the backend folder.

```bash
cd backend
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Create a `.env` file.

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_crm
GROQ_API_KEY=YOUR_GROQ_API_KEY
```

Run the backend.

```bash
python -m uvicorn app.main:app --reload
```

Backend URL:

```
http://localhost:8000
```

Swagger API:

```
http://localhost:8000/docs
```

---

## 3️⃣ Frontend Setup

Open a new terminal.

```bash
cd frontend
```

Install dependencies.

```bash
npm install
```

Create `.env`.

```env
VITE_API_BASE_URL=http://localhost:8000
```

Run the frontend.

```bash
npm run dev
```

Frontend URL:

```
http://localhost:5173
```

---

# 💡 Example Usage

### Log Interaction

```
Today I met Dr. John at KMC Hospital in Manipal.
We discussed diabetes medicines.
The doctor showed positive interest.
I shared a brochure.
```

The AI will automatically:

- Extract important information
- Populate the CRM form
- Save the interaction
- Generate a summary

---

### Edit Interaction

```
Actually the doctor's name is Dr. Janet.
```

---

### Search Doctor

```
Find Dr. John.
```

---

### View History

```
Show Dr. John's interaction history.
```

---

### Follow-up

```
Schedule a follow-up after 15 days.
```

---

# 📌 API Endpoints

| Method | Endpoint | Description |
|---------|----------|-------------|
| POST | `/chat` | AI Assistant |
| POST | `/hcp` | Create HCP |
| GET | `/hcp/{id}` | Get HCP |
| POST | `/interaction` | Create Interaction |
| PUT | `/interaction/{id}` | Update Interaction |
| GET | `/interaction/history/{hcp}` | Interaction History |

---

# 👨‍💻 Developer

**Priya R**  
Master of Computer Applications (MCA) 

**GitHub:** https://github.com/Priyayuktha

**LinkedIn:** https://www.linkedin.com/in/priyar123/

**Email:**  priyayuktha889@gmail.com

---

# 📈 Future Enhancements

- Voice interaction support
- Speech-to-text logging
- Calendar integration
- AI meeting insights
- Analytics dashboard
- Multi-user authentication
- Report generation

---

# 🎯 Project Flow

1. User enters an interaction using natural language.
2. LangGraph processes the request.
3. The LLM extracts entities and determines the user's intent.
4. The appropriate AI tool is selected.
5. Data is saved to PostgreSQL.
6. The CRM form is automatically updated.
7. AI confirms the action with a concise response.

---

⭐ **Developed as part of the AIVOA.AI AI-First CRM Assignment using React, FastAPI, LangGraph, Groq LLM, and PostgreSQL.**