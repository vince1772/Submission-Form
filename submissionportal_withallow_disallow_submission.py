import streamlit as st
import os
from datetime import datetime

# === Configuration ===
QUESTIONS = {
    "Q1": 'Write a Python program that allows a teacher to input the grades of students. The program should continuously prompt the teacher to enter a grade (as a percentage between 0 and 100) or the word "done" to finish entering grades for a class.',
}
num = 0
NUM_QUESTIONS = "questions.py"
LIVE_CODE_FILE = "live_code.py"
STUDENT_CODE_DIR = "submissions-ece12"
SUBMISSION_STATUS_FILE = "allow_submissions.txt"
PROFESSOR_PASSWORD = "secret123"  # Change this password securely

# === Setup Directories and Files ===
os.makedirs(STUDENT_CODE_DIR, exist_ok=True)

# Initialize submission status file if it doesn't exist
if not os.path.exists(SUBMISSION_STATUS_FILE):
    with open(SUBMISSION_STATUS_FILE, "w") as f:
        f.write("true")  # Default: allow submissions

# === App Config ===
st.set_page_config(page_title="📝 Python Coding Portal", layout="wide")
st.title("📝 Python Coding Submission Portal")
st.subheader("CPEN21 - PROGRAMMING LOGIC AND DESIGN")

# Custom HTML for floating top-right announcement
st.markdown("""
    <div style='position:fixed; top:800px; right:10px; background-color:#f9f871; padding:10px 15px;
                border-radius:10px; box-shadow:0 4px 6px rgba(0,0,0,0.1); z-index:9999;'>
        <strong>📢 Announcement:</strong><br>
        Submission deadline is <b>2:30 PM</b>!<br>
        Stay focused and code well!
    </div>
""", unsafe_allow_html=True)


# === Mode Selector ===
st.sidebar.markdown("### 📢 Choose mode")
mode = st.sidebar.radio("",["Student", "Sir Vince Only!"])

# Add vertical space to push the announcement lower
for _ in range(5):  # Adjust number to push lower as needed
    st.sidebar.markdown("&nbsp;", unsafe_allow_html=True)

# Announcement box inside sidebar (lower-left)
st.sidebar.markdown("### 📢 Announcement")
st.sidebar.info("⚠️ Submit your code before **May 20, 2025**!")

# ---------------------- STUDENT MODE ----------------------
if mode == "Student":
    st.header("👨‍🎓 Student Coding Exam Sheet")
    name = st.text_input("Enter your full name:", key="student_name")

    if name.strip():
        st.markdown("---")

        # Check if submissions are allowed
        with open(SUBMISSION_STATUS_FILE, "r") as f:
            allow_submission = f.read().strip().lower() == "true"

        if allow_submission:
            student_answers = []
            for qid, question in QUESTIONS.items():
                st.subheader(f"{qid}:")
                st.markdown(f"**{question}**")
                code_input = st.text_area(f"Write your code for {qid}:", height=200, key=qid)
                student_answers.append(f"# {qid}: {question}\n{code_input.strip()}\n")

            if st.button("📤 Submit My Code"):
                filename = f"{STUDENT_CODE_DIR}/{name.replace(' ', '_').lower()}.py"
                with open(filename, "w") as f:
                    f.write(f"# Submission by: {name}\n")
                    f.write(f"# Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write("\n\n".join(student_answers))
                st.success("✅ Your code has been submitted successfully!")
        else:
            st.warning("🚫 Submissions are currently closed by the professor.")

        st.markdown("---")
        st.subheader("📡 Live Code from Professor")
        if os.path.exists(LIVE_CODE_FILE):
            with open(LIVE_CODE_FILE, "r") as f:
                st.code(f.read(), language="python")
        else:
            st.info("Waiting for professor to start broadcasting...")
    else:
        st.info("Please enter your name to begin.")

# ---------------------- PROFESSOR MODE ----------------------
elif mode == "Sir Vince Only!":
    st.header("🔐 Wag mona subukan. Masisira ang buhay mo!")
    password = st.text_input("Enter Professor Password:", type="password")

    if password == PROFESSOR_PASSWORD:
        st.success("✅ Access Granted. Welcome, Professor!")

        # number_of_questions = int(input("How many questions you want to add: "))
        #
        # #num = 0
        #
        # #avail_na_question = " "
        # for num in range(number_of_questions):
        #     num += 1
        #     avail_question = input(f"Write your question {num} here: ")
        #     QUESTIONS[f'Q{num}'] = avail_question
        #     print(QUESTIONS)
        #
        # if st.button("Submit Questions"):
        #     with open(NUM_QUESTIONS, 'w') as f:
        #         f.write(NUM_QUESTIONS)
        #     st.success("Question Broadcasted")

        st.subheader("📡 Broadcast Live Python Code")
        live_code = st.text_area("Write or paste code here:", height=250)

        if st.button("🚀 Broadcast Code to Students"):
            with open(LIVE_CODE_FILE, "w") as f:
                f.write(live_code)
            st.success("📤 Code broadcasted!")

        st.markdown("---")
        st.subheader("📥 Accept Submissions")

        with open(SUBMISSION_STATUS_FILE, "r") as f:
            current_status = f.read().strip().lower() == "true"

        allow_submissions = st.checkbox("Allow students to submit code", value=current_status)

        with open(SUBMISSION_STATUS_FILE, "w") as f:
            f.write("true" if allow_submissions else "false")

        st.markdown("---")
        st.subheader("📥 Student Submissions")

        files = sorted([f for f in os.listdir(STUDENT_CODE_DIR) if f.endswith(".py")])
        if files:
            for file in files:
                student_name = file.replace(".py", "").replace("_", " ").title()
                st.markdown(f"### 🧑 {student_name}")
                with open(os.path.join(STUDENT_CODE_DIR, file), "r") as f:
                    st.code(f.read(), language="python")
        else:
            st.info("No student submissions yet.")


    elif password != "":
        st.error("❌ Incorrect password.")

for _ in range(5):  # Adjust number to push lower as needed
    st.markdown("&nbsp;", unsafe_allow_html=True)
# Footer
st.markdown("---")
st.caption("© MAY 2025 PYTHON SUBMISSION APP | Developed by ASST. PROF VINCE R. GALLARDO")