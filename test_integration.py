import unittest
import tempfile
import os
from unittest.mock import Mock, patch
from db_setup import PromptDatabase
from prompt_managements import PromptManager
from main import transcribe_audio, generate_response

class TestIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test database and manager"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name

        # Initialize database with sample data
        db = PromptDatabase(self.db_path)
        db.populate_cefr_levels()
        db.populate_sample_prompts()

        self.pm = PromptManager(self.db_path)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    @patch('main.whisper.load_model')
    @patch('main.whisper.transcribe')
    def test_transcribe_audio_integration(self, mock_transcribe, mock_load_model):
        """Test audio transcription integration"""
        # Mock the whisper model and transcription
        mock_model = Mock()
        mock_load_model.return_value = mock_model
        mock_transcribe.return_value = {"text": "Hello, how are you?"}

        # Create a dummy audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            temp_audio.write(b'dummy audio data')
            temp_audio_path = temp_audio.name

        try:
            # Test transcription
            result = transcribe_audio(temp_audio_path)
            self.assertEqual(result, "Hello, how are you?")

            # Verify model was loaded and transcription was called
            mock_load_model.assert_called_once_with("base.en")
            mock_transcribe.assert_called_once()
        finally:
            if os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)

    @patch('main.init_chat_model')
    def test_generate_response_integration(self, mock_init_model):
        """Test response generation integration"""
        # Mock the chat model
        mock_model = Mock()
        mock_model.invoke.return_value.content = "This is a test response."
        mock_init_model.return_value = mock_model

        # Test response generation
        with patch('os.environ', {'GROQ_API_KEY': 'test_key'}):
            response = generate_response("Test prompt", "test-model", "test-key")

        self.assertEqual(response, "This is a test response.")
        mock_init_model.assert_called_once_with("test-model", model_provider="groq")
        mock_model.invoke.assert_called_once_with("Test prompt")

    def test_full_conversation_flow(self):
        """Test the full conversation flow logic"""
        # Select a program
        programs = self.pm.get_programs_by_level("A1")
        self.assertGreater(len(programs), 0)

        program_name = programs[0]['name']

        # Simulate conversation variables
        chat_history = "User: Hello\nAssistant: Hi there!"
        context = "Meeting at a café"

        variables = {
            "Context": context,
            "ChatHistory": chat_history
        }

        # Get the prompt
        prompt = self.pm.get_prompt(program_name, variables=variables)
        self.assertIsInstance(prompt, str)
        self.assertIn(context, prompt)
        self.assertIn(chat_history, prompt)

        # Verify prompt structure (should contain the template content)
        self.assertGreater(len(prompt), 50)  # Reasonable minimum length

    def test_level_progression(self):
        """Test that different levels have appropriate programs"""
        levels = self.pm.get_cefr_levels()

        for level in levels:
            programs = self.pm.get_programs_by_level(level)
            self.assertGreater(len(programs), 0, f"No programs found for level {level}")

            # Check that programs have required metadata
            for program in programs:
                self.assertIn('difficulty', program)
                self.assertIn('tags', program)
                self.assertIsInstance(program['tags'], list)

    def test_coach_prompt_level_appropriateness(self):
        """Test that coach prompts are level-appropriate"""
        level_mappings = {
            'A1': 'English Coach A1-A2',
            'A2': 'English Coach A1-A2',
            'B1': 'English Coach B1-B2',
            'B2': 'English Coach B1-B2',
            'C1': 'English Coach C1-C2',
            'C2': 'English Coach C1-C2'
        }

        for level, expected_coach in level_mappings.items():
            coach_prompt = self.pm.get_coach_prompt(level)
            self.assertIsInstance(coach_prompt, str)
            self.assertGreater(len(coach_prompt), 0)

            # Verify the coach prompt contains level-appropriate content
            if 'A1-A2' in expected_coach:
                self.assertIn('beginner', coach_prompt.lower())
            elif 'B1-B2' in expected_coach:
                self.assertIn('intermediate', coach_prompt.lower())
            elif 'C1-C2' in expected_coach:
                self.assertIn('advanced', coach_prompt.lower())

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test invalid level
        programs = self.pm.get_programs_by_level("InvalidLevel")
        self.assertEqual(len(programs), 0)

        # Test invalid program name
        with self.assertRaises(KeyError):
            self.pm.get_prompt("Invalid Program Name")

        # Test program info for invalid program
        info = self.pm.get_program_info("Invalid Program")
        self.assertIsNone(info)

    def test_database_persistence(self):
        """Test that data persists across manager instances"""
        # Create first manager and add a program
        db = PromptDatabase(self.db_path)
        db.add_prompt_program(
            "Persistence Test",
            "Testing data persistence",
            "B1",
            "Test template",
            ["test"]
        )

        # Create second manager instance
        pm2 = PromptManager(self.db_path)

        # Verify program exists in second instance
        programs = pm2.get_programs_by_level("B1")
        program_names = [p['name'] for p in programs]
        self.assertIn("Persistence Test", program_names)

    def test_prompt_template_formatting(self):
        """Test that prompt templates are correctly formatted with variables"""
        # Get a program that uses variables
        programs = self.pm.get_programs_by_level("A1")
        program_name = programs[0]['name']

        # Test with empty variables
        prompt_no_vars = self.pm.get_prompt(program_name, strict=False)
        self.assertIsInstance(prompt_no_vars, str)

        # Test with some variables
        variables = {"Context": "Test context"}
        prompt_with_vars = self.pm.get_prompt(program_name, variables=variables, strict=False)
        if "{Context}" in prompt_no_vars:
            self.assertIn("Test context", prompt_with_vars)
        else:
            # If Context not in template, prompt should be unchanged
            self.assertEqual(prompt_no_vars, prompt_with_vars)

if __name__ == '__main__':
    unittest.main()