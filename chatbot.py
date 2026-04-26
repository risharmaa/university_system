import os
import google.generativeai as genai 
from dotenv import load_dotenv
from google.generativeai import types

# load environment variable from the .env file
load_dotenv()

# configuring the Gemini API w/ the key from .env file
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except AttributeError:
    print("Error! The GEMINI_API_KEY was not found.")
    exit()


with open("schema.sql", "r") as f:
    sql_schema = f.read()

def advising_chat(user_input, uid):
    system_instruction=f"""You are a college advisor. Using this SQL schema: {sql_schema}, help students (defined by {uid}) 
        to pick classes based on their interests using the courses table. Before submitting your suggestion, check the 
        courses_offered table to make sure that the class is offered this semester. Also check the enrollment table for
        the student using {uid} to see if the student has already taken that class (do not recommend that class!)
        """

    # creating the generative model
    model = genai.GenerativeModel(model_name = 'gemini-2.5-flash', system_instruction = system_instruction)

    try:
        # call the model
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"
