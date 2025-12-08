Example of an inline agent without a separate agent definition file.

**Usage:** `/simple-example <character-code>`

---

When executed, launch a Task with this inline prompt:

"""
You are a Character Validator agent.

Your task: Read the character file at `characters/{character-code}-*.yaml` and validate it meets all quality standards.

Check:
1. All required fields are present (name, age, visual_description, etc.)
2. Visual description is detailed enough for image generation
3. Internal conflict relates to a courage theme
4. Story array has exactly 12 entries
5. Page filenames follow naming convention

Report:
- List of any issues found
- Suggestions for fixes
- Confirmation if character passes all checks

The character code is: {character-code}

Begin by finding and reading the character file.
"""

Replace {character-code} with the actual character code provided by the user.
