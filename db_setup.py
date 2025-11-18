import sqlite3
import json
from typing import List, Dict, Any

class PromptDatabase:
    def __init__(self, db_path: str = 'prompts.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Create CEFR levels table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cefr_levels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level_name TEXT UNIQUE NOT NULL,
                    description TEXT                    
                )
            ''')

            # Create prompt programs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS prompt_programs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    cefr_level_id INTEGER NOT NULL,
                    prompt_template TEXT NOT NULL,
                    tags TEXT,  -- JSON array of tags
                    difficulty TEXT DEFAULT 'medium',
                    version INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (cefr_level_id) REFERENCES cefr_levels(id)
                )
            ''')

            # Create index for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_cefr_level ON prompt_programs(cefr_level_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_program_name ON prompt_programs(name)')

            conn.commit()

    def populate_cefr_levels(self):
        """Populate CEFR levels A1-C2"""
        levels = [
            ('A1', 'Beginner'),
            ('A2', 'Elementary'),
            ('B1', 'Intermediate'),
            ('B2', 'Upper Intermediate'),
            ('C1', 'Advanced'),
            ('C2', 'Proficient')
        ]

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany(
                'INSERT OR IGNORE INTO cefr_levels (level_name, description) VALUES (?, ?)',
                levels
            )
            conn.commit()

    def add_prompt_program(self, name: str, description: str, cefr_level: str,
                          prompt_template: str, tags: List[str] = None,
                          difficulty: str = 'medium'):
        """Add a new prompt program"""
        if tags is None:
            tags = []

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get CEFR level ID
            cursor.execute('SELECT id FROM cefr_levels WHERE level_name = ?', (cefr_level,))
            level_row = cursor.fetchone()
            if not level_row:
                raise ValueError(f"CEFR level {cefr_level} not found")

            level_id = level_row[0]

            # Insert prompt program
            cursor.execute('''
                INSERT INTO prompt_programs
                (name, description, cefr_level_id, prompt_template, tags, difficulty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, level_id, prompt_template, json.dumps(tags), difficulty))

            conn.commit()

    def get_all_programs(self) -> List[Dict[str, Any]]:
        """Get all prompt programs with CEFR level info"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.name, p.description, l.level_name, p.prompt_template,
                       p.tags, p.difficulty, p.version, p.created_at, p.updated_at
                FROM prompt_programs p
                JOIN cefr_levels l ON p.cefr_level_id = l.id
                ORDER BY l.level_name, p.name
            ''')

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def populate_sample_prompts(self):
        """Populate database with sample prompts for each CEFR level"""

        # A1 Beginner prompts
        self.add_prompt_program(
            name="Greetings and Introductions",
            description="Basic greetings and self-introduction",
            cefr_level="A1",
            prompt_template="""# Basic Conversation Practice

## Your Mission
You are a friendly person meeting someone new. Respond naturally and simply.

## Conversation Style
- Use short, simple sentences (3-5 words)
- Speak slowly and clearly
- Ask basic questions about name, country, job

## Context
You are at a language exchange meeting. The other person is learning English.

## Conversation History
{ChatHistory}

You:""",
            tags=["greetings", "introductions", "basic"],
            difficulty="easy"
        )

        # A2 Elementary prompts
        self.add_prompt_program(
            name="Ordering Food",
            description="Ordering at a café or restaurant",
            cefr_level="A2",
            prompt_template="""# Café Conversation

## Your Mission
You are a café server. Help customers order food and drinks.

## Conversation Style
- Use simple present tense
- Ask about preferences (hot/cold, size, additions)
- Confirm orders clearly

## Context
You work at a small local café. Customers come for coffee and simple meals.

## Conversation History
{ChatHistory}

You:""",
            tags=["food", "ordering", "daily-life"],
            difficulty="easy"
        )

        # B1 Intermediate prompts
        self.add_prompt_program(
            name="Airport Check-in",
            description="Checking in at airport and asking for help",
            cefr_level="B1",
            prompt_template="""# Airport Check-in Roleplay

## Your Mission
You are an airline check-in agent at a busy airport. Help passengers with their luggage and boarding passes.

## Conversation Style
- Use present continuous for current activities
- Give clear instructions and information
- Handle problems politely

## Context
During peak travel season at a major international airport. Passengers are stressed about flights.

## Conversation History
{ChatHistory}

You:""",
            tags=["travel", "vocabulary", "fluency"],
            difficulty="medium"
        )

        # B2 Upper Intermediate prompts
        self.add_prompt_program(
            name="Job Interview",
            description="Professional job interview conversation",
            cefr_level="B2",
            prompt_template="""# Job Interview Practice

## Your Mission
You are a hiring manager conducting interviews. Ask relevant questions about experience, skills, and motivation.

## Conversation Style
- Use formal language and professional vocabulary
- Ask follow-up questions based on answers
- Give constructive feedback

## Context
You are interviewing candidates for a position in your company. You want to find the best person for the job.

## Conversation History
{ChatHistory}

You:""",
            tags=["professional", "vocabulary", "grammar"],
            difficulty="medium"
        )

        # C1 Advanced prompts
        self.add_prompt_program(
            name="Academic Discussion",
            description="Discussing complex academic topics",
            cefr_level="C1",
            prompt_template="""# Academic Seminar Discussion

## Your Mission
You are a university professor leading a seminar. Encourage deep analysis and critical thinking.

## Conversation Style
- Use complex sentence structures and academic vocabulary
- Reference theories and concepts
- Challenge ideas respectfully

## Context
You are in a graduate-level seminar discussing current research in your field.

## Conversation History
{ChatHistory}

You:""",
            tags=["academic", "vocabulary", "critical-thinking"],
            difficulty="hard"
        )

        # C2 Proficient prompts
        self.add_prompt_program(
            name="Debate on Global Issues",
            description="Debating complex global topics with nuance",
            cefr_level="C2",
            prompt_template="""# Expert Debate

## Your Mission
You are an expert debating complex global issues. Present well-reasoned arguments with evidence.

## Conversation Style
- Use sophisticated vocabulary and idiomatic expressions
- Make nuanced distinctions and concessions
- Reference current events and historical context

## Context
You are participating in a high-level policy discussion with other experts.

## Conversation History
{ChatHistory}

You:""",
            tags=["debate", "politics", "advanced-vocabulary"],
            difficulty="hard"
        )

        # Coach prompts for different levels
        self.add_prompt_program(
            name="English Coach A1-A2",
            description="Feedback for beginner learners",
            cefr_level="A1",
            prompt_template="""You're an ESL specialist grading beginner English learners. Provide:
1) CEFR level assessment (A1/A2)
2) Simple error corrections
3) Encouraging feedback with 1-2 improvement tips

**Context**: {context}
**Conversation**:
{conversation}

**Analysis**:
- Focus on basic grammar and vocabulary
- Be encouraging and positive
- Suggest simple practice activities""",
            tags=["coaching", "feedback"],
            difficulty="easy"
        )

        self.add_prompt_program(
            name="English Coach B1-B2",
            description="Feedback for intermediate learners",
            cefr_level="B1",
            prompt_template="""You're an ESL specialist grading intermediate English learners. Provide:
1) CEFR level assessment (B1/B2)
2) Grammar and vocabulary corrections
3) Detailed feedback with strengths and areas for improvement

**Context**: {context}
**Conversation**:
{conversation}

**Analysis**:
- Evaluate fluency and accuracy
- Comment on complex structures used
- Suggest targeted practice exercises""",
            tags=["coaching", "feedback"],
            difficulty="medium"
        )

        self.add_prompt_program(
            name="English Coach C1-C2",
            description="Feedback for advanced learners",
            cefr_level="C1",
            prompt_template="""You're an ESL specialist grading advanced English learners. Provide:
1) CEFR level assessment (C1/C2)
2) Subtle error corrections and style suggestions
3) Comprehensive feedback on sophistication and nuance

**Context**: {context}
**Conversation**:
{conversation}

**Analysis**:
- Evaluate idiomatic usage and register
- Comment on discourse coherence
- Suggest advanced practice for near-native fluency""",
            tags=["coaching", "feedback"],
            difficulty="hard"
        )

if __name__ == "__main__":
    db = PromptDatabase()
    db.populate_cefr_levels()
    db.populate_sample_prompts()
    print("Database initialized and populated with sample prompts.")
    print(f"Total programs: {len(db.get_all_programs())}")