Launch the World-Builder agent to generate a world definition file for a storybook set.

**Usage:** `/create-world <set-id>`

**Example:** `/create-world skyreach-friendship`

---

## Instructions

When this command is executed:

1. **Validate the storybook set exists:**
   - Check that `storysets/{set-id}/` directory exists
   - Check that `storysets/{set-id}/config.yaml` exists
   - If not, inform user they need to run `/create-storybook-set` first

2. **Read the agent definition:**
   - Read `.claude/agents/world-builder.md` to get the agent's instructions

3. **Launch the agent:**
   - Use the Task tool with `subagent_type="general-purpose"`
   - Pass the agent definition as the prompt
   - Add the specific set-id as a parameter
   - Use `model="opus"` (world-building is creative work)

4. **Prompt structure:**
   ```
   {CONTENT OF .claude/agents/world-builder.md}

   ---

   The storybook set ID is: {set-id}

   All file paths should use "storysets/{set-id}/" as the base.

   Begin by reading storysets/{set-id}/config.yaml to extract parameters.
   ```

5. **After agent completes:**
   - Show the user the agent's summary
   - Confirm the world.yaml file was created
   - Suggest next step: `/design-arcs {set-id}`
