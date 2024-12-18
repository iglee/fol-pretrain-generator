import openai
import os

def read_file_into_list(file_path):
    """Reads the entire file and returns its contents as a list of lines."""
    with open(file_path, "r") as f:
        lines = f.readlines()
    
    # Strip newline characters from each line
    return [line.strip() for line in lines]

# Define the function to prompt ChatGPT
def prompt_chatgpt(prompt):
    """Sends a prompt to ChatGPT and returns the response using the API key from environment variable."""
    api_key = os.getenv("OPENAI_API_KEY")  # Get API key from environment variable
    
    if not api_key:
        raise ValueError("API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    openai.api_key = api_key  # Set the OpenAI API key
    
    response = openai.Completion.create(
        model="gpt-4o",  # or "gpt-3.5-turbo" depending on the version you're using
        prompt=prompt,
        max_tokens=150  # Adjust this as needed
    )
    
    return response.choices[0].text.strip()  # Return the generated response