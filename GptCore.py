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
    
    def __addSmthToDict(self, name, content, json):
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
        newansDict = self.__addSmthToDict('username', username, ansDict)
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
        newansDict = self.__addSmthToDict('character_id', character["id"], gearDict)

        for item in newansDict:
            self.dbContext.create_record("items", item)

        gearResult = [Converter.DictToString({'Item': item['Name']}) for item in gearDict]
        for i in range(len(gearResult)-1):
            gearResult[i] += '\n'

        abilities = self.__CreateStartingAbilities(worldJson, character, gearDict)
        abilitiesNewDict = [{key: value for key, value in ability.items() if key != 'ShortDescription' and key != 'character_id'} for ability in abilities]
        abilitiesResult = [Converter.DictToString(abilitiesDict) for abilitiesDict in abilitiesNewDict]
        for i in range(len(abilitiesResult)-1):
            abilitiesResult[i] += '\n'

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
            ability['Name'] = gear['Skill']
            ability['ShortDescription'] = gear['SkillShortDescription']
            ability['BeautifulDescription'] = gear['SkillBeautifulDescription']
            abilitiesDict.append(ability)

        newAbilitiesDict = self.__addSmthToDict('character_id', character["id"], abilitiesDict)

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
        newansDict = self.__addSmthToDict('username', username, ansDict)
        self.dbContext.create_record(tableName, newansDict)


    def __saveCompressedInformationAboutATurn(self, username, turnInfo,  worldJson, characterJson, abilitiesJson, previousActions, turn):
        sysMsgs = [self.dbContext.read_record("Prompts", "key", "CompressTurnInfo")["prompt"]]
        world = 'Here is the information about the world in which the campaign is set in ' + worldJson
        character = 'Here is the information about the character who performed the turn ' + characterJson
        abilities = 'Here are the abilities the character has ' + abilitiesJson
        actions = 'Here are the actions the character has previously performed. DO NOT UNDER ANY CIRCUMSTANCES REPEAT THEM IN THE "previousActions" OF THE NEW JSON' + previousActions
        sysMsgs += [world,character,abilities,actions]
        
        answer = self.SendMessage(sysMsgs, turnInfo, 0)
        if '"Possible_Actions":[]' in answer:
            sysMsgs[0] = self.dbContext.read_record("Prompts", "key", "GeneratePossibleActions")["prompt"]
            actions = self.SendMessage(sysMsgs, turnInfo, 0)
            answer = answer.replace('"Possible_Actions":[]', actions.replace('{','').replace('}',''))
        info = JsonManager.ExtractJson(answer)
        events = ''
        if isinstance(info['Main_Previous_Events'], list):
            for x in info['Main_Previous_Events']:
                events += x + ' '
        if len(events)>400:
            prompt = self.dbContext.read_record("Prompts", "key", "CompressTurnInfoDescription")["prompt"]
            desc = self.SendMessage(prompt, events, 0)
            info['Main_Previous_Events'] = desc
        info['Main_Previous_Events'] = previousActions + ' ' + events
        infoDict = self.__addSmthToDict('turn', turn+1, info)        
        newInfoDict = self.__addSmthToDict('username', username, infoDict)
        self.dbContext.update_latest_record('Character_State', 'username', username, newInfoDict)

        return info['Possible_Actions']

 
    def StartCampaign(self, username):
        sysMsgs = [self.dbContext.read_record("Prompts", "key", "StartCampaign")["prompt"]]
        worldInfo = self.dbContext.read_latest_record("world", "username", username)
        character = self.dbContext.read_latest_record("characters", "username", username)
        worldJson = Converter.FilteredDictToJson(worldInfo, ['id', 'username'])
        characterJson = Converter.FilteredDictToJson(character, ['id', 'username'])
        world = 'Here is some information about the world where the campaign will be set in ' + worldJson
        sysMsgs.append(world)

        CampaignStart = self.SendMessage(sysMsgs, characterJson, 1)

        abilities = self.dbContext.read_all_records("abilities", "character_id", character['id'])
        abilitiesJson = ''
        for ability in abilities:
            abilitiesJson += Converter.FilteredDictToJson(ability, ['id', 'character_id', 'beautifuldescription'])

        possibleActions = self.__saveCompressedInformationAboutATurn(username, CampaignStart, worldJson, characterJson, abilitiesJson, '', 0)

        return [CampaignStart, possibleActions]
    

    def MakeATurn(self, username, action, prompt):
        worldInfo = self.dbContext.read_latest_record("world", "username", username)
        character = self.dbContext.read_latest_record("characters", "username", username)
        worldJson = Converter.FilteredDictToJson(worldInfo, ['id', 'username'])
        characterJson = Converter.FilteredDictToJson(character, ['id', 'username'])

        state = self.dbContext.read_latest_record("character_state", "username", username)
        turn = state['turn']
        previousActions = state['main_previous_events']

        abilities = self.dbContext.read_all_records("abilities", "character_id", character['id'])
        abilitiesJson = ''
        for ability in abilities:
            abilitiesJson += Converter.FilteredDictToJson(ability, ['id', 'character_id', 'beautifuldescription'])

        worldStr = 'Here is the information about the world in which the campaign is set in ' + worldJson
        characterStr = 'Here is the information about the character who performed the turn ' + characterJson
        abilitiesStr = 'Here are the abilities the character has ' + abilitiesJson
        prevActionsStr = 'Here is a short summary of previous turns' + previousActions

        sysMsgs = [prompt]
        sysMsgs += [worldStr, characterStr, abilitiesStr, prevActionsStr]

        TurnDescription = self.SendMessage(sysMsgs, action, 1)

        possibleActions = self.__saveCompressedInformationAboutATurn(username, TurnDescription, worldJson, characterJson, abilitiesJson, previousActions, turn)

        return [TurnDescription, possibleActions]


    def MakeExplorationPlayerTurn(self, username, action):
        state = self.dbContext.read_latest_record("character_state", "username", username)
        turn = state['turn']
        prompt = self.dbContext.read_record("Prompts", "key", "DescribeExploration")["prompt"].replace('TURNNUMBER', str(turn)).replace('TOTALTURNS', '10')

        return self.MakeATurn(username, action, prompt)
    

    def StartFinalFight(self, username, interruptedAction):
        prompt = self.dbContext.read_record("Prompts", "key", "StartFinalFight")["prompt"]

        return self.MakeATurn(username, interruptedAction, prompt)
    

    def FinishTheCampaign(self, username):
        state = self.dbContext.read_latest_record("character_state", "username", username)
        previousActions = state['main_previous_events']

        prompt = self.dbContext.read_record("Prompts", "key", "FinishTheCampaign")["prompt"]

        return self.MakeATurn(username, '', prompt)
    