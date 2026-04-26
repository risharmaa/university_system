import os
import google.generativeai as genai 
from dotenv import load_dotenv

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
    config=types.GenerateContentConfig(
        system_instruction=f"""You are a college advisor. Using this SQL schema: {sql_schema}, help students (defined by {uid}) 
        to pick classes based on their interests using the courses table. Before submitting your suggestion, check the 
        courses_offered table to make sure that the class is offered this semester. Also check the enrollment table for
        the student using {uid} to see if the student has already taken that class (do not recommend that class!)
        """
    )

    # creating the generative model
    model = genai.GenerativeModel(model_name = 'gemini-2.5-flash', system_instruction = system_instruction)

    try:
        # Call the model
        response = model.generate_content(user_input)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"


# Start a chat session with no context/history
chat = model.start_chat(history = [])

# main chat
print("Gemini Chatbot is ready! We are using the 2.5 flash version! Type 'quit' if you want to exit the chatbot.")
print("="*50)

while True:
    # get input from the user
    user_input = input("You : ")
    if not user_input.strip():
        print("Gemini needs something to work with. Please enter a valid input!")
        continue
        # skips to the next iteration of loop is data is null
    # check if the user wants to exit the chatbot
    if user_input.lower() == "quit":
        print("\nGoodbye! Thank you for chatting with Gemini 2.5 flash!")
        break
    
    try:
        # user input is sent to LLM
        response = chat.send_message(user_input, stream = True)

        # printing the LLM's response
        print("Gemini : ", end = "")
        for chunk in response:
            print(chunk.text, end = "")
        print("\n")
    except Exception as e:
        print(f"Gemini has an error occur while generating a response : {e}")
        print("\n")