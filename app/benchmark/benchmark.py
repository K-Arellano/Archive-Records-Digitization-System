import csv
import os
from datetime import datetime

def createCSV(filename):
    try:
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        # Define headers for the CSV file
        headers = ["ID", "Scanner", "Entries", "Scanning Time", "Average_WER", "Average_CER", "Date"]
        
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
        
        return True
    except Exception as e:
        print(f"Error creating CSV file: {e}")
        return False

def fetchCSV(filename):
    try:
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r', newline='') as file:
                reader = csv.DictReader(file)
                data = list(reader)
            return data
        else:
            print(f"CSV file '{filename}' does not exist.")
            return None
    except Exception as e:
        print(f"Error fetching CSV file: {e}")
        return None

def updateCSV(benchID, scantype, WER_data, CER_data, no_items, scanSpeed, filename):
    try:
        # Check for missing 
        variables = {
                    'benchID': benchID,
                    'scantype': scantype,
                    'WER_data': WER_data,
                    'CER_data': CER_data,
                    'no_items': no_items,
                    'scanSpeed': scanSpeed,
                    'filename': filename
                    }
        
        missing_variables = [key for key, value in variables.items() if not value]

        if missing_variables:
            print(f"Missing or null value for: {', '.join(missing_variables)}")
            return "missingParameters"
        
        script_dir = os.path.dirname(__file__)  # Directory of the current script
        file_path = os.path.join(script_dir, filename)
        
        if not os.path.exists(file_path):
            create_success = createCSV(filename)
            if not create_success:
                return "failed"
        
        current_data = fetchCSV(filename)
        
        # Check for duplicate benchID
        if current_data:
            for row in current_data:
                if row['ID'] == benchID:
                    return "entry exist"
        
        new_data = {
            'ID': benchID,
            'Scanner': scantype,
            'Entries': no_items,
            'Scanning Time': scanSpeed,
            'Average_WER': WER_data,
            'Average_CER': CER_data,
            'Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        with open(file_path, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=new_data.keys())
            
            if file.tell() == 0:
                writer.writeheader()
            
            writer.writerow(new_data)
        
        return "success"
    
    except Exception as e:
        return f"Error updating CSV file: {e}"
