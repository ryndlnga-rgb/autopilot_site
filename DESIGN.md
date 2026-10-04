# Museum design brief

## Requirements recorded from the user

Build a new public site in `sites/` from the data behind the existing E1/E2/E3 explorers. Preserve those explorers. Provide an entrance page, connected experiment chapters, and optional mini-sites. **All pages must be self-contained HTML files.** Keep the multi-path graph animations. Make the interface intuitive, playful, polished, and useful to a visitor who has not read the paper. Explain the problem, concepts, experiment design, results, insights, implications, and limits through the journey. Give each exhibit a reason to continue.

## Theme directions

| Direction | Unifying story | Signature interactions |
|---|---|---|
| **Orbital Museum** | An observatory of possible routes, a crash chamber, and a relay station ask what survives when an agent stops. | A constellation of routes, a checkpoint capsule, simultaneous path replays, and a race using measured execution times. |
| **Continue? Arcade — selected** | Three worlds ask whether another attempt is the same journey. | Predict the next route, freeze a save point, compare respawns, and earn an optional research-log stamp. |
| **The Clockwork Expedition** | Visitors inspect the gears that turn a decision into an external effect. | Switch tracks, place a memory capsule, turn the execution crank, and hand a committed route to a second machine. |
| **Museum of Possible Futures** | Each room contains alternative continuations of the same history. | Overlaid futures, a movable crash curtain, a wall of thirty outcomes, and a drawer showing the evidence behind a claim. |
| **The Last Delivery** | A courier must finish a delivery after losing contact with its dispatcher. | API city routes, non-repeatable delivery stamps, alternate valid destinations, and a dispatcher-versus-manifest comparison. |
| **The Deep-Sea Relay** | A research sub follows a mission through branching stations; a second vessel must continue it. | Sonar routes, a black-box checkpoint, a pressure-loss event, and a timed handoff. |
| **The Time-Loop Archive** | The museum repeats the same moment and asks what changes. | Thirty parallel timelines, a frozen prefix, a route-difference lens, and a saved-future exhibit. |
| **The Research Railway** | Different locomotives traverse the same switching network, then recover after an outage. | Switchyard heatmaps, dispatch cards, route overlays, and a signal-box failover. |

The user selected **Continue? Arcade — selected**. The implementation uses a midnight cabinet, warm ivory lettering, electric lime, lilac and coral, geometric arcade art, and generous readable body type. World 1 is The Maze, World 2 is Save Point, and World 3 is Player Two. Prediction challenges, route replays, and a local research log connect the worlds. The scientific claims stay literal; decoration never changes a measurement.

## Narrative arc

1. **Entrance — Some decisions should survive a crash.** A short API-call example establishes that earlier actions may have lasting effects. Offer a guided visit or direct data exploration.
2. **E1 / The Maze — Same task. Same model. Same route?** Explain anonymized dependency graphs and thirty repeated trials. Let visitors change the model and graph, compare variation with correctness, and see why one stability score is insufficient. End: “Now stop the agent halfway through.”
3. **E2 / Save Point — We saved the past. Did we save what comes next?** Explain matched prefixes, three checkpoints, ten recoveries each, and five recovery strategies. Visitors inspect the evidence for continuity separately from valid execution. End: “A checkpoint on one machine is only half the story.”
4. **E3 / Player Two — Can another machine carry the decision on?** Explain a primary, two standbys, a service, and shared state/election. Compare Goal completion with strict correctness. Animate measured resumed-execution means while making model/system latency boundaries explicit. End: “What should the system promise before the next call?”
5. **Field guide — Decisions are part of recovery state.** Explain the design implication, the guarantees actually measured, and what remains outside the experiment.

## Mini-exhibits

- **Route Theatre:** real anonymized graphs, multiple observed paths at once, pause/step/scrub, isolate a route, select graph/model/strategy/prefix. Counts and scope remain visible.
- **Crash Lab:** an explicitly labeled illustration. Choose a route, perform one effect, crash, and try a committed continuation, a different valid route, or a repeat. Separate correctness from continuity.
- **Evidence drawers:** definitions and denominators sit one click away; advanced terminology is introduced after the plain-language question.
- **Research log:** optional local progress. No account, tracking, score gate, or forced sequence.

## Scientific presentation rules

- Read current audited CSVs for numerical claims. The draft TeX contains superseded values; the site uses its conceptual structure, not stale tables.
- Continuity is 1 − loss. For online recovery it is 1 − normalized suffix entropy; for planned execution it is the saved-suffix match rate. These are contract-specific definitions, not identical estimands.
- Correctness requires a Goal-reaching, graph-valid, non-repeating execution without extraneous calls or errors. Failed/invalid/repeating runs stay in the denominator.
- Agreement and edit distance include invalid attempted suffixes. Singleton prefixes have no pair estimate; expose their support.
- Coverage is breadth over valid irreducible continuations from the actual crash resources. It is not a success rate. An aggregate mean of fractions is not a ratio of summed counts.
- E2 matches prefixes within a condition, not across all strategies. E3 samples prefixes naturally. Do not imply paired checkpoints across strategies or directly controlled E2/E3 populations.
- E3 system latency is resumed execution, including model calls, RPCs, checkpoint/session writes, and runtime inside execution phases. It excludes detection, election, initial restoration/setup, final artifact export, and between-phase retry control. Model time is contained in system time.
- The benchmark abstracts public APIs into dependency graphs. Do not claim production API coverage, exactly-once semantics for ambiguous in-flight effects, or general fault-tolerance guarantees beyond measured crash-stop boundaries.
- E1's 39.3/19.5/41.2 entropy decomposition uses eight models; Opus remains in the nine-model behavior results.

## Source mapping

- Problem and approach: `latexs/00_abstract.tex`, `01_intro.tex`, `03_approach.tex`.
- Benchmark and E1: `04_methodology.tex`, `05_rq1.tex`.
- Controlled recovery: `06_rq2.tex` plus audited E2 methodology outputs.
- Distributed recovery: `07_rq3.tex` plus audited E3 methodology outputs.
- Interpretation and scope: `08_discussion.tex`, `09_implications.tex`, `10_limitations.tex`, `11_conclusion.tex`.

## Interaction and accessibility

Use one clear question and one primary action per exhibit. Keep direct chapter navigation visible. Defaults must show meaningful evidence immediately. Use native buttons/selects, meaningful labels, visible keyboard focus, a skip link, pause controls, reduced-motion support, and text equivalents for charts. Do not encode correctness by color alone. No mandatory animation, audio, gamification, sign-in, or scrolling trap.

## Selected arcade story: The Last Delivery

The user refined the arcade concept around lasting effects and player goals. Use a delivery arcade: the visitor is the dispatcher, the agent is the courier. Several routes may satisfy the task before commitment. The illustrative objective is to deliver one parcel, pay for transport once, and leave no unfinished reservations.

A ferry route can buy a ticket and reserve a cargo slot before the crash. These are visible, persistent world changes. After recovery, following the booked route uses those effects; turning back toward the bridge may still reach the destination but leaves the ferry reservation open; buying again causes a second charge. Movement backward is not an undo operation. An optional route preference is displayed separately from the basic delivery objective. A faithfully resumed bad plan remains a bad plan.

Keep the three worlds: The Maze (route choice), Save Point (committed future), Player Two (a new courier/process continues). The mini-game is explicitly illustrative. Real trace replays show recorded API calls and crash resources and make no invented claims about real business effects.

## Direct exploration and embedded evidence

The entrance includes a working explorer, not just links to games. Visitors switch E1/E2/E3, model, graph, and strategy and immediately see condition metrics beside real recorded routes. The same component lives inside every experiment chapter. A model × graph heatmap reveals variation hidden by averages; selecting a cell updates metrics and replay. Recovery strategy comparison holds the selected model and graph fixed, but does not imply matched prefixes across strategies. Metric definitions, trial counts, pair support, downloadable condition CSVs, and scope stay visible. Story and evidence are peers: no unlocks or required game sequence.
