import json

def DictToString(dict):
    returnStr = ''
    for key, value in dict.items():
        if key!='id' and key!='username':
            returnStr += f"{key}: {value.strip()},\n"

    returnStr = returnStr.rstrip(",\n")

    return returnStr

def FilteredDictToJson(dict, excluded):
    filtered = {k: dict[k].strip() for k in dict if k not in excluded}

    return json.dumps(filtered)
