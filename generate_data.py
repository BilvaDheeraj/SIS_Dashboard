import pandas as pd
import numpy as np
import random
from faker import Faker
import os

fake = Faker('en_IN')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

NUM_STUDENTS = 500
NUM_COURSES = 20

def generate_data():
    os.makedirs('data/raw', exist_ok=True)
    
    # 1. Student Demographics
    departments = ['Computer Science', 'Business', 'Engineering', 'Arts', 'Science']
    students = []
    for i in range(1, NUM_STUDENTS + 1):
        students.append({
            'StudentID': f'STU{i:04d}',
            'Name': fake.name(),
            'Age': random.randint(18, 26),
            'Gender': random.choice(['M', 'F', 'Other']),
            'Department': random.choice(departments),
            'AdmissionYear': random.randint(2019, 2024)
        })
    df_students = pd.DataFrame(students)
    
    # Inject some missing values for data cleaning phase (Task 1.2) - Missing Ages
    missing_age_idx = df_students.sample(frac=0.05).index
    df_students.loc[missing_age_idx, 'Age'] = np.nan
    df_students.to_csv('data/raw/student_demographics.csv', index=False)
    
    # 2. Course Enrollment & 3. Grade History
    dept_courses = {
        'Engineering': ['Engineering Mathematics', 'Thermodynamics', 'Digital Electronics', 'Control Systems'],
        'Computer Science': ['Data Structures and Algorithms', 'Database Management Systems', 'Operating Systems', 'Machine Learning'],
        'Science': ['Physics – Mechanics', 'Organic Chemistry', 'Cell Biology', 'Environmental Science'],
        'Arts': ['History of Modern World', 'Political Theory', 'Sociology of Culture', 'Philosophy of Ethics'],
        'Business': ['Principles of Management', 'Financial Accounting', 'Marketing Management', 'Business Analytics']
    }
    
    # Flatten course list to assign CourseIDs
    all_course_names = []
    for courses in dept_courses.values():
        all_course_names.extend(courses)
        
    course_dict = {f'CRS{i:03d}': name for i, name in enumerate(all_course_names, 1)}
    # Reverse lookup for assigning courses by name
    name_to_id = {v: k for k, v in course_dict.items()}
    
    enrollments = []
    grades = []
    
    for student in students:
        # Each student takes 2 to 3 courses from their specific department
        available_courses = dept_courses[student['Department']]
        num_courses_taken = random.randint(2, 3)
        enrolled_course_names = random.sample(available_courses, num_courses_taken)
        
        for course_name in enrolled_course_names:
            course_id = name_to_id[course_name]
            
            enrollments.append({
                'EnrollmentID': fake.uuid4(),
                'StudentID': student['StudentID'],
                'CourseID': course_id,
                'CourseName': course_name,
                'Semester': random.choice(['Fall 2023', 'Spring 2024']),
            })
            
            # Generating realistic correlated data for Phase 2 EDA:
            # Hours spent on LMS correlates with Final Grade
            lms_hours = round(random.uniform(5.0, 150.0), 1)
            
            # Base grade is correlated with LMS hours
            base_score = 40 + (lms_hours / 150.0) * 55
            noise = random.uniform(-10, 10)
            final_grade = min(100, max(0, base_score + noise))
            
            # Attendance strongly correlated with Final Grade and LMS Hours
            attendance = min(100, max(20, (lms_hours / 150.0) * 100 + random.uniform(-5, 15)))
            
            grades.append({
                'StudentID': student['StudentID'],
                'CourseID': course_id,
                'LMS_Hours': lms_hours,
                'Attendance_Rate': round(attendance, 2),
                'Midterm_Grade': round(final_grade * 0.8 + random.uniform(-10, 12), 1), # Midterm roughly predicts final
                'Final_Grade': round(final_grade, 1)
            })
            
    df_enrollments = pd.DataFrame(enrollments)
    df_grades = pd.DataFrame(grades)
    
    # Inject dirty data for Phase 1 cleaning:
    # 1. Duplicates in enrollment
    df_enrollments = pd.concat([df_enrollments, df_enrollments.sample(n=15)], ignore_index=True)
    
    # 2. Missing values representing "dropped out" vs "missed exam"
    drop_out_indices = df_grades.sample(frac=0.03).index
    missed_exam_indices = df_grades.drop(drop_out_indices).sample(frac=0.02).index
    
    # Dropouts: Missing final grade and low attendance
    df_grades.loc[drop_out_indices, 'Final_Grade'] = np.nan
    df_grades.loc[drop_out_indices, 'Attendance_Rate'] = round(random.uniform(5, 30), 1) 
    
    # Missed exam: Missing final grade but high attendance
    df_grades.loc[missed_exam_indices, 'Final_Grade'] = np.nan
    df_grades.loc[missed_exam_indices, 'Attendance_Rate'] = round(random.uniform(85, 100), 1)
    
    df_enrollments.to_csv('data/raw/course_enrollment.csv', index=False)
    df_grades.to_csv('data/raw/grade_history.csv', index=False)
    
    print("MOCK DATA GENERATION COMPLETE.")
    print("Files saved to data/raw/:")
    print(" - student_demographics.csv")
    print(" - course_enrollment.csv")
    print(" - grade_history.csv")

if __name__ == "__main__":
    generate_data()
