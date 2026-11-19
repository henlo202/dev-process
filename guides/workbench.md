# Workbench: the process, live in a browser

The workbench is a small web server that shows where the project stands, so the
Owner does not have to open Markdown files. It reads the repository on every page
view, so the repository stays the single source of truth: nothing is built,
cached or synced, and a page can never disagree with the files.

```bash
python .process/workbench.py                 # http://127.0.0.1:8765, this computer only
python .process/workbench.py --lan           # reachable from the local network
python tooling/workbench.py --root ~/dev     # one server for every project found under ~/dev
```

It needs nothing beyond what `status.py` needs (Python and PyYAML). It is read-only.

## What it shows
| Page | Contents |
|------|----------|
| Overview | Phase P0–P5 and the gates G0–G3, the **next step** (and whether the Owner or an agent acts, with the model class and budget), counts of requirements, ADRs and increments, increments in flight, the core documents (present, draft, template stub) and the latest gate decisions |
| Requirements | Every `REQ-` and `NFR-` with priority, status and the increment that covers it |
| Decisions | The ADRs with status |
| Increments | Status, slices ticked, budget used, and all gate decisions |
| Documents | Every Markdown file, filterable, rendered in the browser with working links between documents |

The phase and next step come from `status.py`, the same logic the orchestrator
uses. Pages refresh by themselves when a file or git state changes. `/p/<project>/api/status` returns the same data as JSON.

## Reaching it from other devices
`--lan` listens on all interfaces and prints the address, for example
`http://192.168.1.20:8765/`. On Windows, allow the port for private networks the
first time (Windows Defender Firewall). To keep it running, start it from a
scheduled task at logon.

## Safety
- GET only. It serves only `.md` files and images inside the project, never dot-folders (`.git`, `.process`), files named like secrets, or anything outside the project.
- **There is no login.** Anyone who can reach the port can read the project's documents. Use it on a network you trust, never port-forward it to the internet. Put authentication or a VPN in front of it before exposing it further.
