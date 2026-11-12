# Third-party notices

The Session Hub implementation is MIT (LICENSE). No Pane or T3 implementation
code is included or translated. Pinned research paths/licenses are in
docs/UPSTREAM_REVIEW.md. Ignored downloaded research sources are not distributable
inputs. SDK type files generated locally by Herdr checks are excluded.

## Scoped Herdr header adapter

`mods/session-hub/tabs.js` adapts the installed Herdr 0.1.15 native tabs header,
from [herdrdev/herdr-app defaults/mods/tabs/main.js](https://github.com/herdrdev/herdr-app/blob/b22936225403f38f0e6f38dd2f2fe4b444a85988/defaults/mods/tabs/main.js).
This file remains **Apache-2.0**, independently of this project's MIT license.
The full Apache license is in `mods/session-hub/assets/HERDR-LICENSE.txt`.
Changes expose functional view hooks and add one History toggle to the existing
Files/Changes controls. Shipped native header files are never overwritten; this
adapter is selected only in the new personal layout copy. Original copyright
notices in the upstream distribution remain applicable.

Offline Windows bundles include unmodified binary Python wheels. Each wheel
contains its own full license/notices; retain those files when installing or
redistributing it:

| Package | Version | Upstream license |
|---|---|---|
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause, with bundled third-party notices including OpenSSL |
| cffi | 2.1.1 | MIT-0 |
| pycparser | 3.12 | BSD-3-Clause |

Sources: [PyCA cryptography](https://github.com/pyca/cryptography),
[cffi](https://foss.heptapod.net/pypy/cffi),
[pycparser](https://github.com/eliben/pycparser).
Python, SQLite, Herdr, Node and provider CLIs are separately installed software,
not redistributed by this bundle. Their upstream licenses apply separately.

## Official Herdr artwork

`mods/session-hub/assets/herdr-logo.svg` is the unmodified official sheep mark
from [herdrdev/herdr assets/logo.svg](https://github.com/herdrdev/herdr/blob/ee5bfb5041bb3e4a49d591c72308aae3c81ecdde/assets/logo.svg),
commit `ee5bfb5041bb3e4a49d591c72308aae3c81ecdde`. The repository is Apache-2.0;
its full license is retained beside the image as `HERDR-LICENSE.txt`. The MIT
license of Session Hub does not replace that artwork license. No endorsement or
trademark ownership is claimed.

Agent icons are resolved from the installed Herdr `knownAgents()` catalog at
runtime; they are not copied into this repository or its bundle. Herdr retains
its bundled icon-source license notices. `Program.tint` controls native SVG masks
versus full-color artwork. All other Hub icons are original simple SVG drawings.
