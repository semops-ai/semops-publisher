"""
Formatter Agent - Phase 1

Transforms final draft for different publishing platforms.
"""

import os
from anthropic import Anthropic
from datetime import datetime


class FormatterAgent:
 """
 Formatter agent that:
 1. Generates LinkedIn version (platform-appropriate formatting)
 2. Creates frontmatter for semops-core integration
 """

 def __init__(self):
 self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
 self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

 def format_for_platforms(
 self, final_content: str, slug: str
 ) -> tuple[str, str]:
 """
 Format content for different platforms.

 Args:
 final_content: Final edited draft
 slug: Post slug

 Returns:
 Tuple of (linkedin_md, frontmatter_yaml)
 """

 # Generate LinkedIn version
 linkedin = self._format_linkedin(final_content)

 # Generate frontmatter for semops-core
 frontmatter = self._generate_frontmatter(final_content, slug)

 return linkedin, frontmatter

 def _format_linkedin(self, content: str) -> str:
 """Format for LinkedIn"""

 system_prompt = """You are adapting a blog post for LinkedIn.

Transform the content to:
1. Shorter, punchier paragraphs
2. Remove technical jargon where possible
3. Add line breaks for readability
4. Include engaging hooks and questions
5. Add emoji strategically (but sparingly)
6. End with call-to-action
7. Stay under 3000 characters if possible (trim if needed)
8. Add "Read full article: [LINK]" at end

Focus on the key insights and make it engaging for LinkedIn audience.
"""

 response = self.client.messages.create(
 model=self.model,
 max_tokens=4000,
 system=system_prompt,
 messages=[
 {
 "role": "user",
 "content": f"Adapt this for LinkedIn:\n\n{content}"
 }
 ]
 )

 return response.content[0].text

 def _generate_frontmatter(self, content: str, slug: str) -> str:
 """Generate frontmatter YAML for semops-core"""

 system_prompt = """You are extracting metadata for a knowledge management system.

Extract and structure:
1. Title
2. Summary (1-2 sentences)
3. Key concepts (list)
4. Entities mentioned (people, organizations, technologies)
5. Related topics
6. Tags/categories
7. Links to other content (from citations)

Output as YAML format for frontmatter.
"""

 response = self.client.messages.create(
 model=self.model,
 max_tokens=2000,
 system=system_prompt,
 messages=[
 {
 "role": "user",
 "content": f"""Extract metadata from this content:

Slug: {slug}
Date: {datetime.now.isoformat}

Content:
{content}

Generate frontmatter YAML."""
 }
 ]
 )

 return response.content[0].text
