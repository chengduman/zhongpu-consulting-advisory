# Posted to GitHub

1|# Beyond Playwright Wrappers: Why Browser-Use Needs a Stateful Session Model
2|
3|**Posted by Zhongpu Consulting** · *AI Agent Infrastructure Advisory*
4|
5|---
6|
7|Browser-Use has quickly become a go-to tool in the AI agent ecosystem for good reason — it solves a genuinely hard problem (reliable, LLM-driven browser automation) with a clean abstraction over Playwright. The ability to give an agent a browser and say "go do this task" is powerful, and we've been using it extensively in client engagements involving web-based workflows.
8|
9|After deploying Browser-Use in several production-adjacent scenarios — automated vendor portal data extraction, multi-step SaaS configuration, and web form testing — we've identified what we believe is the single most important architectural gap: **the lack of a first-class, stateful session model.**
10|
11|## The Stateless Session Problem
12|
13|Today, a Browser-Use agent opens a browser context, executes a sequence of actions to accomplish a task, and returns the result. This works well for discrete, short-lived tasks like "scrape product prices from this page."
14|
15|But real-world enterprise workflows look more like:
16|
17|- Log into a CRM portal (login with 2FA).
18|- Navigate through 5 dashboard views to locate an account.
19|- Extract account data, then perform an action in the account (submit a ticket, update a field).
20|- Keep the session alive for human-in-the-loop verification before committing.
21|- Resume the same session hours later after human approval.
22|
23|Each of these steps could be its own Browser-Use task, but they share a **session identity** — cookies, localStorage, navigation history, and crucially, application state (is the user logged in? which record is currently open?).
24|
25|## What a Stateful Session Model Would Unlock
26|
27|If Browser-Use exposed sessions as explicit, serializable, and resumable primitives:
28|
29|```python
30|# Vision for stateful sessions
31|session = await browser_session.create(persist=True)
32|# First task
33|await session.navigate("https://vendor-portal.example.com")
34|await session.login(credentials)
35|snapshot = session.serialize()  # Save full state
36|# ... hours later ...
37|session = await browser_session.restore(snapshot)
38|# Second task — still authenticated, still on the same page
39|result = await session.extract_data("account_table")
40|```
41|
42|This would enable:
43|
44|1. **Long-running, interrupted workflows** — Sessions survive network drops, agent restarts, or human handoffs.
45|2. **Human-in-the-loop** — An agent pauses mid-workflow, a human reviews the browser state via a screenshot + DOM summary, then the agent resumes from the exact same state.
46|3. **Audit trails** — Full replay of a session's sequence of states for compliance (critical in regulated industries).
47|4. **Session pooling** — Pre-warm authenticated sessions (e.g., logged into Salesforce) and reuse them across agent tasks, dramatically reducing startup overhead.
48|
49|## Implementation Considerations
50|
51|Playwright already supports `browser_context.storage_state()` for cookie/localStorage serialization, and CDP sessions can be serialized with some additional work. The gap isn't technical feasibility — it's abstraction design. The community would benefit from a `BrowserSession` class that wraps this complexity with a clean, agent-friendly API.
52|
53|We've built a rudimentary session manager using Redis + Playwright's storage state — it works but is fragile. A native solution would be a game-changer for anyone deploying Browser-Use in production.
54|
55|Would the maintainers consider this direction? Happy to contribute design input or even a reference implementation.
56|