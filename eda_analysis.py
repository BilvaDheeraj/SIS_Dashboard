import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
import os

def run_eda():
    os.makedirs('data/reports', exist_ok=True)
    os.makedirs('data/visualizations', exist_ok=True)
    
    try:
        df = pd.read_csv('data/processed/cleaned_master_dataset.csv')
    except FileNotFoundError:
        print("Cleaned data not found. Please run data_pipeline.py first.")
        return
        
    print("--- Phase 2: Exploratory Data Analysis (EDA) ---")
    
    # Task 2.1: Descriptive Statistics
    print("Calculating descriptive statistics...")
    
    # Grades across different cohorts (Departments)
    cohort_stats = df.groupby('Department', dropna=False)['Final_Grade'].agg(['mean', 'median', 'std', 'count']).reset_index()
    
    # Save text report
    with open('data/reports/eda_summary_report.txt', 'w') as f:
        f.write("EDA Summary Report\n")
        f.write("==================\n\n")
        f.write(f"Total Student Enrollments Analyzed: {len(df)}\n\n")
        f.write("Grade Statistics by Department:\n")
        f.write(cohort_stats.to_string(index=False) + "\n\n")
        
        # Outlier detection (using 2 standard deviations)
        mean_grade = df['Final_Grade'].mean()
        std_grade = df['Final_Grade'].std()
        outliers = df[(df['Final_Grade'] > mean_grade + 2*std_grade) | (df['Final_Grade'] < mean_grade - 2*std_grade)]
        f.write(f"Identified {len(outliers)} grade outliers (>2 std dev from mean).\n")
    print("Descriptive statistics saved to data/reports/eda_summary_report.txt")
    
    # Distribution histograms
    fig_hist = px.histogram(df, x="Final_Grade", color="Department", 
                            title="Distribution of Final Grades by Department",
                            nbins=20, marginal="box")
    fig_hist.write_html("data/visualizations/grade_distribution.html")
    print("Grade distribution histogram saved.")
    
    # Box Plot for Outliers
    fig_box = px.box(df, x="Department", y="Final_Grade", color="Department",
                     title="Grade Outliers by Department", points="all",
                     hover_data=["StudentID", "Name"])
    fig_box.write_html("data/visualizations/grade_outliers_box.html")
    print("Grade outliers box plot saved.")
    
    # Distribution Analysis (Pie Charts): Illustrate grade spread across student populations
    grade_counts = df['Letter_Grade'].value_counts().reset_index()
    grade_counts.columns = ['Letter_Grade', 'Count']
    grade_counts['Letter_Grade'] = pd.Categorical(grade_counts['Letter_Grade'], categories=['A', 'B', 'C', 'D', 'F'], ordered=True)
    grade_counts = grade_counts.sort_values('Letter_Grade')
    
    fig_pie = px.pie(grade_counts, names="Letter_Grade", values="Count",
                     title="Overall Grade Spread (Letter Grades)",
                     color="Letter_Grade", color_discrete_map={'A':'#00cc96', 'B':'#636efa', 'C':'#fecb52', 'D':'#ffa15a', 'F':'#ef553b'})
    fig_pie.write_html("data/visualizations/grade_spread_pie.html")
    print("Grade spread pie chart saved.")

    # Trend Analysis (Line Charts): Track semester-wise performance progressions
    def parse_semester(s):
        parts = str(s).split()
        if len(parts) == 2:
            season, year = parts
            return int(year) * 10 + (1 if season == 'Spring' else (2 if season == 'Summer' else 3))
        return 0
        
    trend_data_dept = df.groupby(['Semester', 'Department'])['Final_Grade'].mean().reset_index()
    trend_data_dept['SortKey'] = trend_data_dept['Semester'].apply(parse_semester)
    trend_data_dept = trend_data_dept.sort_values('SortKey')
    
    fig_trend = px.line(trend_data_dept, x="Semester", y="Final_Grade", color="Department",
                        title="Semester-wise Performance Progression by Department", markers=True)
    fig_trend.write_html("data/visualizations/semester_trend_analysis.html")
    print("Semester-wise trend analysis line chart saved.")

    # Comparison Analysis (Bar Charts): Facilitate departmental and cohort comparisons
    df['AdmissionYear_Str'] = df['AdmissionYear'].astype(str)
    compare_data = df.groupby(['Department', 'AdmissionYear_Str'])['Final_Grade'].mean().reset_index()
    compare_data = compare_data.sort_values('AdmissionYear_Str')
    fig_bar = px.bar(compare_data, x="Department", y="Final_Grade", color="AdmissionYear_Str", barmode="group",
                     title="Average Final Grade by Department and Admission Year (Cohort)")
    fig_bar.write_html("data/visualizations/department_cohort_comparison.html")
    print("Departmental and cohort comparison bar chart saved.")

    # Task 2.2: Correlation and Comparative Analysis
    print("\nRunning correlation tests...")
    
    # Correlation between quantitative variables
    vars_to_correlate = ['LMS_Hours', 'Attendance_Rate', 'Midterm_Grade', 'Final_Grade']
    corr_matrix = df[vars_to_correlate].corr(method='pearson')
    
    with open('data/reports/eda_summary_report.txt', 'a') as f:
        f.write("\nCorrelation Matrix (Pearson's r):\n")
        f.write(corr_matrix.to_string() + "\n\n")
        
        r_lms_grade = corr_matrix.loc['LMS_Hours', 'Final_Grade']
        f.write(f"Correlation between Hours Spent on LMS and Final Grade: {r_lms_grade:.3f}\n")
        
    # Scatter Plot Analysis
    fig_scatter = px.scatter(df, x="LMS_Hours", y="Final_Grade", color="Department", 
                             trendline="ols", hover_data=["StudentID", "Letter_Grade"],
                             title="Hours Spent on LMS vs Final Grade")
    fig_scatter.write_html("data/visualizations/lms_vs_grades_scatter.html")
    print("Correlation scatter plot saved.")

    # Pattern/Correlation Analysis (Heatmaps): Map attendance levels against academic outcomes
    fig_heatmap = px.imshow(corr_matrix, text_auto=".2f", aspect="auto",
                            title="Correlation Heatmap of Academic Metrics",
                            color_continuous_scale="RdBu_r", zmin=-1, zmax=1)
    fig_heatmap.write_html("data/visualizations/correlation_heatmap.html")
    print("Correlation heatmap saved.")
    
    print("\nEDA COMPLETE. Check data/reports/ and data/visualizations/")

if __name__ == "__main__":
    run_eda()
