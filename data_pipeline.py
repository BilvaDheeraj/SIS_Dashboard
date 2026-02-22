import pandas as pd
import numpy as np
import os

def run_pipeline():
    print("Loading raw data...")
    # Load data
    try:
        students = pd.read_csv('data/raw/student_demographics.csv')
        enrollments = pd.read_csv('data/raw/course_enrollment.csv')
        grades = pd.read_csv('data/raw/grade_history.csv')
    except FileNotFoundError as e:
        print(f"Error: {e}. Please run generate_data.py first.")
        return
        
    # --- Task 1.1: Data Integration ---
    print("Joining datasets...")
    # Merge students and enrollments
    merged_df = pd.merge(enrollments, students, on='StudentID', how='left')
    # Merge with grades
    unified_raw = pd.merge(merged_df, grades, on=['StudentID', 'CourseID'], how='left')
    
    os.makedirs('data/processed', exist_ok=True)
    unified_raw.to_csv('data/raw/unified_raw_dataset.csv', index=False)
    print("Unified Raw Dataset saved (Task 1.1).")
    
    # --- Task 1.2: Data Cleaning and Validation ---
    print("Cleaning data...")
    cleaned_df = unified_raw.copy()
    
    # 1. Remove Duplicates
    initial_rows = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates()
    print(f" - Removed {initial_rows - len(cleaned_df)} duplicate rows.")
    
    # 2. Handle Missing Values
    # Age: Fill missing ages with the median age of the department
    cleaned_df['Age'] = cleaned_df.groupby('Department')['Age'].transform(lambda x: x.fillna(x.median()))
    
    # Final_Grade: 
    # If a student has very low attendance (<35) and missing final grade -> Assume Dropout (Assign 0 or 'W')
    dropouts = (cleaned_df['Attendance_Rate'] < 35) & (cleaned_df['Final_Grade'].isna())
    cleaned_df.loc[dropouts, 'Final_Grade'] = 0.0 # Assigning 0 for dropped out
    
    # If a student has high attendance but missing final grade -> Missed Exam (Calculate based on midterm)
    missed_exam = (cleaned_df['Attendance_Rate'] >= 35) & (cleaned_df['Final_Grade'].isna())
    # Assuming Midterm is out of 100 and Final is out of 100, we might extrapolate (or leave as NaN and drop if strict)
    # Let's drop the ones who missed exam, or impute with their midterm score
    cleaned_df.loc[missed_exam, 'Final_Grade'] = cleaned_df.loc[missed_exam, 'Midterm_Grade']
    
    print(f" - Handled missing Final Grades. Inferred {dropouts.sum()} dropouts and {missed_exam.sum()} missed exams.")
    
    # Check for any remaining nulls
    remaining_nulls = cleaned_df.isnull().sum()
    if remaining_nulls.sum() > 0:
        print(" - Note: There are still some null values:")
        print(remaining_nulls[remaining_nulls > 0])
        
    # 3. Normalize grading scales
    # Our data is already 0-100, but let's ensure it's capped at 100 and floor at 0
    cleaned_df['Final_Grade'] = cleaned_df['Final_Grade'].clip(0, 100)
    cleaned_df['Midterm_Grade'] = cleaned_df['Midterm_Grade'].clip(0, 100)
    
    # Calculate Letter Grade for dashboarding purposes later
    def get_letter_grade(score):
        if pd.isna(score): return 'N/A'
        if score >= 90: return 'A'
        if score >= 80: return 'B'
        if score >= 70: return 'C'
        if score >= 60: return 'D'
        return 'F'
        
    cleaned_df['Letter_Grade'] = cleaned_df['Final_Grade'].apply(get_letter_grade)
    
    cleaned_df.to_csv('data/processed/cleaned_master_dataset.csv', index=False)
    print("Cleaned Master Dataset saved (Task 1.2).")
    
if __name__ == "__main__":
    run_pipeline()
