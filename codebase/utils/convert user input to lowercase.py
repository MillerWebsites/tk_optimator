import re

def clean_user_input(user_input):
    # Convert user input to lowercase
    user_input = user_input.lower()
    
    # Remove special characters except for periods, spaces, and commas
    user_input = re.sub(r'[^a-z,. ]', '', user_input)
    
    # Replace multiple spaces with a single space
    user_input = re.sub(r'\s+', ' ', user_input)
    
    # Remove leading and trailing spaces
    user_input = user_input.strip()
    
    return user_input

user_input = input("Please enter some text: ")
result = clean_user_input(user_input)
print(result)