# External Search Path (arxiv MCP preferred → Codex fallback)

## Preferred path: arxiv-mcp-server

If `mcp__arxiv-mcp-server__*` tools are available in this session, **use the MCP directly for external paper retrieval** (no Codex round-trip needed). Workflow:

1. **Gate A challenge round still happens** — but you challenge the angles INTERNALLY (read constraints + draft angles + critique them yourself), or invoke `/codex:rescue` only if Codex is available. With MCP, the round is much cheaper than the Codex+WebFetch path.
2. **Search**: `mcp__arxiv-mcp-server__search_papers` with year_floor + category filters (e.g., `cs.IR`, `cs.LG`) + keyword. Returns structured metadata directly — no need to WebFetch-verify titles because the MCP queries arXiv's official API.
3. **Optional deeper read**: `mcp__arxiv-mcp-server__download_paper` then `read_paper` for any candidate worth full-text review.
4. **Citations**: every paper returned by the MCP is already verified (it came from arXiv). Skip the WebFetch verification step but still apply year_floor enforcement (reject any paper with year < floor — MCP filters are best-effort).

Setup check (run once per session):
```
# In Claude Code, after install:
claude mcp add arxiv-mcp-server uvx arxiv-mcp-server
# Then /reload-plugins or restart session
```

## Fallback path: Codex + WebSearch + WebFetch

Use only when arxiv MCP is NOT available (not installed, group budget OK, or user explicitly prefers Codex challenge):

## Gate A Challenge Round

Invoke `/codex:rescue` with:

`Challenge these search angles for /deep-search Gate A. 1 round only. Reply: ACCEPT / ADD <angle> / DROP <angle> / REFRAME <angle to angle>.`

Rules:

- One round only.
- Codex must challenge search angles, not run the search in this step.
- Resolve disagreements locally and record the final angle list with rationale.

## External Paper Search Delegation

After the user selects angles with chips, invoke `/codex:rescue` with:

`Deep search arXiv + Semantic Scholar for: <angles>. Return for each: paper title, authors, year, venue, arxiv URL, DOI, 2-sentence finding, relevance to your project's ML pipeline. Max 5 papers per angle.`

Do not make inline arXiv or Semantic Scholar API calls from the skill itself.

## Citation Verification

For every paper returned by Codex:

1. WebFetch the arXiv URL.
2. Confirm the fetched title matches the returned title.
3. Keep verified citations in `external_research.md`.
4. Tag bad citations as `[unverified: <reason>]`.
5. Exclude unverified citations from `prior_updates.diff`.

## Reporting

- Summarize Codex-supplied evidence in your own words.
- Keep the report clear about which claims came from local evidence and which came from verified external citations.
- Never treat unverified external citations as support for a prior promotion or demotion.
