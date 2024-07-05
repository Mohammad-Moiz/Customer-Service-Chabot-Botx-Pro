# write your functions here....

import re


def remove_date_and_time(file_path):
    # Regular Expression
    pattern = r"\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?(AM|PM|am|pm) - "

    # Open and Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        conversation = file.read()

    lines = conversation.split('\n')

    cleaned_lines = []
    for line in lines:
        # Remove the date and time, and append in list
        cleaned_line = re.sub(pattern, '', line)
        if cleaned_line.strip():
            cleaned_lines.append(cleaned_line.strip())

    # Join the cleaned lines back into a single string
    cleaned_conversation = '\n'.join(cleaned_lines)
    return cleaned_conversation



def convert_into_list_of_dictionary(cleaned_conversation):
    # Split the conversation into lines
    lines = cleaned_conversation.split('\n')

    # Process each line and structure it into a list of dictionaries
    conversation_data = []
    for line in lines:
        if ": " in line:  # Ensure the line has the expected format
            speaker, message = line.split(": ", 1)
            conversation_data.append({"speaker": speaker, "message": message})

    converted_format = [{item['speaker']: item['message']} for item in conversation_data]
    final_format = converted_format[0:80]
    return final_format

    

# clean_text = remove_date_and_time('data/sami.txt')
# conversation = convert_into_list_of_dictionary(clean_text)
# print(conversation)