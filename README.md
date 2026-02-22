# Student Performance Dashboard 

An interactive, end-to-end data analytics and visualization pipeline representing a Student Information System (SIS). This project encompasses mock data generation, data cleansing, exploratory data analysis (EDA), and a fully interactive Streamlit dashboard featuring predictive "At-Risk" student insights.

## Project Architecture

The project is structured into four distinct phases:

1. **Phase 1: Data Strategy and Preparation (`generate_data.py`, `data_pipeline.py`)**
   - Generates synthetic, highly realistic datasets using Python's `Faker` library (configured for Indian locales).
   - Simulates 500 students distributed across 5 departments, each enrolled in specific departmental courses.
   - Cleanses the data by handling duplicates, missing values, and programmatically extrapolating "Dropouts" vs "Missed Exams" based on attendance correlations.

2. **Phase 2: Exploratory Data Analysis (`eda_analysis.py`)**
   - Computes statistical distributions (Mean, Median, Standard Deviation) grouped by department cohorts.
   - Maps the Pearson correlation between `Hours Spent on LMS` and `Final Grades`.
   - Generates interactive Plotly HTML reports (Distribution Histograms, Correlation Scatter Plots, Outlier Box Plots).

3. **Phase 3: Interactive Visualization (`app.py`)**
   - A highly-polished, responsive Streamlit dashboard modeled after modern, premium SIS layouts (like openSIS).
   - Features advanced visual marks including custom CSS metric cards, Heatmaps (Attendance vs Grade), and a Student Journey Sankey Diagram.

4. **Phase 4: Predictive Insights (`app.py`)**
   - Implements an "Early Warning System" to flag students who are "At-Risk".
   - Flags map to strict logic: A drop of >10 points from midterms, <75% attendance, or a failing grade (<65%).
   - Includes a "Student Profile Details" drill-down to search any student and view a breakdown of their performance on a per-course basis.

---

## Installation & Setup

### Prerequisites
- Python 3.9+
- Git

### Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/BilvaDheeraj/SIS_Dashboard.git
   cd SIS_Dashboard
   ```

2. **Set up a Virtual Environment:**
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\Activate.ps1
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install pandas numpy faker streamlit plotly scipy
   ```

---

## Running the Pipeline

To populate the data and run the dashboard, execute the sequence of scripts:

1. **Generate the Raw Mock Data:**
   ```bash
   python generate_data.py
   ```
   *Creates `student_demographics.csv`, `course_enrollment.csv`, and `grade_history.csv` inside `data/raw/`.*

2. **Cleanse Data and Build the Unified Dataset:**
   ```bash
   python data_pipeline.py
   ```
   *Outputs the final, cleaned merge to `data/processed/cleaned_master_dataset.csv`.*

3. **(Optional) Run Exploratory Data Analysis (EDA):**
   ```bash
   python eda_analysis.py
   ```
   *Outputs `.html` graphs to `data/visualizations/` and a text report to `data/reports/`.*

4. **Launch the Dashboard:**
   ```bash
   streamlit run app.py
   ```
   *The interactive web interface will open at `http://localhost:8501`.*

---

## License

This project was built as an educational case study for data analysis and visualization pipelines.
