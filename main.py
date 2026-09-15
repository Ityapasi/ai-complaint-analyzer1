import os
import shutil
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ai_engine import analyze_complaint_image
from database import ComplaintDB, SessionLocal, init_db
from auth import verify_password, get_password_hash, create_access_token

app = FastAPI(title="AI Complaint Analyzer")


@app.on_event("startup")
def startup_event():
    init_db()


os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- DATA PRIVACY & SECURITY: MOCK USER DB ---
# In a real app, this goes in SQLite, but this is perfect for your Viva!
USERS = {
    "admin": {
        "username": "admin",
        "password_hash": get_password_hash("admin123"),  # Password is admin123
        "role": "admin"
    },
    "citizen": {
        "username": "citizen",
        "password_hash": get_password_hash("citizen123"),  # Password is citizen123
        "role": "citizen"
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/api/login")
def login(request: LoginRequest):
    user = USERS.get(request.username)
    if not user or not verify_password(request.password, user["password_hash"]):
        return {"status": "error", "message": "Invalid username or password"}

    # Generate secure JWT token
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"status": "success", "access_token": token, "role": user["role"]}


# ... (Keep your existing /api/submit-complaint and /api/analytics routes below this!) ...


@app.post("/api/submit-complaint")
async def submit_complaint(
    description: str = Form(...),
    category: str = Form(...),
    imageFile: UploadFile = File(...),
):
  image_filename = f"static/uploads/{imageFile.filename}"
  with open(image_filename, "wb") as buffer:
    shutil.copyfileobj(imageFile.file, buffer)

  # Run Deep Learning AI analysis
  ai_analysis = analyze_complaint_image(image_filename)

  db = SessionLocal()
  new_complaint = ComplaintDB(
      description=description,
      category=category,
      severity_score=ai_analysis["severity_score"],
      severity_level=ai_analysis["severity_level"],
      image_path=image_filename,
  )
  db.add(new_complaint)
  db.commit()
  db.close()

  return {
      "status": "success",
      "message": (
          "Complaint uploaded and analyzed via Deep Learning AI! Score:"
          f" {ai_analysis['severity_score']}"
      ),
  }


@app.get("/api/analytics")
def get_analytics():
  db = SessionLocal()
  complaints = db.query(ComplaintDB).all()
  db.close()

  # 1. Category aggregation for Donut Chart
  category_counts = {}
  # 2. Trend simulation or date aggregation for Line Chart
  trend_dates = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
  trend_counts = [12, 19, 8, 15, 22, 30, 25]  # Simulated weekly volume spikes

  for c in complaints:
    category_counts[c.category] = category_counts.get(c.category, 0) + 1

  return {
      "categories": list(category_counts.keys()),
      "counts": list(category_counts.values()),
      "trend_labels": trend_dates,
      "trend_data": trend_counts,
      "total_complaints": len(complaints),
  }