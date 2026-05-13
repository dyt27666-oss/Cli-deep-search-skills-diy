# Codex Collaboration

Use Codex collaboration only where the workflow explicitly calls for it, primarily Gate A.

## Gate A Challenge Round

Invoke `/codex:rescue` with:

`Challenge these search angles for /deep-search Gate A. 1 round only. Reply: ACCEPT / ADD <angle> / DROP <angle> / REFRAME <angle to angle>.`

Rules:

- One round only.
- Codex must challenge search angles, not run the search in this step.
- Resolve disagreements locally and record the final angle list with rationale.

## External Paper Search Delegation

After the user selects angles with chips, invoke `/codex:rescue` with:

`Deep search arXiv + Semantic Scholar for: <angles>. Return for each: paper title, authors, year, venue, arxiv URL, DOI, 2-sentence finding, relevance to UniRec-KDDCup2026's pCVR pipeline. Max 5 papers per angle.`

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
