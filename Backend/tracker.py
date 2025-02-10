import time
from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
from datetime import datetime
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize TinyDB
bug_db = TinyDB("bugs.json")
comments_db = TinyDB("comments.json")  # Separate DB for comments

# Helper function to convert to DD-MM-YYYY HH:MM format
def get_dateTime():
    return datetime.now().strftime("%m-%d-%Y %H:%M")

def get_bugReportID():
    unix_time = int(time.time())
    formatted = datetime.now().strftime("%m%d")
    report_id = f"{unix_time}{formatted}"
    return report_id

@app.route("/")
def home():
    return "Bug Tracker API is running! Visit /api/"

#####
## These next few sections are for getting and posting bug reports and well as listing all available ones
## /api/bugs
## /api/bugs/{id}
#
# {
#    "id": unix timecode,
#    "issue_id": "unix timecode",
#    "username": "captured username",
#    "date": "dd-mm-yyyy hh:mm",
#    "issue": "captured issue from discord bot",
#    "status": "Open" 
# }
#
#####

@app.route("/api/bugs", methods=["POST"])
def create_bug():
    data = request.json

    # Generate unique ID using Unix timestamp
    bug_id = int(time.time())

    # Extract data from the request, ill get this from the bot later
    username = data.get("username", "Anonymous")
    issue = data.get("issue", "No description provided")

    # Create bug record
    new_bug = {
        "id": bug_id,  
        "issue_id": bug_id,  
        "username": username,
        "date": get_dateTime(),
        "issue": issue,
        "status": "Open"
    }

    # Add the bug to bug_DB
    bug_db.insert(new_bug)
    return jsonify({"message": "Bug reported successfully!", "bug": new_bug}), 201


@app.route("/api/bugs/<int:bug_id>", methods=["GET"])
def get_bug(bug_id):
    try:
        print(f"Debug: Fetching bug with ID = {bug_id}")  # Debugging
        Bug = Query()
        
        # Query bug_db for the bug report
        bug = bug_db.search(Bug.id == bug_id)
        print(f"Debug: Query result = {bug}")  # Debugging

        # Check if the query returned a non-empty list
        if bug and isinstance(bug, list) and len(bug) > 0:
            # Reorder the keys
            ordered_bug = {
                "id": bug[0]["id"],
                "issue_id": bug[0]["issue_id"],  
                "username": bug[0]["username"],
                "date": bug[0]["date"],
                "issue": bug[0]["issue"],
                "status": bug[0]["status"]
            }
            return jsonify(ordered_bug), 200
        else:
            return jsonify({"message": "Bug not found"}), 404
    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return jsonify({"message": "Internal server error", "error": str(e)}), 500
   

@app.route("/api/bugs", methods=["GET"])
def get_all_bugs():
    # Retrieve all bugs from bugs_db
    all_bugs = bug_db.all()
    return jsonify(all_bugs), 200

#####
## These functions are for the comments database, much like bugs it lists all and by id
## /api/comments
## /api/comments/{id}
#
# {
#    "id": "unix timecode",
#    "username": "captured username",
#    "date": "dd-mm-yyyy hh:mm",
#    "comment": "Captured comment",
#    "issue_id": "bug report issue_id",
#    "reply_to": " ",
#    "is_pinned:": false
# }
#
#####

@app.route("/api/comments", methods=["POST"])
def create_comment():
    data = request.json

    # Generate unique ID using Unix timestamp
    comment_id = int(time.time())

    # Extract data from the request
    issue_id = data.get("issue_id")
    comment = data.get("comment", "No comment provided")

    # Create comment record
    new_comment = {
        "id": comment_id,
        "username": "username",
        "date": get_dateTime(),
        "comment": comment,
        "issue_id": issue_id,
        "reply_to": " ",
        "is_pinned": False
    }

    # Add the comment to TinyDB
    comments_db.insert(new_comment)

    return jsonify({"message": "Comment added successfully!", "comment": new_comment}), 201

@app.route("/api/comments/<int:bug_id>", methods=["GET"])
def get_comments_for_issue(bug_id):
    try:
        print(f"Debug: Fetching comments for issue ID = {bug_id}")  # Debugging
        Comment = Query()
        
        # Construct the issue_id string to match the format in comments.json
        issue_id = f"{bug_id}"
        
        # Query TinyDB for comments related to the issue
        comments = comments_db.search(Comment.issue_id == issue_id)
        print(f"Debug: Query result = {comments}")  # Debugging

        # Check if the query returned a non-empty list
        if comments and isinstance(comments, list) and len(comments) > 0:
            return jsonify(comments), 200
        else:
            return jsonify({"message": "No comments found for this issue"}), 404
    except Exception as e:
        print(f"Error: {e}")  # Debugging
        return jsonify({"message": "Internal server error", "error": str(e)}), 500

@app.route("/api/comments", methods=["GET"])
def get_all_comments():
    # Retrieve all comments from comments_db
    all_comments = comments_db.all()
    return jsonify(all_comments), 200

#####
##
## Update bug report status from 'Open', 'In Progress', 'Closed', and 'Resolved'
##
#####

@app.route("/api/bugs/<int:bug_id>/status", methods=["PUT"])
def update_bug_status(bug_id):
    data = request.json
    new_status = data.get("status")

    if not new_status:
        return jsonify({"message": "Status is required"}), 400

    # Query the bug
    Bug = Query()
    bug = bug_db.search(Bug.id == bug_id)

    if not bug:
        return jsonify({"message": "Bug not found"}), 404

    # Update the status
    bug_db.update({"status": new_status}, Bug.id == bug_id)

    return jsonify({"message": "Bug status updated successfully!"}), 200

@app.route("/api/", methods=["GET"])
def api_index():
    endpoint_descriptions = {
        "GET /": "Home page",
        "GET /api/": "List all available API endpoints",
        "GET /api/bugs": "Get all bugs",
        "POST /api/bugs": "Report a new bug",
        "GET /api/bugs/<int:bug_id>": "Get details of a specific bug",
        "PUT /api/bugs/<int:bug_id>/status": "Update the status of a bug",
        "GET /api/comments": "Get all comments",
        "POST /api/comments": "Add a new comment",
        "GET /api/comments/<int:bug_id>": "Get comments for a specific bug"
    }

    endpoints = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint != "static":  # Exclude static routes
            route = rule.rule
            methods = sorted(rule.methods - {"HEAD", "OPTIONS"})
            for method in methods:
                key = f"{method} {route}"
                description = endpoint_descriptions.get(key, "No description available")
                if route not in endpoints:
                    endpoints[route] = {"methods": [], "descriptions": {}}
                    
                endpoints[route]["methods"].append(method)
                endpoints[route]["descriptions"][method] = description

    return jsonify({"endpoints": endpoints}), 200

## Init application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)