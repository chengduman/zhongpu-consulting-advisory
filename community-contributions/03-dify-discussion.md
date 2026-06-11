# Posted to GitHub

1|# Enterprise Multi-Tenancy in Dify: What We Learned Deploying for 3 Enterprise Clients
2|
3|**Posted by Zhongpu Consulting** · *AI Application Platform Advisory*
4|
5|---
6|
7|Dify has become one of our most-recommended platforms for clients who need a visual, low-code environment to build and iterate on LLM-powered applications. The combination of RAG pipelines, agent workflows, and an integrated evaluation framework in a single UI is genuinely compelling — it dramatically shortens the feedback loop from "idea" to "working prototype that business stakeholders can actually test."
8|
9|We've now deployed Dify in production for three enterprise clients across different verticals (financial services, e-commerce, and healthcare logistics). Here's what we learned about the multi-tenancy gap — and a proposal for bridging it.
10|
11|## The Multi-Tenancy Reality
12|
13|Enterprise deployments are almost never single-tenant in the way most open-source tools assume. Even when a single organization deploys Dify, they typically need:
14|
15|| Dimension | Requirement |
16||-----------|-------------|
17|| **Department isolation** | Finance and Customer Support use the same Dify instance but must not see each other's datasets, apps, or API keys. |
18|| **Role-based access** | Not just admin vs. user — but per-workspace roles (dataset editor, app viewer, prompt reviewer, deployment operator). |
19|| **Usage metering** | Each department needs separate cost tracking (token consumption, vector storage, API calls) for internal chargeback. |
20|| **Custom branding** | White-labeling per workspace in the chat UI. |
21|
22|Currently, Dify's workspace model provides some separation, but it's primarily collaborative — members within a workspace see most shared resources. True data isolation, granular RBAC, and per-workspace usage metering require significant customization.
23|
24|## A Pragmatic Proposal
25|
26|Rather than building a full multi-tenant SaaS layer (which may not align with Dify's product direction), we suggest an **extension-point approach**:
27|
28|1. **Pluggable Authentication Backend** — Allow organizations to wire in their own SSO/OIDC provider per workspace, with group-to-role mapping from the upstream IdP (Azure AD, Okta). This is the single highest-impact feature for enterprise adoption.
29|
30|2. **Isolation Hooks** — Expose middleware hooks at key boundaries (dataset queries, app execution, API key validation) where custom isolation logic can be injected. A simple Python plugin interface would let teams implement per-tenant data filtering without forking Dify.
31|
32|3. **Metered Usage Exporter** — A built-in Prometheus endpoint (or webhook sink) that emits per-workspace, per-user usage metrics. Teams can then build their own dashboards and billing integrations externally.
33|
34|## The Good News
35|
36|Dify's architecture is clean enough that these extensions are feasible without a major rewrite. We've implemented a proof-of-concept using FastAPI middleware that wraps Dify's public API — it intercepts workspace context from JWT claims and filters dataset access accordingly. Initial results are promising, but a native plugin system would be far more maintainable.
37|
38|Has the community explored these patterns? We'd be happy to share our middleware implementation if others are facing the same multi-tenancy requirements.
39|