from flask import Flask, render_template, jsonify, request, json
from flask_cors import CORS
import pymysql
from datetime import datetime
import os


# Load environment variables

app = Flask(__name__)
CORS(app)


# MySQL database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="Money@2035",
        database="leads",
        cursorclass=pymysql.cursors.DictCursor
    )
    

@app.route('/')
def index():
    return render_template('index.html')

# Dynamic routes (Optional, for extension later)
@app.route("/Executive")
def Executive():
    return render_template("Executive.html")

@app.route("/Professional")
def Professional():
    return render_template("Professional.html")

@app.route("/student")
def student():
    return render_template("student.html")

@app.route("/Technical_resume")
def Technical_resume():
    return render_template("Technical_resume.html")

@app.route('/submit-profile', methods=['POST'])
def submit_profile():
    try:
        data = request.get_json()

        # Basic input validation
        required_fields = ['fullName', 'email', 'phone', 'linkedin', 'executiveSummary', 'competencies']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400
        
        full_name = data['fullName']
        email = data['email']
        phone = data['phone']
        linkedin = data['linkedin']
        executive_summary = data['executiveSummary']
        competencies = data['competencies']
        experience = json.dumps(data.get('experience', []))
        education = json.dumps(data.get('education', []))

        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check for duplicate email
            cursor.execute("SELECT id FROM executive_profiles WHERE email = %s", (email,))
            existing = cursor.fetchone()
            if existing:
                return jsonify({'status': 'error', 'message': 'Profile with this email already exists.'}), 409

            sql = """
                INSERT INTO executive_profiles (
                    full_name, email, phone, linkedin,
                    executive_summary, competencies,
                    experience, education, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (
                full_name, email, phone, linkedin,
                executive_summary, competencies,
                experience, education
            ))
            connection.commit()
        
        return jsonify({'status': 'success'}), 201

    except Exception as e:
        # Log error internally
        app.logger.error(f"Error inserting profile: {e}")
        return jsonify({'status': 'error', 'message': 'Server error. Please try again later.'}), 500

    finally:
        if 'connection' in locals() and connection:
            connection.close()


@app.route('/submit-resume', methods=['POST'])
def submit_resume():
    try:
        data = request.get_json()

        # Basic input validation
        required_fields = [
            'fullName', 'email', 'phone', 'linkedin',
            'summary', 'education', 'skills', 'certifications'
        ]
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400

        # Extract and sanitize
        full_name = data['fullName']
        email = data['email']
        phone = data['phone']
        linkedin = data['linkedin']
        portfolio = data.get('portfolio', '')  # Optional field
        summary = data['summary']
        
        # Safely convert all JSON-like fields to JSON strings
        work_experience = json.dumps(data.get('workExperience', []))
        education = json.dumps(data['education'])
        skills = json.dumps(data['skills'])
        certifications = json.dumps(data['certifications'])

        # Database connection
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # Check for duplicate
            cursor.execute("SELECT id FROM resumes WHERE email = %s", (email,))
            existing = cursor.fetchone()
            if existing:
                return jsonify({'status': 'error', 'message': 'A resume with this email already exists.'}), 409

            # Insert data
            sql = """
                INSERT INTO resumes (
                    full_name, email, phone, linkedin, portfolio,
                    summary, work_experience, education, skills, certifications, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (
                full_name, email, phone, linkedin, portfolio,
                summary, work_experience, education, skills, certifications
            ))
            connection.commit()

        return jsonify({'status': 'success'}), 201

    except Exception as e:
        app.logger.error(f"Error inserting resume: {e}")
        return jsonify({'status': 'error', 'message': 'Server error. Please try again later.'}), 500

    finally:
        if 'connection' in locals() and connection:
            connection.close()
            
@app.route('/submit-tech', methods=['POST'])
def submit_tech():
    try:
        data = request.get_json()

        required_fields = ['fullName', 'email', 'phone', 'linkedin']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 400

        full_name = data['fullName']
        email = data['email']
        phone = data['phone']
        linkedin = data['linkedin']
        portfolio = data.get('portfolio', '')
        summary = data.get('summary', '')
        prog_langs = data.get('progLangs', '')
        frameworks = data.get('frameworks', '')
        tools = data.get('tools', '')

        experience = json.dumps(data.get('experience', []))
        education = json.dumps(data.get('education', []))
        projects = json.dumps(data.get('projects', []))
        certifications = json.dumps(data.get('certifications', []))

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM tech_profiles WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Profile already exists'}), 409

            cursor.execute("""
                INSERT INTO tech_profiles (
                    full_name, email, phone, linkedin, portfolio,
                    summary, prog_langs, frameworks, tools,
                    experience, education, projects, certifications, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                full_name, email, phone, linkedin, portfolio,
                summary, prog_langs, frameworks, tools,
                experience, education, projects, certifications, datetime.now()
            ))
            connection.commit()

        return jsonify({'status': 'success'}), 201

    except Exception as e:
        app.logger.error(f"Submit profile error: {e}")
        return jsonify({'status': 'error', 'message': 'Server error'}), 500
    finally:
        if 'connection' in locals():
            connection.close()
            
@app.route('/submit-student-profile', methods=['POST'])
def submit_student_profile():
    connection = None
    try:
        data = request.get_json()

        # Basic input validation
        required_fields = ['fullName', 'email', 'phone', 'linkedin', 'objective']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'status': 'error', 'message': f'Missing required field: {field}'}), 422

        full_name = data['fullName']
        email = data['email']
        phone = data['phone']
        linkedin = data['linkedin']
        objective = data['objective']
        education = json.dumps(data.get('education', []))
        experience = json.dumps(data.get('experience', []))
        technical_skills = json.dumps(data.get('technicalSkills', []))
        soft_skills = json.dumps(data.get('softSkills', []))
        certifications = json.dumps(data.get('certifications', []))

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM student_profiles WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'status': 'error', 'message': 'Profile with this email already exists.'}), 409

            sql = """
                INSERT INTO student_profiles (
                    full_name, email, phone, linkedin, objective,
                    education, experience, technical_skills,
                    soft_skills, certifications, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            cursor.execute(sql, (
                full_name, email, phone, linkedin, objective,
                education, experience, technical_skills,
                soft_skills, certifications
            ))
            connection.commit()

        return jsonify({'status': 'success'}), 201

    except Exception as e:
        app.logger.error(f"Error inserting student profile: {e}")
        return jsonify({'status': 'error', 'message': 'Server error. Please try again later.'}), 500

    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    app.run(debug=True)
