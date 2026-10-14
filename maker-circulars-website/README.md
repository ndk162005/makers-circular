# Maker Circulars - Data Management Platform

A professional web-based application for importing, storing, viewing, searching, filtering, and editing Excel tabular data. Built with FastAPI (Python) and React (TypeScript).

![Platform Overview](https://img.shields.io/badge/Platform-Web%20Application-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLite-green)
![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-cyan)

## 🏗️ Architecture

```
Excel File (.xlsx)
       ↓
  Web Upload Interface
       ↓
  FastAPI Backend
       ↓
  Excel Parsing (Pandas + OpenPyXL)
       ↓
  Data Validation & Preview
       ↓
  User Confirmation
       ↓
  SQLite Database (Persistent Storage)
       ↓
  Web Dashboard (CRUD Operations)
```

## 🛠️ Technology Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.11+ | Runtime |
| FastAPI | Web framework & REST API |
| SQLAlchemy | ORM & database management |
| SQLite | Persistent database |
| Pandas | Data processing |
| OpenPyXL | Excel file parsing |
| Pydantic | Data validation |
| Uvicorn | ASGI server |

### Frontend
| Technology | Purpose |
|---|---|
| React 18 | UI framework |
| TypeScript | Type safety |
| Vite | Build tool & dev server |
| Axios | HTTP client |
| React Icons | Icon library |
| React Hot Toast | Notifications |

## 📁 Project Structure

```
maker-circulars-website/
│
├── backend/                    # FastAPI Backend
│   ├── main.py                 # Application entry point
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── crud.py                 # CRUD operations
│   ├── api/                    # API route handlers
│   │   ├── import_api.py       # Excel import endpoints
│   │   ├── datasets.py         # Dataset management
│   │   ├── records.py          # Record CRUD
│   │   ├── makers.py           # Maker filter endpoints
│   │   ├── columns.py          # Column management
│   │   └── stats.py            # Statistics endpoints
│   └── services/               # Business logic
│       ├── excel_importer.py   # Excel parsing service
│       └── database_service.py # Database utilities
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API service layer
│   │   ├── types/              # TypeScript type definitions
│   │   ├── App.tsx             # Main application
│   │   ├── main.tsx            # Entry point
│   │   └── index.css           # Global styles
│   ├── package.json
│   └── vite.config.ts
│
├── data/                       # SQLite database directory
│   └── .gitkeep
│
├── uploads/                    # Temporary upload directory
│   └── .gitkeep
│
├── requirements.txt            # Python dependencies
├── start.bat                   # Windows batch startup
├── start.ps1                   # PowerShell startup
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+**: Download from [python.org](https://python.org)
   - During installation, check "Add Python to PATH"
2. **Node.js 18+**: Download from [nodejs.org](https://nodejs.org)
   - The LTS version is recommended

### Option 1: Automatic Startup (Windows)

```batch
# Using batch file
start.bat

# OR using PowerShell
powershell -ExecutionPolicy Bypass -File start.ps1
```

This will automatically:
- Create a Python virtual environment
- Install all Python dependencies
- Install all frontend dependencies
- Start the backend server (port 8000)
- Start the frontend dev server (port 5173)
- Open the application in your browser

### Option 2: Manual Startup

#### 1. Setup Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows CMD:
.venv\Scripts\activate.bat
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Setup Frontend

```bash
cd frontend
npm install
```

#### 3. Start Backend

```bash
# From project root, with venv activated
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Start Frontend

```bash
# In a new terminal
cd frontend
npm run dev
```

#### 5. Open Application

Navigate to **http://localhost:5173** in your browser.

## 📊 How to Use

### Importing Excel Data

1. Open the application at `http://localhost:5173`
2. Click the **"Import Excel"** button
3. Select your `.xlsx` file (drag & drop is also supported)
4. Choose the worksheet to import (if multiple sheets exist)
5. Review the import preview (file info, columns, sample rows)
6. Click **"Import Dataset"** to confirm
7. Your data is now stored in SQLite and displayed in the dashboard

### Managing Data

- **Search**: Use the search bar to search across all fields
- **Filter by Maker**: Click maker buttons to filter records
- **Sort**: Click column headers to sort ascending/descending
- **Pagination**: Navigate pages and change page size (25/50/100)
- **Add Record**: Click "+ Add Row" to create a new record
- **Edit Record**: Click the Edit button on any row
- **Delete Record**: Click the Delete button (with confirmation)

### Managing Columns

- Click **"Manage Columns"** to add, rename, or delete columns
- Supported data types: Text, Number, Boolean, Date
- Column changes are applied to the database schema

### Multiple Datasets

- Import multiple Excel files as separate datasets
- Switch between datasets using the dataset selector
- Each dataset's records are kept separate

## 🗄️ Database

### Location
```
data/maker_circulars.db
```

### Tables

| Table | Purpose |
|---|---|
| `datasets` | Metadata for imported Excel files |
| `records` | Individual data records (JSON storage) |
| `column_definitions` | Column schema definitions |

### Reset Database

To reset all data, simply delete the database file:

```bash
# Windows
del data\maker_circulars.db

# Linux/Mac
rm data/maker_circulars.db
```

The database will be recreated automatically on next startup.

## 🔌 REST API

The backend provides a comprehensive REST API. Full documentation is available at:

**http://localhost:8000/docs** (Swagger UI)

### Key Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/import/upload` | Upload Excel file |
| `POST` | `/api/import/preview` | Preview import data |
| `POST` | `/api/import/confirm` | Confirm and execute import |
| `GET` | `/api/datasets` | List all datasets |
| `GET` | `/api/datasets/{id}` | Get dataset details |
| `DELETE` | `/api/datasets/{id}` | Delete dataset |
| `GET` | `/api/records` | List records (paginated) |
| `GET` | `/api/records/{id}` | Get single record |
| `POST` | `/api/records` | Create record |
| `PUT` | `/api/records/{id}` | Update record |
| `DELETE` | `/api/records/{id}` | Delete record |
| `GET` | `/api/makers` | Get unique makers |
| `GET` | `/api/columns` | Get column definitions |
| `POST` | `/api/columns` | Add column |
| `PUT` | `/api/columns/{id}` | Rename column |
| `DELETE` | `/api/columns/{id}` | Delete column |
| `GET` | `/api/stats` | Get statistics |

### Query Parameters (GET /api/records)

| Parameter | Type | Description |
|---|---|---|
| `dataset_id` | integer | Required. Dataset to query |
| `page` | integer | Page number (default: 1) |
| `page_size` | integer | Records per page (default: 25) |
| `search` | string | Search across all fields |
| `maker` | string | Filter by maker |
| `sort_by` | string | Column to sort by |
| `sort_order` | string | `asc` or `desc` |

## 🔒 Security

- File type validation (.xlsx only)
- File size limit (50MB)
- Path traversal prevention
- Parameterized SQL queries (via SQLAlchemy)
- Input validation (via Pydantic)
- URL sanitization for document links
- No internal stack traces exposed to users

## 🐛 Troubleshooting

### Port already in use

```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Kill process on port 5173
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Python virtual environment issues

```bash
# Recreate virtual environment
rmdir /s /q .venv
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Frontend build issues

```bash
cd frontend
rmdir /s /q node_modules
del package-lock.json
npm install
```

### Database corruption

```bash
# Delete and restart - database will be recreated
del data\maker_circulars.db
```

### Excel import fails

- Ensure the file is a valid `.xlsx` file (not `.xls` or `.csv`)
- Check that the file size is under 50MB
- Try opening and re-saving the file in Excel

## 📝 Expected Excel Format

The application is optimized for Excel files with these columns:

| Column | Description |
|---|---|
| `_id` | Unique identifier |
| `Maker` | Manufacturer/maker name |
| `Breadcrumb` | Navigation breadcrumb |
| `Document Name` | Document title |
| `Document Link` | URL to the document |
| `DMS` | Document Management System reference |

However, the application dynamically detects columns and can work with **any** Excel file structure.

## 📄 License

This project is provided as-is for internal use.
