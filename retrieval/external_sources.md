# External Sources (Web + Community Platforms)

Beyond arXiv/Semantic Scholar (covered in `codex_collaboration.md`), the project also tracks community discussion on platforms like 小红书 (Xiaohongshu), Zhihu, B站, etc. This file defines the staged protocol for accessing them.

**Default posture**: NEVER scrape unless local evidence is genuinely insufficient and the user has explicitly authorized Phase 2. Even then, frequency is capped to protect the user's account.

---

## Phase 1 — WebSearch + WebFetch (zero account risk, default)

**When to use**: any external-search step in Gate A that targets community discussion (not papers).

**Protocol**:
1. WebSearch with platform-qualified query, e.g.:
   - `<your-project-keyword> 经验贴 小红书`
   - `site:xiaohongshu.com <your-project-keyword> 经验贴`
   - `<your-competition-or-project-keyword> 经验分享`
   - `site:zhihu.com <your-project-keyword> 复盘`
2. For each candidate URL (≤5):
   - WebFetch the URL with a prompt like "extract the post body and top-3 comments, summarize what they say about <your-project-keyword> / pipeline / 架构 / 经验"
   - If WebFetch returns a 403 / paywall / "请登录" wall → mark as `[behind-login: <url>]` and continue
3. Synthesize: which sources gave actual content vs. which hit the wall.
4. Output goes to `external_research.md` under the run's output dir, alongside any paper findings.

**Hard rules**:
- No login simulation. No cookies. No browser automation.
- Account risk: zero (we never identify ourselves).
- Coverage limit: many XHS notes only show full content after login, so Phase 1 will frequently hit the wall on XHS specifically. This is expected.

---

## Phase 2 — MediaCrawler CDP mode (rate-limited, opt-in)

**When to use**: ONLY when ALL of these are true:
1. Phase 1 hit the login wall twice in a row for the same query, AND
2. The user has approved Phase 2 via Gate A chips, AND
3. The user has an 小号 (alt account) logged in via a manually-launched Chrome instance with `--remote-debugging-port=9222`.

**Tool reference** (cloned read-only at `<MEDIACRAWLER_ROOT>/`):
- Repository: `NanmiCoder/MediaCrawler`
- License: `NON-COMMERCIAL LEARNING LICENSE 1.1` — `<MEDIACRAWLER_ROOT>/LICENSE`. Personal research is in scope; commercial use is NOT.
- Platforms supported: XHS, 抖音, 快手, B站, 微博, 贴吧, 知乎 (see `media_platform/<platform>/`)
- XHS module: `<MEDIACRAWLER_ROOT>/media_platform/xhs/`
- Authentication: CDP mode (connects to a Chrome instance YOU launched, not file-based cookies)
- Dependencies (NOT installed by default): `playwright` + `chromium` + Python venv. Total install footprint ~600 MB.

**Protocol**:
1. Before Phase 2 ever runs, this skill MUST verify:
   - `<MEDIACRAWLER_ROOT>/main.py` exists (clone present)
   - User has confirmed Chrome is running with remote debugging
   - User has explicitly approved THIS query going to Phase 2 via Gate A chips
2. Install dependencies on demand (only first time). Surface a chip first:
   - `要装 playwright + chromium 吗？~600MB`
   - Don't auto-install.
3. Execution rules:
   - One query per Gate A invocation. NO crawling loops.
   - Max 5 posts inspected per query.
   - Min 2-second delay between requests.
   - Daily cap: 10 Phase-2 queries across all `/deep-search` runs. Skill must read `<PROJECT_ROOT>/docs/research/deep_search/.phase2_quota.json` to check; if today's count ≥ 10, refuse and tell user to wait until next day.
4. After execution:
   - Append a record to `.phase2_quota.json`: `{"date": "YYYY-MM-DD", "count": N, "queries": [...]}`.
   - Append findings to `external_research.md` under a `## Phase 2 — Community Platform Findings (MediaCrawler)` section.
   - Cite each finding with the original post URL.

**Account-risk mitigations**:
- Always use the user's 小号, never their main account.
- CDP mode is preferred over cookie-file auth because Chrome's own session handling (rotation, fingerprint stability) stays intact.
- Random 2–5 second jitter between requests.
- If the user reports the 小号 was rate-limited or banned, this skill IMMEDIATELY moves Phase 2 to disabled state in `.phase2_quota.json` (`{"disabled_until": "YYYY-MM-DD"}`) and refuses further Phase 2 calls.

---

## Phase 3 — Chat platforms (not implemented)

Out of scope for v0. If the user later asks for Telegram / Discord / QQ integration, add a separate `phase3_*.md` file with platform-specific protocols.

---

## Selection rule (which phase to use)

| Source needed | Phase 1 first | Phase 2 fallback allowed |
|---|---|---|
| arXiv / Semantic Scholar (paper search) | n/a — papers go through `codex_collaboration.md` | n/a |
| Zhihu / B站 articles (mostly public) | YES | NO (Phase 1 usually enough) |
| 小红书 笔记 (mostly behind wall) | YES | YES (if user approves) |
| 微博 / 抖音 / 快手 | YES | Only if user asks specifically |
| Tencent algo.qq.com official forum | YES (anonymous + WebFetch) | NO |
