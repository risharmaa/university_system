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

# creating the generative model
model = genai.GenerativeModel('gemini-2.5-flash')

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