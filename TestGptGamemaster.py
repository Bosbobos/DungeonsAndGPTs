import unittest
from unittest.mock import MagicMock, patch
from GptCore import GptGamemaster  # Replace YourModule with the actual module name

class TestGptGamemaster(unittest.TestCase):
    def setUp(self):
        # Mock the necessary dependencies or objects
        self.mock_openai = MagicMock()
        self.mock_db_context = MagicMock()

    def test_send_message(self):
        # Mock the OpenAI client and set expected values
        with patch("openai.OpenAI", return_value=self.mock_openai):
            self.mock_openai.chat.completions.create.return_value.choices[0].message.content = "Test Message"

            # Create an instance of GptGamemaster
            gamemaster = GptGamemaster(apiKey="your_api_key", dbContext=self.mock_db_context)

            # Test SendMessage method
            result = gamemaster.SendMessage(systemMsgs=["system message"], userMsg="user message", temperature=0.5)

            # Assert the result
            self.assertEqual(result, "Test Message")


    def test_create_world(self):
        expected = "{\"Name\":\"TestWorld\", \"MainFeatures\":\"TestFeatures\"}"
        # Mock dependencies and set expected values
        with patch("openai.OpenAI", return_value=self.mock_openai):
            self.mock_db_context.read_record.return_value = {"prompt": "Test Prompt"}
            self.mock_openai.chat.completions.create.return_value.choices[0].message.content = expected

            # Create an instance of GptGamemaster
            gamemaster = GptGamemaster(apiKey="your_api_key", dbContext=self.mock_db_context)

            # Test CreateWorld method
            result = gamemaster.CreateWorld(username="test_user", setting="Test Setting")

            # Assert the result
            self.assertEqual(result, expected)


    def test_create_character(self):
        # Mock dependencies and set expected values
        with patch("openai.OpenAI", return_value=self.mock_openai):
            self.mock_db_context.read_record.return_value = {"prompt": "Test Prompt"}
            self.mock_openai.chat.completions.create.return_value.choices[0].message.content = "Character Created"

            # Create an instance of GptGamemaster
            gamemaster = GptGamemaster(apiKey="your_api_key", dbContext=self.mock_db_context)

            # Test CreateCharacter method
            result = gamemaster.CreateCharacter(username="test_user", introduction="Test Introduction")

            # Assert the result
            self.assertEqual(result, "Character Created")


    def test_create_starting_gear_and_abilities(self):
        expectedGear = '[{""id": 1, "character_id": 1,Name":"Sword","Skill":"Cut","SkillShortDescription":"Sharp and deadly","SkillBeautifulDescription":"Test long description"}]'
        expectedAbilities = '[]'
        with patch("openai.OpenAI", return_value=self.mock_openai):
            self.mock_db_context.read_record.side_effect = [
                {"prompt": "Gear Prompt"},
                {"id": 1, "username": "test_user"},
                { "Name":"Sword","Skill":"","SkillShortDescription":"Sharp and deadly","SkillBeautifulDescription":"Test long description"}
            ]
            self.mock_openai.chat.completions.create.return_value.choices[0].message.content = expectedGear

            # Create an instance of GptGamemaster
            gamemaster = GptGamemaster(apiKey="your_api_key", dbContext=self.mock_db_context)

            # Test CreateStaringGearAndAbilities method
            result = gamemaster.CreateStaringGearAndAbilities(username="test_user")

            # Assert the result
            self.assertEqual(result, [["Item: Sword\n"], ['"Name":"StrongAbility","ShortDescription":"Sharp and deadly","BeautifulDescription":"Test long description"']])

    # Add more test methods for other functions in GptGamemaster

if __name__ == '__main__':
    unittest.main()
