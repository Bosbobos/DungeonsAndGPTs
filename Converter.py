import json

def DictToString(dict):
    returnStr = ''
    for key, value in dict.items():
        returnStr += f"{key}: {value},\n"

    returnStr = returnStr.rstrip(",\n")

    return returnStr

def FilteredDictToJson(dict, excluded):
    filtered = {k: dict[k] for k in dict if k not in excluded}

    return json.dumps(filtered)
