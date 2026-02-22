import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="openSIS Student Performance Dashboard", layout="wide", initial_sidebar_state="expanded")

# --- Custom Styling for Premium openSIS Feel ---
st.markdown("""
    <style>
    .main {
        background-color: #f4f7f6;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 5px solid #0056b3;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #0056b3;
    }
    .metric-label {
        color: #495057;
        font-size: 1rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .at-risk-badge {
        background-color: #ffeaea;
        color: #d9534f;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        return pd.read_csv('data/processed/cleaned_master_dataset.csv')
    except Exception:
        return pd.DataFrame()

df = load_data()

st.title("🎓 Student Performance & Analytics Dashboard")
st.markdown("*Modeled after openSIS - Empowering Educational Insights*")

if df.empty:
    st.error("Data not found! Please run `data_pipeline.py` first.")
    st.stop()

# --- Predictive Analytics Logic (Task 4.1) ---
# Early warning system logic: Flag students whose final grade dropped significantly purely based on midterm.
# Stricter At-Risk Logic to flag earlier warning signs.
df['Grade_Drop'] = df['Midterm_Grade'] - df['Final_Grade']
df['At_Risk'] = (df['Grade_Drop'] > 10) | (df['Attendance_Rate'] < 75) | (df['Final_Grade'] < 65)

# SIDEBAR FILTERS
st.sidebar.header("🎯 Filter Options")
selected_dept = st.sidebar.selectbox("Department", ["All"] + list(df['Department'].unique()))
selected_semester = st.sidebar.selectbox("Semester", ["All"] + list(df['Semester'].unique()))

filtered_df = df.copy()
if selected_dept != "All":
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_semester != "All":
    filtered_df = filtered_df[filtered_df['Semester'] == selected_semester]

# TOP METRICS
total_students = filtered_df['StudentID'].nunique()
# Average Final Grade across all records (course-level average)
avg_grade = filtered_df['Final_Grade'].mean()

# Calculate Unique At-Risk Students
# A student is 'at-risk' if they are flagged in ANY of their courses
at_risk_students_df = filtered_df[filtered_df['At_Risk'] == True]
at_risk_count = at_risk_students_df['StudentID'].nunique()

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Students</div><div class='metric-value'>{total_students}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Average Final Grade</div><div class='metric-value'>{avg_grade:.1f}%</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>At-Risk Students</div><div style='color:#ef4444;' class='metric-value'>{at_risk_count}</div></div>", unsafe_allow_html=True)

st.divider()

# PHASE 3: ADVANCED VISUALS
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Performance Heatmap (Task 3.2)")
    # Heatmap of Attendance vs Final Grade binned
    fig_heat = px.density_heatmap(filtered_df, x="Attendance_Rate", y="Final_Grade", 
                                  nbinsx=12, nbinsy=12, color_continuous_scale="Tealrose",
                                  labels={"Attendance_Rate":"Attendance (%)", "Final_Grade":"Final Grade (%)"})
    fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_heat, use_container_width=True)

with c2:
    st.subheader("🔄 Student Journey Flow (Task 3.2)")
    # Sankey Diagram: Department -> Semester -> Letter Grade
    nodes_dept = list(filtered_df['Department'].unique())
    nodes_sem = list(filtered_df['Semester'].unique())
    nodes_grade = list(filtered_df['Letter_Grade'].unique())
    # Sort grades for better visual order A -> F
    nodes_grade.sort()
    
    all_nodes = nodes_dept + nodes_sem + nodes_grade
    node_indices = {node: i for i, node in enumerate(all_nodes)}
    
    source = []
    target = []
    value = []
    
    # Links: Department -> Semester
    dept_sem = filtered_df.groupby(['Department', 'Semester']).size().reset_index(name='count')
    for _, row in dept_sem.iterrows():
        source.append(node_indices[row['Department']])
        target.append(node_indices[row['Semester']])
        value.append(row['count'])
        
    # Links: Semester -> Letter Grade
    sem_grade = filtered_df.groupby(['Semester', 'Letter_Grade']).size().reset_index(name='count')
    for _, row in sem_grade.iterrows():
        source.append(node_indices[row['Semester']])
        target.append(node_indices[row['Letter_Grade']])
        value.append(row['count'])
        
    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 15,
          thickness = 20,
          line = dict(color = "black", width = 0.5),
          label = all_nodes,
          color = "#0056b3"
        ),
        link = dict(
          source = source,
          target = target,
          value = value,
          color = "rgba(0, 86, 179, 0.2)"
      ))])
      
    fig_sankey.update_layout(margin=dict(t=30, l=0, r=0, b=0), plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_sankey, use_container_width=True)

st.divider()

c3, c4 = st.columns(2)

with c3:
    st.subheader("📈 LMS Engagement vs Performance")
    fig_scatter = px.scatter(filtered_df, x="LMS_Hours", y="Final_Grade", color="At_Risk",
                             color_discrete_map={True: '#d9534f', False: '#5cb85c'},
                             hover_name="StudentID", hover_data=["Department"],
                             trendline="ols", title="Impact of LMS Engagement on Final Grades",
                             labels={"LMS_Hours": "Hours Spent on LMS", "Final_Grade": "Final Grade (%)"})
    fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter, use_container_width=True)

with c4:
    st.subheader("📦 Grade Outliers (EDA)")
    fig_box = px.box(filtered_df, x="Department", y="Final_Grade", color="Department",
                     title="Grade Distribution and Outliers by Department", points="all",
                     hover_data=["StudentID", "Name"])
    fig_box.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

st.divider()

# PHASE 3: INTERACTIVE DRILL-DOWN (Task 3.1)
st.subheader("🔍 Student Profile Details (Course-Level Analysis)")
st.markdown("Search for any student below to view their detailed performance and attendance history across all enrolled courses.")

# Allow searching ANY student, not just At-Risk
student_list = filtered_df['Name'].unique()
student_list.sort()

if len(student_list) > 0:
    selected_student = st.selectbox("Search Student Name:", student_list)
    
    # Get all records for the selected student
    student_records = filtered_df[filtered_df['Name'] == selected_student]
    student_info = student_records.iloc[0]
    
    st.markdown(f"#### Profile: **{student_info['Name']}** ({student_info['StudentID']}) | Department: **{student_info['Department']}**")
    
    # Calculate aggregate stats for the student
    avg_attendance = student_records['Attendance_Rate'].mean()
    avg_final = student_records['Final_Grade'].mean()
    total_lms = student_records['LMS_Hours'].sum()
    
    sc1, sc2, sc3 = st.columns(3)
    sc1.metric("Avg. Attendance", f"{avg_attendance:.1f}%")
    sc2.metric("Avg. Final Grade", f"{avg_final:.1f}")
    sc3.metric("Total LMS Hours", f"{total_lms:.1f}")
    
    st.markdown("##### 📚 Course Enrollment & Performance")
    
    # Formatting the table for display
    display_cols = ['CourseID', 'CourseName', 'Semester', 'Attendance_Rate', 'Midterm_Grade', 'Final_Grade', 'Letter_Grade', 'LMS_Hours', 'At_Risk']
    display_df = student_records[display_cols].copy()
    
    # Format specific columns for the UI
    display_df['Attendance_Rate'] = display_df['Attendance_Rate'].apply(lambda x: f"{x}%")
    display_df['Midterm_Grade'] = display_df['Midterm_Grade'].apply(lambda x: f"{x:.1f}")
    
    # Handle Dropouts in the display table
    def format_final_grade(row):
        if row['Final_Grade'] == 0.0 and float(row['Attendance_Rate'].replace('%', '')) < 35.0:
            return "0.0 (Dropout)"
        return f"{row['Final_Grade']:.1f}"
    
    display_df['Final_Grade'] = display_df.apply(format_final_grade, axis=1)
    
    # Rename for cleaner UI
    display_df.rename(columns={
        'CourseID': 'ID',
        'CourseName': 'Course',
        'Attendance_Rate': 'Attendance',
        'Midterm_Grade': 'Midterm',
        'Final_Grade': 'Final',
        'Letter_Grade': 'Grade',
        'LMS_Hours': 'LMS Hrs',
        'At_Risk': 'Warning'
    }, inplace=True)
    
    # Use Streamlit's dataframe for an interactive table
    st.dataframe(display_df, use_container_width=True, hide_index=True)
    
    # Show warning if any course is At-Risk
    if student_records['At_Risk'].any():
        st.error("⚠️ This student is flagged as 'At-Risk' in one or more courses due to significant grade drops or poor attendance. Early intervention recommended.")
    else:
        st.success("✅ This student is currently on track across all enrolled courses.")

else:
    st.info("No students found for the current filters.")

