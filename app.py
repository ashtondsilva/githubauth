import os
import requests
from flask import Flask, redirect, request, session, jsonify, render_template, send_file
import tempfile
import shutil
import zipfile

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure random secret key

# GitHub OAuth Config
GITHUB_CLIENT_ID = "Ov23liyBBcRGPZLTiDqg"
GITHUB_CLIENT_SECRET = "acc065cffe4347255df3afbb517e4ce941b10f82"
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com/user"

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
    session["access_token"] = token_json.get("access_token")
    
    # Step 5: Get user details
    headers = {"Authorization": f"token {session['access_token']}"}
    user_response = requests.get(GITHUB_API_URL, headers=headers)
    session["user"] = user_response.json().get("login")
    
    return redirect("/repos")

# Step 6: Fetch and display user repositories
@app.route("/repos")
def repos():
    if "access_token" not in session:
        return redirect("/login")
    
    headers = {"Authorization": f"token {session['access_token']}"}
    repos_response = requests.get("https://api.github.com/user/repos", headers=headers)
    repos_json = repos_response.json()
    
    return render_template("repos.html", user=session["user"], repos=repos_json)

# Step 7: Download Repository
@app.route("/download_repo/<owner>/<repo_name>")
def download_repo(owner, repo_name):
    if "access_token" not in session:
        return redirect("/login")
    
    headers = {"Authorization": f"token {session['access_token']}"}
    
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

if __name__ == "__main__":
    app.run(debug=True)