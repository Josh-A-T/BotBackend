from flask import Flask, request, jsonify
from tinydb import TinyDB, Query
import time
from datetime import datetime
import os
if os.path.exists("bugs.json"):
    os.remove("bugs.json")

# Reinitialize TinyDB
db = TinyDB("bugs.json")

# Insert test data
db.insert_multiple([
    {
        "id": 1707409001,
        "username": "GameTester42",
        "date": "039",
        "issue": "The game crashes when trying to load a saved file."
    },
    {
        "id": 1707409102,
        "username": "Anonymous",
        "date": "039",
        "issue": "The main character's animation freezes when jumping near walls."
    },
    {
        "id": 1707409203,
        "username": "DevQA",
        "date": "039",
        "issue": "Music stops playing after completing level 3."
    },
    {
        "id": 1707409304,
        "username": "SpeedRunnerPro",
        "date": "039",
        "issue": "Enemies disappear when moving quickly through the level."
    }
])