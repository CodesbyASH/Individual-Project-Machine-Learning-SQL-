**FitFusion Assistant: Personalized Fitness Generator**

A Flask-based intelligent fitness recommendation system that leverages machine learning for personalized workout and diet planning.

Project Overview

FitFusion is a smart fitness web app built to empower beginners in their fitness journey(gym enthusiasts) by delivering tailored workout routines, nutritional advice, progress tracking, and motivational content. Designed for both beginners and fitness enthusiasts, the application makes personalized training accessible using advanced machine learning models, Flask-based architecture, and MySQL database integration.

🚀Key Features
🧮 BMI Calculator – Calculates BMI according to the user input.

🧠 ML-Powered Recommendation Engine – Uses Random Forest & Decision Tree algorithms to provide the workout.

🥗 Diet Plan Generator – Personalized based on fitness goals (build, lose, maintain) with a pdf version available.

📈 Progress Tracker – Regression model to analyze performance and adjust plans.

🧘 Workout Mistake Detection – Educational content to avoid common errors with a video demostration to reduce those errors.

📹 Embedded Video Support – Instructional demos for better understanding.

🧑‍🤝‍🧑 Community-Oriented – Future ready for social interaction and feedback loops.

The technology stack involved:

Frontend:	HTML5, CSS Templates
Backend:	Python (Flask), SQLAlchemy
Database:	MySQL
Machine Learning Libraries:	Scikit-learn (Random Forest, Regression, Decision Trees), Pandas, NumPy
Visualization & Docs:	Matplotlib, PDFKit, Markdown

📊 Machine Learning Models
Model	Purpose
Random Forest Classifier: To	predict suitable workout plans based on user inputs (age, BMI, goal, muscle group).
Decision Tree:	Recommends dietary options aligned with fitness objectives.
Regression Analysis:	Predicts user progress (e.g., BMI change, strength gains) over time.

🧱 System Architecture

User Input (Age, Height, Weight, Goal) 
    ↓
Flask Interface → ML Engine (RandomForest / Decision Tree)
    ↓
MySQL DB ←→ Workout/Diet Modules
    ↓
User Dashboard (BMI, Plan, Exercises, Diet, Progress Tracker)

![image](https://github.com/user-attachments/assets/79573fa8-594e-4776-b1ee-24536209eb38)

📅 Project Timeline Highlights
Phase	Tasks:
Sprint 1	Project proposal & planning
Sprint 2	Dataset collection & preprocessing
Sprint 3	Model training & validation
Sprint 4	Flask app development
Sprint 5	Integration & UI design
Sprint 6	Testing, optimization, documentation(Runs on cloud initially)

Project Demo:

![image](https://github.com/user-attachments/assets/4983c1d5-2233-4345-a143-94bdbf861e9f)


📚 Documentation attached:
✔ Final Project Report

✔ Literature Review

✔Project Management Plan

✔Flask Code(app.py)


🎯 Future Enhancements:
Integration with wearable devices

Real-time feedback through NLP

Cloud-based deployment (Azure)

Mental health wellness modules











