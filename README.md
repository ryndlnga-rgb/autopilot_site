# CONTINUE? — The Agent Recovery Arcade

An Autopilot-branded public, offline research companion to the FSE paper in `latexs/`. It presents E1, E2, and E3 as a connected museum visit, with optional interactive exhibits and access to the underlying measurements.

**Every visitor-facing page is a self-contained HTML file.** CSS, JavaScript, selected data, and SVG illustrations are embedded. Each page works when opened directly from disk, without a server, CDN, runtime download, or adjacent asset file. Navigation links connect the HTML pages when the package is kept together.

The existing three explorers and the manuscript are read-only inputs. This pipeline does not rebuild or edit them.

## Build

From the repository root:

```sh
python3 sites/scripts/build.py
```

The build uses the Python standard library. It reads the current experiment exports and curated graph assets, checks their trial counts, validates the assets, and writes the museum HTML files and `build-manifest.json` into `sites/`. The manifest records source hashes and dataset sizes. Run with `--out /tmp/continuation-museum` to build elsewhere.

## Visitor map

- `index.html` — the museum entrance, a fully working data/graph explorer, and the three-act journey.
- `e1.html` — The Maze: Tutorial and Expert delivery/crash games, followed by expandable recorded model × graph results, replay, and metrics.
- `e2.html` — Save Point: model × graph × strategy recovery comparisons and replays.
- `e3.html` — Player Two: distributed recovery replays, quality, and model/system latency.
- `theatre.html` — multi-path animation of recorded E1/E2/E3 traces.
- `lab.html` — an explicitly illustrative, hands-on crash-and-resume experiment.
- `field-guide.html` — metric definitions, study design, evidence, and limitations.

## Source of truth

Numerical claims come from the audited methodology CSVs, not numbers copied out of the evolving TeX draft. E1 has nine models and 20 graphs; its reported entropy decomposition excludes Opus and uses eight models. E2 contains 3,600 planned recoveries; E3 contains 1,800 distributed trials. The build verifies these inputs rather than hard-coding chart results.

The public data projection includes only model/graph identities, aggregate metrics, anonymized call sequences, counts, and selected graph artwork. It excludes prompts, conversations, provider telemetry bodies, local filesystem paths, and deployment details.

Read `DESIGN.md` for the museum concept, alternative themes, and the narrative plan.

## Verify and continue

```sh
python3 sites/scripts/verify.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/plex-playwright data_analysis/.venv/bin/python sites/scripts/browser_check.py
```

The optional browser check uses Playwright and writes desktop/mobile screenshots to `/tmp/arcade-*.png`. Open `index.html` directly to visit the site. Generated pages are currently about 50 KB–1 MB each.

See `HANDOFF.md` for implementation details, completed checks, scientific constraints, and optional next refinements. Edit `src/`, then rebuild; do not hand-edit the generated pages.
