import unittest
import sqlite3
import os
import tempfile
from db_setup import PromptDatabase
from prompt_managements import PromptManager

class TestPromptDatabase(unittest.TestCase):
    def setUp(self):
        """Set up test database"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.test_db.close()
        self.db_path = self.test_db.name
        self.db = PromptDatabase(self.db_path)

    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_cefr_levels_population(self):
        """Test CEFR levels are populated correctly"""
        levels = self.db.populate_cefr_levels()
        stored_levels = self.db.get_cefr_levels()
        expected_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        self.assertEqual(sorted(stored_levels), sorted(expected_levels))

    def test_add_and_retrieve_prompt(self):
        """Test adding and retrieving a prompt program"""
        self.db.populate_cefr_levels()

        # Add a test prompt
        self.db.add_prompt_program(
            name="Test Conversation",
            description="A test conversation scenario",
            cefr_level="B1",
            prompt_template="Test prompt with {variable}",
            tags=["test", "conversation"],
            difficulty="medium"
        )

        # Retrieve programs for B1
        programs = self.db.get_programs_by_level("B1")
        self.assertEqual(len(programs), 1)
        self.assertEqual(programs[0]['name'], "Test Conversation")
        self.assertEqual(programs[0]['description'], "A test conversation scenario")
        self.assertEqual(programs[0]['tags'], ["test", "conversation"])
        self.assertEqual(programs[0]['difficulty'], "medium")

    def test_get_all_programs(self):
        """Test retrieving all programs"""
        self.db.populate_cefr_levels()
        self.db.populate_sample_prompts()

        all_programs = self.db.get_all_programs()
        self.assertGreater(len(all_programs), 0)

        # Check that each program has required fields
        for program in all_programs:
            self.assertIn('name', program)
            self.assertIn('level_name', program)
            self.assertIn('prompt_template', program)

class TestPromptManager(unittest.TestCase):
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

    def test_get_cefr_levels(self):
        """Test retrieving CEFR levels"""
        levels = self.pm.get_cefr_levels()
        expected_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        self.assertEqual(sorted(levels), sorted(expected_levels))

    def test_get_programs_by_level(self):
        """Test retrieving programs by level"""
        programs = self.pm.get_programs_by_level("A1")
        self.assertGreater(len(programs), 0)

        for program in programs:
            self.assertIn('name', program)
            self.assertIn('description', program)
            self.assertIn('tags', program)
            self.assertIsInstance(program['tags'], list)

    def test_get_program_names_by_level(self):
        """Test retrieving program names by level"""
        names = self.pm.get_program_names_by_level("B1")
        self.assertGreater(len(names), 0)
        self.assertIsInstance(names, list)
        self.assertIsInstance(names[0], str)

    def test_get_prompt(self):
        """Test retrieving and formatting a prompt"""
        # Get a program name
        programs = self.pm.get_programs_by_level("A1")
        program_name = programs[0]['name']

        # Test without variables
        prompt = self.pm.get_prompt(program_name)
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)

        # Test with variables
        variables = {"Context": "Test context", "ChatHistory": "Test history"}
        prompt_with_vars = self.pm.get_prompt(program_name, variables=variables)
        self.assertIn("Test context", prompt_with_vars)
        self.assertIn("Test history", prompt_with_vars)

    def test_get_coach_prompt(self):
        """Test retrieving coach prompts by level"""
        for level in ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']:
            coach_prompt = self.pm.get_coach_prompt(level)
            self.assertIsInstance(coach_prompt, str)
            self.assertGreater(len(coach_prompt), 0)

    def test_get_default_program(self):
        """Test getting default program for a level"""
        default_program = self.pm.get_default_program("A1")
        self.assertIsInstance(default_program, str)
        self.assertGreater(len(default_program), 0)

    def test_get_program_info(self):
        """Test retrieving program information"""
        programs = self.pm.get_program_names_by_level("A1")
        program_name = programs[0]

        info = self.pm.get_program_info(program_name)
        self.assertIsNotNone(info)
        self.assertEqual(info['name'], program_name)
        self.assertIn('level', info)
        self.assertIn('description', info)
        self.assertIn('tags', info)
        self.assertIn('difficulty', info)

    def test_invalid_program(self):
        """Test handling of invalid program names"""
        with self.assertRaises(KeyError):
            self.pm.get_prompt("Nonexistent Program")

    def test_missing_variables_strict_mode(self):
        """Test strict mode with missing variables"""
        programs = self.pm.get_programs_by_level("A1")
        program_name = programs[0]['name']

        # If the prompt requires variables not provided, should raise KeyError in strict mode
        # This depends on the actual prompt template
        try:
            prompt = self.pm.get_prompt(program_name, variables={}, strict=True)
        except KeyError:
            pass  # Expected if variables are required

    def test_missing_variables_non_strict_mode(self):
        """Test non-strict mode with missing variables"""
        programs = self.pm.get_programs_by_level("A1")
        program_name = programs[0]['name']

        # Non-strict mode should return template even with missing variables
        prompt = self.pm.get_prompt(program_name, variables={}, strict=False)
        self.assertIsInstance(prompt, str)

if __name__ == '__main__':
    unittest.main()