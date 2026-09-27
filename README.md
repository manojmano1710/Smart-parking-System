# Smart Parking System

OpenCV-based parking space detection and management system.

## Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```
Runs at http://127.0.0.1:8000

## Frontend
```bash
cd frontend
npm install
npm run dev
```
Runs at http://localhost:5173

Demo login: **admin / admin123**

Detection uses predefined 16 parking slots and OpenCV image processing; no YOLO or ML model is used.
