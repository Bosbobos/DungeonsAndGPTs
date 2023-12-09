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

        result = Converter.DictToString(ansDict)

        return result

    
    def CreateStaringGearAndAbilities(self, username):
        sysMsgs = [self.dbContext.read_record("Prompts", "key", "StartingGearCreation")["prompt"]]
        worldInfo = self.dbContext.read_latest_record("world", "username", username)
        character = self.dbContext.read_latest_record("characters", "username", username)
        worldJson = Converter.FilteredDictToJson(worldInfo, ['id', 'username'])
        characterJson = Converter.FilteredDictToJson(character, ['id', 'username'])
        sysMsgs.append(worldJson)
        gear = self.SendMessage(sysMsgs, characterJson, 0)
        gearDict = JsonManager.ExtractJson(gear)
        newansDict = self.__addSmthToJson('character_id', character["id"], gearDict)

        for item in newansDict:
            self.dbContext.create_record("items", item)

        gearResult = [Converter.DictToString({'Item': item['Name']}) for item in gearDict]

        abilities = self.__CreateStartingAbilities(worldJson, character, gearDict)
        abilitiesNewDict = ["".join(f"{key}: {value}" for key, value in ability.items() if key != 'ShortDescription') for ability in abilities]
        abilitiesResult = [Converter.DictToString(abilitiesNewDict)]

        return [gearResult, abilitiesResult]
        

    def __CreateStartingAbilities(self, worldJson, character, gearDict):
        characterJson = Converter.FilteredDictToJson(character, ['id', 'username'])
        gearJson = '['
        for gear in gearDict:
            gearJson += Converter.FilteredDictToJson(gear, ['id', 'character_id', 'Name', 'SkillBeautifulDescription']) + ','
        gearJson += ']'
        sysMsgs = [self.dbContext.read_record("Prompts", "key", "StartingAbilitiesCreation")["prompt"]]
        existingSkills = self.dbContext.read_record("Prompts", "key", "SkillsGivenByItems")["prompt"] + gearJson
        sysMsgs.append(existingSkills)
        sysMsgs.append(worldJson)
        abilities = self.SendMessage(sysMsgs, characterJson, 0)
        abilitiesDict = JsonManager.ExtractJson(abilities)

        for gear in gearDict:
            ability = {}
            ability['ShortDescription'] = gear['SkillShortDescription']
            ability['BeautifulDescription'] = gear['SkillBeautifulDescription']
            abilitiesDict.append(ability)

        newAbilitiesDict = self.__addSmthToJson('character_id', character["id"], abilitiesDict)

        for skill in newAbilitiesDict:
            self.dbContext.create_record("abilities", skill)
        
        return newAbilitiesDict


    def ChangeCharacterInfo(self, username, attribute, newValue):
        newInfo = {attribute: newValue}
        self.dbContext.update_latest_record('characters', 'username', username, newInfo)

        record = self.dbContext.read_latest_record('characters', 'username', username)
        result = Converter.DictToString(record)

        return result


    def __saveCompressedInformation(self, username, tableName, text, format):
        sysMsg = self.dbContext.read_record("Prompts", "key", format)["prompt"]
        answer = self.SendMessage(sysMsg, text, 0)
        ansDict = JsonManager.ExtractJson(answer)
        newansDict = self.__addSmthToJson('username', username, ansDict)
        self.dbContext.create_record(tableName, newansDict)
