import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Body
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
from pydantic import BaseModel
import os
import argparse
import subprocess
import time

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from haversine import haversine
import numpy as np

import json
from typing import List, Tuple, Dict, Any, Literal, TypedDict
######################################################################################
#                                  SERVER BASICS                                     #
######################################################################################
app = FastAPI()

class SearchRequest(BaseModel):
    preferences: str
    keywords: str
    location: Tuple[float, float]

######################################################################################
#                                 EVENT HANDLING                                     #
######################################################################################
model:SentenceTransformer = None
events:List[Dict[str, Any]] = None
event_embeddings:List[np.ndarray] = None

def load_events():
    directory = os.path.dirname(os.path.realpath(__file__))
    directory = os.path.join(directory, "data", "events")

    #this directory contains a ton of json files that should be read in to create the events list to be checked against.
    events = []
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), 'r') as file:
            events.append(json.load(file))

    return events

@asynccontextmanager
def lifespan():
    # Start up
    events = load_events()
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    event_embeddings = model.encode([e["hashtags"] + " " + e["short_description"] for e in events])
    yield

    # Clean up
    del events
    del event_embeddings


######################################################################################
#                                EMBEDDING HANDLING                                 #
# ####################################################################################

def updateEmbeddings(username: str, preferences: List[str]):
    """Updates the user embeddings implicitely based on the preferences
    
    Args:
        username (str): The username of the user
        preferences (List[str]): The preferences of the user
    """
    #get the user from the users dictionary
    user = users.get(username)
    #encode the user preferences individually and then cluster vie 3-means to generate a 3d preference embedding for the user
    preference_embeddings = model.encode(preferences)
    #cluster the embeddings
    kmeans = KMeans(n_clusters=3, random_state=0).fit(preference_embeddings)
    user["embeddings"] = kmeans.cluster_centers_

def compare_preference_events(username: str) -> np.ndarray:
    """Computes the events best fitting the user's preferences
    
    Args:
        username (str): The username of the user
        
    Returns:
        np.ndarray: Similarity scores for the events to the user's preferences. Shape is (n_events,)
    """
    user = users.get(username)
    user_similarities = cosine_similarity([user.get("preferences")], event_embeddings)
    max_indexes = list(np.argmax(user_similarities, axis=0)) #get the best match for each event
    user_similarities = np.array([user_similarities[max_indexes, i] for i in range(len(max_indexes))])

    return user_similarities

######################################################################################
#                                   LOCAL DATABASE                                   #
######################################################################################
# User Database (for demonstration purposes)
class User(TypedDict):
    username: str
    password: str
    user_id: int
    preferences: List[str]
    embeddings: np.ndarray

users:Dict[str, User] = {
    "testname1": {
        "username": "testname1",
        "password": "simplepassword",
        "user_id": 0,
        "preferences": ["music", "concerts", "rock", "hard rock", "classical", "drummer", "orchestra", "male vocalist", "van gogh", "impressionism", "post-war"],
        "embeddings" : np.array([np.nan])
    },
    "testname2": {
        "username": "testname2",
        "password": "simplepassword",
        "user_id": 1,
        "preferences": ["ballet", "modern pop", "dance", "performing arts", "choreography", "female vocalist", "pop concerts", "contemporary dance", "music festivals", "theater", "taylor swift"],
        "embeddings" : np.array([np.nan])
    },
}
# In-memory session storage (for demonstration purposes)
sessions = {}

def security(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    return credentials

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = users.get(credentials.username)
    if user is None or user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def create_session(user_id: int):
    session_id = random.randint(0, 2**31)
    sessions[session_id] = user_id
    return session_id

# Custom middleware for session-based authentication
def get_authenticated_user_from_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id is None or int(session_id) not in sessions:
        raise HTTPException(
            status_code=401,
            detail="Invalid session ID",
        )
    # Get the user from the session
    user = get_user_from_session_id(int(session_id))
    return user

# Use the valid session id to get the corresponding user from the users dictionary
def get_user_from_session_id(session_id: int):
    user = None
    for user_data in users.values():
        if user_data['user_id'] == sessions.get(session_id):
            user = user_data
            break

    return user

# Create a new dependency to get the session ID from cookies
def get_session_id(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id is None or int(session_id) not in sessions:
        raise HTTPException(status_code=401, detail="Invalid session ID")
    return int(session_id)

@app.post("/signup")
def sign_up(username: str = Body(...), password: str = Body(...)):
    user = users.get(username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    new_user_id = random.randint(0, 2**31)
    new_user = {
        "username": username,
        "password": password,
        "user_id": new_user_id,
        "preferences": [],
        "embeddings" : np.array([0])
    }
    users[username] = new_user
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: dict = Depends(authenticate_user)):
    session_id = create_session(user["user_id"])
    return {"message": "Logged in successfully", "session_id": session_id}

@app.get("/getusers/me")
def read_current_user(user: dict = Depends(get_user_from_session_id)):
    return user

# Logout endpoint - Removes the session
@app.post("/logout")
def logout(session_id: int = Depends(get_session_id)):
    if session_id not in sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    sessions.pop(session_id)
    return {"message": "Logged out successfully", "session_id": session_id}

@app.post("/deleteuser")
def delete_user(user: dict = Depends(get_user_from_session_id)):
    username = user["username"]
    del users[username]
    return {"message": f"User '{username}' deleted successfully"}

######################################################################################
#                                   PROTECTED ENDPOINTS                              #
######################################################################################

@app.get("/preferences")
def get_preferences(user:User = Depends(get_authenticated_user_from_session_id)):
    return {"preferences": user["preferences"]}

@app.put("/preferences")
def update_preferences(preferences: Dict[Literal["add"|"remove"]: List[str]], user: User= Depends(get_authenticated_user_from_session_id)):
    # Update the user's preferences, add new ones, remove specified ones
    if "add" in preferences:
        user["preferences"].extend([p for p in preferences["add"] if p not in user["preferences"]])
    if "remove" in preferences:
        user["preferences"].remove([p for p in preferences["remove"] if p in user["preferences"]])

    #update the user embeddings
    updateEmbeddings(user["username"], user["preferences"])

    return {"message": "Preferences updated successfully"}


#TOOD: get good values for alpha, beta, gamma, threshold
@app.post("/search")
def search_events(request: SearchRequest, user:User = Depends(get_authenticated_user_from_session_id)):

    user_similarities = compare_preference_events(user.get("username"))

    # Get event scores by keywords
    search_embedding = model.encode(request.keywords)  
    search_similarities = cosine_similarity([search_embedding], event_embeddings)[0]

    # Adjust for location
    max_distance = 5000  # Example max distance in km
    location_scores = [
        1 - min(haversine(request.location, e["location_coords"]) / max_distance, 1)
        for e in events
    ]

    #TODO do we expose these values to the user?
    alpha = 0.3
    beta = 0.5
    gamma = 0.2

    # Combine scores (weights: similarity 70%, location 30%)
    final_scores = [
        user * alpha + search*beta +  loc * gamma for user, search, loc in zip(user_similarities, search_similarities, location_scores)
    ]
    #normalization
    max_score = max(final_scores)
    final_scores = [score / max_score for score in final_scores]


    # Rank and return events
    ranked_events = sorted(
        zip(final_scores, events), key=lambda x: x[0], reverse=True
    )

    #take only the events that make up X% of the total score mass
    threshold = 0.3
    total_score = sum([score for score, _ in ranked_events])
    current_score = 0
    threshold_event = 0

    for i, (score, _) in enumerate(ranked_events):
        current_score += score
        if current_score >= threshold * total_score:
            threshold_event = i
            break
    ranked_events = ranked_events[:threshold_event+1]

    return {"ranked_events": [{"event": e, "score": s} for s, e in ranked_events]}


if __name__ == "__main__":
    #argparsing
    parser = argparse.ArgumentParser(description='Run the server')
    parser.add_argument('--dev', '-d', action='store_true', default=False, help='Run the frontend server in development mode')
    parser.add_argument('--kill-on-exit', '-k', action='store_true', default=True, help='Kill the frontend server when the backend server is killed')
    parser.add_argument('--no-kill-on-exit', '-nk', action='store_false', dest='kill_on_exit', help='Do not kill the frontend server when the backend server is killed')
    parser.add_argument('--backend-only', '-b', action='store_true', default=False, help='Run only the backend server')
    args = parser.parse_args()

    #add CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    #create another process for the frontend server
    frontend_process = None
    if not args.backend_only:
        run_command = "npm run dev" if args.dev else "npm run build"
        if args.kill_on_exit:
            run_command += " &"
        frontend_process = subprocess.Popen(" && ".join(["echo 'Starting frontend server...'", run_command]), shell=True)

    #start the backend server
    uvicorn.run(app, host="127.0.0.1", port=8000)

    
    #wait for the frontend server to start
    if args.kill_on_exit and not args.backend_only:
        #if we got to here the uvicorn server has been killed
        print("Killing frontend server...")
        #differentiate windows , unix
        frontend_pid = frontend_process.pid
        frontend_process.kill()
        timeout = time.time() + 5 #wait for 5 seconds
        while frontend_process.poll() is None and timeout - time.time() > 0:
            pass

        #search for the frontend server process
        if os.name == 'nt':
            is_alive = os.system(f'tasklist | findstr {frontend_pid}')
        else:
            is_alive = os.system(f'ps -p {frontend_pid}')
        if is_alive == 0:
            print("Frontend server could not be killed. Please kill it manually.")
        else:
            print("Successfully killed the frontend server.")

    print("Exiting successfully.")
    exit(0)



