from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pdfkit

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configure the MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%40pplE%21375@localhost/fitdata'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define the WorkoutData model to map to the fitness_recommender table
class WorkoutData(db.Model):
    __tablename__ = 'fitness_recommender'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    age = db.Column(db.Integer, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    muscle_group = db.Column(db.String(50), nullable=False)
    specific_muscle = db.Column(db.String(50), nullable=False)
    fitness_goal = db.Column(db.String(50), nullable=False)
    workout_plan = db.Column(db.String(50), nullable=False)
    exercises = db.Column(db.Text, nullable=False)
    exercise_image_1 = db.Column(db.String(255), nullable=True)
    exercise_image_2 = db.Column(db.String(255), nullable=True)
    exercise_image_3 = db.Column(db.String(255), nullable=True)
    diet_recommendation = db.Column(db.String(50), nullable=False)
    daily_calorie_intake = db.Column(db.Integer, nullable=False)
    diet_details = db.Column(db.Text, nullable=True)
    initial_weight = db.Column(db.Float, default=0)
    mistakes_performed = db.Column(db.Text, nullable=True)
    video_link = db.Column(db.String(255), nullable=True)
    strength_level = db.Column(db.Integer, default=50)
    weight_change = db.Column(db.Float, default=0)
    body_fat_percentage_change = db.Column(db.Float, default=0)
    training_duration = db.Column(db.Integer, default=1)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi():
    try:
        # Get user input from form
        height = float(request.form['height'])
        weight = float(request.form['weight'])  # Get current weight from form
        age = int(request.form['age'])
        fitness_goal = request.form['fitness_goal'].lower()
        muscle_group = request.form['muscle_group'].lower()
        specific_muscle = request.form['specific_muscle'].lower()

        # Calculate BMI
        bmi = weight / (height * height)

        # Fetch the user's workout data from the database
        workout_data = WorkoutData.query.all()

        # Prepare the data for training the Random Forest model
        df = pd.DataFrame([(d.age, d.bmi, d.muscle_group, d.specific_muscle, d.fitness_goal, d.workout_plan,
                            d.diet_recommendation, d.daily_calorie_intake)
                           for d in workout_data],
                          columns=['age', 'bmi', 'muscle_group', 'specific_muscle', 'fitness_goal',
                                   'workout_plan', 'diet_recommendation', 'daily_calorie_intake'])

        # Encode categorical columns
        le_goal = LabelEncoder()
        le_muscle = LabelEncoder()

        df['muscle_group'] = le_muscle.fit_transform(df['muscle_group'])
        df['specific_muscle'] = df['specific_muscle'].astype('category').cat.codes
        df['fitness_goal'] = le_goal.fit_transform(df['fitness_goal'])
        df['workout_plan'] = df['workout_plan'].astype('category')

        # Features and target for workout plan prediction
        X = df[['age', 'bmi', 'muscle_group', 'specific_muscle', 'fitness_goal']]
        y = df['workout_plan'].cat.codes

        # Train the Random Forest Classifier model for workout plans
        rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
        rf_model.fit(X, y)

        # Encode the user input for prediction
        fitness_goal_encoded = le_goal.transform([fitness_goal])[0]
        muscle_group_encoded = le_muscle.transform([muscle_group])[0]
        specific_muscle_encoded = pd.Series([specific_muscle]).astype('category').cat.codes[0]

        # Input data for prediction
        input_data = np.array([[age, bmi, muscle_group_encoded, specific_muscle_encoded, fitness_goal_encoded]])

        # Predict workout plan
        predicted_plan_encoded = rf_model.predict(input_data)[0]
        predicted_plan = df['workout_plan'].cat.categories[predicted_plan_encoded]

        # Fetch specific exercises and images based on predicted plan
        recommended_exercises = WorkoutData.query.filter_by(workout_plan=predicted_plan,
                                                            specific_muscle=specific_muscle).first()

        if recommended_exercises:
            exercises = recommended_exercises.exercises
            image_1 = recommended_exercises.exercise_image_1
            image_2 = recommended_exercises.exercise_image_2
            image_3 = recommended_exercises.exercise_image_3
            diet_recommendation = recommended_exercises.diet_recommendation
            daily_calorie_intake = recommended_exercises.daily_calorie_intake
            diet_details = recommended_exercises.diet_details

            # Fetch mistakes and video link for the exercises
            mistakes = recommended_exercises.mistakes_performed
            video_link = recommended_exercises.video_link
        else:
            exercises = "No exercises found."
            image_1 = image_2 = image_3 = "images/default.jpg"
            diet_recommendation = "No diet recommendation found."
            daily_calorie_intake = "No calorie intake data available."
            diet_details = "No detailed diet plan available."
            mistakes = "No workout mistakes available."
            video_link = "#"

        # Check if initial_weight is 0 and set it to the current weight
        if recommended_exercises and recommended_exercises.initial_weight == 0:
            recommended_exercises.initial_weight = weight
            db.session.commit()  # Save the updated initial weight to the database

        # Render the results.html template, passing all the data
        return render_template('results.html',
                               bmi=bmi,
                               plan=predicted_plan,
                               exercises=exercises,
                               image_1=image_1,
                               image_2=image_2,
                               image_3=image_3,
                               diet=diet_recommendation,
                               calories=daily_calorie_intake,
                               diet_details=diet_details,
                               mistakes=mistakes,
                               video_link=video_link)

    except ValueError:
        flash('Please enter valid numbers for height, weight, and age.', 'error')
        return redirect(url_for('home'))


@app.route('/update_progress', methods=['POST'])
def update_progress():
    try:
        # Get progress tracking data from form
        current_weight = float(request.form['current_weight'])
        strength_lifted = float(request.form['strength_lifted'])
        body_fat_percentage = request.form.get('body_fat_percentage', None)

        if body_fat_percentage:
            body_fat_percentage = float(body_fat_percentage)

        # Fetch the user's data from the database
        user_data = WorkoutData.query.first()

        # Calculate weight change based on initial_weight (already stored)
        initial_weight = user_data.initial_weight
        weight_change = current_weight - initial_weight

        # Calculate strength level increase
        initial_strength = 50  # Placeholder for initial strength
        strength_increase = (strength_lifted - initial_strength) / initial_strength * 100

        # Optional: Calculate body fat percentage change
        if body_fat_percentage:
            initial_body_fat = 20  # Placeholder, adjust as needed
            body_fat_change = body_fat_percentage - initial_body_fat
        else:
            body_fat_change = None

        # Update the user's progress in the database
        user_data.weight_change = weight_change
        user_data.strength_level = strength_increase
        user_data.training_duration += 1  # Increment training duration
        if body_fat_change is not None:
            user_data.body_fat_percentage_change = body_fat_change

        db.session.commit()  # Save the updated values

        # Fetch mistakes and video link again
        mistakes = user_data.mistakes_performed
        video_link = user_data.video_link

        flash('Progress updated successfully!', 'success')

        # Render the results page again with updated progress data and workout mistakes
        return render_template('results.html',
                               bmi=user_data.bmi,
                               plan=user_data.workout_plan,
                               exercises=user_data.exercises,
                               image_1=user_data.exercise_image_1,
                               image_2=user_data.exercise_image_2,
                               image_3=user_data.exercise_image_3,
                               diet=user_data.diet_recommendation,
                               calories=user_data.daily_calorie_intake,
                               diet_details=user_data.diet_details,
                               weight_change=weight_change,
                               strength_level=strength_increase,
                               body_fat_percentage_change=body_fat_change,
                               training_duration=user_data.training_duration,
                               mistakes=mistakes,
                               video_link=video_link)

    except Exception as e:
        print(f"Error: {e}")
        flash('There was an error updating your progress. Please try again.', 'danger')
        return redirect(url_for('home'))


# PDF Generation Route
config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    diet = request.form.get('diet', 'Balanced Diet')  # Default to Balanced Diet
    calories = 2200
    breakfast = "Oats with fresh fruits and almonds."
    lunch = "Grilled chicken with quinoa and mixed vegetables."
    dinner = "Salmon with steamed broccoli and sweet potato."
    snacks = "Greek yogurt, a handful of nuts."

    # Determine the image based on the diet
    if diet == "Low Carb Diet":
        diet_image = "images/low_carb.png"
        breakfast = "Scrambled eggs with avocado."
        lunch = "Grilled salmon with a side of spinach."
        dinner = "Zucchini noodles with a tomato sauce."
    elif diet == "High Protein Diet":
        diet_image = "images/high_protein.png"
        breakfast = "Egg white omelette with spinach."
        lunch = "Grilled chicken breast with quinoa and vegetables."
        dinner = "Turkey meatballs with brown rice."
    else:
        diet_image = "images/balanced_diet.png"

    rendered = render_template('diet_pdf.html',
                               diet=diet,
                               calories=calories,
                               breakfast=breakfast,
                               lunch=lunch,
                               dinner=dinner,
                               snacks=snacks,
                               diet_image=diet_image)

    pdf = pdfkit.from_string(rendered, False, configuration=config)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=diet_plan.pdf'
    return response

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(debug=True)
