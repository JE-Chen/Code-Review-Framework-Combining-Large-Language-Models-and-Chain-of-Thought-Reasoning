# Longitudinal team study protocol

This protocol evaluates the claimed learning loop without changing merge policy
mid-study.

## Design

- Pre-register repositories, study dates, exclusion rules, primary metrics, and
  analysis before inspecting outcomes.
- Run a two-week observation baseline followed by at least six intervention
  weeks. Prefer a randomized stepped-wedge rollout when several teams are
  available.
- Freeze model revision and generation parameters within each phase. Record any
  operational exception in the run manifest.
- Obtain contributor consent and remove personal data from the research export.

## Primary measures

- accepted suggestions / actionable suggestions;
- dismissed findings / all findings;
- false positives per PR from blinded human adjudication;
- issue-level recall against human review comments;
- time to first review and time to merge.

Secondary measures are token cost, latency, review volume, reproducibility, and
the fraction of comments receiving no interaction. Report confidence intervals,
missing-data counts, and repository-level results; do not pool repositories
without accounting for clustering.

## Audit data

For every reviewed PR retain only approved research fields: anonymized PR and
repository IDs, head SHA, manifest hash, finding IDs, timestamps, disposition,
and adjudication. Never export source code, secrets, raw author identities, or
private model prompts unless the approved protocol explicitly permits it.
