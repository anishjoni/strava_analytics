# Learning Log for Strava Analytics Project

## Table of Contents
- [Learning Log for Strava Analytics Project](#learning-log-for-strava-analytics-project)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Goals and Objectives](#goals-and-objectives)
  - [Daily Progress](#daily-progress)
  - [Challenges and Solutions](#challenges-and-solutions)
  - [Key Learnings](#key-learnings)
  - [Resources and References](#resources-and-references)
  - [Future Improvements](#future-improvements)

---

## Project Overview
- Build end-to-end data pipeline of Strava data to enable data exploration and analytics.
- Main purpose of this project is to learn by building and breaking stuff. 
- Scope of the project includes:
    * Data sourcing via Strava API.
    * Data ingestion into MySQL DB.
    * Exploratory data analysis using Python.
    * Predictive modeling using Python.
  

## Goals and Objectives
- **Primary goal** of this project is to have a working web app built from my cycling and running activities on Strava. The process of building a live web app powered by data is the goal and the *what* of the app would come from the process of building and exploration of the data. 
- Measurable objectives:
  - Automate activities data pulls from Strava and ingestion into MySQL database.
  - Identify 3 periods of performance plateau or improvement patterns using training metrics.
  - [Optional] Predict monthly activites by sport for next 3 months. 

## Daily Progress
  **Date:** 2025-05-07  
- Tasks completed:
    - Set up API Authentication and handling expiring tokens.
    - Blocked by missing read scope, despite requesting and getting a response with read, read_all scope via authorization request. 
- Insights gained:
  - *requests* package can handle most API requests including auth, data pulls and manual data ingestion. 
  - Handling expiring tokens might take some time to get used to. 
- Next steps:
  - Incorporate [stravalib](https://stravalib.readthedocs.io/en/latest/get-started/authenticate-with-strava.html) for handling Strava API requests. 
  - Find a way to pull Strava activities evading the missing read scope problem.

## Challenges and Solutions
- Document issues encountered.
  - Cannot pull activities data due to no read scope error, despite the authorization token having the read scope.
- Describe how they were resolved.
  - df

## Key Learnings
- Summarize important concepts or skills learned.

## Resources and References
- List articles, tutorials, or documentation used.

## Future Improvements
- Ideas for enhancing the project.
- Features to add or optimize.
- Areas for further learning.
