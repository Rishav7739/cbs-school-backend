# CBS Sr. Sec. School - Backend API

FastAPI REST API backend providing authentication, school management, admissions, notices, gallery, documents, and student/teacher records.

## 🚀 Getting Started

### 1. Create and Activate Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run the API Server
```bash
uvicorn main:app --reload --port 8000
```
- Interactive API Docs (Swagger): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 🌐 Deploy to Vercel
1. Import this repository into Vercel.
2. Framework Preset: **Other**
3. Root Directory: `./` (or leave default if imported directly)
4. Environment Variables in Vercel:
   - `SECRET_KEY`: Random 32+ character string
   - `DEFAULT_ADMIN_PASSWORD`: Your chosen default admin password
