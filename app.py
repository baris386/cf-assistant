from typing import Optional
import os
import requests
import random
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
import markdown
import mimetypes

mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

# Load API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

client = None
if api_key:
    client = genai.Client(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not found in .env")

app = FastAPI()

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

# Mount static files for HTML/JS/CSS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
os.makedirs(FRONTEND_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

# --- MODELS ---
class HandleRequest(BaseModel):
    handle: str

class ProblemRequest(BaseModel):
    problem_id: str

class RecommendRequest(BaseModel):
    handle: str
    tags: list[str]
    min_rating: int
    max_rating: int

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    action: str  # "hint", "editorial", "recommend", "chat"
    message: Optional[str] = None
    problem_context: Optional[str] = None
    hint_count: Optional[int] = None
    history: list[ChatMessage] = []
    recommendation_prompt: Optional[str] = None

# --- HELPER FUNCTIONS ---
def get_solved_problems(handle):
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None, "User not found or CF API is down."
        data = response.json()
        if data["status"] != "OK":
            return None, "Error fetching user data."
        
        solved = set()
        for submission in data["result"]:
            if submission.get("verdict") == "OK":
                prob = submission.get("problem", {})
                contest_id = prob.get("contestId")
                index = prob.get("index")
                if contest_id and index:
                    solved.add(f"{contest_id}{index}")
        return list(solved), None
    except Exception as e:
        return None, f"API Connection error: {e}"

def fetch_filtered_problems(tags, min_rating, max_rating, solved_problems):
    if not tags:
        return []

    seen_ids = set()
    valid_problems = []
    solved_set = set(solved_problems)

    for tag in tags:
        cf_tag = tag.lower()
        if cf_tag == "constructive":
            cf_tag = "constructive algorithms"
        url = f"https://codeforces.com/api/problemset.problems?tags={cf_tag}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                continue
            data = response.json()
            if data["status"] != "OK":
                continue

            for prob in data["result"]["problems"]:
                rating = prob.get("rating")
                contest_id = prob.get("contestId")
                index = prob.get("index")
                name = prob.get("name")

                if rating and contest_id and index:
                    prob_id = f"{contest_id}{index}"
                    if (
                        min_rating <= rating <= max_rating
                        and prob_id not in solved_set
                        and prob_id not in seen_ids
                    ):
                        seen_ids.add(prob_id)
                        valid_problems.append({
                            "contestId": contest_id,
                            "index": index,
                            "name": name,
                            "rating": rating,
                        })
        except Exception:
            continue

    return valid_problems

def get_cf_problem(problem_id):
    problem_id = problem_id.strip().upper().replace("/", "")
    contest_id = "".join([c for c in problem_id if c.isdigit()])
    problem_letter = "".join([c for c in problem_id if c.isalpha()])
    
    if not contest_id or not problem_letter:
        return None, "Invalid format. Use '1920A'."
    
    urls_to_try = [
        f"https://codeforces.com/problemset/problem/{contest_id}/{problem_letter}",
        f"https://codeforces.com/contest/{contest_id}/problem/{problem_letter}"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for url in urls_to_try:
        try:
            response = requests.get(url, timeout=10, headers=headers)
            if response.status_code != 200:
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            problem_statement = soup.find("div", {"class": "problem-statement"})
            
            if problem_statement:
                return problem_statement.get_text(separator="\n"), url
        except Exception:
            continue
            
    return None, "Problem not found or statement could not be parsed. (Check if the ID is correct)"

SYSTEM_INSTRUCTION = (
    "You are an expert Competitive Programming (CP) coach. "
    "CRITICAL RULES:\n"
    "1. Respond exclusively in ENGLISH.\n"
    "2. STRICTLY FORBIDDEN from providing full source code.\n"
    "3. Provide logical observation hints or step-by-step editorial structures.\n"
)

# --- ENDPOINTS ---
@app.post("/api/sync-profile")
def api_sync_profile(req: HandleRequest):
    solved, err = get_solved_problems(req.handle)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return {"solved_problems": solved}

@app.post("/api/load-problem")
def api_load_problem(req: ProblemRequest):
    prob_text, url_or_err = get_cf_problem(req.problem_id)
    if not prob_text:
        raise HTTPException(status_code=400, detail=url_or_err)
    return {"problem_text": prob_text, "url": url_or_err}

@app.post("/api/recommend")
def api_recommend(req: RecommendRequest):
    solved, err = get_solved_problems(req.handle)
    if err:
        solved = []
        
    matched_pool = fetch_filtered_problems(
        req.tags,
        req.min_rating,
        req.max_rating,
        solved
    )
    
    chosen_problems = random.sample(matched_pool, min(len(matched_pool), 3))
    if not chosen_problems:
        return {"problems": [], "message": f"No unsolved problems found for tags: {', '.join(req.tags)}"}
        
    return {"problems": chosen_problems}

@app.post("/api/chat")
def api_chat(req: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API Key missing.")

    prompt = ""
    if req.action == "hint":
        prompt = f"Provide Hint {req.hint_count} for this problem. No full code:\n\n{req.problem_context}"
    elif req.action == "editorial":
        prompt = f"Explain the editorial approach step by step. No full code:\n\n{req.problem_context}"
    elif req.action == "recommend":
        prompt = req.recommendation_prompt
    else:
        context = ""
        if req.problem_context:
            context = f"Active Problem Context:\n{req.problem_context}\n\n"
        prompt = context + req.message

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config={"system_instruction": SYSTEM_INSTRUCTION}
        )
        
        # Convert markdown response to HTML for the frontend to render directly
        html_content = markdown.markdown(response.text, extensions=['fenced_code', 'tables'])
        
        return {"response": response.text, "html": html_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
