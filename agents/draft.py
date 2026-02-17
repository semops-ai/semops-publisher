"""
Draft Agent - Phase 1

Generates full prose from outline, matching existing blog style.
"""

import os
from pathlib import Path

from anthropic import Anthropic


# Load blog style guide for prompt context
def _load_style_guide() -> str:
    """Load BLOG_STYLE_GUIDE.md content for prompt context."""
    style_guide_path = Path(__file__).parent.parent / "BLOG_STYLE_GUIDE.md"
    if style_guide_path.exists():
        return style_guide_path.read_text()
    return ""


class DraftAgent:
    """
    Draft agent that:
    1. Generates full article text from outline
    2. Matches style of reference blog posts
    3. Integrates citations naturally
    4. Places concept tags appropriately
    5. Adds image/diagram placeholders with specs
    """

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

    def generate_draft(self, outline_content: str, style_refs: list[str] = None) -> str:
        """
        Generate full draft from outline.

        Args:
            outline_content: Final approved outline
            style_refs: Optional list of reference post contents for style matching

        Returns:
            Full draft as markdown
        """

        # Build style reference section
        style_section = ""
        if style_refs:
            style_section = "\n\n# Style References\n\n"
            for i, ref in enumerate(style_refs, 1):
                # Only include first 1500 chars of each reference to save tokens
                style_section += f"## Reference {i}\n{ref[:1500]}\n...\n\n"

        # Load style guide
        style_guide = _load_style_guide()

        style_guide_section = ""
        if style_guide:
            style_guide_section = f"""
# Blog Style Guide

Follow these style guidelines for voice, tone, and conventions:

{style_guide}

---

"""

        system_prompt = f"""You are a draft agent for blog post writing.
{style_guide_section}
Your job is to transform the outline into a complete, polished blog post that:

1. **Full Prose**:
   - Expand outline into complete paragraphs
   - Natural flow and transitions
   - Engaging, conversational tone
   - Clear and accessible language

2. **Style Matching**:
   - Match the tone and voice of reference posts (if provided)
   - Use similar sentence structure and pacing
   - Maintain consistent perspective (1st person, 3rd person, etc.)

3. **Citations**:
   - Integrate citation markers naturally in text
   - Link to sources smoothly
   - Maintain citations list at bottom

4. **Concept Integration**:
   - Use {{concept}} tags where appropriate
   - Define terms clearly when first introduced
   - Link related concepts throughout

5. **Visual Placeholders**:
   - Add clear image/diagram placeholders
   - Include specifications for asset creation
   - Format: ![Description](placeholder-name.png)
   - Add notes on Mermaid/Excalidraw specs

6. **Polish**:
   - Strong opening hook
   - Clear section transitions
   - Compelling conclusion
   - Proofread quality

Output Format:
# [Title]

![Hero image description: ...](hero-image.png)
*Image specs: [dimensions, style, key elements]*

## Introduction

[Engaging opening that hooks the reader...]

[First mention of key {{concept}} with definition...]

![Diagram suggestion: Mermaid flowchart showing...](diagram-1.mermaid.png)
```mermaid
[If applicable, include Mermaid code here]
```

## [Main Section]

[Well-developed paragraphs with smooth transitions...]

Evidence shows that... [^1]

The {{concept-name}} approach differs because...

![Concept illustration: ...](illustration-2.png)
*Excalidraw sketch showing [specific elements]*

## Conclusion

[Strong wrap-up and call to action...]

---

## Citations

[^1]: [Full citation with link]
[^2]: [Full citation with link]

## About the Concepts

{{concept-1}}: [Expanded definition and context]
{{concept-2}}: [Expanded definition and context]

---

*[Any final notes or author bio]*
"""

        # Build user message
        user_message = f"Create a full draft based on this outline:\n\n{outline_content}"
        if style_section:
            user_message += f"\n{style_section}\nPlease match the style and tone of these references."

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_message
                }
            ]
        )

        return response.content[0].text
