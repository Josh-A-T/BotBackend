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

# Helper function to convert to Julian date
def get_julian_date():
    return datetime.now().strftime("%j")  

@app.route("/")
def home():
    return "Bug Tracker API is running! TEST"


#####
## These next few sections are for getting and posting bug reports and well as listing all available ones
## /api/bugs
## /api/bugs/{id}
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
        "issue_id": f"{bug_id}",  
        "username": username,
        "date": get_julian_date(),
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
        "date": get_julian_date(),
        "comment": comment,
        "issue_id": issue_id
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
## Update bug report status from 'Open', 'In Progress', 'Closed', and 'Resolved'
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


## Init application

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)