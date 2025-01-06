import streamlit as st
import pandas as pd
from streamlit_cognito_auth import CognitoAuthenticator
import os
from PyPDF2 import PdfReader
import json
import boto3
from anthropic import Anthropic


pool_id = st.secrets["pool_id"]
app_client_id = st.secrets["app_client_id"]

# anthropic 
anthropic = Anthropic(
    api_key = st.secrets["anthropic_api_key"]
)
anthropic_model_id = "claude-3-5-sonnet-latest"
 
# Authenticate user
if pool_id and app_client_id:
    authenticator = CognitoAuthenticator(
        pool_id=pool_id,
        app_client_id=app_client_id,
    )
    #authenticator.logout()
    is_logged_in = authenticator.login()
    st.session_state['is_logged_in'] = is_logged_in
    if not is_logged_in:
        st.stop()
    
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def call_anthopric(model_id, messages): 
    response = anthropic.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": messages,
            }
        ],
        model=model_id,
    )
    return response

if __name__ == "__main__":

    st.title("Path Planer")
    st.write("Welcome to PathPlanner, your personal academic advisor for achieving your goals! Follow these simple steps to get started:")

    
    goal = st.pills(
        "Your goal",
        default="Go to college",
        options=("Get a high school diploma", "Go to college"),
    )

    grade_level = st.pills(
        "Your upcoming high school year",
        default="Grade 9",
        options=("Grade 9", "Grade 10"),
    )

    # select interested majors
    # Load the CSV data

    df = pd.read_csv("data/data.csv")

    # Remove NaN values from the 'Major' column
    df_cleaned = df["Major"].dropna()

    # Add 'None' as the first option (if desired)
    majors = ["None"] + df_cleaned.tolist()

    # Initialize the multiselect widget
    # Default value will only be "None" if the user hasn't selected anything yet
    majors_selected = st.multiselect(
    "Choose 2 of your interested majors", 
    options=majors,  # List of options including "None"
    default=[] if len(df_cleaned) > 1 else ["None"],  # Default to "None" if no major is selected
    max_selections=2  # Limiting to 2 selections
    )

    # 1. Subjects they excel in and those they struggle with (Text Area)
    subjects_excel = st.text_area(
    "What subjects do you excel in? Please list them:",
    placeholder="List subjects you excel in here."
    )

    subjects_struggle = st.text_area(
    "Do you struggle with any subjects? Please list them:",
    placeholder="List subjects you struggle with here."
    )

    # 2. Interest in taking advanced courses (AP, honors, IB, etc.) - Multiselect remains
    advanced_courses = st.multiselect(
    "Are you interested in taking any advanced courses? Choose all that applies", 
    options=["AP", "Honors", "IB", "Other Acceleration Options"],
    default=[]
    )

    # 3. credit req
    credit_requirements = st.text_area(
    "Does your school have specific graduation credit requirements or a required number of classes per year? If so, please list them.",
    placeholder="For example: 4 English credits, 3 Math credits, 3 Science credits, 1 PE credit, etc."
    )

    # 4. Specific subjects or extracurricular activities they are passionate about (Text Area)
    passionate_about = st.text_area(
    "What subjects or extracurricular activities are you passionate about and would like to explore further?", 
    placeholder="Describe subjects or activities you're passionate about."
    )

    # Ask if the student has already taken some classes
    math_completed = st.text_area(
    "What math courses have you already completed, and what is the highest-level math class you’ve taken? This helps determine your next steps in the math sequence.",
    placeholder="For example: Algebra 1, Geometry, Algebra 2."
    )

    science_completed = st.text_area(
    "What science courses have you already completed? This will help ensure your plan follows the correct progression.",
    placeholder="For example: Biology, Chemistry, Physics."
    )

    #majors = st.multiselect("choose 2 of your interested majors", options=df.columns[1:], default=["None"], max_selections=2)
    #score_sat = st.number_input("Your recent SAT score", placeholder=1200, step=100, min_value=400, max_value=1500)
    #st.write("or")
    
    score_gpa = st.number_input("What is your Target Weighted GPA score?", placeholder=4.0, step=0.1, min_value=2.5, max_value=5.0)

    uploaded_file = st.file_uploader("Upload the school course catalog document", type="pdf")
    pdf_text = None

    if uploaded_file is not None:
        try:
            # Extract text
            pdf_text = extract_text_from_pdf(uploaded_file)
        except Exception as e:
            st.error(f"An error occurred while processing the PDF: {e}")

        if st.button("Get recommendation"):
            # Send to LLM

            anthropic_prompts = f'''
                                You are a high school academic advisor. Your task is to create a 3-4 year course plan tailored to the student's goals, strengths, and circumstances. Please present the plan in a clear table format.

                                The student provides the following information:

                                Goal: {goal}
                                Upcoming grade level: {grade_level}
                                Preferred majors: {majors_selected}
                                School course catalog: {pdf_text}
                                Subjects of strength (prioritize these): {subjects_excel}
                                Subjects of difficulty (regular or omit if not required): {subjects_struggle}
                                Advanced courses of interest: {advanced_courses}
                                Passionate subjects/extracurriculars: {passionate_about}
                                Graduation credit requirements (if not listed in catalog): {credit_requirements}
                                Math progression details: {math_completed}
                                Science progression details: {science_completed}
                                Requirements:

                                Only include courses that exist in the provided course catalog. Verify availability before including.
                                Determine the correct number of classes per year based on the course catalog or student-provided graduation requirements.
                                Follow logical progression paths for core subjects, ensuring prerequisites are met.
                                Create a balanced and realistic plan that aligns with the student's academic goals, strengths, and weaknesses.
                                Estimate GPA based on an A average, with advanced courses weighted.
            '''
            # call bedrock
            with st.spinner('Evaluating...'):
                #response = call_bedrock(bedrock_model_id, messages)
                response = call_anthopric(anthropic_model_id,anthropic_prompts)
                
                st.write(response.content[0].text)