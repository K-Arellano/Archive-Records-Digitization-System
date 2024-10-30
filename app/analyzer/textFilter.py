import re
import pandas as pd

def removeUnwantedCharacters(raw_inputArray):
    updated_studentNames = []
    
    # Loop through each name in the input array
    for name in raw_inputArray:
        cleaned_name = re.sub(r'[^a-zA-ZÑñ.,]', ' ', name) # Remove characters that are not letters, dots, commas, or spaces
        cleaned_name = re.sub(r'\.{2,}', '.', cleaned_name)  # Replace multiple dots with a single dot
        cleaned_name = re.sub(r',{2,}', ',', cleaned_name)  # Replace multiple commas with a single comma
        cleaned_name = cleaned_name.strip() # Remove leading and trailing spaces

        # Remove leading periods before an uppercase letter
        if cleaned_name.startswith("."):
            cleaned_name = cleaned_name[1:]
        # Remove leading periods before an uppercase letter
        if cleaned_name.startswith(","):
            cleaned_name = cleaned_name[1:]
        
        # If no comma is found, find the nearest period to convert
        if ',' not in cleaned_name:
            period_index = cleaned_name.rfind('.') # Find the last period to potentially convert to comma

            #  check if there is at least one dot ('.') present in the cleaned_name string
            if period_index != -1:
                next_word_start = period_index + 1 # Calculate the start index of the next word after the dot
                next_space_index = cleaned_name.find(' ', next_word_start) # Find the index of the next space after the dot

                if next_space_index != -1: # If there's a space after the dot, extract the next word
                    next_word = cleaned_name[next_word_start:next_space_index] 
                else: # If no space is found, take the rest of the string as the next word
                    next_word = cleaned_name[next_word_start:]

                # If the next word is at least 3 characters long, replace dot with comma
                if len(next_word) >= 3:
                    cleaned_name = cleaned_name[:period_index] + ',' + cleaned_name[period_index + 1:]  # Replace the dot with a comma

        cleaned_name = re.sub(r'([A-Z])', r' \1', cleaned_name) # Add single space after every Uppercase
        cleaned_name = re.sub(r',', ' , ', cleaned_name) # Add leading and trailing space between commas
        cleaned_name = re.sub(r'\.', '. ', cleaned_name) # Add trailing space after period
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name) # Replace multiple spaces with single space 
        cleaned_name = cleaned_name.title() # Title case the cleaned name
        
        updated_studentNames.append(cleaned_name)
    return updated_studentNames

def redundancyRemoval(row):
    df = pd.DataFrame({'col': row}) # Create a DataFrame with 'col' as column name
    df.drop_duplicates(inplace=True) # using drop_duplicates() method to remove duplicate entries
    return df['col'].tolist() # Converting DataFrame back to list

def filterdata(out_array):
    try:
        # Lists of grades and remarks to filter out non-name data
        grades = ['1.0', '1.25', '1.5', '1.75', '2.0', '2.25', '2.5', '2.75', '3.0', 'inc']
        remarks = ['pass', 'passed', 'fail', 'inc', 'failed',
                   'no grades', 'dropped', 'dropped.', 'no final exam', 'no final exam.', 'exam', 'no exam', 'final',
                   'no requirement', 'no requirements']

        if out_array:
            entries = []

            for row in out_array:
                filtered_row = []
                newData = redundancyRemoval(row)  # Remove duplicates from the current row list
                for i in range(len(newData)):
                    item = re.sub(r'\s+', ' ', newData[i]).strip().lower() # Normalize the string
                   # Check if both columns are not in grades or remarks
                    if item not in grades and item not in remarks:  
                        filtered_row.append(newData[i]) # If there are two different columns, join them as the name

                joined_row = ' '.join(filtered_row) # Join filtered elements into a single string
                entries.append(joined_row) # Append the joined string to entries list
                
            print('No# of Entries: ',len(out_array))
            print('Processing Entries: ',len(entries))

            return entries

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
