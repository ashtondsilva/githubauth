import os
import requests
import datetime
from flask import Flask, redirect, request, session, jsonify, render_template, send_file
import tempfile
import shutil
import zipfile
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from models import db, Token

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random secret key

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize SQLAlchemy with the app
db.init_app(app)

# GitHub OAuth Config
GITHUB_CLIENT_ID = "Ov23liYJuH7HwBE7Bhz2"
GITHUB_CLIENT_SECRET = "16bb7c8351818f713bb16baeaae7f95897ca0e6a"
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com/user"

# Initialize database tables on startup
with app.app_context():
    db.create_all()

# Function to get a valid token for a user
def get_valid_token(username):
    with app.app_context():
        token = Token.get_valid_token(username)
        return token.access_token if token else None

# Step 1: Home Page
@app.route("/")
def home():
    return render_template("index.html", user=session.get("user"))

# Step 2: Redirect users to GitHub for login
@app.route("/login")
def login():
    return redirect(f"{GITHUB_AUTH_URL}?client_id={GITHUB_CLIENT_ID}&scope=repo")

# Step 3: GitHub redirects back with a code
@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code:
        return "Error: No code received."
    
    # Step 4: Exchange code for access token
    token_response = requests.post(
        GITHUB_TOKEN_URL,
        headers={"Accept": "application/json"},
        data={"client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code},
    )
    token_json = token_response.json()
    access_token = token_json.get("access_token")
    token_type = token_json.get("token_type")
    scope = token_json.get("scope")
    
    # Store token in session for current use
    session["access_token"] = access_token
    
    # Step 5: Get user details
    headers = {"Authorization": f"token {access_token}"}
    user_response = requests.get(GITHUB_API_URL, headers=headers)
    username = user_response.json().get("login")
    session["user"] = username
    
    # Store token in database with expiration (30 days from now)
    expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
    
    try:
        new_token = Token(
            username=username,
            access_token=access_token,
            token_type=token_type,
            scope=scope,
            expires_at=expires_at
        )
        db.session.add(new_token)
        db.session.commit()
    except Exception as e:
        print(f"Error storing token: {e}")
        db.session.rollback()
    
    return redirect("/repos")

# Step 6: Fetch and display user repositories
@app.route("/repos")
def repos():
    if "user" not in session:
        return redirect("/login")
    
    username = session["user"]
    # Try to get token from database first
    access_token = get_valid_token(username)
    
    # If no valid token in database, use session token or redirect to login
    if not access_token:
        if "access_token" not in session:
            return redirect("/login")
        access_token = session["access_token"]
    
    headers = {"Authorization": f"token {access_token}"}
    repos_response = requests.get("https://api.github.com/user/repos", headers=headers)
    repos_json = repos_response.json()
    
    return render_template("repos.html", user=username, repos=repos_json)

# Step 7: Download Repository
@app.route("/download_repo/<owner>/<repo_name>")
def download_repo(owner, repo_name):
    if "user" not in session:
        return redirect("/login")
    
    username = session["user"]
    # Try to get token from database first
    access_token = get_valid_token(username)
    
    # If no valid token in database, use session token or redirect to login
    if not access_token:
        if "access_token" not in session:
            return redirect("/login")
        access_token = session["access_token"]
    
    headers = {"Authorization": f"token {access_token}"}
    
    # Create a temporary directory to store the downloaded repository
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Download repository as zip
        zip_url = f"https://api.github.com/repos/{owner}/{repo_name}/zipball"
        zip_response = requests.get(zip_url, headers=headers, stream=True)
        
        # Save the zip file
        zip_path = os.path.join(temp_dir, f"{repo_name}.zip")
        with open(zip_path, 'wb') as f:
            for chunk in zip_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Send the file for download
        return send_file(zip_path, as_attachment=True, download_name=f"{repo_name}.zip")
    
    except Exception as e:
        return f"Error downloading repository: {str(e)}"
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)

# Step 8: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Admin interface to view stored tokens
@app.route("/admin/tokens")
def admin_tokens():
    tokens = Token.query.order_by(Token.created_at.desc()).all()
    
    # Pass current time to template for expiration checking
    now = datetime.datetime.now()
    
    return render_template("admin_tokens.html", tokens=tokens, now=now)

if __name__ == "__main__":
    app.run(debug=True)