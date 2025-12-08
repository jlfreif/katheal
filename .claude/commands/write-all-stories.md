Launch parallel agents to write all character stories simultaneously.

**Usage:** `/write-all-stories <set-id>`

---

## Instructions

When executed:

1. **Read configuration** to determine number of characters
   - Read `storysets/{set-id}/config.yaml`
   - Count characters in the `characters` array

2. **Launch parallel agents** (one per character)

   **IMPORTANT:** Use a single message with multiple Task invocations to run in parallel!

   For each character, launch a Task with:
   - subagent_type: "general-purpose"
   - model: "sonnet" (solo spreads are template-driven, use cheaper model)
   - prompt:
     ```
     You are a Story Writer agent for character: {character-name}

     Read:
     - storysets/{set-id}/characters/{char-id}-{char-name}.yaml
     - storysets/{set-id}/world.yaml
     - engine/templates/page-example.yaml

     Write all SOLO spreads for this character (skip shared node spreads).

     For each solo spread:
     1. Create pages/{char-id}-{spread-number}.yaml
     2. Follow the beat from the character's story array
     3. Include proper scene structure (left/right pages)
     4. Match writing style from config
     5. Ensure transitions between spreads

     Return: Summary of spreads created and any issues encountered.
     ```

3. **Also launch a node writer** (in the same parallel batch)
   - model: "opus" (nodes are harder, use better model)
   - Writes all meeting/mirrored/resonant node scenes

4. **Wait for all agents to complete**

5. **Launch Consistency Guardian** (after others finish)
   - Reviews all pages for consistency
   - Checks cross-character elements
   - Returns validation report

## Example Execution

For a 3-character set:
```
Send ONE message with 4 Task invocations:
- Task 1: Write Aria's solo spreads (Sonnet)
- Task 2: Write Zephyr's solo spreads (Sonnet)
- Task 3: Write Moss's solo spreads (Sonnet)
- Task 4: Write all node scenes (Opus)

[Wait for all to complete]

Then send another message with 1 Task:
- Task 5: Validate consistency (Sonnet)
```

This runs Tasks 1-4 in parallel, then Task 5 after.
