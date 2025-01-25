def handle_query(resume_data, job_description_data, user_query):
    """Handles user queries by interfacing with the Hugging Face API."""
    from transformers import pipeline

    # Load the Hugging Face model for question answering
    qa_pipeline = pipeline("question-answering")

    # Prepare the context from resume and job description
    context = f"Resume: {resume_data}\nJob Description: {job_description_data}"

    # Get the answer from the model
    result = qa_pipeline(question=user_query, context=context)

    return result['answer'] if 'answer' in result else "I'm sorry, I couldn't find an answer to your query."