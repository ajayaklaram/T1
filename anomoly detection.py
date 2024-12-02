import os
import string
from nltk.corpus 
import wordnet as wn
import nltk

# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('omw-1.4')

# Define the base path for word classification folders
base_path = os.path.join(os.getcwd(), 'word_classifier')

# Ensure the folders exist
folders = ['fight', 'argument', 'abusive']
for folder in folders:
    os.makedirs(os.path.join(base_path, folder), exist_ok=True)
    print(f"Folder checked/created: {os.path.join(base_path, folder)}")

# Function to get synonyms for a category
def get_synonyms(category):
    synonyms = set()
    for syn in wn.synsets(category):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

# Get synonyms for each category
fight_synonyms = get_synonyms('fight')
argument_synonyms = get_synonyms('argument')
abusive_synonyms = get_synonyms('abuse')

# Function to process the input text
def classify_text(text):
    # Remove punctuation and tokenize text
    translator = str.maketrans('', '', string.punctuation)
    cleaned_text = text.translate(translator).lower()
    words = cleaned_text.split()

    # Classify and sort words
    for word in words:
        if word in fight_synonyms:
            target_folder = 'fight'
        elif word in argument_synonyms:
            target_folder = 'argument'
        elif word in abusive_synonyms:
            target_folder = 'abusive'
        else:
            continue

        # Create a file for the word in the respective folder
        with open(os.path.join(base_path, target_folder, f'{word}.txt'), 'w') as f:
            f.write(word)
        print(f"Word '{word}' classified to {target_folder}")

    print("Words have been classified and sorted into their respective folders.")

# Example usage
conversation_file_path = os.path.join(os.getcwd(), 'conversation_folder', 'conversation.txt')

# Print the path being checked
print(f"Checking path: {conversation_file_path}")

# Check if the file exists
if os.path.exists(conversation_file_path):
    print(f"File found: {conversation_file_path}")
    
    # Check file read permissions
    try:
        with open(conversation_file_path, 'r') as file:
            conversation = file.read()
        print("File read successfully.")
    except PermissionError:
        print(f"PermissionError: Unable to read the file at {conversation_file_path}.")
    
    # Classify the text from the file
    classify_text(conversation)
else:
    print(f"File not found: {conversation_file_path}")
