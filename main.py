def main():
    import sys
    import time
    import speech_recognition as sr
    from audio import transcribe_audio
    from resume_parser import parse_resume
    from job_description_parser import parse_job_description
    from query_handler import handle_query

    print("Welcome to the Language Model Project!")
    
    # Get user inputs for resume and job description
    resume_path = input("Please enter the path to your resume: ")
    job_description_path = input("Please enter the path to the job description: ")

    # Parse the resume and job description
    resume_data = parse_resume(resume_path)
    job_description_data = parse_job_description(job_description_path)

    print("Starting audio transcription...")
    audio_transcription = transcribe_audio()

    # Handle user queries based on the parsed data and audio transcription
    while True:
        user_query = input("Please enter your query (or type 'exit' to quit): ")
        if user_query.lower() == 'exit':
            print("Exiting the application.")
            break
        response = handle_query(user_query, resume_data, job_description_data, audio_transcription)
        print("Response:", response)

if __name__ == "__main__":
    main()