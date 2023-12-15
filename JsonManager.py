import json

def ExtractJson(input_string):
    """
    Extract JSON data from a given input string or its substring, if possible. If not, raises a ValueError

    @param input_string: The input string containing JSON data.
    @type input_string: str

    @return: The parsed JSON data.
    @rtype: dict

    @raise ValueError: If the input string does not contain a valid JSON.
    """
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
        