import streamlit as st
import os
import csv
import json
import pandas as pd
from datetime import datetime
import time


# === Configuration ===
# DEFAULT_QUESTIONS is currently an empty dictionary. If you want to add default questions
# for the coding assignments, you can populate this dictionary.
# Example:
# DEFAULT_QUESTIONS = {
#     "Q1": "Write a Python function to calculate the factorial of a number.",
#     "Q2": "Create a program that checks if a given string is a palindrome."
# }

#st_autorefresh(interval=10000, key="student-refresh")
DEFAULT_QUESTIONS = {}

# File paths for various data storage
NUM_QUESTIONS_FILE = "questions.json"  # Stores coding assignment questions (currently not used for dynamic questions)
LIVE_CODE_FILE = "live_code.py"  # Stores code broadcasted by the professor
STUDENT_CODE_DIR = "submissionFINALS-BSCPE3-2hdl"  # Directory for student code submissions
SUBMISSION_STATUS_FILE = "allow_submissions.txt"  # Controls if student submissions are open/closed
SUBMISSION_STATUS_FOR_REVIEW = "allow_review.txt" #Control if the student can review the exam
SUBMISSION_STATUS_FOR_PROF_REVIEW = "allow_prof_review.txt" # to display the exam result of the student
SUBMISSION_FINAL_EXAM = "final_exam_submission.txt" #Control if the prog wanted to open/close the submissiong for exam
STUDENT_LIST_FILE = "students.csv"  # Stores student numbers and names
GRADES_FILE = "grades.csv"  # Stores final semester grades
FINAL_EXAM_QUESTIONS_FILE = "final_exam_questions.csv"  # Stores final exam questions
FINAL_EXAM_RESULTS_FILE = "FINALExAMBSCPE3-2hdl_results.csv"  # Stores final exam scores
FINAL_EXAM_STUDENT_ANSWERS_FILE = "FINALExamBSCPE3-2hdlstudent_answers.csv"  # Stores student's answers for final exam

# Professor password for accessing the admin section
PROFESSOR_PASSWORD = "securedpass123"  # IMPORTANT: In a real-world scenario, use a more secure method for passwords!

# === Setup Directories/Files ===
# Create the submissions directory if it doesn't exist
os.makedirs(STUDENT_CODE_DIR, exist_ok=True)

# Create the student list CSV file with headers if it doesn't exist
if not os.path.exists(STUDENT_LIST_FILE):
    with open(STUDENT_LIST_FILE, "w") as f:
        f.write("student_number,full_name\n")

# Create the submission status file and set it to 'true' (open) by default
if not os.path.exists(SUBMISSION_STATUS_FILE):
    with open(SUBMISSION_STATUS_FILE, "w") as f:
        f.write("true")

# Create the submission status file and set it to 'true' (open) by default
if not os.path.exists(SUBMISSION_STATUS_FOR_REVIEW):
    with open(SUBMISSION_STATUS_FOR_REVIEW, "w") as f:
        f.write("false")

if not os.path.exists(SUBMISSION_STATUS_FOR_PROF_REVIEW):
    with open(SUBMISSION_STATUS_FOR_PROF_REVIEW, "w") as f:
        f.write("false")

# Create the final exam results CSV file with headers if it doesn't exist
if not os.path.exists(FINAL_EXAM_RESULTS_FILE):
    with open(FINAL_EXAM_RESULTS_FILE, "w") as f:
        f.write("student_number,full_name,score\n")

# Create the final exam student answers CSV file with headers if it doesn't exist
if not os.path.exists(FINAL_EXAM_STUDENT_ANSWERS_FILE):
    with open(FINAL_EXAM_STUDENT_ANSWERS_FILE, "w") as f:
        f.write("student_number,full_name,question_index,question,student_answer,correct_answer\n")

# Create the final exam CSV file with headers if it doesn't exist
if not os.path.exists(SUBMISSION_FINAL_EXAM):
    with open(SUBMISSION_FINAL_EXAM, "w") as f:
        f.write("student_number,full_name\n")

# === App Config ===
# Set Streamlit page configuration for a wide layout and a custom page title
st.set_page_config(page_title="Second Semester Grade", layout="wide")
st.title("📝 SECOND SEMESTER GRADE")
st.subheader(" SUBJECTS: CPEN21A, CPEN115, CPEN100")


# === Helper Functions ===

def load_questions():
    """
    Loads coding assignment questions from NUM_QUESTIONS_FILE.
    If the file doesn't exist or is invalid, returns a copy of DEFAULT_QUESTIONS.
    """
    try:
        if os.path.exists(NUM_QUESTIONS_FILE):
            with open(NUM_QUESTIONS_FILE, "r") as f:
                return json.load(f)
        else:
            return DEFAULT_QUESTIONS.copy()
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_QUESTIONS.copy()


def validate_student(number, name):
    """
    Validates student credentials (student number and full name) against STUDENT_LIST_FILE.
    Performs case-insensitive comparison for the full name.
    """
    try:
        with open(STUDENT_LIST_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Strip whitespace and compare student number and case-insensitive full name
                if (row['student_number'].strip() == number.strip() and
                        row['full_name'].strip().lower() == name.strip().lower()):
                    return True
        return False
    except FileNotFoundError:
        # If the student list file doesn't exist, no students can be validated
        return False


def list_student_submissions(name):
    """
    Lists all Python code submissions for a given student.
    Submissions are identified by filename starting with a 'safe' version of the student's name.
    Returns a sorted list of filenames (most recent first).
    """
    # Create a safe filename by replacing spaces and periods
    safe_name = name.replace(" ", "_").replace(".", "")
    return sorted(
        [f for f in os.listdir(STUDENT_CODE_DIR) if f.startswith(safe_name) and f.endswith(".py")],
        reverse=True  # Sort in reverse to show most recent first
    )


def load_final_exam_questions():
    """
    Loads final exam questions from FINAL_EXAM_QUESTIONS_FILE into a Pandas DataFrame.
    Handles file not found or empty data errors.
    """
    try:
        df = pd.read_csv(FINAL_EXAM_QUESTIONS_FILE)
        return df
    except FileNotFoundError:
        st.error("Final exam questions file not found. Please upload it in the professor section.")
        return pd.DataFrame()  # Return empty DataFrame on error
    except pd.errors.EmptyDataError:
        st.warning("Final exam questions file is empty. Please upload questions.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading final exam questions: {e}")
        return pd.DataFrame()


def record_final_exam_score(student_number, full_name, score):
    """
    Records a student's final exam score in FINAL_EXAM_RESULTS_FILE.
    If the student has already taken the exam, their previous score is overwritten.
    """
    try:
        # Try to load existing results
        df = pd.read_csv(FINAL_EXAM_RESULTS_FILE)
    except pd.errors.EmptyDataError:
        # If the file is empty, create a new DataFrame with the correct columns
        df = pd.DataFrame(columns=['student_number', 'full_name', 'score'])
    except FileNotFoundError:
        # If the file doesn't exist, create a new DataFrame with the correct columns
        df = pd.DataFrame(columns=['student_number', 'full_name', 'score'])

    # Remove any existing entry for this student number to allow for score updates/overwrites
    df = df[df['student_number'].astype(str).str.strip() != student_number.strip()]

    # Create a new DataFrame for the current entry
    new_entry_df = pd.DataFrame([[student_number, full_name, score]], columns=['student_number', 'full_name', 'score'])

    # Concatenate the old DataFrame (without the old entry) and the new entry
    df = pd.concat([df, new_entry_df], ignore_index=True)

    # Save the updated DataFrame back to the CSV file
    df.to_csv(FINAL_EXAM_RESULTS_FILE, index=False)


def has_taken_final_exam(student_number):
    """
    Checks if a student has already taken the final exam by looking up their student number
    in the final exam results file.
    """
    try:
        df = pd.read_csv(FINAL_EXAM_RESULTS_FILE)
        # Check if the stripped student number exists in the 'student_number' column
        return student_number.strip() in df['student_number'].astype(str).str.strip().values
    except pd.errors.EmptyDataError:
        # If the file is empty, no one has taken the exam
        return False
    except FileNotFoundError:
        # If the file doesn't exist, no one has taken the exam
        return False

def record_final_exam_answers(student_number, answers_list):
    """
    Records a student's answers for the final exam in FINAL_EXAM_STUDENT_ANSWERS_FILE.
    answers_list is a list of dictionaries, each containing:
    {'question_index', 'question', 'student_answer', 'correct_answer'}
    """
    try:
        existing_df = pd.read_csv(FINAL_EXAM_STUDENT_ANSWERS_FILE)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        existing_df = pd.DataFrame(
            columns=['student_number','full_name', 'question_index', 'question', 'student_answer', 'correct_answer'])

    # Filter out existing entries for the current student to allow overwrite
    existing_df = existing_df[existing_df['student_number'].astype(str).str.strip() != student_number.strip()]

    new_answers_df = pd.DataFrame(answers_list)
    new_answers_df['student_number'] = student_number  # Add student number to each row

    updated_df = pd.concat([existing_df, new_answers_df], ignore_index=True)
    updated_df.to_csv(FINAL_EXAM_STUDENT_ANSWERS_FILE, index=False)


# === Sidebar ===
st.sidebar.markdown("## Choose Mode")
# Radio buttons to select the application mode
mode = st.sidebar.radio("Select Mode:", ["Student", "Sir Vince Only!"])
st.sidebar.markdown("---")
st.sidebar.info("Goodluck class!")  # Display a submission deadline



# === Student Section ===
if mode == "Student":
    #st.header("🎓 Student Coding Exam Section")

    # Input fields for student credentials
    stu_number = st.text_input("Student Number:", max_chars=20).strip()
    stu_name = st.text_input("Full Name: (SURNAME, FIRSTNAME MI.)", max_chars=50).strip()

    # Proceed only if both student number and name are provided
    if stu_number and stu_name:
        # Validate student credentials
        if not validate_student(stu_number, stu_name):
            st.error("Invalid credentials. Please check your student number and name.")
            st.stop()  # Stop execution if validation fails

        # Check submission status
        with open(SUBMISSION_STATUS_FILE, "r") as f:
            submissions_open = f.read().lower() == "true"

        if not submissions_open:
            st.warning("Submission is currently closed. Please contact your professor.")
            st.stop()  # Stop if submissions are closed

        st.subheader("🎓 Semester Grade")
        # Display student's final grade
        try:
            grades_df = pd.read_csv(GRADES_FILE)
            # Find the student's row in the grades DataFrame
            student_row = grades_df[
                (grades_df['student_number'].astype(str).str.strip() == stu_number.strip()) &
                (grades_df['full_name'].str.strip().str.lower() == stu_name.strip().lower())
                ]
            if not student_row.empty:
                final_grade = student_row.iloc[0]['final_grade']
                st.success(f"Your Final Grade: **{final_grade}**")
            else:
                st.info("Your grade has not been uploaded yet or your details do not match the grade roster.")
        except FileNotFoundError:
            st.warning("Grades are not yet available.")
        except Exception as e:
            st.error(f"Error loading grades: {e}")

# === Professor Section ===
elif mode == "Sir Vince Only!":
    st.header("HUWAG SUBUKAN, MASISIRA ANG BUHAY MO!")  # Humorous warning for unauthorized access
    password = st.text_input("Enter Password:", type="password")  # Password input for professor

    # Check password
    if password != PROFESSOR_PASSWORD:
        if password:  # Only show error if password was actually entered
            st.error("Incorrect password")
        st.stop()  # Stop execution if password is incorrect

    st.success("Access Granted")  # Grant access if password is correct

    st.subheader("Student Roster Management")
    # File uploader for student list CSV
    uploaded_file = st.file_uploader("Upload Student CSV (student_number,full_name)", type="csv")
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            required_cols = {'student_number', 'full_name'}
            if required_cols.issubset(df.columns):  # Check if required columns are present
                df.to_csv(STUDENT_LIST_FILE, index=False)  # Save uploaded CSV
                st.success("Student list updated successfully!")
            else:
                st.error("CSV missing required columns: 'student_number', 'full_name'")
        except Exception as e:
            st.error(f"Error processing file: {e}")

    # Display current student roster
    try:
        student_df = pd.read_csv(STUDENT_LIST_FILE)
        st.dataframe(student_df)
    except pd.errors.EmptyDataError:
        st.warning("No students registered yet.")
    except FileNotFoundError:
        st.warning("Student list file not found.")

    st.subheader("📄 Upload Semester Grades")
    # File uploader for grades CSV
    grade_file = st.file_uploader("Upload Grades CSV (student_number,full_name,final_grade)", type="csv",
                                  key="grades_csv")  # Unique key for this uploader
    if grade_file:
        try:
            grade_df = pd.read_csv(grade_file)
            required_cols = {'student_number', 'full_name', 'final_grade'}
            if required_cols.issubset(grade_df.columns):  # Check required columns
                grade_df.to_csv(GRADES_FILE, index=False)  # Save uploaded grades
                st.success("Grades uploaded successfully!")
            else:
                st.error("CSV must include: 'student_number', 'full_name', 'final_grade'")
        except Exception as e:
            st.error(f"Error processing grade file: {e}")


    st.subheader("Live Code Broadcast")
    live_code_content = ""
    if os.path.exists(LIVE_CODE_FILE):
        with open(LIVE_CODE_FILE, "r") as f:
            live_code_content = f.read()  # Load existing live code

    # Text area for professor to enter code to broadcast
    live_code = st.text_area("Enter code to share with students:", height=300, value=live_code_content)
    if st.button("Broadcast Code"):
        try:
            with open(LIVE_CODE_FILE, "w") as f:
                f.write(live_code)  # Write new live code to file
            st.success("Code broadcasted successfully!")
        except Exception as e:
            st.error(f"Error broadcasting code: {e}")

    st.subheader("Questions")
    if 'questions' not in st.session_state:
        st.session_state.questions = load_questions()

    st.markdown("### Add New Questions")
    num_new = st.number_input("Number of new questions:", 1, 10, 1)

    new_qs = []
    for i in range(num_new):
        q = st.text_area(f"Question {i + 1}", key=f"newq_{i}", height=100)
        new_qs.append(q.strip())

    if st.button("Add Questions"):
        added = 0
        start_num = len(st.session_state.questions) + 1
        for q in new_qs:
            if q:
                qid = f"Q{start_num + added}"
                st.session_state.questions[qid] = q
                added += 1

        if added:
            with open(NUM_QUESTIONS_FILE, "w") as f:
                json.dump(st.session_state.questions, f, indent=2)
            st.success(f"Added {added} new questions")
            st.rerun()

    st.markdown("### Current Questions")
    if st.session_state.questions:
        for qid, qtext in st.session_state.questions.items():
            cols = st.columns([0.1, 0.8, 0.1])
            cols[0].markdown(f"**{qid}**")
            cols[1].markdown(qtext)
            if cols[2].button("×", key=f"del_{qid}"):
                del st.session_state.questions[qid]
                with open(NUM_QUESTIONS_FILE, "w") as f:
                    json.dump(st.session_state.questions, f, indent=2)
                st.rerun()
    else:
        st.info("No questions available")

    st.subheader("Allow the student to see the grade")
    # Checkbox to control submission status
    current_status = open(SUBMISSION_STATUS_FILE).read().strip().lower() == "true"
    new_status = st.checkbox("Allow", value=current_status)
    if new_status != current_status:  # If status changed, update the file and rerun
        with open(SUBMISSION_STATUS_FILE, "w") as f:
            f.write("true" if new_status else "false")
        st.rerun()
    st.info(f"Current submission status: {'OPEN' if current_status else 'CLOSED'}")



# === Footer ===
st.markdown("---")
st.caption("© MAY 2025 Submission Portal | Developed by ASST. PROF I VINCE R. GALLARDO")
