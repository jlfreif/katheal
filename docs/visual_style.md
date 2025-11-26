# Visual Style Guide for Kathaél Illustrations

## Overview
All illustrations should maintain consistent style across all books while allowing each character's aesthetic to shine through.

## Reference Images
- Character reference images are stored in `ref-images/` directory
- Organized by character code (e.g., `no-*.jpg` for Noah, `el-*.jpg` for Elise)
- Image generation automatically references character-specific images
- Update reference images as style evolves

## General Style
- **Medium**: Digital illustration, painterly style
- **Age Group**: Appeal to 9-12 year olds
- **Tone**: Warm, inviting, slightly magical but grounded
- **Detail Level**: Rich enough to explore, simple enough to read clearly

## Character Consistency
- Use reference images for facial features, clothing, proportions
- Hair color, style, and general appearance must match across all pages
- Character expressions should be natural and age-appropriate
- Body language should match the text and action

## The Heart Crystal
- Massive crystalline structure, tall as a building
- 6 visible facets when shown in full
- Transparent/translucent with internal light
- Cracks should be visible and dramatic when damaged
- Light refracts through facets in rainbow colors
- Can show different facets glowing different colors for different aspects
- Each facet corresponds to a different character/aspect:
  - Noah's facet = story-facet (words, narratives, books)
  - Elise's facet = color-facet (art, painting, beauty)
  - Future characters will have their own facets

## Golden Threads
- Visible, glowing lines of golden light
- Can be thin as hair or thick as rope depending on context
- Flow and move like living things
- Emit soft warm light
- When frayed: ends are wispy, flickering
- When healthy: smooth, bright, complete
- Connect to the Heart Crystal, flowing like light through a prism

## Kathaél Environment
- Forest setting with ancient trees
- Luminous, magical quality to natural elements
- Moss that glows softly
- Strange but beautiful flora and fauna
- Crossroads, clearings, groves as key locations
- Day/night lighting should match text

## Creatures
- Rabbits, foxes, deer, birds with "knowing eyes"
- Slightly more expressive than realistic animals
- Not anthropomorphized, but clearly intelligent
- Should feel like guides and witnesses
- Can interact with characters in meaningful ways

## Color Palette
- Rich, warm natural tones
- Golden light for magic
- Deep greens and browns for forest
- Crystal: clear with rainbow refraction
- Avoid overly saturated or garish colors
- Noah's story: Warmer, amber-toned palette
- Elise's story: Softer, more pastel watercolor palette

## Page Layout
- 1 illustration per page
- Images should support but not overwhelm text
- Leave space for 3-4 sentences of text
- Important action should be clear and centered
- Background details can be rich but shouldn't distract

## Emotional Tone by Story Beat

### Beginning
- Warm, familiar, slightly wistful
- Ordinary world feeling safe but slightly restless

### Discovery
- Awe and wonder, bright and magical
- Sense of stepping into something extraordinary

### Challenges
- Dynamic, tense but not scary
- Physical action visible
- Visible consequences when things go wrong

### Low Point
- Darker, more muted, rain/shadows okay
- But never hopeless - maintain gentle light

### Climax
- Dramatic, bright, energetic
- Physical action at its peak
- Crystal blazing with light

### Resolution
- Warm, glowing, peaceful joy
- Sense of completion and new beginning

## Technical Notes
- Resolution: High enough for print (300 DPI recommended)
- Format: As specified by gen_image.py script
- Consistency: Cross-reference previous images for same character
- Lighting: Should match time of day in text

## Action & Movement
Per the age 9-12 guidelines, illustrations should show:
- Characters actively doing things (running, climbing, reaching, touching)
- Physical interactions with environment
- Creatures that are actively participating
- Visible magical effects (sparks, glows, light flowing)
- Consequences of actions (flowers dying/blooming, cracks spreading/sealing)

## What to Avoid
- Static, passive scenes
- Characters just standing and thinking
- Overly detailed backgrounds that distract from action
- Dark, scary imagery inappropriate for age group
- Inconsistent character appearances
- Breaking the fourth wall (characters looking at camera)

## Character-Specific Visual Notes

### Noah
- Curious, active expression
- Often holding notebook or pen
- Interacts physically with golden threads
- Surrounded by words/letters in the air when stories are active
- Expression should show wonder more than worry

### Elise
- Gentle, observant expression
- Watercolor set visible (at wrist or in hand)
- Interacts with colors and light
- Surrounded by soft color washes when magic is active
- Expression should show quiet strength

## Image Generation Workflow
1. Read character reference images from `ref-images/{char-code}-*.jpg`
2. Apply consistent character appearance
3. Follow visual description from page YAML
4. Incorporate lighting and mood from story beat
5. Ensure action and movement are visible
6. Check that consequences are shown clearly

## Quality Checklist
Before finalizing an illustration, verify:
- [ ] Character appearance matches reference images
- [ ] Action is visible and dynamic
- [ ] Lighting matches time of day and mood
- [ ] Heart Crystal appearance is correct if shown
- [ ] Golden threads follow established rules
- [ ] Creatures are active participants
- [ ] Color palette is appropriate
- [ ] Age-appropriate tone (9-12 years)
- [ ] Text placement leaves room for 3-4 sentences
- [ ] Overall composition supports the story moment
