import os
import shutil
import string
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('omw-1.4')
nltk.download('punkt')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()

# Function to read and tokenize text
def read_and_tokenize(text):
    translator = str.maketrans('', '', string.punctuation)
    cleaned_text = text.translate(translator).lower()
    words = cleaned_text.split()
    lemmatized_words = [lemmatizer.lemmatize(word) for word in words]
    print(f"Text cleaned and tokenized. Number of words: {len(lemmatized_words)}")
    return lemmatized_words

# Function to get all related lexical relations for a category
def get_related_words(category):
    print(f"Fetching related words for category: {category}")
    related_words = set()
    for syn in wn.synsets(category):
        for lemma in syn.lemmas():
            related_words.add(lemma.name())
            # Derivationally related forms
            for deriv in lemma.derivationally_related_forms():
                related_words.add(deriv.name())
        # Hypernyms (more general terms)
        for hypernym in syn.hypernyms():
            for lemma in hypernym.lemmas():
                related_words.add(lemma.name())
        # Hyponyms (more specific terms)
        for hyponym in syn.hyponyms():
            for lemma in hyponym.lemmas():
                related_words.add(lemma.name())
        # Antonyms (opposite meanings)
        for lemma in syn.lemmas():
            for antonym in lemma.antonyms():
                related_words.add(antonym.name())
        # Meronyms (parts of the whole)
        for meronym in syn.part_meronyms():
            for lemma in meronym.lemmas():
                related_words.add(lemma.name())
        # Holonyms (whole to which parts belong)
        for holonym in syn.part_holonyms():
            for lemma in holonym.lemmas():
                related_words.add(lemma.name())
        # Attributes (attributes of the concept)
        for attribute in syn.attributes():
            for lemma in attribute.lemmas():
                related_words.add(lemma.name())
    print(f"Related words for {category}: {related_words}")
    return related_words

# Get related words for each category
abuse_related_words = get_related_words('abuse')
anger_related_words = get_related_words('anger')
argument_related_words = get_related_words('argument')

# Add specific abusive words


# Function to classify the words
def classify_words(words):
    print(f"Classifying words based on related words")
    detected_words = set()
    for word in words:
        if word in abuse_related_words or word in anger_related_words or word in argument_related_words:
            detected_words.add(word)
            print(f"Word '{word}' detected as relevant")
    print(f"Classification complete. Detected words: {detected_words}")
    return detected_words

# Function to store words in the test_output.txt file
def store_words_in_file(data, file_path):
    try:
        print(f"Storing words in {file_path}")
        with open(file_path, 'w') as file:
            for word in data:
                file.write(word + '\n')
        print(f"Words stored in {file_path}")
        
        # Verify the content
        with open(file_path, 'r') as file:
            content = file.read().strip()
        print(f"Content of {file_path} after writing:\n{content}")
    except Exception as e:
        print(f"Error writing to file: {e}")

# Store the conversation text in a variable
conversation_text = """
In the midst of a heated argument, tempers flared and voices were raised. "You useless idiot!" John shouted, his face red with anger. The conflict quickly escalated as insults were exchanged back and forth. "How dare you speak to me like that!" Sarah yelled, her eyes blazing with fury. The verbal abuse continued, with each side unwilling to back down. "You always ruin everything! Can't you do anything right?" he snarled. The atmosphere was tense, the room filled with the echoes of their hostile words. "I'm sick of your constant fighting!" she retorted, her frustration evident. The argument had reached a boiling point, leaving both parties seething with anger and resentment.

The quarrel started over something trivial, but soon turned into a battle of egos. John couldn't believe how stubborn Sarah could be, and Sarah was equally shocked at John's arrogance. "You're always so negative and abusive," John accused, his voice dripping with disdain. "Abusive? You're the one who's always abusive!" Sarah countered, her voice rising. "You're the most arrogant person I know," John fired back. The fight was getting out of control, and there seemed to be no end in sight.

As the argument continued, harsh words flew across the room. "You’re nothing but a lazy bum," John sneered. "Lazy? At least I'm not a manipulative liar like you," Sarah snapped. Their words were like daggers, each one hitting its mark and leaving emotional scars. "You're always so angry and hostile," John shouted. "Hostile? You’re the one who started this fight!" Sarah yelled back. The tension was palpable, and the room seemed to vibrate with hostility.

The abusive language continued, with insults being hurled from both sides. "You’re just a useless piece of trash," John said. "And you're a controlling tyrant," Sarah replied. The fight had reached its peak, with both parties feeling the full weight of their words. "I can't stand you," John shouted, his voice breaking. "The feeling is mutual," Sarah responded coldly.

The argument had become a toxic exchange, with both parties unwilling to concede. "You always act like a victim," John accused. "Because you’re always attacking me," Sarah replied. "You’re such a coward," John shouted. "Coward? Look who's talking," Sarah shot back. The room was filled with a sense of despair, the fight leaving both John and Sarah feeling drained and broken.

Their voices were now hoarse from shouting, but the anger and resentment remained. "I hate you," John said through gritted teeth. "The feeling is mutual," Sarah replied icily. The words hung heavy in the air, the weight of their argument almost tangible. "You’ll never change," John muttered. "Neither will you," Sarah retorted. The fight had left both of them feeling hopeless, their relationship seemingly beyond repair.

The verbal sparring continued, each word like a blow. "You’re pathetic," John sneered. "And you’re a tyrant," Sarah shot back. The fight had left them both feeling battered and bruised, their words having inflicted deep emotional wounds. "I can’t do this anymore," John finally said, his voice weary. "Good, because I’m done with you too," Sarah replied, her voice filled with finality.

As the argument finally came to an end, the silence was deafening. Both John and Sarah were left feeling the heavy burden of their words, the fight having left deep scars. "I hope you’re happy," John said bitterly. "I’m not, but I’m free," Sarah replied. The fight had ended, but the damage was done. The room was filled with an uneasy calm, the aftermath of their fight leaving both John and Sarah feeling empty and alone.

The relationship had been poisoned by their constant fighting, their words having torn each other apart. "You’re nothing to me," John said, his voice hollow. "And you’re nothing to me," Sarah replied, her voice devoid of emotion. The fight had left them both feeling numb, their anger and resentment having consumed them. As they walked away from each other, the words of their argument echoed in their minds, a constant reminder of their broken relationship.

The room was now quiet, the echoes of their argument fading. The fight had taken its toll, leaving both John and Sarah feeling emotionally exhausted. Their words had been weapons, each one cutting deep. "Maybe one day you’ll realize what you’ve lost," John said as he left. "Maybe one day you’ll realize what you’ve done," Sarah replied. The fight was over, but the wounds remained, a painful reminder of their toxic relationship."""

# Main process
def process_text():
    print(f"Processing conversation text")
    # Read and tokenize the conversation text
    words = read_and_tokenize(conversation_text)
    # Classify the words into respective categories
    detected_words = classify_words(words)
    # Store the classified words in the test_output.txt file in the current directory
    test_output_file_path = 'test_output.txt'
    store_words_in_file(detected_words, test_output_file_path)
    print(f"Text processing complete")

    # Move the file to word_classifier folder
    destination_path = r"C:\Users\Ajaya\OneDrive\Documents\Desktop\T1\word_classifier\test_output.txt"
    shutil.move(test_output_file_path, destination_path)
    print(f"File moved to {destination_path}")

# Run the main process
process_text()
