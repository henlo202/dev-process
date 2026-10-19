---
artefact: user-docs
status: approved
owner: Documenter agent
updated: 2026-10-19
---
# Command-line reference

```
python -m greeter NAME [--lang {en,sv}]
```

| Argument | Meaning |
|----------|---------|
| `NAME` | The name to greet. It must not be empty. |
| `--lang` | The language: `en` (default) or `sv`. |

Exit codes: `0` success, `2` invalid input.
