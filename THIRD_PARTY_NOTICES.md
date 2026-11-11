# Third-party notices

The Session Hub implementation is MIT (LICENSE). No Pane or T3 implementation
code is included or translated. Pinned research paths/licenses are in
docs/UPSTREAM_REVIEW.md. Ignored downloaded research sources are not distributable
inputs. SDK type files generated locally by Herdr checks are excluded.

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
