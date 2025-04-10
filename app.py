from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import requests
import os
import shutil
import git

from models import Token, get_db

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="your-super-secret-key",
    session_cookie="github_oauth_session"
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

REPO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'repos')

GITHUB_CLIENT_ID = "Ov23liYJuH7HwBE7Bhz2"
GITHUB_CLIENT_SECRET = "16bb7c8351818f713bb16baeaae7f95897ca0e6a"
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com/user"

def ensure_repo_dir():
    if not os.path.exists(REPO_DIR):
        os.makedirs(REPO_DIR)

def get_valid_token(username: str, db: Session) -> Optional[str]:
    token = db.query(Token).filter(Token.username == username).order_by(Token.created_at.desc()).first()
    return token.access_token if token and not token.is_expired() else None

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "user": request.session.get("user")})

@app.get("/login")
async def login():
    return RedirectResponse(f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=repo")

@app.get("/callback")
async def callback(code: str, request: Request, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="No code received")
    
    token_response = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={"client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code},
    )
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    token_type = token_json.get("token_type")
    scope = token_json.get("scope")
    
    headers = {"Authorization": f"token {access_token}"}
    user_response = requests.get(GITHUB_API_URL, headers=headers)
    username = user_response.json().get("login")
    
    expires_at = datetime.now() + timedelta(days=30)
    new_token = Token(
        username=username,
        access_token=access_token,
        token_type=token_type,
        scope=scope,
        expires_at=expires_at
    )
    
    try:
        db.add(new_token)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    
    request.session["user"] = username
    request.session["access_token"] = access_token
    
    return RedirectResponse(url="/repos")

@app.get("/repos")
async def repos(request: Request, db: Session = Depends(get_db)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    
    username = request.session["user"]
    access_token = get_valid_token(username, db)
    
    if not access_token:
        return RedirectResponse(url="/login")
    
    headers = {"Authorization": f"token {access_token}"}
    repos_response = requests.get(f"https://api.github.com/user/repos", headers=headers)
    repos = repos_response.json()
    
    return templates.TemplateResponse(
        "repos.html",
        {"request": request, "repos": repos, "user": username}
    )

@app.get("/clone_repo/{owner}/{repo}")
async def clone_repo(owner: str, repo: str, request: Request, db: Session = Depends(get_db)):
    if "user" not in request.session:
        return RedirectResponse(url="/login")
    
    username = request.session["user"]
    access_token = get_valid_token(username, db)
    
    if not access_token:
        return RedirectResponse(url="/login")
    
    ensure_repo_dir()
    repo_path = os.path.join(REPO_DIR, f"{owner}_{repo}")
    
    if os.path.exists(repo_path):
        shutil.rmtree(repo_path)
    
    clone_url = f"https://{access_token}@github.com/{owner}/{repo}.git"
    git.Repo.clone_from(clone_url, repo_path)
    
    return RedirectResponse(url="/repos")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)