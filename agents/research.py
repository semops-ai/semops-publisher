"""
Research Agent - Phase 1

Understands POV, finds supporting/refuting evidence from 1P repos and 3P sources.
"""

import os
from anthropic import Anthropic
from pathlib import Path


class ResearchAgent:
 """
 Research agent that:
 1. Understands the POV/point being made
 2. Searches referenced repos for supporting/refuting content
 3. Distinguishes 1P (proprietary) vs 3P (external) sources
 4. Finds citation opportunities for traffic/networking
 5. Extracts key concepts and entities
 """

 def __init__(self):
 self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
 self.model = os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022")

 def research(self, notes_content: str) -> str:
 """
 Execute research phase based on notes.

 Args:
 notes_content: Content from notes.md

 Returns:
 Research findings as markdown
 """

 # Build system prompt for research
 system_prompt = """You are a research agent for blog post preparation.

Your job is to analyze the notes and:

1. **Understand the POV**: What point or argument is being made?

2. **Find 1P Evidence**:
 - Look for supporting/refuting content in referenced repos
 - These are proprietary sources (marked as 1P)
 - Extract relevant quotes, concepts, or data

3. **Identify 3P Citation Opportunities**:
 - Find external sources worth citing
 - Prioritize industry bloggers and thought leaders (traffic/networking value)
 - Avoid only citing major corp blogs (Nvidia, Google, etc.)

4. **Extract Concepts & Entities**:
 - Key concepts that should be highlighted
 - Entities to link to knowledge graph
 - Technical terms to define

5. **Assess Source Quality**:
 - Credibility of sources
 - Recency and relevance
 - Potential impact

Output Format:
# Research Findings: [Topic]

## POV Summary
[What argument/perspective is being made]

## Supporting Evidence (1P)
### [Source/Repo Name]
- **Location**: [file path or URL]
- **Relevance**: [why this supports the POV]
- **Key Quote/Data**: [extract]

## Refuting Evidence / Counterarguments
[Balance the perspective]

## Recommended 3P Citations
### [Source Name]
- **Type**: [Industry blogger / Research paper / Case study]
- **Why Cite**: [Traffic value / Networking / Authority]
- **Key Point**: [what to reference]
- **Link**: [URL if known]

## Key Concepts
- {{concept-name}}: [definition and relevance]

## Entities to Link
- [Entity name]: [context]

## Research Quality Notes
- Gaps in research
- Additional sources needed
- Questions to address
"""

 # Call Claude API
 response = self.client.messages.create(
 model=self.model,
 max_tokens=4000,
 system=system_prompt,
 messages=[
 {
 "role": "user",
 "content": f"Here are the notes for the blog post:\n\n{notes_content}\n\nPlease conduct research based on these notes."
 }
 ]
 )

 return response.content[0].text

 def search_repos(self, repo_paths: list[str], query: str) -> list[dict]:
 """
 Search local repos for relevant content.

 This is a placeholder for Phase 1 - manual lookup is expected.
 Phase 2 will implement actual repo searching with RAG.

 Args:
 repo_paths: List of repo directories to search
 query: Search query

 Returns:
 List of relevant documents/snippets
 """
 # Phase 1: Return empty - expect manual references in notes
 # Phase 2: Implement with grep/ripgrep + vector search
 return []

 def find_external_sources(self, topic: str, keywords: list[str]) -> list[dict]:
 """
 Find external citation opportunities.

 Phase 1: Manual suggestions only
 Phase 2: Web search integration

 Args:
 topic: Main topic
 keywords: Key search terms

 Returns:
 List of recommended sources
 """
 # Phase 1: Return empty - agent makes suggestions in research.md
 # Phase 2: Implement with web search API
 return []
