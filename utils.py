import json


def clean_json(data):
    """
    Clean up the JSON string or ensure the data is a valid JSON object.
    
    :param data: Raw JSON string or already-parsed JSON object (list/dict)
    :return: Cleaned JSON dictionary or list
    """
    # If data is already a list or dictionary, no need to clean it
    if isinstance(data, (list, dict)):
        return data
    
    # Ensure data is a string before attempting to clean it
    if isinstance(data, str):
        # Clean up the string by removing newline characters and fixing escaped quotes
        cleaned_string = data.replace('\n', '').replace('\"', '"')
        return cleaned_string 
            
    # If the input is neither a string nor JSON-like, return None
    return None
    

def handle_exception(e):
    """
    Handle exceptions and return a JSON response.
    
    :param e: Exception object
    :return: JSON formatted error message
    """
    return {"error": f"Unexpected error: {str(e)}"}

def print_json(data, title=""):
    """
    Pretty print JSON data with a title.

    :param data: JSON data to print
    :param title: Optional title to print before the JSON
    """
    if title:
        print(f"---- {title}")
    print(json.dumps(data, indent=4))
    print("------------------------------------------------------------------------")
