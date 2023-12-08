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
    
    def __addUsername(self, username, answer_json):
        return {'username': username, **answer_json}

    def CreateCharacter(self, username, introduction):
        sysMsg = self.dbContext.read_record("Prompts", "key", "CreateCharacter")["prompt"]
        answer = self.SendMessage(sysMsg, introduction, 0)
        ansJson = JsonManager.ExtractJson(answer)
        if ansJson['Race'] == "Unknown":
            ansJson['Race'] = "Human"
        newAnsJson = self.__addUsername(username, ansJson)
        self.dbContext.create_record("characters", newAnsJson)

        result = Converter.DictToString(newAnsJson)

        return result

    def CreateWorld(self, username, setting):
        sysMsg = self.dbContext.read_record("Prompts", "key", "WorldCreation")["prompt"]
        answer = self.SendMessage(sysMsg, setting, 1)
        self.__saveCompressedInformation(username, "World", answer, "CompressWorldInfo")
        return answer
        
    def __saveCompressedInformation(self, username, tableName, text, format):
        sysMsg = self.dbContext.read_record("Prompts", "key", format)["prompt"]
        answer = self.SendMessage(sysMsg, text, 0)
        ansJson = JsonManager.ExtractJson(answer)
        newAnsJson = self.__addUsername(username, ansJson)
        self.dbContext.create_record(tableName, newAnsJson)
