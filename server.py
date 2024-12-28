import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, APIRouter, Request, Body
from fastapi.responses import JSONResponse
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
from datetime import datetime, date, timedelta
from typing import List, Tuple, Dict, Any, Literal, TypedDict

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, (np.floating, np.complexfloating)):
            return float(obj)
        if isinstance(obj, (np.integer)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.str_):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, timedelta):
            return str(obj)
        return super(NpEncoder, self).default(obj)
class NumpyResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            cls=NpEncoder,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

######################################################################################
#                                  SERVER BASICS                                     #
######################################################################################

class SearchRequest(BaseModel):
    keywords: str
    lat: float = 38.89511
    long: float = -77.03637
    threshold: float = 0.3 #threshold to cut off the search results
    start_index: int=0 #start index to return
    end_index: int=50 #end index to return, by default quite high, so that the user can scroll through the results
class LocationRequest(BaseModel):
    #default location is washington dc
    lat: float = 38.89511
    long: float = -77.03637
    start_index: int=0 #start index to return
    end_index: int=50 #end index to return, by default quite high, so that the user can scroll through the results

class ExploreRequest(BaseModel):
    topics: List[str]
    lat: float = 38.89511
    long: float = -77.03637
    threshold: float = 0.5 #similarity threshold to the selected topics
    start_index: int = 0 #start index to return
    end_index: int = 50 #end index to return, by default quite high, so that the user can scroll through the results


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
    for id, filename in enumerate(os.listdir(directory)):
        if filename.startswith("example"):
            continue
        with open(os.path.join(directory, filename), 'r') as file:
            events.append(json.load(file))
            events[-1]["id"] = id

    print(f"Loaded {len(events)} events.")
    return events

#is done on actual starting of the server
@asynccontextmanager
async def lifespan(app:FastAPI):
    # Start up
    global events, model, event_embeddings
    events = load_events()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    event_embeddings = model.encode([e["theme"] +": " + ", ".join(e["hashtags"]) + ";" + e["short_description"] for e in events])

    #do the user embeddings
    for user in users:
        if user != "average_user":
            updateEmbeddings(user, users[user]["preferences"]) #average user embeddings are updated in the function automatically

    yield

    # Clean up
    del events

app = FastAPI(lifespan=lifespan)
#add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

    updateAverageUserEmbeddings()

def compare_preference_events(username: str) -> np.ndarray:
    """Computes the events best fitting the user's preferences
    
    Args:
        username (str): The username of the user
        
    Returns:
        np.ndarray: Similarity scores for the events to the user's preferences. Shape is (n_events,)
    """
    user = users.get(username)
    print(f"User: {user}") #debug
    user_similarities = cosine_similarity(user.get("embeddings"), event_embeddings)
    max_indexes = list(np.argmax(user_similarities, axis=0)) #get the best match for each event
    user_similarities = np.array([user_similarities[max_indexes, i] for i in range(len(max_indexes))])

    return user_similarities

def updateAverageUserEmbeddings():
    """Updates the average user embeddings based on the embeddings of all users
    
    """
    #get all user embeddings
    user_embeddings = [user["embeddings"] for user in users.values() if user["username"] != "average_user"]
    #throw out nan embeddings
    user_embeddings = [embedding for embedding in user_embeddings if not np.isnan(embedding).any()]

    #compute the average
    average_user_embeddings = np.mean(user_embeddings, axis=0)
    print(f"Average user embeddings: {average_user_embeddings}")
    #update the average user embeddings
    users["average_user"]["embeddings"] = average_user_embeddings
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
    "average_user": {
        "username": "average_user",
        "password": "alfjbxsfb249748agsbxfby2f78gadkf", #make it unaccessible
        "user_id": -1,
        "preferences": [],
        "embeddings" : np.array([np.nan])
    },
    "testname1": {
        "username": "testname1",
        "password": "simplepassword",
        "user_id": 0,
        "preferences": ["music", "concerts", "rock", "hard rock", "classical", "drummer", "orchestra", "male vocalist", "van gogh", "impressionism", "post-war"],
        "embeddings" : np.array([np.nan])
    },
    "testname2": {
        "username": "testname2",
        "password": "otherpassword",
        "user_id": 1,
        "preferences": ["ballet", "modern pop", "dance", "performing arts", "choreography", "female vocalist", "pop concerts", "contemporary dance", "music festivals", "theater", "taylor swift"],
        "embeddings" : np.array([np.nan])
    },
}

# In-memory session storage (for demonstration purposes)
sessions = {}
security = HTTPBasic()

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    user = users.get(credentials.username)
    if user is None or user["password"] != credentials.password:
        print(f"User {credentials} failed to log in with password {credentials.password}. User: \n{user}\n\tout of \n{users}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return user

def create_session(user: User):
    session_id = random.randint(0, 2**31)
    sessions[session_id] = user.get("username")
    return session_id

# Custom middleware for session-based authentication
def get_authenticated_user_from_session_id(request: Request):
    session_id = request.cookies.get("session_id") or request.headers.get("session_id")
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
    user = users.get(sessions.get(session_id))
    return user

# Create a new dependency to get the session ID from cookies
def get_session_id(request: Request):
    session_id = request.cookies.get("session_id") or request.headers.get("session_id")
    print(f"Session ID: {session_id}, got these sessions: {sessions}")
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
    session_id = create_session(user)
    return {"message": "Logged in successfully", "session_id": session_id}

#getCurrentUser, logout and delete are protected, thus shown below

@app.get("/users")
def get_users():
    return {"users": users}

@app.get("/users/{username}")
def get_user(username: str):
    user = users.get(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/events")
def get_events(count: int=50):
    return {"events": events}

@app.get("/events/{event_id}")
def get_event(event_id: int):
    if event_id < 0 or event_id >= len(events):
        raise HTTPException(status_code=404, detail="Event not found")
    return events[event_id]

@app.get("/events/{event_id}/similar")
def get_similar_events(event_id: int, count: int=5):
    if event_id < 0 or event_id >= len(events):
        raise HTTPException(status_code=404, detail="Event not found")
    event_embedding = event_embeddings[event_id]
    similarities = cosine_similarity([event_embedding], event_embeddings)[0]
    similar_events = sorted(
        zip(similarities, events), key=lambda x: x[0], reverse=True
    )
    return NumpyResponse({"similar_events": [{"event": e, "score": s} for s, e in similar_events[1:count]]})

@app.get("/nearbyevents")
def get_nearby_events(location: LocationRequest = Depends()):
    """Get events that are nearby the specified location"""

    # Adjust for location
    max_distance = 5000
    nearby_events = [
        e for e in events
        if haversine((location.lat, location.long), (e["coords"]["lat"], e["coords"]["lng"])) < max_distance
    ]

    # rank based on distance
    nearby_events = sorted(
        nearby_events, 
        key=lambda x:haversine(
            (location.lat, location.long), 
            (x["coords"]["lat"], x["coords"]["lng"])
        )
    )

    return {"events": nearby_events}

@app.get("/search")#same as /user/search but without the user stuff
def search_events(request: SearchRequest = Depends()):
    search_embedding = model.encode(request.keywords)
    search_similarities = cosine_similarity([search_embedding], event_embeddings)[0]

    # Adjust for location
    max_distance = 5000
    location_scores = [
        1 - min(haversine(
                (request.lat, request.long), 
                (e["coords"]["lat"], e["coords"]["lng"])
            )/max_distance, 1)
        for e in events
    ]
    #remove the events with more than 5000 km distance
    user_similarities = np.array([user_similarities[i] for i, score in enumerate(location_scores) if score < 1])
    location_scores = [score for score in location_scores if score < 1]

    # Combine scores (weights: similarity 70%, location 30%)
    alpha = 0.7
    beta = 0.3

    final_scores = [
        search * alpha + loc * beta for search, loc in zip(np.linalg.norm(search_similarities, ord=1), np.linalg.norm(location_scores, ord=1))
    ]

    # Rank and return events
    ranked_events = sorted(
        zip(final_scores, events), key=lambda x: x[0], reverse=True
    )

    #only return certain percentage by score of the events
    threshold = request.threshold
    total_score = sum([score for score, _ in ranked_events])
    current_score = 0
    threshold_event = 0

    for i, (score, _) in enumerate(ranked_events):
        current_score += score
        if current_score >= threshold * total_score:
            threshold_event = i
            break
    ranked_events = ranked_events[:threshold_event+1]

    return NumpyResponse({"events": [{"event": e, "score": s} for s, e in ranked_events]})

@app.get("/explore")
def explore_events(request: ExploreRequest = Depends()):
    topic_embeddings = model.encode(request.topics)
    topic_similarities = cosine_similarity(topic_embeddings, event_embeddings)
    event_scores = list(np.max(topic_similarities, axis=0))
    selected_events = [e for e, score in zip(events, event_scores) if score >= request.threshold]

    # Adjust for location
    max_distance = 5000
    location_scores = [
        1 - min(haversine(
                (request.lat, request.long), 
                (e["coords"]["lat"], e["coords"]["lng"])
            )/max_distance, 1)
        for e in events
    ]
    #remove the events with more than 5000 km distance
    user_similarities = np.array([user_similarities[i] for i, score in enumerate(location_scores) if score < 1])
    location_scores = [score for score in location_scores if score < 1]

    # Combine scores (weights: similarity 70%, location 30%)
    alpha = 0.7
    beta = 0.3

    final_scores = [
        user * alpha + loc * beta for user, loc in zip(np.linalg.norm(topic_similarities.sum(axis=0), ord=1), np.linalg.norm(location_scores, ord=1))
    ]

    # Rank and return events
    ranked_events = sorted(
        zip(final_scores, selected_events), key=lambda x: x[0], reverse=True
    )

    return NumpyResponse({"events": [{"event": e, "score": s} for s, e in ranked_events]})

@app.get("/recommendations")
def get_recommendations(location: LocationRequest = Depends()):
    #use the average user embeddings to get the recommendations
    user_similarities = compare_preference_events("average_user")

    # Adjust for location
    max_distance = 5000
    location_scores = [
        1 - min(haversine(
                (location.lat, location.long), 
                (e["coords"]["lat"], e["coords"]["lng"])
            )/max_distance, 1)
        for e in events
    ]
    #remove the events with more than 5000 km distance
    user_similarities = np.array([user_similarities[i] for i, score in enumerate(location_scores) if score < 1])
    location_scores = [score for score in location_scores if score < 1]

    # Combine scores (weights: similarity 70%, location 30%)

    alpha = 0.7
    beta = 0.3

    final_scores = [
        user * alpha + loc * beta for user, loc in zip(np.linalg.norm(user_similarities, ord=1), np.linalg.norm(location_scores, ord=1))
    ]

    # Rank and return events
    ranked_events = sorted(
        zip(final_scores, events), key=lambda x: x[0], reverse=True
    )

    return NumpyResponse({"events": [{"event": e, "score": s} for s, e in ranked_events]})


######################################################################################
#                                   PROTECTED ENDPOINTS                              #
######################################################################################
# Get the current user
@app.get("/getme")
def read_current_user(user: User = Depends(get_authenticated_user_from_session_id)):
    return user

# Logout endpoint - Removes the session
@app.post("/logout")
def logout(session_id: int = Depends(get_session_id)):
    if session_id not in sessions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    sessions.pop(session_id)
    return {"message": "Logged out successfully", "session_id": session_id}

@app.post("/deleteuser")
def delete_user(user: User = Depends(get_authenticated_user_from_session_id)):
    username = user["username"]
    del users[username]
    return {"message": f"User '{username}' deleted successfully"}

@app.get("/user/preferences")
def get_preferences(user:User = Depends(get_authenticated_user_from_session_id)):
    return {"preferences": user["preferences"]}

@app.put("/user/preferences")
def update_preferences(preferences: Dict[Literal["add","remove"], List[str]], user: User= Depends(get_authenticated_user_from_session_id)):
    # Update the user's preferences, add new ones, remove specified ones
    if "add" in preferences:
        user["preferences"].extend([p for p in preferences["add"] if p not in user["preferences"]])
    if "remove" in preferences:
        user["preferences"].remove([p for p in preferences["remove"] if p in user["preferences"]])

    #update the user embeddings
    updateEmbeddings(user["username"], user["preferences"])

    return {"message": "Preferences updated successfully"}


#TOOD: get good values for alpha, beta, gamma, threshold
@app.post("/user/search")
def search_events_user(request: SearchRequest = Depends(), user:User = Depends(get_authenticated_user_from_session_id)):

    user_similarities = compare_preference_events(user.get("username"))

    # Get event scores by keywords
    search_embedding = model.encode(request.keywords)  
    search_similarities = cosine_similarity([search_embedding], event_embeddings)[0]

    # Adjust for location
    max_distance = 5000  # Example max distance in km
    location_scores = [
        1 - min(haversine(
                (request.lat, request.long), 
                (e["coords"]["lat"], e["coords"]["lng"])
            )/max_distance, 1)
        for e in events
    ]
    #remove the events with more than 5000 km distance
    user_similarities = np.array([user_similarities[i] for i, score in enumerate(location_scores) if score < 1])
    location_scores = [score for score in location_scores if score < 1]

    #TODO do we expose these values to the user?
    alpha = 0.3
    beta = 0.5
    gamma = 0.2

    # Combine scores (weights: similarity 70%, location 30%)
    final_scores = [
        user * alpha + search*beta +  loc * gamma for user, search, loc in zip(np.linalg.norm(user_similarities, ord=1),np.linalg.norm( search_similarities, ord=1), np.linalg.norm(location_scores, ord=1))
    ]


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

    return NumpyResponse({"events": [{"event": e, "score": s} for s, e in ranked_events]})


@app.get("/user/explore")
def explore_events_user(request:ExploreRequest = Depends(), user:User = Depends(get_authenticated_user_from_session_id)):
    #filter the events based on a similarity threshold to any of the topics
    #rank by similarity to the user preferences

    user_similarities = compare_preference_events(user.get("username"))

    #TODO: get good value for threshold, 
    #TODO: do we expose the threshold to the user, if so we should expose a transformed value, maybe exp or sth
    threshold = request.threshold

    # Get event scores by topics
    topic_embeddings = model.encode(request.topics)
    topic_similarities = cosine_similarity(topic_embeddings, event_embeddings)
    #select events that have at least once a similarity above the threshold
    event_scores = list(np.max(topic_similarities, axis=0))
    selected_events = [e for e, score in zip(events, event_scores) if score >= threshold]

    # Adjust for location
    max_distance = 5000  # Example max distance in km
    location_scores = [
        1 - min(haversine(
                (request.lat, request.long), 
                (e["coords"]["lat"], e["coords"]["lng"])
            )/max_distance, 1)
        for e in events
    ]
    #remove the events with more than 5000 km distance
    user_similarities = np.array([user_similarities[i] for i, score in enumerate(location_scores) if score < 1])
    location_scores = [score for score in location_scores if score < 1]

    #rank by similarity to the user preferences and location
    alpha = 0.7
    beta = 0.3

    final_scores = [
        user * alpha + loc * beta for user, loc in zip(np.linalg.norm(user_similarities, ord=1), np.linalg.norm(location_scores, ord=1))
    ]

    # Rank and return events
    ranked_events = sorted(
        zip(final_scores, selected_events), key=lambda x: x[0], reverse=True
    )

    return NumpyResponse({"events": [{"event": e, "score": s} for s, e in ranked_events]})

@app.get("/user/recommendations")
def get_recommendations_user(location:LocationRequest = Depends(), user:User = Depends(get_authenticated_user_from_session_id)):
    #get recommendations just by user similarity and distance

    user_similarities = compare_preference_events(user.get("username"))

    # Adjust for location
    max_distance = 5000  # Example max distance in km
    location_scores = [
        1 - min(haversine(
                (location.lat, location.long), 
                (e["coords"]["lat"], e["coords"]["lng"])
            )/max_distance, 1)
        for e in events
    ]
    #remove the events with more than 5000 km distance
    user_similarities = np.array([user_similarities[i] for i, score in enumerate(location_scores) if score < 1])
    location_scores = [score for score in location_scores if score < 1]

    #TODO do we expose these values to the user? i we do, we expose them as a slider with multiple markers
    alpha = 0.7
    beta = 0.3

    # Combine scores (weights: similarity 70%, location 30%)

    final_scores = [
        user * alpha + loc * beta for user, loc in zip(np.linalg.norm(user_similarities, ord=1), np.linalg.norm(location_scores, ord=1))
    ]

    # Rank and return events
    ranked_events = sorted(
        zip(final_scores, events), key=lambda x: x[0], reverse=True
    )

    return NumpyResponse({"events": [{"event": e, "score": s} for s, e in ranked_events]})



if __name__ == "__main__":
    #argparsing
    parser = argparse.ArgumentParser(description='Run the server')
    parser.add_argument('--dev', '-d', action='store_true', default=False, help='Run the frontend server in development mode')
    parser.add_argument('--kill-on-exit', '-k', action='store_true', default=True, help='Kill the frontend server when the backend server is killed')
    parser.add_argument('--no-kill-on-exit', '-nk', action='store_false', dest='kill_on_exit', help='Do not kill the frontend server when the backend server is killed')
    parser.add_argument('--backend-only', '-b', action='store_true', default=False, help='Run only the backend server')
    args = parser.parse_args()

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



