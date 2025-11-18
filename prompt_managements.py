import sqlite3
import json
from typing import List, Dict, Any, Optional

class PromptManager:
    def __init__(self, db_path: str = 'prompts.db'):
        self.db_path = db_path
        # Initialize database if it doesn't exist
        from db_setup import PromptDatabase
        PromptDatabase(db_path)

    def get_cefr_levels(self) -> List[str]:
        """Get all available CEFR levels"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT level_name FROM cefr_levels ORDER BY level_name')
            return [row[0] for row in cursor.fetchall()]

    def get_programs_by_level(self, level_name: str) -> List[Dict[str, Any]]:
        """Get all prompt programs for a specific CEFR level"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.name, p.description, p.prompt_template, p.tags, p.difficulty
                FROM prompt_programs p
                JOIN cefr_levels l ON p.cefr_level_id = l.id
                WHERE l.level_name = ?
                ORDER BY p.name
            ''', (level_name,))

            columns = [desc[0] for desc in cursor.description]
            programs = []
            for row in cursor.fetchall():
                program = dict(zip(columns, row))
                program['tags'] = json.loads(program['tags']) if program['tags'] else []
                programs.append(program)
            return programs

    def get_program_names_by_level(self, level_name: str) -> List[str]:
        """Get program names for a specific CEFR level (for UI dropdowns)"""
        programs = self.get_programs_by_level(level_name)
        return [p['name'] for p in programs]

    def get_prompt(
            self,
            program_name: str,
            variables: dict = None,
            strict: bool = True
    ) -> str:
        """
        Render a prompt by substituting variables.

        Args:
            program_name: Name of the prompt program.
            variables: Variables to override defaults.
            strict: If True, missing variables raise an error.

        Returns:
            Rendered prompt string.

        Raises:
            KeyError: If program name is invalid or variables are missing (strict mode).
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT prompt_template FROM prompt_programs WHERE name = ?
            ''', (program_name,))

            row = cursor.fetchone()
            if not row:
                raise KeyError(f"Prompt program '{program_name}' not found.")

            template = row[0]

        # Handle variable substitution
        if variables:
            try:
                return template.format(**variables)
            except KeyError as e:
                if not strict:
                    return template  # Return unformatted template on failure
                missing = e.args[0]
                raise KeyError(f"Missing variable: '{missing}' in prompt '{program_name}'.") from e

        return template

    def get_coach_prompt(self, level_name: str, variables: dict = None) -> str:
        """Get appropriate coach prompt for a CEFR level"""
        # Map levels to coach prompt names
        coach_mapping = {
            'A1': 'English Coach A1-A2',
            'A2': 'English Coach A1-A2',
            'B1': 'English Coach B1-B2',
            'B2': 'English Coach B1-B2',
            'C1': 'English Coach C1-C2',
            'C2': 'English Coach C1-C2'
        }

        coach_name = coach_mapping.get(level_name, 'English Coach A1-A2')
        return self.get_prompt(coach_name, variables)

    def get_default_program(self, level_name: str) -> Optional[str]:
        """Get the first program for a level as default"""
        programs = self.get_program_names_by_level(level_name)
        return programs[0] if programs else None

    def list_programs(self) -> List[str]:
        """Return names of all stored prompt programs."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name FROM prompt_programs ORDER BY name')
            return [row[0] for row in cursor.fetchall()]

    def get_program_info(self, program_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a program"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.name, p.description, l.level_name, p.tags, p.difficulty, p.version
                FROM prompt_programs p
                JOIN cefr_levels l ON p.cefr_level_id = l.id
                WHERE p.name = ?
            ''', (program_name,))

            row = cursor.fetchone()
            if row:
                return {
                    'name': row[0],
                    'description': row[1],
                    'level': row[2],
                    'tags': json.loads(row[3]) if row[3] else [],
                    'difficulty': row[4],
                    'version': row[5]
                }
            return None


# Initialize manager
pm = PromptManager()