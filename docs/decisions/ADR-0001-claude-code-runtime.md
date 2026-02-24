# ADR-0001: Use Claude Code as Agent Runtime

> **Status:** Complete
> **Date:** 2024-11-30
> **Related Issue:** N/A
> **Builds On:** [PHASE1-MANUAL-FIRST](./PHASE1-MANUAL-FIRST.md)

---

## Executive Summary

Use Claude Code (this environment) as the agent runtime instead of writing Python scripts that call the Anthropic API. Agents are defined as prompt templates executed by Claude Code using the user's existing Claude subscription.

---

## Context

**Initial Approach:** Write Python agent classes that use Anthropic API:
```python
from anthropic import Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(model="claude-3-5-sonnet", ...)
```

**Problems:**
- Requires separate Anthropic API key (additional setup)
- Adds API costs on top of Claude subscription
- Need to manage: API client, retries, errors, token limits, context
- More complex to iterate on prompts (edit code, run, debug)
- Harder to test (deploy/rebuild cycle)

**Realization:** User is already using Claude Code, which provides:
- Agent runtime (this environment)
- Tool access via hooks (GitHub CLI, file access, etc.)
- Context management (automatic)
- Uses existing Claude subscription (no separate API key)
- Instant iteration on prompts

---

## Decision

**Agents = Prompt Templates + Slash Commands**

Instead of Python API code:
1. **Prompt Templates** (`prompts/[agent]-agent.md`) - Define agent behavior
2. **Slash Commands** (`.claude/commands/[step].md`) - Orchestrate workflow
3. **Claude Code** (this environment) - Execute with user's subscription

### Example: Research Agent

**Prompt Template:**
```markdown
# prompts/research-agent.md

You are a research agent for blog posts.

## Input
- notes.md with topic, POV, 1P references

## Tasks
1. Understand POV
2. Fetch 1P files via GitHub CLI
3. Analyze for evidence
4. Suggest 3P citations
5. Extract concepts

## Output
Generate research.md with findings
```

**Slash Command:**
```markdown
# .claude/commands/research.md

1. Read posts/<slug>/notes.md
2. Load prompts/research-agent.md
3. Execute research agent with inputs
4. Save output to research.md
```

**User Workflow:**
```
User: /research
Claude Code: [executes] → ✓ research.md generated
```

---

## Consequences

**Positive:**
- ✅ No API key management (uses Claude subscription)
- ✅ Simpler implementation (prompts not API code)
- ✅ Cheaper (no separate API costs)
- ✅ Faster iteration (instant prompt updates)
- ✅ Better tools (hooks provide GitHub CLI, file access)
- ✅ Automatic context management
- ✅ Easier debugging (full conversation history visible)

**Negative:**
- ❌ Requires Claude Code environment (can't run standalone)
- ❌ Limited to Claude (no dual model in Phase 1)
- ❌ Dependent on Claude Code features/limits

**Risks:**
- If Claude Code changes or becomes unavailable, workflow breaks
- No offline capability
- Can't easily run in CI/CD (but not needed for Phase 1)

**Mitigations:**
- Keep API-based implementation option for Phase 2+ (in archive)
- Document prompts clearly for potential future migration
- Accept Phase 1 constraint (manual workflow, Claude Code only)

---

## Implementation Plan

### Phase 1: Prompt-Based Agents ✅
- [x] Remove Anthropic API key requirement
- [x] Update .env.example (no API keys)
- [x] Update hooks (no API validation)
- [x] Document Claude Code approach
- [ ] Create prompt templates in `prompts/`
- [ ] Update slash commands to load/execute prompts
- [ ] Test workflow end-to-end

### Phase 2+: Optional API Wrapper 📋
- [ ] Add Python wrapper for API execution (if needed)
- [ ] Support both Claude Code and standalone modes
- [ ] Add dual model comparison (Claude + Gemini)

---

## Session Log

### 2024-11-30: Claude Code Approach Clarified
**Status:** Completed

**Completed:**
- Removed ANTHROPIC_API_KEY from .env.example
- Updated user-prompt-submit.sh hook (no API validation)
- Created CLAUDE_CODE_APPROACH.md documentation
- Updated START_HERE.md with simplified quick start
- Documented prompt template strategy
- Created this ADR

**Key Insight:**
User correctly identified that hooks give access to Claude Code runtime - no separate API needed. This is simpler and better suited for Phase 1 manual workflow.

**Next Session Should Start With:**
1. Create `prompts/` directory
2. Write first prompt template (research-agent.md)
3. Update `.claude/commands/research.md` to load and execute prompt
4. Test with sample post

---

## References

- [CLAUDE_CODE_APPROACH.md](../../CLAUDE_CODE_APPROACH.md) - Complete explanation
- [Anthropic Claude Code Docs](https://docs.claude.com/claude-code)
- [archive/phase2-implementation-options/agents/](../../archive/phase2-implementation-options/agents/) - API-based implementation reference

---

**End of Document**
