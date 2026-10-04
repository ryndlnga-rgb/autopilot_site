# CONTINUE? — handoff

Updated 2026-10-04. A working first version of all seven pages is complete. Autopilot branding appears in the shared header/footer and entrance. No deployment or remote publication was performed.

## User intent and decisions

Build a public research arcade from the FSE paper and the data behind the existing E1/E2/E3 sites. Preserve the existing sites and manuscript. Every visitor page must be a self-contained HTML file. The selected theme is **retro arcade**, refined into **The Last Delivery**: visitor as dispatcher, agent as courier, several valid initial routes, persistent effects after a crash.

The user's latest emphasis is equal access to the story and the data. The entrance must itself support graph/metric exploration. Multi-path animations must appear in E1, E2, and E3. Do not hide data behind game progress. Show model × graph effects and model × graph × strategy results interactively, and explain implications next to them.

## Completed

- `index.html`: entrance with a working three-experiment explorer, plus the story/game entry points.
- `e1.html`: methodology, prediction challenge, model/graph selectors, six metric cards, model comparison, clickable model × graph metric heatmap, embedded multi-path replay, and scoped entropy decomposition.
- `e2.html`: recovery narrative, five strategy comparisons, exact-prefix replay, full-condition metrics, whole-experiment results, prediction challenge explaining agreement versus own-plan continuity.
- `e3.html`: distributed handoff narrative, all five strategies, replay and condition metrics, complete strategy results, separate model/system latency chart with per-model filtering and pooled mean/median/p95 model latencies.
- `theatre.html`: direct E1/E2/E3 replay and metrics.
- `e1.html` and `lab.html`: shared delivery prototype with visible moves, persistent route-specific passes and bookings, a forced crash and random alternate route, resource mismatch, and two recovery decisions. See the iteration notes below.
- `field-guide.html`: definitions, experiment scopes, strategy explanations, weighting, limitations, provenance, optional local chapter stamps.
- All explorers retain the existing shared multi-path renderer, embedded read-only. Controls: play/pause, step, scrub, start, crash point (E2/E3), route isolation, all routes, zoom, drag pan, fit, expanded view.
- Condition CSV download, including full-precision data for every condition of the selected experiment.
- Build checks all 10,800 trials and route/correctness agreement; source-hash manifest and verification scripts are included.

## Architecture and commands

Edit `src/` and `scripts/build.py`; generated HTML is overwritten on rebuild.

```sh
python3 sites/scripts/build.py
python3 sites/scripts/verify.py
PLAYWRIGHT_BROWSERS_PATH=/tmp/plex-playwright data_analysis/.venv/bin/python sites/scripts/browser_check.py
```

The build and static verifier use only the standard library. Browser verification requires Playwright/Chromium; in the current restricted environment Chromium needs execution outside the sandbox. Screenshots go to `/tmp/arcade-*.png`.

`src/frame.html` contains the shared shell. `src/style.css` supplies the arcade theme. `src/app.js` implements the shared explorer, replay controls, summaries, quizzes, latency chart, local stamps, and delivery game. Other `src/*.html` files hold page-specific narrative. `data_analysis/templates/path_animation.js` is embedded without modification.

The default output is `sites/`. `--out /tmp/continuation-museum` creates another build. The current static verifier checks the default `sites/` output. No running server is required: open `sites/index.html` in a browser.

## Verification completed

- Source counts: E1 180 conditions / 5,400 trials; E2 120 / 3,600; E3 60 / 1,800.
- Every embedded condition's trial, Goal, and correct counts match its route groups.
- Source and output SHA256 checks; local page/fragment links; no runtime external assets, fetches, or absolute workstation paths in generated pages.
- Browser checks across all seven pages at desktop and 390px mobile width, including graph controls, experiment switches, all five strategy selections, heatmap selection, and three game outcomes.
- Zero browser JS errors and zero external requests. No horizontal page overflow at the tested mobile size.
- Screenshots visually reviewed for entrance, E1, E3, and the game.
- Build verifies unchanged legacy explorers and all TeX files. Existing repository changes predate this task; do not revert them.

## Scientific details to preserve

- Use audited condition CSVs, never copy numerical claims from draft TeX tables; several manuscript numbers remain stale by the user's choice.
- Rcorr is strict valid/Goal/non-repeating/no-extra/no-error correctness, with **all trials** in the denominator. Valid non-repeat is the numerator, not another filtered population.
- A and D use attempted suffixes, including invalid/repeated attempts, within matching prefixes. Singleton groups cannot supply a pair metric; supported trial counts are shown.
- Coverage is a mean of prefix-specific fractions over valid irreducible continuations from actual crash resources. Do not present it as one pooled numerator/denominator or a quality score.
- Prefix metrics are trial-weighted inside a condition; global metric summaries weight model × graph conditions equally. Correctness counts add directly.
- Planned-strategy Ψ is own-saved-suffix match; online Ψ is 1 − normalized entropy. They assess different contracts. Perfect Autopilot Ψ does not imply perfect agreement or correctness.
- E1 has nine models; entropy decomposition uses eight and excludes Opus. E2/E3 do not include Opus.
- E1 latency is recorded trial duration. E2 model latency is additional model time after crash. E3 system time contains model time plus API/network/checkpoint/session/runtime work **inside timed resumed phases**, excludes detection/election/initial restore/setup/final export/inter-phase retry control, and is not full crash-to-finish latency.
- Actual graph names and call/resource labels remain anonymized benchmark identities. Delivery charges and reservations are explicitly illustrative, not inferred effects of recorded operations.

## E1 Tutorial and Expert levels (2026-10-04 iteration)

The user asked to preserve the first simple game as **Tutorial**, shown first, and put the richer game in an **Expert** tab. Both appear on E1 and the shared lab page. Switching tabs retains independent in-memory progress; keyboard arrows switch tabs. Recorded E1 data remains available independently below the game.

The story is now explicit: the player is Pip, a parcel robot carrying a repair part to Mara’s workshop. Pip has a generated transparent pixel avatar, embedded into each HTML file. “Navigation crash” replaces the misleading “Connection lost.”

- Tutorial preserves the simple route/pass, crash, mismatch, restore-or-buy loop. Source: `tutorial-game.html`, `.css`, `.js`.
- Expert starts with 2 credits and 7 battery. Ferry costs 2 credits / 1 crossing battery; lift costs 1 / 2 and refunds unused bookings; canal road costs 0 / 4. Each trip to/from the fork and each radio call costs 1 battery.
- Expert books a crossing, equips Pip, and sends Mara to the selected workshop entrance before driving to the fork. The planner crashes at the fork. Recovery selects another road but does not move Pip. The next action visibly follows the connected road.
- Reservations hold the ferry, keep the lift powered, or close a road barrier to traffic. They persist with the payment, equipment, and Mara’s location. Cancelling old bookings and redirecting Mara are separate battery-consuming calls. The lift refund can fund another crossing. Crossings release their own infrastructure.
- Both levels keep their action controls below the map. Expert uses a shorter map and compact HUD/console spacing so the cabinet fits common laptop viewports; browser checks cover 1366×768 and 1280×720, including the extra equipment after buying another pass. Both wallets display borrowed balances as negative credits.
- Backtracking costs energy. A charging loop costs 1 battery and 1 credit, restores 3 battery, and returns to the fork. The game permits explicitly labeled borrowing. Insufficient energy disables crossings; exhausted battery produces a failed delivery report with replay.
- Expert can finish cleanly after changing routes; it requires enough money/battery and accounting for old effects. Delivering to the workshop locker while Mara waits elsewhere reaches the destination but leaves the notification promise unfulfilled.
- Replay restores the entire crash snapshot, including the reservation, equipment, money, battery, and Mara’s location. Full restart resets just the active level.

Sources: `src/game-tabs.*`, `src/tutorial-game.*`, `src/delivery-game.*`, and `src/assets/pip-parcel-robot.png`. The builder inlines both levels and the sprite. Sprite provenance and prompt are in `src/assets/README.md`. These are invented teaching graphs and game scores, not benchmark measurements or strict correctness metrics.

Next iteration should follow user feedback on the Expert decisions and route movement; do not assume a full polish pass is wanted.

## Optional next refinements

The current package is usable. These are improvements, not prerequisites left blocking it:

1. Get user feedback on the delivery story, visual density, and the balance of games versus direct data exploration.
2. Add a paired-condition comparison panel or scatterplot to inspect two metrics at once (e.g. variation versus correctness) without replacing existing exact-condition cards.
3. Add audited prefix-specific coverage numerators/denominators to the replay panel if wanted. Do not reconstruct them by summing condition aggregates. The current cards deliberately show full-condition metrics with explicit scope.
4. Iterate on the E1 delivery prototype after user feedback; avoid a full game polish pass yet.
5. Add a printable paper-to-exhibit map or self-contained paper reading page if requested. Current pages walk through the paper's reasoning but do not embed the manuscript PDF.
6. Conduct broader accessibility review and user testing. Current checks cover native controls, focus styling, reduced-motion CSS, text equivalents, and one mobile width; they are not a formal accessibility certification.
7. If publication is requested, choose the static hosting destination with the user. Do not assume that the `sites/` folder means the Sites connector service.
