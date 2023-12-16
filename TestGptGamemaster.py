import unittest
from unittest.mock import MagicMock, patch, ANY
from GptCore import GptGamemaster


class TestGptGamemaster(unittest.TestCase):

    @patch('openai.OpenAI')
    def test_SendMessage(self, mock_openai):
        # Mocking openai.OpenAI
        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[0].message.content = "MockedResponse"

        gamemaster = GptGamemaster(apiKey="your_api_key", dbContext=None)
        result = gamemaster.SendMessage(
            systemMsgs=["system_msg"], userMsg="user_msg", temperature=1.0)

        mock_openai.assert_called_once_with(api_key="your_api_key")
        instance.chat.completions.create.assert_called_once_with(
            messages=[
                {"role": "system", "content": "system_msg"},
                {"role": "user", "content": "user_msg"}
            ],
            model="gpt-3.5-turbo",
            temperature=1.0
        )
        self.assertEqual(result, "MockedResponse")

    @patch('openai.OpenAI')
    def test_CreateWorld(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_record.return_value = {"prompt": "MockedPrompt"}
        mock_db_context.create_record.return_value = None

        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[
            0].message.content = '{"content": "MockedResponse"}'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)
        result = gamemaster.CreateWorld(
            username="test_user", setting="test_setting")

        mock_db_context.read_record.assert_called_with(
            "Prompts", "key", 'CompressWorldInfo')
        mock_db_context.create_record.assert_called_once_with(
            "World", {"username": "test_user", "content": "MockedResponse"})
        self.assertEqual(result, '{"content": "MockedResponse"}')

    @patch('openai.OpenAI')
    def test_CreateCharacter(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_record.return_value = {"prompt": "MockedPrompt"}
        mock_db_context.create_record.return_value = None

        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[
            0].message.content = '{"Race": "human"}'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)
        result = gamemaster.CreateCharacter(
            username="test_user", introduction="test_intro")

        mock_db_context.read_record.assert_called_once_with(
            "Prompts", "key", "CreateCharacter")
        mock_db_context.create_record.assert_called_once_with(
            "characters", {"username": "test_user", "Race": "human"})
        self.assertEqual(result, 'Race: human')

    @patch('openai.OpenAI')
    def test_CreateStaringGearAndAbilities(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_record.return_value = {"prompt": "MockedPrompt"}
        mock_db_context.read_latest_record.return_value = {
            "id": 1, "username": "test_user"}
        mock_db_context.create_record.return_value = None

        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[0].message.content = '[{"Name": "Item1", "Skill": "Skill1", "SkillShortDescription":"SkillShortDescription1", "SkillBeautifulDescription":"SkillBeautifulDescription1"}, {"Name": "Item2", "Skill": "Skill1", "SkillShortDescription":"SkillShortDescription1", "SkillBeautifulDescription":"SkillBeautifulDescription1"}]'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)
        result = gamemaster.CreateStaringGearAndAbilities(username="test_user")

        mock_db_context.read_record.assert_called_with(
            "Prompts", "key", "SkillsGivenByItems")
        mock_db_context.read_latest_record.assert_called_with(
            'characters', "username", "test_user")
        self.assertTrue(result)  # Adjust based on your expected output

    @patch('openai.OpenAI')
    def test_MakeATurn(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_latest_record.return_value = {
            "id": 0, "turn": 1,  "main_previous_events": "previous_actions"}

        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[
            0].message.content = '{"Main_Previous_Events":["All of them","None"],"Possible_Actions": []}'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)
        result = gamemaster.MakeATurn(
            username="test_user", action="test_action", prompt="test_prompt")

        mock_db_context.read_latest_record.assert_called()
        instance.chat.completions.create.assert_called()

        self.assertTrue(result)

    @patch('openai.OpenAI')
    def test_CreateWorld_Exception(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_record.return_value = {"prompt": "MockedPrompt"}
        mock_db_context.create_record.side_effect = Exception("Database error")

        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[
            0].message.content = '{"content": "MockedResponse"}'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)

        # Use assertRaises to check for the expected exception
        with self.assertRaises(Exception) as context:
            gamemaster.CreateWorld(username="test_user",
                                   setting="test_setting")

        # Optionally, check the exception message or other details
        self.assertEqual(str(context.exception), "Database error")

    @patch('openai.OpenAI')
    def test_CreateCharacter_ValueError(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_record.return_value = {"prompt": "MockedPrompt"}
        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[
            0].message.content = 'Wow, cool character'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)

        # Use assertRaises to check for the expected ValueError
        with self.assertRaises(ValueError) as context:
            gamemaster.CreateCharacter(
                username="test_user", introduction="test_intro")

        # Optionally, check the exception message or other details
        self.assertEqual(str(context.exception),
                         "No JSON found in the input string")

    @patch('openai.OpenAI')
    def test_MakeATurn_DatabaseError(self, mock_openai):
        mock_db_context = MagicMock()
        mock_db_context.read_latest_record.side_effect = Exception(
            "Database error")

        instance = mock_openai.return_value
        instance.chat.completions.create.return_value.choices[
            0].message.content = '{"Main_Previous_Events":["All of them","None"],"Possible_Actions": []}'

        gamemaster = GptGamemaster(
            apiKey="your_api_key", dbContext=mock_db_context)

        # Use assertRaises to check for the expected exception
        with self.assertRaises(Exception) as context:
            gamemaster.MakeATurn(username="test_user",
                                 action="test_action", prompt="test_prompt")

        # Optionally, check the exception message or other details
        self.assertEqual(str(context.exception), "Database error")


if __name__ == '__main__':
    unittest.main()
