def DictToString(dict):
    returnStr = ''
    for key, value in dict.items():
        if key != "username": returnStr += f"{key}: {value},\n"

    returnStr = returnStr.rstrip(",\n")

    return returnStr
