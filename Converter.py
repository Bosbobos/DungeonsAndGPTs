import json


def DictToString(dict):
    returnStr = ''
    for key, value in dict.items():
        if key != 'id' and key != 'username':
            if isinstance(value, str):
                returnStr += f"{key}: {value.strip()},\n"
            else:
                returnStr += f"{key}: {value},\n"

    returnStr = returnStr.rstrip(",\n")

    return returnStr


def FilteredDictToJson(dict, excluded):
    filtered = {k: dict[k].strip() if isinstance(
        dict[k], str) else dict[k] for k in dict if k not in excluded}

    return json.dumps(filtered)
