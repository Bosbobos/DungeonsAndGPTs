import json

def ExtractJson(input_string):
    try:
        json_data = json.loads(input_string)
        return json_data
    except json.JSONDecodeError:
        start_index = input_string.find('{')
        end_index = input_string.rfind('}')
        
        if start_index != -1 and end_index != -1:
            json_str = input_string[start_index:end_index + 1]
            try:
                json_data = json.loads(json_str)
                return json_data
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format")
        else:
            raise ValueError("No JSON found in the input string")
        