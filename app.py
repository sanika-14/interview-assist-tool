import streamlit as st
import fitz  # PyMuPDF
import speech_recognition as sr
import google.generativeai as genai
import time
from resume_parser import parse_resume, extract_skills, extract_experience, extract_qualifications



# Function to handle login with email and password
def login(email, password):
    if email not in st.session_state.USER_CREDENTIALS:
        st.error("Email not registered. Please sign up.")
        return False
    elif st.session_state.USER_CREDENTIALS[email] != password:
        st.error("Invalid password.")
        return False
    else:
        st.session_state.logged_in = True
        st.session_state.username = email
        return True


# Function to handle logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""

# Configure Gemini
GOOGLE_API_KEY = "AIzaSyCVne5Ru2NBatL22caSJpgN_6gZxDmMPPY"  # Your API key from earlier
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize speech recognizer
recognizer = sr.Recognizer()

def parse_pdf(file_content):
    """Extracts text from a PDF file using BytesIO."""
    try:
        document = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page_num in range(len(document)):
            page = document[page_num]
            text += page.get_text()
        document.close()
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"

def transcribe_audio():
    """Captures and transcribes live audio."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=30)
            transcription = recognizer.recognize_google(audio)
            return transcription
        except sr.WaitTimeoutError:
            return None  # No speech detected
        except sr.UnknownValueError:
            return None  # Could not understand the audio
        except sr.RequestError as e:
            return f"Could not request results: {e}"

def generate_response(question: str, resume_text: str = "", job_description: str = "") -> str:
    """Generate a response using the Gemini API."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Acting as an AI interviewer, consider the following:
        
        Question: {question}
        
        Resume Information: {resume_text}
        
        Job Description: {job_description}
        
        Please provide a detailed response addressing the question while considering 
        the candidate's background and the job requirements.
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_introduction(resume_text: str) -> str:
    """Generate an introduction based on the resume text using the Gemini API."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        prompt = f"""
        Generate an introduction for a candidate with the following resume data:
        
        {resume_text}
        
        The introduction should start from a first-person perspective, for example: "I am".
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating introduction: {str(e)}"

# Streamlit UI
st.title("AI Interview Simulator")

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

# Initialize session state for authentication toggle
if 'show_signup' not in st.session_state:
    st.session_state.show_signup = False

# Initialize session state for user credentials
if 'USER_CREDENTIALS' not in st.session_state:
    st.session_state.USER_CREDENTIALS = {
        "user1@example.com": "password1",
        "user2@example.com": "password2"
    }

# Function to handle user registration
def signup(email, password):
    if not email.strip() or not password.strip():
        st.error("Please enter both email and password.")
        return False
    if email in st.session_state.USER_CREDENTIALS:
        st.error("Email already registered.")
        return False
    else:
        st.session_state.USER_CREDENTIALS[email] = password
        st.success("Registration successful. You can now log in.")
        return True

# Authentication Check
if not st.session_state.logged_in:
    if st.session_state.show_signup:
        st.subheader("Sign Up")
        new_email = st.text_input("Email", key="signup_email")
        new_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign Up"):
            signup(new_email, new_password)
        if st.button("Back to Login"):
            st.session_state.show_signup = False
    else:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            login(email, password)
        
        st.write("OR")
   
        
        st.write("---")
        if st.button("Sign Up"):
            st.session_state.show_signup = True
else:
    # Show logout button
    st.sidebar.button("Logout", on_click=logout)

    # Session state for storing resume text and chat history
    if 'resume_text' not in st.session_state:
        st.session_state.resume_text = ""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'interview_active' not in st.session_state:
        st.session_state.interview_active = False

    # Upload Resume PDF
    uploaded_file = st.file_uploader("Upload Resume PDF", type="pdf")
    if uploaded_file is not None:
        resume_text = parse_pdf(uploaded_file.read())
        if resume_text.startswith("Error"):
            st.error(resume_text)
        else:
            st.session_state.resume_text = resume_text
            # Parse Resume
            parsed_resume = parse_resume(resume_text)
            st.success("Resume data has been parsed successfully.")

            # Generate Introduction
            introduction = generate_introduction(resume_text)
            st.subheader("Generated Introduction")
            st.write(introduction)

    # Job Description Input
    job_description = st.text_area("Enter Job Description")

    # Live Chat Window
    st.subheader("Live Interview Chat")

    # Placeholder for chat messages
    chat_placeholder = st.empty()

    # Start/Stop Interview Buttons
    if not st.session_state.interview_active:
        if st.button("Start Interview"):
            st.session_state.interview_active = True
            st.session_state.chat_history = []  # Reset chat history
            st.write("Interview started. Speak into your microphone...")

    if st.session_state.interview_active:
        if st.button("Stop Interview"):
            st.session_state.interview_active = False
            st.write("Interview stopped.")

    # Continuously listen and respond during the interview
    if st.session_state.interview_active:
        while st.session_state.interview_active:
            # Transcribe audio
            transcription = transcribe_audio()
            if transcription:
                # Add user's question to chat history
                st.session_state.chat_history.append(("You", transcription))
                
                # Generate AI response
                response = generate_response(
                    transcription, 
                    st.session_state.get('resume_text', ''), 
                    job_description
                )
                # Add AI's response to chat history
                st.session_state.chat_history.append(("AI", response))

                # Update the chat window
                chat_placeholder.empty()
                for speaker, text in st.session_state.chat_history:
                    if speaker == "You":
                        chat_placeholder.write(f"**You:** {text}")
                    else:
                        chat_placeholder.write(f"**AI:** {text}")

            # Add a small delay to avoid overloading the app
                time.sleep(1)