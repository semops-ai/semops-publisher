"""
Outline Agent - Phase 1

Structures argument with citations, concepts, and image suggestions.
"""

import os
from anthropic import Anthropic


class OutlineAgent:
    """
    Outline agent that:
    1. Structures argument based on POV
    2. Integrates research findings with clear citations
    3. Highlights concepts throughout
    4. Suggests images/diagrams with descriptions
    5. Offers alternative perspectives
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def generate_outline(self, notes_content: str, research_content: str) -> str:
        """
        Generate outline from notes and research.

        Args:
            notes_content: Original notes
            research_content: Research findings

        Returns:
            Outline as markdown
        """

        system_prompt = """You are an outline agent for blog post structure.

Your job is to create a clear, compelling outline that:

1. **Structure the Argument**:
   - Opening hook
   - Clear progression of ideas
   - Strong conclusion
   - Logical flow

2. **Integrate Research**:
   - Use citation markers like [^1], [^2]
   - Link citations to sources at the bottom
   - Balance 1P and 3P sources
   - Support key claims with evidence

3. **Highlight Concepts**:
   - Use {{concept-name}} tags for key concepts
   - Define important terms
   - Link related ideas

4. **Suggest Visuals**:
   - Diagrams (Mermaid, Excalidraw)
   - Images (hero, concept illustrations)
   - Screenshots or examples
   - Provide text descriptions

5. **Alternative Perspectives**:
   - Acknowledge counterarguments
   - Suggest critiques or refinements
   - Identify gaps or weaknesses

Output Format:
# Outline: [Title]

## Meta
- **Target Audience**: [who this is for]
- **Key Takeaway**: [main point]
- **Estimated Length**: [words]

## I. Introduction
### Hook
[Opening that grabs attention]

### Context
[Background and why this matters]

### Thesis
[Clear statement of POV with {{concept}} tags]

**Visual Suggestion**: [Description of hero image or opening diagram]

## II. [Main Section 1]
### [Subsection]
- Key point [^1]
- Supporting detail with {{concept-tag}}
- Evidence or example [^2]

**Visual Suggestion**: [Mermaid diagram showing X, Excalidraw sketch of Y]

## III. [Main Section 2]
[Continue structure...]

## IV. Conclusion
### Summary
[Recap main points]

### Call to Action / Next Steps
[What readers should do]

### Future Questions
[Areas for further exploration]

## Citations
[^1]: [Source name and link] - [1P/3P]
[^2]: [Source name and link] - [1P/3P]

## Concept Glossary
- {{concept-1}}: [Definition]
- {{concept-2}}: [Definition]

## Alternative Approaches Considered
- [Different angle or structure]
- [Counterargument to address]

## Notes for Draft Phase
- [Tone guidance]
- [Style considerations]
- [Specific examples to include]
"""

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"""Create an outline based on these inputs:

# Original Notes
{notes_content}

# Research Findings
{research_content}

Please create a comprehensive outline that structures the argument effectively."""
                }
            ]
        )

        return response.content[0].text
