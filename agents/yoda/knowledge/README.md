# Knowledge Base

This directory is the agent's persistent knowledge store. It is **auto-updated** by the learner pipeline (`learner/resource_parser.py` and the knowledge-extraction stage) every time new resources are ingested.

## How it works

1. **Domain files** -- Each markdown file covers a single domain (concepts, architecture, training insights, datasets, etc.). New domains are created automatically when the agent encounters topics that do not fit existing files.
2. **Timestamped entries** -- Every piece of knowledge is recorded with a UTC timestamp and a source citation so the agent (and humans) can trace where an insight came from and how fresh it is.
3. **Append-only by default** -- New entries are appended under the appropriate heading. The agent may consolidate or deduplicate during an evolution cycle, but raw entries are never silently deleted.
4. **Evolution log** -- `evolution_log.md` tracks every code-evolution event: what changed, why, and which knowledge entries triggered it.

## File inventory

| File | Purpose |
|---|---|
| `concepts.md` | Core JEPA / VL-JEPA theoretical concepts |
| `architecture.md` | Model architecture details and design decisions |
| `training_insights.md` | Hyperparameters, schedules, and training tricks |
| `datasets.md` | Dataset descriptions, statistics, and licensing |
| `evolution_log.md` | Chronological record of every model/code evolution |

## Adding knowledge manually

You can add entries by hand -- just follow the existing timestamp/source format:

```
## [YYYY-MM-DD HH:MM] Source: <where this came from>

- **Term**: Explanation ...
```

The agent will respect manually-added entries and will not overwrite them.
