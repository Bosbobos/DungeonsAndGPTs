import openai

class GptGamemaster:
    def __init__(self, apiKey, prompts, compressionFormats):
        self.apiKey = apiKey
        self.prompts = prompts
        self.compressionFormats = compressionFormats

    def SendMessage(self, systemMsgs: list, userMsg: str, temperature: float):
        client = openai.OpenAI(api_key=self.apiKey)
        
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

        chat_completion = client.chat.completions.create(
            messages=msgs,
            model="gpt-3.5-turbo",
            temperature=temperature
        )

        return chat_completion.choices[0].message.content
    
    def CompressDescription(self, description, outputFormat):

    
    def CreateWorld(self, setting):
        sysMsgs = [self.prompts["WorldCreation"], self.prompts["DescriptionGenerationInfo"]]
        answer = self.SendMessage(sysMsgs, setting, 1)
        return answer
        