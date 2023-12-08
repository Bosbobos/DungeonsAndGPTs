import openai
import JsonManager
import Converter

class GptGamemaster:
    def __init__(self, apiKey, dbContext):
        self.__apiKey = apiKey
        self.dbContext = dbContext

    def SendMessage(self, systemMsgs: list, userMsg: str, temperature: float):
        client = openai.OpenAI(api_key=self.__apiKey)
        if isinstance(systemMsgs, (list,tuple)):
            msgs = []
            for i in systemMsgs:
                msgs.append(
                    {
                        "role": "system",
                        "content": i
                    }
                )
            msgs.append(
                {
                    "role": "user",
                    "content": userMsg,
                }
            )
        else:
            msgs = [
                {
                    "role": "system",
                    "content": systemMsgs
                },
                {
                    "role": "user",
                    "content": userMsg,
                }
            ]

        chat_completion = client.chat.completions.create(
            messages=msgs,
            model="gpt-3.5-turbo",
            temperature=temperature
        )

        return chat_completion.choices[0].message.content
    
    def __addSmthToJson(self, name, content, json):
        if isinstance(json, (tuple, list)): return [{name: content, **item} for item in json]
        return {name: content, **json}
        

    def CreateWorld(self, username, setting):
        sysMsg = self.dbContext.read_record("Prompts", "key", "WorldCreation")["prompt"]
        answer = self.SendMessage(sysMsg, setting, 1)
        self.__saveCompressedInformation(username, "World", answer, "CompressWorldInfo")
        return answer
    

    def CreateCharacter(self, username, introduction):
        sysMsg = self.dbContext.read_record("Prompts", "key", "CreateCharacter")["prompt"]
        answer = self.SendMessage(sysMsg, introduction, 0)
        ansDict = JsonManager.ExtractJson(answer)
        if ansDict['Race'] == "Unknown":
            ansDict['Race'] = "Human"
        newansDict = self.__addSmthToJson('username', username, ansDict)
        self.dbContext.create_record("characters", newansDict)

        gear = self.__CreateStaringGear(username)

        result = Converter.DictToString(ansDict)

        return [result, gear]

    
    def __CreateStaringGear(self, username):
        sysMsgs = [self.dbContext.read_record("Prompts", "key", "StartingGearCreation")["prompt"]]
        worldInfo = self.dbContext.read_latest_record("world", "username", username)
        character = self.dbContext.read_latest_record("characters", "username", username)
        worldJson = Converter.FilteredDictToJson(worldInfo, ['id', 'username'])
        characterJson = Converter.FilteredDictToJson(worldInfo, ['id', 'username'])
        sysMsgs.append(worldJson)
        gear = self.SendMessage(sysMsgs, characterJson, 0)
        gearDict = JsonManager.ExtractJson(gear)
        newansDict = self.__addSmthToJson('character_id', character["id"], gearDict)

        for item in newansDict:
            self.dbContext.create_record("items", item)

        return gearDict
        

    def __saveCompressedInformation(self, username, tableName, text, format):
        sysMsg = self.dbContext.read_record("Prompts", "key", format)["prompt"]
        answer = self.SendMessage(sysMsg, text, 0)
        ansDict = JsonManager.ExtractJson(answer)
        newansDict = self.__addUsername(username, ansDict)
        self.dbContext.create_record(tableName, newansDict)