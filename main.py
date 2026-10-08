import uvicorn
from fastapi import FastAPI, Request, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid
from gemini_utils import get_gemini_recommendations

app = FastAPI(title="PocketSmart AI Engine")
templates = Jinja2Templates(directory="templates")

# Memory State Context Managers (Replace with SQL databases for live production)
SESSIONS = {}
USER_DB = {"admin": "password123"}
HISTORY_DB = {}

def get_current_user(request: Request) -> Optional[str]:
    sid = request.cookies.get("session_id")
    return SESSIONS.get(sid)

@app.get("/", response_class=HTMLResponse)
async def main_root(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/testimonials", response_class=HTMLResponse)
async def view_testimonials(request: Request):
    user = get_current_user(request)
    return templates.TemplateResponse("testimonials.html", {"request": request, "user": user})

@app.get("/register", response_class=HTMLResponse)
async def reg_view(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "error": None})

@app.post("/register")
async def handle_reg(username: str = Form(...), password: str = Form(...)):
    if username in USER_DB:
        return templates.TemplateResponse("register.html", {"request": {}, "error": "Username is already taken."})
    USER_DB[username] = password
    HISTORY_DB[username] = []
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
async def handle_login(username: str = Form(...), password: str = Form(...)):
    if username in USER_DB and USER_DB[username] == password:
        sid = str(uuid.uuid4())
        SESSIONS[sid] = username
        if username not in HISTORY_DB:
            HISTORY_DB[username] = []
        resp = RedirectResponse(url="/planner", status_code=status.HTTP_303_SEE_OTHER)
        resp.set_cookie(key="session_id", value=sid)
        return resp
    return templates.TemplateResponse("login.html", {"request": {}, "error": "Invalid credential verification credentials."})

@app.get("/logout")
async def handle_logout():
    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie(key="session_id")
    return resp

@app.get("/planner", response_class=HTMLResponse)
async def plan_dashboard(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("planner_home.html", {"request": request, "user": user})

@app.get("/planner/home-interior", response_class=HTMLResponse)
async def route_interior(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login")
    return templates.TemplateResponse("planner_home_interior.html", {"request": request, "user": user})

@app.get("/planner/party", response_class=HTMLResponse)
async def route_party(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login")
    return templates.TemplateResponse("planner_party.html", {"request": request, "user": user})

@app.get("/planner/jewelry", response_class=HTMLResponse)
async def route_jewelry(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login")
    return templates.TemplateResponse("planner_jewelry.html", {"request": request, "user": user})

@app.post("/recommendations-details", response_class=HTMLResponse)
async def run_calculations(
    request: Request,
    category: str = Form(...),
    budget: float = Form(...),
    preferences: str = Form(...),
    image_file: Optional[UploadFile] = File(None)
):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    img_bytes = None
    if image_file and image_file.filename:
        img_bytes = await image_file.read()
        
    ai_data = get_gemini_recommendations(category, budget, preferences, img_bytes)
    
    log = {
        "category": category.upper(),
        "budget": budget,
        "preferences": preferences,
        "summary": ai_data.get("category_summary", "Compiled Report Details"),
        "breakdown": ai_data.get("breakdown", [])
    }
    if user in HISTORY_DB:
        HISTORY_DB[user].append(log)
        
    return templates.TemplateResponse("recommendations_result.html", {
        "request": request, "user": user, "category": category, "result": ai_data
    })

@app.get("/history", response_class=HTMLResponse)
async def view_history_log(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse("history.html", {"request": request, "user": user, "history": HISTORY_DB.get(user, [])})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
