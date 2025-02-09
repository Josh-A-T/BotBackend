# Discord Bug Tracker and Fullstack App

This is an attempt to create a discord bot and associated application to track simple issues. Right now it consists of 3 parts
1. A Flask + TinyDB backend. This creates the API out Frontend will talk to
2. A Discord bot that does not exist. In the future users can use slash commands to file, track and update bug reports
3. A react + Vite frontend. This is how the developer will be able to track, update, comment and close bug reports. potentially also allowing users to comment after a reports been filed. Right now it is hard coded to pull from one test report that has two associated comments. 


This is the first part, the flask and tinydb backend

Do not install, barely works for me now. There is an attempt at documenting the API in src/docs/testing.html but its late. 