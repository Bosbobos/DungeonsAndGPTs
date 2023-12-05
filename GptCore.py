import openai

class GptGamemaster:
    def __init__(self, apiKey, prompts):
        self.apiKey = apiKey
        self.prompts = prompts

    def SendMessage(self, systemMsg, userMsg, temperature):
        client = openai.OpenAI(api_key=self.apiKey)
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": systemMsg
                },
                {
                    "role": "user",
                    "content": userMsg,
                }
            ],
            model="gpt-3.5-turbo",
            temperature=temperature
        )

        return chat_completion.choices[0].message.content
    
    def CreateWorld(self, setting):
        sysMsg = self.prompts["WorldCreation"] + ' ' + self.prompts["DescriptionGenerationInfo"]
        answer = self.SendMessage(sysMsg, setting, 1)
        return answer
        