# GitHub charts

Data source: GitHub GraphQL API, collected 2026-10-29 UTC. `github-data.json` preserves the exact aggregates used by the charts.

- Activity: daily contribution calendar aggregated by calendar month. First and last months are partial. The calendar may include anonymized private contributions, depending on the account and API visibility. Contributions are not commits alone or a productivity score. No private repository identifiers are published.
- Languages: sum of GitHub Linguist code bytes across owned public, non-fork repositories. Top six languages plus Other; percentages use the complete byte total. This is not proficiency, authorship of every line, or time spent. GitHub's Linguist exclusions apply.
- SVG charts use a zero baseline and explicit values. Snapshots are not live widgets.

## Refresh

With Python 3 and authenticated GitHub CLI, from the repository root:

```sh
python scripts/refresh-stats.py --output assets/stats
```

Inspect the SVGs and data before committing. Update snapshot dates, counts and image alternative text in README.md to match the refreshed data. No automated refresh is configured.
