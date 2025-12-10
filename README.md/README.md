# IEE 305 – National Parks Data Explorer  
### Final Term Project — Fall 2025

This repository contains the completed **IEE 305 Term Project**, based on the team proposal submitted earlier in the semester.  
The project integrates **FastAPI**, **Streamlit**, and a **SQLite** database to create an interactive National Parks Data Explorer.

The system demonstrates an end-to-end data workflow:

- Retrieving data from the National Park Service (NPS) API  
- Cleaning & transforming JSON into relational tables  
- Storing data in a SQLite database  
- Building a REST API using FastAPI  
- Displaying results in an interactive Streamlit frontend  

---

## 📌 Project Features

### Backend / API
Your API exposes the following real endpoints (from Swagger UI):

- `GET /` — Root welcome endpoint  
- `GET /parks` — List all parks  
- `GET /parks/{park_code}` — Get a single park  
- `GET /visitor-centers` — List all visitor centers  
- `GET /events` — List all events  
- `GET /stats/events-per-park` — Events per park summary  
- `GET /stats/visitor-centers-per-park` — Visitor centers per park summary  

### Frontend (Streamlit)
The Streamlit app allows users to:

- Explore parks, visitor centers, and events  
- View tables and bar charts  
- Rank parks by number of events or visitor centers  
- Filter events by park  
- Interact with the dataset through an intuitive UI  

### SQL & Database Features  
The SQLite database follows the relational schema from the proposal and includes tables such as:

- `parks`  
- `visitor_centers`  
- `events`  

The project demonstrates **all 7 required SQL concepts**:

1. **JOIN**  
2. **GROUP BY**  
3. **HAVING**  
4. **Subqueries**  
5. **WHERE filtering**  
6. **ORDER BY & LIMIT**  
7. **Parameterized queries**  

All SQL deliverables are provided in:  
`database/sql_queries.sql`

### Documentation Included
- `docs/proposal.md` — Original project proposal  
- `docs/er_diagram.png` — ER Diagram  
- `docs/relational_schema.*` — Table descriptions  
- `docs/final_report.md` — Final project write-up  

---

## 📁 Folder Structure

```text
.
├── backend/
│   ├── database.py
│   ├── fetch_data.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   ├── .gitignore
│   └── __pycache__/            
│
├── database/
│   ├── nps.db                  
│   ├── schema.sql              
│   ├── sql_queries.sql         
│   └── query_results*          
│
├── docs/
│   ├── er_diagram.png
│   ├── final_report.md
│   ├── proposal.md
│   └── relational_schema.*
│
├── frontend/
│   ├── app.py                  
│   ├── README.md               
│   └── nps.db                  
│
└── README.md                   
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- Python 3.x  
- pip  
- (Recommended) virtual environment (`venv`)  
- Backend dependencies: `backend/requirements.txt`

---

## 🖥️ Running the Backend (FastAPI)

```bash
cd backend

# (optional but recommended) create a virtual environment
python -m venv .venv

# macOS/Linux:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate

# install backend dependencies
pip install -r requirements.txt

# run FastAPI backend
uvicorn main:app --reload
```

Backend available at:  
- http://127.0.0.1:8000  
- http://127.0.0.1:8000/docs (Swagger)

---

## 📊 Running the Frontend (Streamlit)

```bash
cd frontend

# reuse backend virtual environment OR install frontend dependencies
pip install -r ../backend/requirements.txt

# run Streamlit UI
streamlit run app.py
```

Streamlit opens at:  
- http://localhost:8501

---

## 🗄️ Database & SQL

```
Main database:          database/nps.db  
Schema file:            database/schema.sql  
SQL queries file:       database/sql_queries.sql  
Data fetch logic:       backend/fetch_data.py  
Database helpers:       backend/database.py  
```

The database is populated from the official NPS API, then transformed into normalized tables based on project requirements.

---

## 🌐 API Endpoints Overview

```
GET /                               # Root endpoint  
GET /parks                          # List all parks  
GET /parks/{park_code}              # Retrieve a single park  
GET /visitor-centers                # List all visitor centers  
GET /events                         # List all events  
GET /stats/events-per-park          # Summarize events by park  
GET /stats/visitor-centers-per-park # Summarize visitor centers by park  

Interactive documentation:
http://127.0.0.1:8000/docs
```

---

## ✅ Testing & Validation

```bash
# 1. Start backend
uvicorn main:app --reload

# 2. Open Swagger UI and test every endpoint
http://127.0.0.1:8000/docs

# 3. Start frontend
cd frontend
streamlit run app.py

# 4. Validate:
# - Tables load correctly
# - Bar charts display without errors
# - Filters/dropdowns respond correctly
# - No red Streamlit error boxes appear
# - No Python tracebacks appear in terminal
```

This confirms full integration between backend, frontend, and database.

---

## 📚 Acknowledgements

- **National Park Service (NPS) API** — data source  
- **IEE 305 instructors & TAs** — project guidelines  
- Tools used: FastAPI, Streamlit, SQLite, Python, Requests, Uvicorn  

---
