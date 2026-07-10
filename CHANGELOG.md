# Changelog

All notable changes to Stet are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and Stet
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.9.0] - 2026-07-10

Promotes the fully verified `v0.9.0-rc.2` candidate to stable with no product behavior changes. Stet 0.9 makes agentic grading decision-authoritative across verification contracts, confined binary and RewardKit judges, task decisions, and trial reports; expands Docker-free worktree execution and repairable build receipts; and ships the same asset set, source traceability, and installer behavior proven by RC2.

[v0.9.0]: https://github.com/benredmond/stet/compare/v0.9.0-rc.2...v0.9.0

## [v0.9.0-rc.2] - 2026-07-10

This candidate makes Stet's agentic grading path substantially more decision-authoritative: verification contracts now drive confined binary, pointwise, and pairwise judges into task decisions and trial reports, while build and validation receipts preserve more of the evidence needed to repair failed runs. It also expands Docker-free worktree execution and operator-facing model-comparison surfaces, while deliberately excluding the incomplete WS4 Bazel cache work before tagging.

### Added
- Add the v2.alpha agentic grading stack: verification-contract schemas and synthesis, grading workspaces, RewardKit pointwise and pairwise runners, multi-arm sidecars and ranking, a confined binary judge, prompt-only Claude transport, atomic pairwise authority, decision/report materialization, per-dimension judge controls, and a rederived 0-100 code-review score ([72304bda], [41ffe3b5], [29f27abc], [73806168], [32ebcab6], [05c44fc7], [05460567], [dc33e328], [8dcdb1b8], [d72c892d], [79308cd4], [bfc30d35], [7e2bcf30], [cb9ad226], [80a6800c], [e67481e1])
- Add a Docker-free worktree dataset-build backend, Cursor worktree execution, Codex plugin overlays, context-exclusion controls, and a customer-perspective `stet-dogfood` workflow ([aa2979d1], [1486b268], [3a65ff75], [cbfa6d7b], [082c6c89])
- Add durable rejected-task receipts and `--retry-rejected`, an honest A/B instruction floor, prompt-preserving Bazel selector support, C++/Node test-file classification, and truthful broad-fallback infrastructure taxonomy ([f6a3a4b1], [e724e98f], [feb789f5], [2450ca2d], [5d966f8d])
- Add a contact page, homepage experiment, and Sonnet 5 versus Opus 4.8 reasoning-dial material to the leaderboard ([55bad7b6], [6b0024e6], [9138d715], [9cc576f5], [f72f20e6])

### Changed
- Reduce default build flake reruns from three to two and polish the leaderboard landing and comparison guidance ([97492a8f], [174bd7cb])

### Fixed
- Keep RewardKit grading fail-closed and reproducible by invalidating stale pairwise evidence, binding workspace criteria, wiring synthesis and seeds, preserving legacy runner provenance, routing Claude through the agent judge, enforcing judge timeouts, reliably applying agent patches, and blinding the judge ([0b40caab], [f6dcc5a5], [ee09ad1e], [f9b1e802], [d67395d3], [110522dd], [2d2fed14], [c6aae863])
- Preserve evidence-bearing PASS tasks and discover manifests, accept natural grader phrasing, retry exhausted provider-schema calls, surface repairable invalid patches and multi-arm direction, and correct mechanical-cleanliness, parser, citation, truncation, and persisted-review recovery ([6296340a], [8c10eb0c], [33a1b5f6], [662ba5b6], [58ac7492], [948ef38a], [66762b4c], [e1adf9d7], [d877a754])
- Harden worktree, build, and harness evidence by completing integrity contracts, bounding discover work, proving Bazel F2P labels, forwarding batch context exclusions, and applying Codex overlay instructions and skills ([65a4bab1], [0503633f], [1a1fc15d], [ed99b575], [5bbb3dd5], [6e8f4eab])
- Make Harbor and agent startup more reliable by aligning the published agent pin, raising agent timeouts, failing fast on Cursor bootstrap no-signal runs, and tolerating concurrent Docker-cleanup races ([05396474], [78646513], [2ba1f51b], [c70ead21])
- Restore first-run quality-grader guidance and correct the dogfood brief boundary ([618e8c70], [4f0b0a09])

### Removed
- Exclude the incomplete WS4 verifier-isolation, per-task Bazel action-cache, query-output-root, and cache-proof plumbing from RC2; both the original commits and their clean reversions remain in history as evidence ([9889adbc], [7b90d738], [552f0d14], [6f6fe4c7], [3915bee2], [5e10d3be], [e6fc9006], [9f438d07])

### Internal
- Record the grader calibration harness, certification contract, gap register, corpus inventories, approval packets, scope-discipline experiments, and paused XID gap-fill state ([4cc6e4dc], [d34b9b9d], [d2d45d47], [1a39a8f8], [3e7a69bb], [d2241c11], [654aba3f], [a8fe320c], [ea51d1d3], [0dbd681e], [9779ac33], [63e397ff], [31b2856d], [ffdd4c87], [551c5542], [cb925e26], [937b7f86], [164c61a0], [8fe1caf6], [f4bd1bbd], [419a8171], [b63288ab], [8925e5d2], [021f7996], [2d806afd], [02bed6ff], [4e365ccf])
- Record RewardKit alpha guidance, calibration preregistration, judge-route amendments, timeout and provenance pins, and the agentic grader design evolution ([0e24b390], [c8ddb5fb], [8c3b973f], [67b1d70d], [87302253], [8cd2811e], [9f335bdf])
- Refresh self-dogfood recipes, ignored generated artifacts, closeout policy, beta dist prose, worktree-backend follow-ups, lead scans, pointwise grading smoke coverage, and RC2 dist skill collateral ([436908fe], [e555469e], [11db63eb], [6d972054], [db1c9f64], [1b4e985c], [31b6a504], [d7c56956], [8f8f1d73])

[v0.9.0-rc.2]: https://github.com/benredmond/stet/compare/v0.9.0-rc.1...v0.9.0-rc.2

[7b90d738]: https://github.com/benredmond/stet/commit/7b90d7383d6aeadac80fa454ded0cad7f254995a
[6f6fe4c7]: https://github.com/benredmond/stet/commit/6f6fe4c795aba55441ed458c8eda20495fe9e58f
[5e10d3be]: https://github.com/benredmond/stet/commit/5e10d3be6a092d8c6ed52dc5b7981e7e0892748b
[9f438d07]: https://github.com/benredmond/stet/commit/9f438d078d035e57cda5530514d113a14329c05c
[e6fc9006]: https://github.com/benredmond/stet/commit/e6fc9006614e908614361d545ebe0dc92994f7d1
[80a6800c]: https://github.com/benredmond/stet/commit/80a6800ca24c05cd76ad0a6a099c2bbb938418e4
[3915bee2]: https://github.com/benredmond/stet/commit/3915bee2f723062b4a91bf8b5244044175ff77eb
[552f0d14]: https://github.com/benredmond/stet/commit/552f0d1425189c7f00e552d3cbe706100bd15045
[9f335bdf]: https://github.com/benredmond/stet/commit/9f335bdfdbcabcbcf5a9634806e6b3dda266bb6e
[cb9ad226]: https://github.com/benredmond/stet/commit/cb9ad226e4f0b54fbe1c25ec64b7788acc3ce039
[7e2bcf30]: https://github.com/benredmond/stet/commit/7e2bcf3038b4682c4a670dec8ba09a496934fe4b
[bfc30d35]: https://github.com/benredmond/stet/commit/bfc30d35e485514d26cdd0b38984f0415581cfec
[79308cd4]: https://github.com/benredmond/stet/commit/79308cd4de7d18375dc6cf500b3c402adbcaf98b
[d72c892d]: https://github.com/benredmond/stet/commit/d72c892df1ad27e7e4f44e862cdbd1b00deeac3f
[31b6a504]: https://github.com/benredmond/stet/commit/31b6a5049880de3ea7dc56fa317883d491e64d79
[6e8f4eab]: https://github.com/benredmond/stet/commit/6e8f4eab47d6821a330724c215ec52f1b79edf3c
[5bbb3dd5]: https://github.com/benredmond/stet/commit/5bbb3dd5dab266c1b885b320bff75eacb84e2253
[9889adbc]: https://github.com/benredmond/stet/commit/9889adbc9ca0698391cec8cd0da5dda221981d34
[f6a3a4b1]: https://github.com/benredmond/stet/commit/f6a3a4b10070db1c2d9595a617907fba63c38a2d
[d877a754]: https://github.com/benredmond/stet/commit/d877a7547276cd96d12626b49d0ee7bf9f870b8f
[e1adf9d7]: https://github.com/benredmond/stet/commit/e1adf9d7ab51a70d0ce85e66584c05e656efe397
[66762b4c]: https://github.com/benredmond/stet/commit/66762b4c3436a159f80faf2d2a90160cecc5c37d
[e724e98f]: https://github.com/benredmond/stet/commit/e724e98fe5cbb3522cef6e90fdd8763b492ba2c3
[6d972054]: https://github.com/benredmond/stet/commit/6d9720546676478c92cd95d4eb017044e1919a04
[5d966f8d]: https://github.com/benredmond/stet/commit/5d966f8d26ba9827c6dea1476e7e9d78f76583d8
[2450ca2d]: https://github.com/benredmond/stet/commit/2450ca2d2d9c2e8c1af96d161f9abe7b5f737f94
[feb789f5]: https://github.com/benredmond/stet/commit/feb789f5952975675b349d1d3a96110945612752
[97492a8f]: https://github.com/benredmond/stet/commit/97492a8f326875524aa10c0c821a1ebfdd82a2fe
[f72f20e6]: https://github.com/benredmond/stet/commit/f72f20e678949c3df3d247ab1b184a9c80d114eb
[9cc576f5]: https://github.com/benredmond/stet/commit/9cc576f578be51c2c5200e6a3054c6809acc1b7b
[db1c9f64]: https://github.com/benredmond/stet/commit/db1c9f649bb1178692e3517cfa1f8bdd693a6838
[aa2979d1]: https://github.com/benredmond/stet/commit/aa2979d1d7b4c55f380fabeb287a7a485ed88dfb
[ed99b575]: https://github.com/benredmond/stet/commit/ed99b5755e22bbf0af20b867c83b79a7a1cd3927
[9138d715]: https://github.com/benredmond/stet/commit/9138d715cd4af9b7ceb66c9a7027bfddf2c96fce
[1a1fc15d]: https://github.com/benredmond/stet/commit/1a1fc15d32614e312f4c87676652e47e6c3d3ce6
[0503633f]: https://github.com/benredmond/stet/commit/0503633fedb68076b3104d82ec1cb62c08e2bf25
[65a4bab1]: https://github.com/benredmond/stet/commit/65a4bab1fae324b9f07e5075eb70b02978f0b8d2
[e67481e1]: https://github.com/benredmond/stet/commit/e67481e187f0d43bfe92c6add26ead7575db8cdd
[1486b268]: https://github.com/benredmond/stet/commit/1486b268ed48244e0149c6f947370f337a385a49
[948ef38a]: https://github.com/benredmond/stet/commit/948ef38a74fae006151558a72e00d042e4ca1499
[6b0024e6]: https://github.com/benredmond/stet/commit/6b0024e69bcf7a1561ed3c0e53415678f1b01f3f
[c70ead21]: https://github.com/benredmond/stet/commit/c70ead21b894255f4d28bdf7c270ea40c6047fd3
[2ba1f51b]: https://github.com/benredmond/stet/commit/2ba1f51bfee614cad52a03308930853511cf9de9
[8cd2811e]: https://github.com/benredmond/stet/commit/8cd2811e525851436e6131f9ad54471fe4a5028c
[c6aae863]: https://github.com/benredmond/stet/commit/c6aae863bfa12ec57a5761623a94ddcac09d8bbd
[cbfa6d7b]: https://github.com/benredmond/stet/commit/cbfa6d7baa89a4143f465f652503214fcfe75901
[87302253]: https://github.com/benredmond/stet/commit/87302253a3f9aae873be5574ee5c2d7854865a40
[2d2fed14]: https://github.com/benredmond/stet/commit/2d2fed14687ba3d0d01dd19c282d689786f72de9
[67b1d70d]: https://github.com/benredmond/stet/commit/67b1d70dc0c65307c70a6cc5832275989c200891
[110522dd]: https://github.com/benredmond/stet/commit/110522dddd1c9f168d45db1a439e46b141a27cc1
[8c3b973f]: https://github.com/benredmond/stet/commit/8c3b973f16092c17af8d8b417fa3a096e9f78c06
[d67395d3]: https://github.com/benredmond/stet/commit/d67395d30f24b00d54e62ef747f74c287bc717dd
[c8ddb5fb]: https://github.com/benredmond/stet/commit/c8ddb5fb7039020267bd3fc34d09d5d0c973ee4b
[f9b1e802]: https://github.com/benredmond/stet/commit/f9b1e802e8f1ebc547627af246bf40898a07942e
[1b4e985c]: https://github.com/benredmond/stet/commit/1b4e985cd092b277d751489dfc3d49556f30377e
[174bd7cb]: https://github.com/benredmond/stet/commit/174bd7cbd7bc5a10679c59103c02d5f418d01a6e
[11db63eb]: https://github.com/benredmond/stet/commit/11db63eb1b10ec229b72bc7160db6e99f894d69b
[58ac7492]: https://github.com/benredmond/stet/commit/58ac74923586f063e79824308fe7ace951c14e11
[662ba5b6]: https://github.com/benredmond/stet/commit/662ba5b6b86241368982a607d5483c3340756cea
[3a65ff75]: https://github.com/benredmond/stet/commit/3a65ff754df20186ca8765ca30e930be91a41215
[436908fe]: https://github.com/benredmond/stet/commit/436908fe72f23259346807856af11c6c7d47bf94
[e555469e]: https://github.com/benredmond/stet/commit/e555469e436efaa02696f9180665b64862c02ab5
[78646513]: https://github.com/benredmond/stet/commit/786465132254815e08c3f142265dab2139cdc160
[0e24b390]: https://github.com/benredmond/stet/commit/0e24b390f5540b889cf3fc66bea20bbd69728d9f
[ee09ad1e]: https://github.com/benredmond/stet/commit/ee09ad1e3eac17d685bafaa7d7779071dcdbe00d
[f6dcc5a5]: https://github.com/benredmond/stet/commit/f6dcc5a56c838e0a21ded4fedf2c2063523a788a
[d7c56956]: https://github.com/benredmond/stet/commit/d7c569563a2c5a48bd1335036cc940df891a6100
[0b40caab]: https://github.com/benredmond/stet/commit/0b40caabd3503830f10374a7e1a8da17ede4da19
[8dcdb1b8]: https://github.com/benredmond/stet/commit/8dcdb1b8ddba8a98c6d3e45402b2e5738d0aaf76
[dc33e328]: https://github.com/benredmond/stet/commit/dc33e328e0ac0c782fabf48ace2a62befcb58b3b
[05460567]: https://github.com/benredmond/stet/commit/054605676c678926e7cfaa2b34b4264ea71c85e5
[05c44fc7]: https://github.com/benredmond/stet/commit/05c44fc73db8565c4fe11dd09ba0786fe5cf6bff
[32ebcab6]: https://github.com/benredmond/stet/commit/32ebcab67076f2b387ced90dbc429593cd2a03f6
[73806168]: https://github.com/benredmond/stet/commit/73806168c2bd5f83fb76e8dd8ef99717acae208e
[29f27abc]: https://github.com/benredmond/stet/commit/29f27abc60d40e66df324aa586559c75bd362670
[41ffe3b5]: https://github.com/benredmond/stet/commit/41ffe3b513ca490c55a23f19a5c4c887760ffca8
[4e365ccf]: https://github.com/benredmond/stet/commit/4e365ccfd755ad47d39afa8b1a722d1e058eadeb
[72304bda]: https://github.com/benredmond/stet/commit/72304bdaf87c3b83344b2a35e9b3fee9f5cd8314
[02bed6ff]: https://github.com/benredmond/stet/commit/02bed6fff5073e3b33ebd559f23dfd71d28c0f30
[2d806afd]: https://github.com/benredmond/stet/commit/2d806afdf24f239e551f310ba7c6731daf203202
[021f7996]: https://github.com/benredmond/stet/commit/021f7996b3a58e8b7240a3da1380a921273913aa
[8925e5d2]: https://github.com/benredmond/stet/commit/8925e5d21e3efa922784bbda85e965d8c6180c57
[b63288ab]: https://github.com/benredmond/stet/commit/b63288abce4ea2208d61ca343191038b40d1f4a3
[419a8171]: https://github.com/benredmond/stet/commit/419a8171693d7b66f05d3de4a61279e56ecef356
[f4bd1bbd]: https://github.com/benredmond/stet/commit/f4bd1bbd2ebdd58a309543142d400341c43bb7f7
[8fe1caf6]: https://github.com/benredmond/stet/commit/8fe1caf6c877f8108dde5ed5f331fb61348ad63c
[164c61a0]: https://github.com/benredmond/stet/commit/164c61a04c87564c572acabc3d779d8c14fc72b1
[937b7f86]: https://github.com/benredmond/stet/commit/937b7f86b9b417c714a599ac96e514cea0f913b9
[cb925e26]: https://github.com/benredmond/stet/commit/cb925e26e0f99a6dd25450e750c96b843a413007
[551c5542]: https://github.com/benredmond/stet/commit/551c5542731defa85deb61191c6a1430b6869f8b
[ffdd4c87]: https://github.com/benredmond/stet/commit/ffdd4c870037bfe19010b84cf8f2731d22a3cdcb
[31b2856d]: https://github.com/benredmond/stet/commit/31b2856d77fb504966e310dde168789f582f200c
[63e397ff]: https://github.com/benredmond/stet/commit/63e397ff7d4657726d6b07264dba9c8515417aec
[9779ac33]: https://github.com/benredmond/stet/commit/9779ac33e79daa076a8f776f57df82b3936e7739
[0dbd681e]: https://github.com/benredmond/stet/commit/0dbd681e07343ea53fcf14100796cde5d8f7038a
[ea51d1d3]: https://github.com/benredmond/stet/commit/ea51d1d3ceafcbbc4aa0ca24f1b7417f15b44e1d
[a8fe320c]: https://github.com/benredmond/stet/commit/a8fe320cda1ae3cfbd85b1025fad56b597a91f6b
[654aba3f]: https://github.com/benredmond/stet/commit/654aba3f24a6e906d728e117cc3dd812eae300c0
[d2241c11]: https://github.com/benredmond/stet/commit/d2241c11a9557fd3f1e9f927b7357375ced5a301
[3e7a69bb]: https://github.com/benredmond/stet/commit/3e7a69bb8c1ee47ccff0fff118e9da992888370d
[1a39a8f8]: https://github.com/benredmond/stet/commit/1a39a8f876e7d4b161f08cbad70e0d258fbe01cb
[d2d45d47]: https://github.com/benredmond/stet/commit/d2d45d477d30b326a49a9631d62023445b6f43cb
[33a1b5f6]: https://github.com/benredmond/stet/commit/33a1b5f6f2bfc51bf43526437a7208a9b835793b
[d34b9b9d]: https://github.com/benredmond/stet/commit/d34b9b9d770bfc987e97062848ab32d925b4d006
[4cc6e4dc]: https://github.com/benredmond/stet/commit/4cc6e4dc72cff7febddf2a9e79cb25440518e7ae
[8c10eb0c]: https://github.com/benredmond/stet/commit/8c10eb0c955bb0bf56db515f55981dc88694fb19
[6296340a]: https://github.com/benredmond/stet/commit/6296340a20777e0271b7b03d7cc7f11173d38e3d
[4f0b0a09]: https://github.com/benredmond/stet/commit/4f0b0a09e3221fb1fc47924ecddcf6a2fbfac715
[082c6c89]: https://github.com/benredmond/stet/commit/082c6c897f56ed12a730def87d6abac5e15ecd03
[05396474]: https://github.com/benredmond/stet/commit/05396474cec0e3732ef4e279283d8f2f03fe706e
[55bad7b6]: https://github.com/benredmond/stet/commit/55bad7b6b5ee308f14ebad8e06cade4f59fcc04f
[618e8c70]: https://github.com/benredmond/stet/commit/618e8c70e1fbf5343df3275371c841725538a320
[8f8f1d73]: https://github.com/benredmond/stet/commit/8f8f1d7327dce6a76df38624910929a21fc55a6a

## [v0.9.0-rc.1] - 2026-07-06

Adds an interpretation layer to Stet receipts so coding agents get a trusted, performance-first read of an eval instead of relaying a bare posture token, calibrated confidence so strong evidence can promote without over-hedging, and a pinned grader identity so decision-grade evidence is reproducible. Operators also get per-arm harness levers (Claude Code plugin overlays), native Windows builds, and unified disk reclaim.

### Added
- Surface a machine-readable `interpretation` block on eval receipts: a preflight brief for `eval rules plan` that forbids performance claims pre-run and frames inspect/invalid/blocked as fixable states with the charged next action, plus a performance read for `eval report` that leads with how the candidate made the agent perform on real tasks — per-grader quality tallies, gold-test 3-state flips, credited rescue lanes, and token direction — with evidence confidence demoted to a secondary honesty rail ([3476fe71], [079cab46])
- Calibrate confidence on eval compares: direction-aware P(superiority) on every bootstrap metric, gold-correctness Beta-Binomial on task flips, a calibrated strong-correctness bypass that lifts inspect to promote (P≥0.95 + 0 regressions, or quality-dim P≥0.95 with majority support) while structural blockers still force inspect, and a promote-with-caveat path allowing one isolated regression at P≥0.90; honesty floor preserved on evidence_quality and claim entries ([079cab46])
- Pin grader identity for decision-grade evidence: compile-time grader bundle sha256, judge prompt-template digest, and reducer version freezable via `stet graders promote`, with `stet graders status|show` classifying the running binary against the pin and compare execution refusing under drift before arm spend; candidate/scratch/drifted builds always force inspect so they can never yield decision-grade claims; with no pin, behavior is byte-identical to today ([e073a019])
- Add a per-arm `plugin_overlay` run-config lever that activates a pre-baked Claude Code plugin/hook/MCP HOME snapshot (e.g. Caveman, Ponytail, RTK, Context Mode) with a fail-fast activation assertion, in both the worktree and Harbor/Docker backends, via `stet eval run --plugin-overlay <dir>`; a missing or failed activation records a typed `plugin_not_active` failure and drops the patch without suppressing real agent failures ([b75026c1])
- Add Windows build support: cross-compile and package `stet.exe` as a zip asset, an `install.ps1` for Windows install, and a self-update swap helper since Windows cannot overwrite a running executable in place, plus a `windows-latest` CI job that builds, installs, and runs `stet.exe` ([26e8c9dd])
- Surface trajectory/behavioral metrics in multi-arm compare: per-arm standings, pairwise deltas, and win/loss/tie for tool_calls, shell_calls, trajectory_length, and patch_rewrite_ratio, plus new bounded `time_to_first_edit` and `new_files_added` metrics, with `eval_report.behavior` now populated ([55d13685])
- Extend variance-reduction estimator blocks (per-pair raw-delta + Wilcoxon + CUPED with gold-patch-size covariate) to the continuous quality dimension graders on `stet eval compare --multi-arm`, matching the two-arm path so dimension comparisons are statistically tighter; strictly additive and categorical graders stay on McNemar ([163a7e3a])
- Render a per-arm "Behavioral recall" panel in `stet eval` output and `eval_report.v1.json`, showing the strict precise-gold-fn pass-rate as a high-precision lower bound against the recall-supported rate, with a credited / inconclusive / non_solve breakdown; stays silent on clean test-backed corpora ([9f059a31])
- Add `claude-sonnet-5` to the model-name registry (alias "sonnet 5") and the h2h pricing table ([3eb46f7c])
- Show grader-level and per-task interpretation summaries in the HTML report, sourced from each grader's interpretation object ([9d0531cd])
- Add `--rebuild-builtin-prompts` regrade mode that re-renders built-in equivalence/code-review grader prompts from the current embedded template instead of re-grading the stored prompt, with a retained-patch fallback for locating agent patches ([8fa249a8])
- Add a `graded_equivalence` derived 0-4 score grader projected from the binary equivalence payload, surfacing per-grader scores and code-review rubric scores on task detail, plus `stet runs regrade-graders --rederive-only` to backfill derived artifacts from `validation.json` with zero LLM calls; back-compat-preserving (excluded from grader-profile fingerprints, compares admit it only when a persisted decision metric exists on both arms) ([358d3592])
- Add `stet graders` surface alongside the grader-identity pinning: `stet graders promote|status|show` for pinning and classifying the live grader profile ([e073a019])
- Surface selector-proof coverage in eval output and named eval-study receipts for tracked comparisons ([75bf293a], [40f939dc])
- Add explicit quality posture selection to `stet init` ([6cc90580])

### Changed
- Interpretation rewrite: confidence tier (strong/likely/flat) with odds-language ("19-in-20"), a composed VP-ready one-liner, a headline that leads with effect-size and always names any regression, and `must_convey`/`must_not_claim` obligations that enforce plain, jargon-free wording; all agent-facing strings de-jargoned ([079cab46])
- Unify disk reclaim behind one `Reclaimer` engine: root scratch/patch, the Harbor export cache, and Docker/Harbor daemon objects now share one dry-run/JSON/byte-accounting contract via `stet artifacts compact --include-docker`, with no change to what any existing engine deletes or when it deletes automatically ([ad9c9a50])
- Auto-resolve the evaluator provider and pin the requested model on the evaluator subprocess via `--ai-model-id`, and inject Claude OAuth env into the evaluator and preflight shell commands so the evaluator invokes the intended model rather than the provider default ([9c061817], [e180a03c])
- Require non-interactive `stet init` (`--yes` or non-TTY) to fail fast and write no config when a runnable provider is detected, requiring an explicit `--ai-provider`; `eval rules plan` now reports the full enforced quality grader panel instead of letting a legacy evaluator-only profile suppress it ([a8926d3e])
- Switch the Harbor eval image to `python:3.12-slim` + uv, replacing the hand-rolled terminal-bench Ubuntu image ([53d4746b])
- Pin the harbor CLI bundled by Stet to 0.17.1 (was 0.8.0) ([069da7ac])
- Tighten review and equivalence grading: add a ship-decision rubric and verifier-contradiction guard to the review grader, require strict obligation-aware equivalence parsing with a malformed-output retry loop, and tighten the craft/discipline grader rubrics for scoped-ownership and near-equal-footprint judgments ([63a66a3b], [28382292], [3c78e2d2])

### Fixed
- Make `stet dataset regenerate-f2p` idempotent and align rules fixtures with the digest gate so repeat runs don't re-derive clean artifacts ([888c69dd])
- Detect subscription/rolling usage caps (e.g. z.ai 5-hour "Usage limit reached") in the quota classifier so quota-killed tasks are recorded as hard-runtime rate-limit failures and engage the resume path, instead of being recorded as honest no-patch results that bias validity and skip on `--resume` ([e55376c7])
- Recover usage-limit-masked cells and partial-arm Harbor resume so interrupted compares don't silently drop arms ([e4166afd])
- Resolve `--grader-ai-model-id` independently on the experiment validate path and forward the Claude setup-token to remaining evaluator/grader clients so invoked-model provenance is correct ([0857afb5], [92a54d6a])
- Recover rules reports across manifest aliases and derive `repair-patches` evaluator from the suite `grader_ai_cmd` so repaired runs grade with the intended model ([49b11bee], [80aeded2])
- Write `repair-tests` `validation.json` flags as a canonical object and accept legacy string-array flags in `MatrixFlags` decode ([e977e40c], [d6a55300])
- Decouple `--stitch-rerun` merge-back from full validate+grade so real agent patches land in canonical runs per-cell best-effort, with a `pending-stitch.v1.json` breadcrumb and recovery command on unrecoverable merges ([f969e137])
- Generalize the run-root integrity guard so partial roots cannot read as "complete" and `regrade-graders` summary/report writes are atomic and stale-safe on partial failure ([a492bacc], [8fc611d6])
- Resolve `agent.patch` across run-root layouts in `repair-patches` ([0bf5fb2e])
- Stop forcing cargo offline when the install runs at RUN time, fixing Rust task builds ([6f84e978])
- Tolerate prose preamble in quality-lane assessor JSON and clamp over-deep rev-ranges on short-history repos during discover ([bd8d425c], [cef0254b])
- Allow dataset-backed rules suites to omit `selection.mode` and give an honest weak-signal off-ramp for zero-yield onboarding instead of a confusing failure ([57a9ada4], [ff86a6f1])
- Reuse build gold/F2P proof under identity match so equivalent rebuilds don't re-prove the feature ([4fffea4d])
- Converge `human_patch_guard.py` to a class-based source-fetch denial for the Harbor verifier ([98dfd9e1])
- Reuse proved selectors for rules replay validity and credit repaired targeted-F2P cells as discriminating test verdicts ([f7955bdd], [2cf4c352])
- Block partial instruction datasets, tiny config-diff slices, and instruction bootstrap shortcuts during onboarding, and enforce the onboarding task floor for instruction rules so low-quality datasets can't slip through ([c6529d4c], [c805053c], [f80c7d9e], [cd9693f3])
- Make onboarding honest and directional: surface directional inspect signal, actionable partial-dataset repairs, onboarding receipt blockers, test-relevance-mismatch warnings with lifecycle guidance, and guide wrapper repos to their implementation roots ([8a264f91], [0310b58f], [6e79eeb3], [637a6e3c], [2cdffdd8])
- Recognize locked uv pytest selectors, dependency groups, transparent test wrappers, pest test selection, and valueless flags, and retain F2P selector/rejection evidence during build ([5832b008], [6fcfcf81], [8283b7dd], [8af2c25d], [75ec9322], [43493c52], [f965a9e5], [2a3e352f], [0d0df83d])
- Fail closed on unbuildable install-config synthesis and on partial suite roots; classify targeted runtime unknowns as infra and separate executor/infra runtime failures from dataset failures ([44b5da1d], [9e96eb78], [59c7dacc], [82280491])
- Resolve test commands into inspectable command plans for targeted F2P (npm/pnpm/yarn/bun aliases, safe `&&` chains), with provenance recorded, so new language onboarding yields ready tasks instead of zero-yield builds ([d8b82caf])
- Preserve configured test commands in suite build, bootstrap uv starter harnesses and task environments, and improve python uv onboarding defaults ([5c8f60ad], [918bd7d0], [1a0841a8], [214d31ba])
- Make `--stitch-rerun` merge-back honor recipe tests for onboarding builds and keep `tests.failure_mode` coherent after test repair ([978876f2], [d81ef68c])
- Stop pinning node and toolchains in the generated harness, and install Go in the generated onboarding harness ([a6e27868], [07261287], [c1bfc18d])
- Surface grader claim readiness and missing-equivalence repair guidance in status; treat post-write grader gaps as inspect, clear stale `no_test_signal` exclusions on repaired cells, and auto-repair fresh grader coverage gaps while keeping recommended quality on instruction graders ([bbb9c839], [0d01a422], [59296b07], [2009491d], [e0bc10b0], [f2f10108])
- Bundle history from shallow clones, report dev-source commits, and loosen the default install allowlist ([638ed9be], [6a92b85c], [3e319224])

### Removed
- Delete the pre-product Python F2P selector scripts (`fix_f2p_test_selectors.py`, `write_f2p_targeted.py`, `verify_f2p_targeted.py`) now that function-level F2P selection lives entirely in the product via `stet dataset regenerate-f2p` ([9c472648])

### Internal
- Add build-time BuildKit task-dependency cache mounts for Harbor image bakes, replacing the broken run-time bind-mount cache that never populated; on by default, opt out with `STET_TASK_DEP_CACHE=off`, with reclaim via `stet harbor cleanup --prune-buildkit` ([07d69145], [7ef559f2], [5c5fb536])
- Dedup the Harbor export cache via a content-addressed blob store (files ≥1 MiB stored once and hardlinked) and cut eval-run I/O churn via snapshot excludes and copy-on-write export copy ([f48b0a6c], [b99f3cc6])
- Land grader-discrimination calibration internals and evaluator OAuth env plumbing ([e180a03c])
- Collapse six repair/rerun verbs (`--stitch-rerun`, `repair-patches`, `revalidate-tests`, `repair-tests`, `repair-ai-coverage`, `regrade-graders`) onto one invariant-preserving run-mutation substrate so atomicity, breadcrumbing, derived-artifact regeneration, scratch GC, and the integrity check are defined once behind a commit chokepoint; behavior-preserving with no change to verb flags or behavior ([715dbbdd])
- Refresh onboarding prompts, agent docs, and rules-skill-loop guidance, and rename craft/discipline graders to quality graders in skill docs ([99d45afa], [9874c882], [133bcfab], [0967129c], [8395ebca])

[Unreleased]: https://github.com/benredmond/stet/compare/v0.9.0...HEAD

[v0.9.0-rc.1]: https://github.com/benredmond/stet/compare/v0.8.0...v0.9.0-rc.1

[3476fe71]: https://github.com/benredmond/stet/commit/3476fe710e7582c5bebdc6b8333fdc9e6364e58a
[079cab46]: https://github.com/benredmond/stet/commit/079cab46345c58f4c947b7cececc477acfcf177a
[e073a019]: https://github.com/benredmond/stet/commit/e073a0199c4dc72a20c93795407ad27df773fec3
[b75026c1]: https://github.com/benredmond/stet/commit/b75026c10d36faf910c076f9e60bb0ca3109655b
[26e8c9dd]: https://github.com/benredmond/stet/commit/26e8c9ddd93e834f5b97bedf98a6763a30e4b227
[55d13685]: https://github.com/benredmond/stet/commit/55d13685c46f274543d07da140ebb6b0eeb93b3a
[163a7e3a]: https://github.com/benredmond/stet/commit/163a7e3a397b7f3208ba1dda0076e09208c2dce9
[9f059a31]: https://github.com/benredmond/stet/commit/9f059a3103413add442bb976c1cb6058646ea944
[3eb46f7c]: https://github.com/benredmond/stet/commit/3eb46f7cc6634da0abaecda13ed86adb8b5d7a5a
[9d0531cd]: https://github.com/benredmond/stet/commit/9d0531cd1b7fa53a830b6a09f85e35793f7680bc
[8fa249a8]: https://github.com/benredmond/stet/commit/8fa249a8c70de05a7fda27c732fc7af888782daa
[358d3592]: https://github.com/benredmond/stet/commit/358d3592fa7baf108bf5e485a3ddf02e69ccb2d4
[75bf293a]: https://github.com/benredmond/stet/commit/75bf293ab55fd38f58bdc2bb219e10827c9f4c01
[40f939dc]: https://github.com/benredmond/stet/commit/40f939dc1ecbd01699e89ee501387f0bc1cc25d2
[6cc90580]: https://github.com/benredmond/stet/commit/6cc9058002639b3ec2ee1260cb759def7e837b03
[ad9c9a50]: https://github.com/benredmond/stet/commit/ad9c9a501f3645a75385480981dea95f4512fa52
[9c061817]: https://github.com/benredmond/stet/commit/9c0618178309d1122eb4fc4fba45af32995253cf
[e180a03c]: https://github.com/benredmond/stet/commit/e180a03ccea9d1bc45171cdb66ada9ba2a579a63
[a8926d3e]: https://github.com/benredmond/stet/commit/a8926d3eb8ad08db3948d9295b2f06f0d8a16313
[53d4746b]: https://github.com/benredmond/stet/commit/53d4746b7fe455fc377280f6ebd4a18f21f05eb7
[069da7ac]: https://github.com/benredmond/stet/commit/069da7ac79d46b0792903de801330ad6497d5fcd
[63a66a3b]: https://github.com/benredmond/stet/commit/63a66a3be66c9c3e176dcc5a23c7ead49129508a
[28382292]: https://github.com/benredmond/stet/commit/283822928648c5ede805c117ae90e67d73da27ac
[3c78e2d2]: https://github.com/benredmond/stet/commit/3c78e2d2d52db02a4a3b9f073ad699a8c69bc700
[e55376c7]: https://github.com/benredmond/stet/commit/e55376c7e1b1b5acf7435acb2b9f9567ce02f14e
[715dbbdd]: https://github.com/benredmond/stet/commit/715dbbddefecf80d21736ca958ca1238ab148410
[888c69dd]: https://github.com/benredmond/stet/commit/888c69ddaae582d99e74d7e73127f9206ea5b78c
[e4166afd]: https://github.com/benredmond/stet/commit/e4166afd50313587cc3080281f952fc4d7c5f76c
[0857afb5]: https://github.com/benredmond/stet/commit/0857afb5c5d51e55b16131cf06ecf424756d7f7a
[92a54d6a]: https://github.com/benredmond/stet/commit/92a54d6a4b1c32baf7a8a1d6c9db55b63a754113
[49b11bee]: https://github.com/benredmond/stet/commit/49b11bee3fb02bd1ed326608c507d6ffafab1516
[80aeded2]: https://github.com/benredmond/stet/commit/80aeded25e919d151c02b6135956b63e54e20b7d
[e977e40c]: https://github.com/benredmond/stet/commit/e977e40cb8264537ff7abbbbf89954b5821a4a05
[d6a55300]: https://github.com/benredmond/stet/commit/d6a553005f8156370529fb47b970433b8f9ce7e1
[f969e137]: https://github.com/benredmond/stet/commit/f969e137c643950fe59f9d50a50032d2693060d6
[a492bacc]: https://github.com/benredmond/stet/commit/a492bacc286d37df3643d8e23115ec6459ddf47f
[8fc611d6]: https://github.com/benredmond/stet/commit/8fc611d6182493d1b94cf172ea420dddee8580db
[0bf5fb2e]: https://github.com/benredmond/stet/commit/0bf5fb2ea2637dd9a7e6b4e52ad91d0775ad75a2
[6f84e978]: https://github.com/benredmond/stet/commit/6f84e9786989cb800be163b5eaf75ed76b1a612d
[bd8d425c]: https://github.com/benredmond/stet/commit/bd8d425c1ed5948385f87cd54581ce81e80ab5f9
[cef0254b]: https://github.com/benredmond/stet/commit/cef0254b8046534cd01dadeae910fe90fadf3a22
[57a9ada4]: https://github.com/benredmond/stet/commit/57a9ada48f28e42f1c599309cb5f53ae7cc4092c
[ff86a6f1]: https://github.com/benredmond/stet/commit/ff86a6f1bbbc1ab978451f158086380f6f2758ce
[4fffea4d]: https://github.com/benredmond/stet/commit/4fffea4df98fff8bdb7e9474ac9f3cf5b73a214d
[98dfd9e1]: https://github.com/benredmond/stet/commit/98dfd9e1b00f331357f2152ac6de83e9edf6ed4c
[f7955bdd]: https://github.com/benredmond/stet/commit/f7955bdd6954e1153c8205ca2f2cdaf93368c5a6
[2cf4c352]: https://github.com/benredmond/stet/commit/2cf4c352a85acaf8c41e644daa643363fd88f2e7
[c6529d4c]: https://github.com/benredmond/stet/commit/c6529d4ca325f056d13a0f082c73b2a4adf22e04
[c805053c]: https://github.com/benredmond/stet/commit/c805053cea6d605f3454438db6f901c216a30375
[f80c7d9e]: https://github.com/benredmond/stet/commit/f80c7d9e7acac3851f7bd4f7a81fc5a3c9db6fc9
[cd9693f3]: https://github.com/benredmond/stet/commit/cd9693f3a14ff57190ed2b8bf7e06d096f21e7ca
[8a264f91]: https://github.com/benredmond/stet/commit/8a264f91b8baa9b6a56b532141ba3e254f284836
[0310b58f]: https://github.com/benredmond/stet/commit/0310b58f32e2e8177862cfccf97575894215c691
[6e79eeb3]: https://github.com/benredmond/stet/commit/6e79eeb3784eae380913c9d5c29d550fd1053f9c
[637a6e3c]: https://github.com/benredmond/stet/commit/637a6e3c2e6a5a74152880e4d17f0919106e8717
[2cdffdd8]: https://github.com/benredmond/stet/commit/2cdffdd823178ed78e3b03a6048c50d46df57a79
[5832b008]: https://github.com/benredmond/stet/commit/5832b008ae79fc6ce0dfe51a0d146905787c0cf8
[6fcfcf81]: https://github.com/benredmond/stet/commit/6fcfcf81b58b6d13892a036217e6452efea59d6a
[8283b7dd]: https://github.com/benredmond/stet/commit/8283b7dd4a9708ee56de5fbc1dcb08ddaf4b116c
[8af2c25d]: https://github.com/benredmond/stet/commit/8af2c25db6b4354df637f786d8a199b5f4e37863
[75ec9322]: https://github.com/benredmond/stet/commit/75ec9322cce33660d0bba5177d1e149f32cb76fa
[43493c52]: https://github.com/benredmond/stet/commit/43493c529dcc3d388955b1f611cd49be7db1a719
[f965a9e5]: https://github.com/benredmond/stet/commit/f965a9e58f8dd3dd4f20093e37fb0012752c7bdb
[2a3e352f]: https://github.com/benredmond/stet/commit/2a3e352ff4c86cee396fe18145341785480db96b
[0d0df83d]: https://github.com/benredmond/stet/commit/0d0df83d78ef8916c5c1df0fb24335a4e7cfeec0
[44b5da1d]: https://github.com/benredmond/stet/commit/44b5da1d9490f0d6f77c39f7f91e9f150be7e2b2
[9e96eb78]: https://github.com/benredmond/stet/commit/9e96eb784dc5b45a7662ccbe6533aeffae406b9c
[59c7dacc]: https://github.com/benredmond/stet/commit/59c7dacc97baf476156f396b391cf7cf26d062cc
[82280491]: https://github.com/benredmond/stet/commit/8228049199d913678d7bbb334566e26875db01c3
[d8b82caf]: https://github.com/benredmond/stet/commit/d8b82cafe065be230f6ed0c774bce7127f2cade0
[5c8f60ad]: https://github.com/benredmond/stet/commit/5c8f60ad6c351e41d3fd6e835b03dc1eb98f29e1
[918bd7d0]: https://github.com/benredmond/stet/commit/918bd7d035cdb7023aa8d0cc79f6c09b66a2e7c6
[1a0841a8]: https://github.com/benredmond/stet/commit/1a0841a8ee04fa090666eaaf18b6b4c0f6e50baa
[214d31ba]: https://github.com/benredmond/stet/commit/214d31ba13e8ac97d632eeec0cedceaf73d32120
[978876f2]: https://github.com/benredmond/stet/commit/978876f293471de8e955e9bcf126bb7813db2d9d
[d81ef68c]: https://github.com/benredmond/stet/commit/d81ef68cea1c7d93527acfd260d662665af122bb
[a6e27868]: https://github.com/benredmond/stet/commit/a6e278686c1ab2d34ab12fa5c6d8e2f3c8d2727a
[07261287]: https://github.com/benredmond/stet/commit/07261287eb49f55eef2182cf018f627f660e48df
[c1bfc18d]: https://github.com/benredmond/stet/commit/c1bfc18d7ca79a894a4f42dafc1fe211a0b87f45
[bbb9c839]: https://github.com/benredmond/stet/commit/bbb9c839330b6305ac85d5a032716e053c671aae
[0d01a422]: https://github.com/benredmond/stet/commit/0d01a422e900517e147d2503525167e24ed6cc14
[59296b07]: https://github.com/benredmond/stet/commit/59296b07e955cb30b6381fc07e38c1af4d87e33d
[2009491d]: https://github.com/benredmond/stet/commit/2009491d22c3b23f4a7035e95a884d0fdbea6ce4
[e0bc10b0]: https://github.com/benredmond/stet/commit/e0bc10b08f0817591b4f23fa4acc6ef4931d0a23
[f2f10108]: https://github.com/benredmond/stet/commit/f2f1010837db5275d13ed6398035afb5664ae580
[638ed9be]: https://github.com/benredmond/stet/commit/638ed9be914a2219814f6623799416412981dcd0
[6a92b85c]: https://github.com/benredmond/stet/commit/6a92b85c3d712213f6c5a9f3d4ce395bf6f53981
[3e319224]: https://github.com/benredmond/stet/commit/3e319224b85b5d254cc5c44f0cd41e96441cb8be
[9c472648]: https://github.com/benredmond/stet/commit/9c4726485ce72a28782e75c0a2a926160671f698
[7ef559f2]: https://github.com/benredmond/stet/commit/7ef559f2abb6e9e6b7ec03428f87cbf16e6d7d91
[5c5fb536]: https://github.com/benredmond/stet/commit/5c5fb536d8017d672a7aeb3a36625ee08fccdb50
[f48b0a6c]: https://github.com/benredmond/stet/commit/f48b0a6cf1460e0f75b89a144659b83ee3faf0f4
[b99f3cc6]: https://github.com/benredmond/stet/commit/b99f3cc694a96bf8c2f2feb0914d0c19c304c290
[99d45afa]: https://github.com/benredmond/stet/commit/99d45afa03c5c1970658494e17704d9c42520f64
[9874c882]: https://github.com/benredmond/stet/commit/9874c882ee3a6ffff4daa5a07aad29486e983cf1
[133bcfab]: https://github.com/benredmond/stet/commit/133bcfabc1122a2ec8f5276eb866982b4fdd1fe0
[0967129c]: https://github.com/benredmond/stet/commit/0967129cb5b298f9885f6d1c8be8f3d1c2c9d206
[8395ebca]: https://github.com/benredmond/stet/commit/8395ebcaaa72ca8e300abf0f6ae34e823ed2d296

## [v0.8.0] - 2026-06-24

Adds a worktree-native Harbor backend for `stet eval` runs, a deterministic targeted-F2P dataset build path (per-language fail-to-pass extractors, install-config recipes, Rust onboarding), receipt-first resumable `eval combine`, native multi-arm compare, and `stet eval calibrate` for grader-discrimination policy. Operators get more isolated and reproducible eval execution, recoverable combine/relaunch flows, and validity gates that close equivalence fail-open and contamination bypasses so Trial Results stay trustworthy.

### Added
- Build targeted fail-to-pass datasets deterministically: `stet dataset regenerate-f2p`, `stet suite build --install-config` consuming committed install-config recipes, per-language F2P extractors (Go/Rust/JVM and more) with a candidate ladder plus proof-aware P2P narrowing, dynamic proof of the targeted feature, and end-to-end F2P verification against the committed corpus ([d78641e7], [29cc7206], [d6be690b], [9b47a131], [5c00adac], [9cc8cef6], [86d76217], [80c35e2a], [3bfedb68])
- Onboard Rust toolchains and pre-fill workspace test selection in `stet init`, with a `test_selection` config override and workspace auto-detect ([29cc7206], [333b93f7])
- Add a worktree-native Harbor backend for eval execution: a worktree lifecycle primitive, Harbor-shaped agent runner and verifier roles, worktree-native validation staging, runtime provenance, and execution-integrity guardrails, selectable via `--harbor-backend worktree` on `stet eval rules` and `stet eval smoke` ([cd75e79d], [1a816a71], [b8d701d4], [f09ddbda], [d4280b0c], [b86994b5], [b8111584], [4f90703a], [4533afcb], [10813c32], [04626fc1], [f0cd6413])
- Make `stet eval combine` receipt-first, incremental, and resumable via `--finalize` ([68ff1607])
- Add `--relaunch-arm` to `stet eval rules resume` so operators can recover a single wiped-out arm without rerunning the whole comparison ([2a5e8756])
- Report native multi-arm compares with per-arm quality-metric statistics ([4c47d851], [5517f6d3])
- Add `stet eval calibrate` to measure grader discrimination and gate eval decisions on the calibrated policy ([0ae3bbae], [0ab2122e])
- Add a `stet runs repair-patches` flow to repair runs from stranded or missing agent patches ([6ec65fc2])

### Changed
- Make per-cell verdicts tests-first so an equivalence judge no longer fails open on test-bearing corpora, and gate equivalence-only test-verdict corpora explicitly ([ab36df6c], [66945125])
- Flag agent-answer contamination on a graded cell instead of blocking grading outright, keeping the Trial Result while marking the provenance risk ([125c4a38])
- Surface stranded agent patches in the run instead of silently dropping them, so recoverable work is visible to repair flows ([c4b030b4])
- Mark superseded trial directories after a repair so the canonical outcome is unambiguous ([a3fb0fc6])
- Update shipped skill guidance for dataset onboarding and for the worktree and repair rules workflows ([daaadc01], [eaa8f6f5])

### Fixed
- Make targeted-F2P build robust: scope gradle valueless-flag handling to the JVM/gradle path, force-add ignored files into the synthetic base so the test-file revert is faithful, install a no-op solve for corpus tasks lacking `solution.sh`, ensure verdicts measure the gold feature, and fix guarded toolchain-root inference ([f4208d11], [89dfbc27], [23c8dc81], [7cc1f98c], [90405960])
- Harden worktree and Harbor eval execution: fix worktree eval parity and Composer evidence, harden Harbor export migration and the Go toolchain environment, and allow current worktree paths through integrity scans ([ce0a3636], [ff731ad8], [99ada10e], [5a4bcc80])
- Repair grader-coverage recovery, verifier retest repair-outcome projection, H2H repair-outcome surfaces, and the Harbor non-verdict projection so repaired and verdict-less outcomes report correctly ([682771d6], [bb3318f6], [5e017239], [ffd4e4d9])
- Exclude infra-verifier failures from quality scoring so toolchain/infra noise does not score against the model ([3cb809f0])
- Fix provider-schema classification of unsupported flags so unsupported levers are reported rather than silently mishandled ([4247d5d3])
- Improve `stet artifacts doctor` repo-cleanup UX ([4bdc5b0f])
- Serialize concurrent H2H progress emits to avoid interleaved progress output ([75b75ac6])

[d78641e7]: https://github.com/benredmond/stet/commit/d78641e7f9f5442f67cef5527557f3d563603b10
[29cc7206]: https://github.com/benredmond/stet/commit/29cc720659ce77a3fc9bab3a338846272b6b68cc
[d6be690b]: https://github.com/benredmond/stet/commit/d6be690bf1aff0d2f56e1252adbeac704eb5657b
[9b47a131]: https://github.com/benredmond/stet/commit/9b47a131aa89f635ca022956e1cfdc1800c8963e
[5c00adac]: https://github.com/benredmond/stet/commit/5c00adac0566aa42b2f100c32191f9fcb777bca4
[9cc8cef6]: https://github.com/benredmond/stet/commit/9cc8cef651012c233bbb2005503402c08a2874bc
[86d76217]: https://github.com/benredmond/stet/commit/86d7621742c07042689bc9a3c1f753d5aea82897
[80c35e2a]: https://github.com/benredmond/stet/commit/80c35e2a0053ab0955cb2d887137704ac390951a
[3bfedb68]: https://github.com/benredmond/stet/commit/3bfedb68cde13e1ecaf7fc3c45fe16f51b2f6cc0
[333b93f7]: https://github.com/benredmond/stet/commit/333b93f7933b6b362bf1676d00ea8bbb33ab275d
[cd75e79d]: https://github.com/benredmond/stet/commit/cd75e79d3a4a61f074d1370b27438c8ed875b6ca
[1a816a71]: https://github.com/benredmond/stet/commit/1a816a71df638b7f7930b0ef781134407a36f27d
[b8d701d4]: https://github.com/benredmond/stet/commit/b8d701d43527756da153b1a78f934213b42f45bc
[f09ddbda]: https://github.com/benredmond/stet/commit/f09ddbda4a3e10bea9ddc64d0e580fb398235ad2
[d4280b0c]: https://github.com/benredmond/stet/commit/d4280b0cafebdc56ebe2b769ebd2000c1b8dcf2a
[b86994b5]: https://github.com/benredmond/stet/commit/b86994b57ed9b54dad418b36124baffd680c1881
[b8111584]: https://github.com/benredmond/stet/commit/b8111584402cbec8d099647d94a03863315d4951
[4f90703a]: https://github.com/benredmond/stet/commit/4f90703ac7768636e3247804c2d45b86cf331fe1
[4533afcb]: https://github.com/benredmond/stet/commit/4533afcb1451bbbb73e3e9ecec59a01a593d1b09
[10813c32]: https://github.com/benredmond/stet/commit/10813c322823833f8223b9515fec9050bd4488ec
[04626fc1]: https://github.com/benredmond/stet/commit/04626fc117c597b55126744278dc721f2ce53cca
[f0cd6413]: https://github.com/benredmond/stet/commit/f0cd6413257b297c86150d679b18419d23014e8e
[68ff1607]: https://github.com/benredmond/stet/commit/68ff16075ee9198fa1ea0b207a139df8bb85ca6d
[2a5e8756]: https://github.com/benredmond/stet/commit/2a5e875647fb874f7462491f44a2dd0669a854cb
[4c47d851]: https://github.com/benredmond/stet/commit/4c47d851d05d5cbf504fb037cdb10b881a3bb76f
[5517f6d3]: https://github.com/benredmond/stet/commit/5517f6d3078c823548b279ee3de7a885232a85bf
[0ae3bbae]: https://github.com/benredmond/stet/commit/0ae3bbae7ee13cc2b910d8df96a5ec9f9b8317ec
[0ab2122e]: https://github.com/benredmond/stet/commit/0ab2122e8eaa6d15d669545ff7d19391040acb0d
[6ec65fc2]: https://github.com/benredmond/stet/commit/6ec65fc27746d9ca9db795e380c8b051a45474e5
[ab36df6c]: https://github.com/benredmond/stet/commit/ab36df6c7e4752111e1235ac880775c3322f5f6d
[66945125]: https://github.com/benredmond/stet/commit/669451254ae60e7dc9a6a7fd96e70224e2d1e91f
[125c4a38]: https://github.com/benredmond/stet/commit/125c4a386ae02f9e27c61f409cf1dbfe5f9e821f
[c4b030b4]: https://github.com/benredmond/stet/commit/c4b030b46fc1f5f42031b89a127f1b549034c947
[a3fb0fc6]: https://github.com/benredmond/stet/commit/a3fb0fc6681409ec49aabf6a7838f090438b7258
[daaadc01]: https://github.com/benredmond/stet/commit/daaadc019a6fe162579f35e18407ae64b4e892fb
[eaa8f6f5]: https://github.com/benredmond/stet/commit/eaa8f6f5716f6e63f5fe06719fe479e48abdc56f
[f4208d11]: https://github.com/benredmond/stet/commit/f4208d11806304bea210377a3bdfb2e75a361499
[89dfbc27]: https://github.com/benredmond/stet/commit/89dfbc27e39e2c0a3d8f3cc5ed370497071313a7
[23c8dc81]: https://github.com/benredmond/stet/commit/23c8dc814a5efe93200eaa48da9381b4a419fd1c
[7cc1f98c]: https://github.com/benredmond/stet/commit/7cc1f98ce4ab8daafea44ddf273fbf7f87321609
[90405960]: https://github.com/benredmond/stet/commit/904059602c58b7c1fee80c4a29b918f7f362d246
[ce0a3636]: https://github.com/benredmond/stet/commit/ce0a3636c9cd1814c4635f441edb2d6fc5567664
[ff731ad8]: https://github.com/benredmond/stet/commit/ff731ad8e872e302da499466d3e282fc93001a8a
[99ada10e]: https://github.com/benredmond/stet/commit/99ada10e29824407c9dfd7271ebe45a4e4d49cc5
[5a4bcc80]: https://github.com/benredmond/stet/commit/5a4bcc8036ce8f67c4433ae82c77a7527d747f85
[682771d6]: https://github.com/benredmond/stet/commit/682771d6b8de19545cd8ad111a33230ed1680472
[bb3318f6]: https://github.com/benredmond/stet/commit/bb3318f63a8536eb398d961338927d6a81a55a12
[5e017239]: https://github.com/benredmond/stet/commit/5e0172391e360ac74cd5ba261257ab1038982d0e
[ffd4e4d9]: https://github.com/benredmond/stet/commit/ffd4e4d9e6afaf9499c26c5ab5b35f8c32ce7846
[3cb809f0]: https://github.com/benredmond/stet/commit/3cb809f09e00df184557c17d34df8b8873953eef
[4247d5d3]: https://github.com/benredmond/stet/commit/4247d5d31fa3a114c28f0b535e37b6309913de0d
[4bdc5b0f]: https://github.com/benredmond/stet/commit/4bdc5b0f1303bf797c3da6420e495633891ccb0f
[75b75ac6]: https://github.com/benredmond/stet/commit/75b75ac6d693e75003d2c6c489c7ad744460a7e1
[v0.8.0]: https://github.com/benredmond/stet/releases/tag/v0.8.0

## [v0.7.0] - 2026-06-15

Promotes Stet's optimize loop from evidence sidecar to public release workflow. Operators can now plan task slices, launch guarded optimization branches, inspect loop/frontier/decision receipts, narrow existing eval roots, and reclaim scratch artifacts safely while Stet keeps promotion, Harbor isolation, and Trial Results fail-closed.

### Added
- Add native optimize-loop artifacts, workbench views, trajectory scans, rejected-lever tracking, and uncertainty-aware decisions so operators can inspect what changed, why a candidate advanced or stopped, and whether evidence is ready ([ff48d44f], [199384eb], [7ec24c18], [e6f63feb], [230b9e10], [99a70928])
- Add guarded optimize launch and frontier selection receipts so promotion evidence records candidate identity, selected harness surface, and the launch basis ([9d134184], [820b7e4c], [d7cd1911])
- Add objective policy profiles and measuring-device grader profiles so optimization decisions are scoped to the intended quality target and required grader coverage ([0051c5dd], [f836938c])
- Add native task-slice planning and explicit lane suites so operators can split evals into named, replayable task slices ([dfe9bfec], [8cec3ec3])
- Add default garbage collection for regeneratable per-run scratch, plus opt-in `stet artifacts compact --include-datasets` reclaim for materialized datasets ([3cc2930c], [5355fecd])
- Register Claude Fable 5 pricing and model aliases for h2h runs ([99a7ee8a])

### Changed
- Support existing-root task selectors so compare/report workflows can narrow durable eval roots without rerunning or mutating source roots ([95e1e5ff])
- Harden dataset onboarding around selector evidence, Bazel proof, LLM diagnostics, generalized readiness, and descriptive validation modes ([2d38b7f8], [943a42ed], [8ca9d3e6], [6457e2d9], [4604ec75], [25e23b2b])
- Require replay tasks to carry `repo.repository_slug` metadata, with dataset builds deriving it from canonical change-request remotes ([96ab61ea])
- Show the eval status reportability tree so operators can see why a run is or is not reportable ([1d292a08])

### Fixed
- Keep optimize promotion fail-closed across holdout readiness, lane awareness, suite identity, candidate identity, decision-subject validity, evidence handling, fixed candidate context, launch status, and child-lane control-plane paths ([df58c11b], [e3c538ee], [46be6415], [14e7fb6a], [62052fbc], [f2f984d7], [5b91124b], [fba1208d], [6b64909e], [c6e36f10])
- Preserve Trial Result and report integrity across runtime token evidence, profile policy projections, provider-schema judging, repair profiles, grader stat refreshes, eval-rules terminal state, summary-only compare status, and hardened orchestration ([4cf9878e], [ec86be5c], [c4e881cc], [b63bf95d], [06f2d8aa], [7ef85bd8], [4ef77abb], [4aded968], [d203bce6])
- Fail closed on invalid eval inputs and incompatible roots, including empty eval patches, frozen-baseline compatibility, overlapping combine compare sources, explicit lane-suite replay gates, and claim readiness ([a1311943], [996bb7b3], [313d2e42], [2711dd78], [47d63508])
- Close Harbor and contamination bypasses by gating network-contamination waivers, rendering prompt templates across auth agents, defaulting exports to runtime internet, isolating Go runtime behavior, closing guard source bypasses, and hardening Fable answer-contamination guards ([a4035e87], [e9f26502], [a6a0bc38], [1a40ebbf], [389d7f46], [d9bfd909])
- Improve artifact reclaim safety, retired Harbor cache cleanup, and trial-result read caching during artifact regeneration ([8a214153], [b2f0022a], [156b6e4f])

[v0.7.0]: https://github.com/benredmond/stet/releases/tag/v0.7.0
[4ef77abb]: https://github.com/benredmond/stet/commit/4ef77abb115ffeac7377f701424de5417c3b9648
[14e7fb6a]: https://github.com/benredmond/stet/commit/14e7fb6ab142fb3cd40704ba43826133cfe0f5ac
[4aded968]: https://github.com/benredmond/stet/commit/4aded968e0a706f41321e6c3425cd38357a57f9d
[156b6e4f]: https://github.com/benredmond/stet/commit/156b6e4fa248fe18c564ff68ea4d2bc720ce27ad
[7ef85bd8]: https://github.com/benredmond/stet/commit/7ef85bd8d6320eb9c92bb6f0e56eef8c08f0bf38
[313d2e42]: https://github.com/benredmond/stet/commit/313d2e424748c0fc55583fdbf0615c4da3905bb9
[389d7f46]: https://github.com/benredmond/stet/commit/389d7f4657123336bb0dd89d26229a1ebcd9a689
[2711dd78]: https://github.com/benredmond/stet/commit/2711dd78668dc338f18c85714da287738f758172
[8a214153]: https://github.com/benredmond/stet/commit/8a21415357dd5bdd6417cd98ec9c454f406a8d6c
[d203bce6]: https://github.com/benredmond/stet/commit/d203bce61b0ebd472f2c527f6e4fb91041cfa18a
[1a40ebbf]: https://github.com/benredmond/stet/commit/1a40ebbff419bb2910285b9d644cd41538e1842a
[8cec3ec3]: https://github.com/benredmond/stet/commit/8cec3ec3ecc1e88af7856f4f6765727345ed2927
[5355fecd]: https://github.com/benredmond/stet/commit/5355fecd854eb1f81610a87bb1982b09ba8c697b
[95e1e5ff]: https://github.com/benredmond/stet/commit/95e1e5ff74c3d6935f670a33b185f841d557f19b
[3cc2930c]: https://github.com/benredmond/stet/commit/3cc2930cf2a379434da9ed79082e69e4fe6aa917
[4604ec75]: https://github.com/benredmond/stet/commit/4604ec753d693f111c310b1b784d7c26b1054dea
[c6e36f10]: https://github.com/benredmond/stet/commit/c6e36f10d8b5f88f7da74b9bc31ae55693bab6e1
[943a42ed]: https://github.com/benredmond/stet/commit/943a42edbb382144a3659b3808c497422e845565
[8ca9d3e6]: https://github.com/benredmond/stet/commit/8ca9d3e62e9f63beab354678a980c82871e620bc
[a1311943]: https://github.com/benredmond/stet/commit/a131194317c4b0153114be19e1326fd2cb57635e
[6457e2d9]: https://github.com/benredmond/stet/commit/6457e2d9aace51e089675b74103ad96a3f746b38
[e3c538ee]: https://github.com/benredmond/stet/commit/e3c538eefd9f79415df0ff9c60a9d6e590b0dc2c
[25e23b2b]: https://github.com/benredmond/stet/commit/25e23b2b94f988fdd0820ad5d4cf13527f960e55
[96ab61ea]: https://github.com/benredmond/stet/commit/96ab61eac7ac4aa52a28030b917e0cf0d972dac0
[2d38b7f8]: https://github.com/benredmond/stet/commit/2d38b7f8c9eed7fb600ee4d6f38eb5150abbf575
[a6a0bc38]: https://github.com/benredmond/stet/commit/a6a0bc3805d5c907e8a19b201962ee8dd2e238bd
[6b64909e]: https://github.com/benredmond/stet/commit/6b64909e8244c7df12cd6206db8fb525d3118481
[62052fbc]: https://github.com/benredmond/stet/commit/62052fbc8e304fdca6bac7e504f5782bcc2fabca
[d9bfd909]: https://github.com/benredmond/stet/commit/d9bfd90953b28f737634f44131c95121514b8da6
[46be6415]: https://github.com/benredmond/stet/commit/46be6415ed6278b16f4e25cbc4684dcee7479320
[06f2d8aa]: https://github.com/benredmond/stet/commit/06f2d8aa2afd280ee054c27fe33e4037e862c05b
[5b91124b]: https://github.com/benredmond/stet/commit/5b91124b34a991778d19641c7150af6b5ae0eb17
[99a7ee8a]: https://github.com/benredmond/stet/commit/99a7ee8ab2d28eca8727d5fcde623acc851ce6e5
[d7cd1911]: https://github.com/benredmond/stet/commit/d7cd19117105704bb046a9b2033359dbbdeabc2c
[47d63508]: https://github.com/benredmond/stet/commit/47d635086d7ed52892c552ace4514da8e9f1e47d
[c4e881cc]: https://github.com/benredmond/stet/commit/c4e881cc67cfc760ba8cc29eff8fc12edeeb0213
[99a70928]: https://github.com/benredmond/stet/commit/99a70928af1954960dfbb5acce3c450678fb1cfd
[e6f63feb]: https://github.com/benredmond/stet/commit/e6f63febbd140d08019726a6317239a7eab492e9
[fba1208d]: https://github.com/benredmond/stet/commit/fba1208db0a927649cd5c4c4e1cd32de2eba2f8a
[820b7e4c]: https://github.com/benredmond/stet/commit/820b7e4ccb1fc880b5aafa8ad62c2c53ac7a3f7d
[9d134184]: https://github.com/benredmond/stet/commit/9d134184220c7bb79aed042255b2029ffa64fc16
[7ec24c18]: https://github.com/benredmond/stet/commit/7ec24c183664b5d931ebda20f6b902cd21ccf171
[f836938c]: https://github.com/benredmond/stet/commit/f836938cff605a25e332783b22441d9b46660f4c
[1d292a08]: https://github.com/benredmond/stet/commit/1d292a0899cb07170b5351c9a3686c468719a9c1
[199384eb]: https://github.com/benredmond/stet/commit/199384ebbcdaf7d3c375ce836134efc5dbecada7
[ec86be5c]: https://github.com/benredmond/stet/commit/ec86be5c5f44edd819341458ff9cfc5336658d5d
[e9f26502]: https://github.com/benredmond/stet/commit/e9f26502790f3e79e55fcdb7cbb09dbc023a4745
[df58c11b]: https://github.com/benredmond/stet/commit/df58c11b3f22e0797f46231e2b7bdb6189ea1fba
[f2f984d7]: https://github.com/benredmond/stet/commit/f2f984d7af9d6a1aab9fabea6ce279f81c00fd85
[0051c5dd]: https://github.com/benredmond/stet/commit/0051c5dd92d1f9b352ec9a21fab0a998166a70df
[dfe9bfec]: https://github.com/benredmond/stet/commit/dfe9bfec2592d7ed74adb85c79af44661fead914
[230b9e10]: https://github.com/benredmond/stet/commit/230b9e1050aa7b065d037cc1dffb31ba889e240c
[996bb7b3]: https://github.com/benredmond/stet/commit/996bb7b39a90fc62540e941b691aa2cb166b53db
[ff48d44f]: https://github.com/benredmond/stet/commit/ff48d44f3753c9d115d6b91bd83e7abe3fbac589
[4cf9878e]: https://github.com/benredmond/stet/commit/4cf9878eac561991be5c29528f33ffa354426b1e
[b2f0022a]: https://github.com/benredmond/stet/commit/b2f0022aa19431b6202b79fc26b2bfdb49dffe92
[b63bf95d]: https://github.com/benredmond/stet/commit/b63bf95d1335e04921d37ae3803b71f12003cb25
[a4035e87]: https://github.com/benredmond/stet/commit/a4035e87b27490732c825aa8dd326fc1480ea62b

## [v0.6.0] - 2026-06-02

Prepares the next release around decision-grade eval evidence, safer task materialization, and more complete operator workflows. This release adds decision-grade receipts, richer h2h report diagnostics, Cursor-backed Harbor evals, matched A/A/B workbench planning, self-serve trial paths, and stricter Harbor/build behavior so operators can understand why an eval promoted, held, or failed closed.

### Added
- Add Cursor CLI support for Harbor-backed evals, including model resolution, pricing metadata, auth handling, behavior telemetry, and post-run hook support ([47786a51], [ed9eb49f], [24bf67f4])
- Add Opus 4.8 model resolution and pricing metadata so new-model eval reports can price runs accurately ([43e1127f])
- Add provider-native structured grader runtimes with explicit evaluator config, runtime provenance, and fail-closed custom-grader validation ([13495052], [edae64fd])
- Add smoke policy receipts and persisted skill-loop proposed edits so probe/gate outcomes carry more actionable trial-result evidence ([57159cee], [cd7f9bf5])
- Add h2h report diagnostics for benchmark economics, process behavior, missing equivalence evidence, patch reliability, and default compare statistics ([c346edb7], [86a7cf86], [94d5086d], [f21f268c], [cec492f5], [bb98fc7a], [77b75968])
- Add multi-arm standing and variance-reduction analysis for leaderboard and model-comparison reads ([c6e7fa87], [81aca262])
- Add compare cost-attribution diagnostics and a no-spend matched A/A/B workbench planner for optimizer decisions over existing Trial Results ([ada9a178], [eac3419b])
- Support combining split eval roots, including repaired-verifier evidence via `stet runs repair-tests`, so operators can finish n=20+n=5 benchmark runs without losing provenance ([b1d85108], [576c4868], [f3893aef])
- Narrow eligible broad verifier commands during build, with deterministic coverage checks and LLM abstain/retry handling so generated task suites avoid overly broad test runs ([112838fa], [dd1054e7], [a0f39cd1], [de656c3f], [36a840dc], [5c9c5317], [1bc5f290])
- Add the self-serve CLI signup flow and extend the default commercial trial window to 21 days ([4b5843a4], [8e50d415])
- Publish the Codex agents iteration post, composer-comparison visualization, and Opus 4.8 launch comparison visualization for the leaderboard site ([c60f6188], [71b6fb81], [eac3419b])

### Changed
- Pin the Harbor invocation Stet uses and refresh the shipped operator docs around invocation provenance, release lifecycle, compare/check-in, rubric authoring, and dist install behavior ([bac3f2ec])
- Update shipped Stet guidance so operator-facing next steps, review-agent waiting, and dataset-build instructions match the current CLI surface ([ca1c6e84], [d3cd9477])
- Clarify build-time verifier narrowing and dataset guidance, including the GraphQL Go Tools rev range used by leaderboard dogfood runs ([cd4c66fe], [41abe228])

### Fixed
- Fail closed for incomparable cost deltas, noise-aware recommendations, missing instruction evidence, repaired grader decisions, grader timeouts, asymmetric grader coverage, unknown equivalence, active-run status, frozen-baseline staleness, and decision-grade cost evidence ([b81016be], [cd76bbb6], [9a9bf65f], [9bd742a1], [04b5bcfc], [e1268e43], [0e03a876], [bc6b23ea], [d7b2e8c8], [1f1f03f2])
- Preserve cache artifact cost provenance and canonical patch-presence semantics, attribute skill-activation evidence to the candidate arm, normalize behavior telemetry across reports, exclude scratch files from compare staging, clean up partial arms, and invalidate no-patch trial evidence ([c26fc24a], [d6504750], [c7de2548], [68fdade2], [37567d9d], [dab771c8])
- Disable Harbor task network access by default, freeze Go toolchains from `runtime_version`, require Go runtime metadata for toolchain injection, and preserve `test.patch` trees during gold/F2P validation ([5e4667b1], [17ebb4fa], [cd85a5e4], [53410be4])
- Make eval dataset discovery explicit for Harbor-backed runs, drop harness preambles from assembled instructions, and route rules validation through `stet eval agent` so candidate and validation flows bind the intended task corpus and canonical command surface ([9d922b16], [b549f55f], [b4c9182a])
- Add an explicit operator-reviewed waiver path for known-benign agent network contamination while preserving fail-closed default behavior and waiver audit trails ([eac3419b])
- Increase Harbor agent timeout budgets for long-running eval tasks ([fc537baf])
- Remove the blocked self-install CTA from private trial surfaces and improve leaderboard SEO/AI crawl assets ([cc1a0005], [a7b36f43])

### Internal
- Add Stet-specific subagent definitions, refine lead-scanner seed state, and expand token-discipline, workflow, and QA docs used by agents working in this repo ([edad6844], [98289bc5], [d30e410c], [34c63a58], [7c6d5c06], [cca87164])

[v0.6.0]: https://github.com/benredmond/stet/releases/tag/v0.6.0
[eac3419b]: https://github.com/benredmond/stet/commit/eac3419b6443ea539ca0e1090051688f44fbbbdf
[ada9a178]: https://github.com/benredmond/stet/commit/ada9a178b9b6c89940be6724b4a99d9ebd41c611
[cca87164]: https://github.com/benredmond/stet/commit/cca87164805b8a81460122c295edafa1c5f3315a
[53410be4]: https://github.com/benredmond/stet/commit/53410be4b72c8797b38e522ed98aa5e2a65ad312
[d30e410c]: https://github.com/benredmond/stet/commit/d30e410cde91e05af8d45a61fca5e1377baa3426
[41abe228]: https://github.com/benredmond/stet/commit/41abe228ae29f6d617bfbf6df91bed19efbcbee7
[24bf67f4]: https://github.com/benredmond/stet/commit/24bf67f4693ceb6c1207de6b16a7e1f840488993
[7c6d5c06]: https://github.com/benredmond/stet/commit/7c6d5c06009dd32abd12ebdd602a73a8cedfe6bf
[77b75968]: https://github.com/benredmond/stet/commit/77b75968f7e85a0ce7a8338456fbcd6b0f7d0396
[cd85a5e4]: https://github.com/benredmond/stet/commit/cd85a5e48d693dfbc091200787f6036af14a2ee5
[dab771c8]: https://github.com/benredmond/stet/commit/dab771c85e61d4d99d9405a65c6d8d085143ec26
[c6e7fa87]: https://github.com/benredmond/stet/commit/c6e7fa873d3f90f77f3b7ed14b6925b745bef8e9
[17ebb4fa]: https://github.com/benredmond/stet/commit/17ebb4fa5a0ee1a629630903916051ce834ef886
[1bc5f290]: https://github.com/benredmond/stet/commit/1bc5f29053462cf94ec647b9e2d50f111491cce5
[5e4667b1]: https://github.com/benredmond/stet/commit/5e4667b177185ff5752be0c946e1270dcae15663
[bb98fc7a]: https://github.com/benredmond/stet/commit/bb98fc7a0b8ea854bf6943b98eab8aa1aaa66f4f
[cec492f5]: https://github.com/benredmond/stet/commit/cec492f54b15d9c87d78bf9c04d381255a18fe68
[cd4c66fe]: https://github.com/benredmond/stet/commit/cd4c66fefa9a72ee74bfa13c8a8701021299ce1f
[36a840dc]: https://github.com/benredmond/stet/commit/36a840dcc6a396092766b821f073606d06661058
[de656c3f]: https://github.com/benredmond/stet/commit/de656c3fcbfde52e13387a2d7db1c0df5e103a94
[a0f39cd1]: https://github.com/benredmond/stet/commit/a0f39cd11f60b2b68d796380d8b4e8fedc7424cd
[dd1054e7]: https://github.com/benredmond/stet/commit/dd1054e740c42bcd2a3731cd3ee2605e73399a6f
[112838fa]: https://github.com/benredmond/stet/commit/112838fa44726601c9c40abfeb3b8ec76666bd08
[5c9c5317]: https://github.com/benredmond/stet/commit/5c9c5317b3808f6c37ccb7e66dd2686244f04914
[81aca262]: https://github.com/benredmond/stet/commit/81aca26230d15b047a8e0a6851e327ed303ac0c5
[1f1f03f2]: https://github.com/benredmond/stet/commit/1f1f03f259059ebaf145e868f439884bba7916be
[bc6b23ea]: https://github.com/benredmond/stet/commit/bc6b23ea58b3cf1ed9c6b8adedd2df84a7070ca7
[d7b2e8c8]: https://github.com/benredmond/stet/commit/d7b2e8c80c3e7df00ae5a61bca154ceec798f1c9
[f3893aef]: https://github.com/benredmond/stet/commit/f3893aef76ab2aba88cfbad86b2fbae38a9d289d
[576c4868]: https://github.com/benredmond/stet/commit/576c486870086b7d174de8923d7fe54bc112bf2f
[37567d9d]: https://github.com/benredmond/stet/commit/37567d9db87200ae5907cce6943831e6d9733e88
[d6504750]: https://github.com/benredmond/stet/commit/d650475036acbc96d73bfa5ecb37395af0d13700
[b1d85108]: https://github.com/benredmond/stet/commit/b1d85108de054dbcf60f4a27e23cdbea6057176a
[0e03a876]: https://github.com/benredmond/stet/commit/0e03a876db5d5209d23ad746a563292120256cd4
[e1268e43]: https://github.com/benredmond/stet/commit/e1268e43c4c22c13f78e0c8464d137de75c9b04f
[57159cee]: https://github.com/benredmond/stet/commit/57159cee08d2f44df054cf959ac2e6417ca9b702
[c26fc24a]: https://github.com/benredmond/stet/commit/c26fc24ad118f783a0d63996270c4f9085aab63f
[4b5843a4]: https://github.com/benredmond/stet/commit/4b5843a466dea2f170b61ae988c319ad603ca264
[b4c9182a]: https://github.com/benredmond/stet/commit/b4c9182a5cc3b3f50ede9e045bf55c68de458bec
[71b6fb81]: https://github.com/benredmond/stet/commit/71b6fb81b0ef18b14e614c81883ba66bafe20d4d
[43e1127f]: https://github.com/benredmond/stet/commit/43e1127f510f7f26ad985acafbf7bc0ab5fc71ba
[a7b36f43]: https://github.com/benredmond/stet/commit/a7b36f43cde65c75e0759631209b6a08e238c6e1
[68fdade2]: https://github.com/benredmond/stet/commit/68fdade22306f26fe8401b286959ba81f97a0b82
[34c63a58]: https://github.com/benredmond/stet/commit/34c63a586bb066792b8e04e772fefcab8357414c
[f21f268c]: https://github.com/benredmond/stet/commit/f21f268c5f701225265d73464aec5a85603ed2bd
[c60f6188]: https://github.com/benredmond/stet/commit/c60f61889099c18eeae33da33cce1429b2ea11d3
[cc1a0005]: https://github.com/benredmond/stet/commit/cc1a00053e7ca8fa00636bd55cffb7485fa37641
[bac3f2ec]: https://github.com/benredmond/stet/commit/bac3f2ec99e1738f39fb3224f805c64805dd7181
[04b5bcfc]: https://github.com/benredmond/stet/commit/04b5bcfc028aff8770672583b0f42ea1298b01c8
[94d5086d]: https://github.com/benredmond/stet/commit/94d5086d7383d2d82a275cd2212382e2dd18a5b0
[8e50d415]: https://github.com/benredmond/stet/commit/8e50d415890d5872a6c888276e2cbcc71863a7df
[86a7cf86]: https://github.com/benredmond/stet/commit/86a7cf86f9e54bef57bba7cffdbd95baeec0492a
[d3cd9477]: https://github.com/benredmond/stet/commit/d3cd94772cf0f8c72bcff575d29410cbe7222e4e
[13495052]: https://github.com/benredmond/stet/commit/13495052eaaddc63cf261f5da2b22e0b6bbd3a53
[ca1c6e84]: https://github.com/benredmond/stet/commit/ca1c6e84c799e1c5750740f97cbb2ee612305074
[cd7f9bf5]: https://github.com/benredmond/stet/commit/cd7f9bf567eba637725925ede272819c4ae5c13c
[edae64fd]: https://github.com/benredmond/stet/commit/edae64fd028da9b20576e6f84c3bae2de1777377
[9bd742a1]: https://github.com/benredmond/stet/commit/9bd742a12a87818d255c87a357e02fd56790a3c6
[c7de2548]: https://github.com/benredmond/stet/commit/c7de2548aa92a6283e80e6cefbdf608f806bc579
[9a9bf65f]: https://github.com/benredmond/stet/commit/9a9bf65fa26146d4a18793b42ba7d472b12499ea
[9d922b16]: https://github.com/benredmond/stet/commit/9d922b16141b566b645f46b46679497c54e3d4a5
[98289bc5]: https://github.com/benredmond/stet/commit/98289bc5c4629b24ca671474491d0e03216e6222
[edad6844]: https://github.com/benredmond/stet/commit/edad68448d5f9207bf9615306a3a32c9fb21cabf
[ed9eb49f]: https://github.com/benredmond/stet/commit/ed9eb49fb352f7e999d0de32f5123bb7f5c39ca3
[b549f55f]: https://github.com/benredmond/stet/commit/b549f55f976d7aec4d89444dfbed2c3341d8ff45
[c346edb7]: https://github.com/benredmond/stet/commit/c346edb725be05aa090bc27708b4c5eb47dbd1fc
[fc537baf]: https://github.com/benredmond/stet/commit/fc537baf6a70db4086b58fad171cc3c88f7ecf63
[cd76bbb6]: https://github.com/benredmond/stet/commit/cd76bbb6c5d95341fc7559eb6635a732d1659788
[b81016be]: https://github.com/benredmond/stet/commit/b81016bed5666a263b8e8f45c7a0c6cfdd5baa43
[47786a51]: https://github.com/benredmond/stet/commit/47786a51c6bd717f48f780e9949cc144e52967e9

## [v0.5.0] - 2026-05-23

Expands Stet's operator surface for customer trials and multi-provider change requests. This release adds GitLab change-request support, auto-update plumbing for installed CLIs, replay-valid suite selection, declarative frozen-baseline reuse in change manifests, and tighter report/plan diagnostics so eval outcomes fail closed instead of drifting into ambiguous states.

### Added
- Add GitLab change-request providers and thread provider identity through dataset and discovery flows ([9de6d051], [8c0f1fac], [a80b63c0])
- Add CLI auto-update support for installed Stet binaries, including runtime identity and dist-update routing ([380fd72c])
- Generate `ai_task` for rev-range and base-head build modes so generated task corpora carry executable task prose ([36e5b5f5])
- Add replay-valid suite selection for rules evals so operators can select tasks whose replay evidence is trustworthy ([8bb784d0])
- Add declarative frozen-baseline reuse in change manifests for rules evals ([e9ab7984])
- Add posture-aware h2h evidence framing for capability-release reads (STET-397) ([73ce7573])
- Add leaderboard AI crawl and private-eval FAQ schema surfaces for search and answer-engine ingestion ([e3fd6c91], [8a3055e1])

### Changed
- Publish beta/customer Stet guide updates and tighten shipped Stet agent guidance for report interpretation and post-run learning capture ([721ebd3f], [50fa0884], [95325017])
- Clarify independent grader-model cost controls, completed compare adequacy caching, disk cleanup boundaries, and GitLab support closeout docs ([4aa8485d], [b6e280b6], [2ab39e06], [c084fa79])

### Fixed
- Detect repaired compare evidence in manifest-backed status and report flows ([6a0bd5a5])
- Add mixed grader-profile diagnostics so compare/report output exposes profile disagreements instead of hiding them in aggregate state ([26cde721])
- Preserve smoke-reuse behavior telemetry and staged-skill activation during `skill_diff` evals ([4c600bd3], [6040da19])
- Tune validation patch guardrails without weakening release-gate semantics ([7ef15ca3])
- Stabilize custom grader metric ordering and preserve custom graders when refreshing regrade decisions ([a44f7883], [f354b569])
- Retry transient replay-validity failures so temporary verifier noise does not become durable eval state ([c879f140])
- Block GitLab merge-request human-patch access in Harbor candidate runs ([cc6e81d8])
- Preserve rules compare report binding and surface Harbor validator disagreement provenance ([b2e3e382], [3a1ec6ca])
- Fail closed when `stet eval rules plan` sees unresolved baseline context ([1d382037])
- Reconcile terminal compare state after finalized eval runs ([5b563f26])

[v0.5.0]: https://github.com/benredmond/stet/releases/tag/v0.5.0
[721ebd3f]: https://github.com/benredmond/stet/commit/721ebd3fedc7fc1f8819a5d865f9cd1863c25eac
[e3fd6c91]: https://github.com/benredmond/stet/commit/e3fd6c91356cd8c939229716a73b612cca37f31c
[50fa0884]: https://github.com/benredmond/stet/commit/50fa088468c299ede31fd4b73c6dd851ca870d16
[8a3055e1]: https://github.com/benredmond/stet/commit/8a3055e18bc6a48c7f767146ee8e7b004d24740d
[6a0bd5a5]: https://github.com/benredmond/stet/commit/6a0bd5a5b376c6fcfa0b4f2bcd362d01c22831e6
[26cde721]: https://github.com/benredmond/stet/commit/26cde721a83889d7e2ffab3643f73d35879268f8
[36e5b5f5]: https://github.com/benredmond/stet/commit/36e5b5f5ea8ad146728abdb0dd7c37cc40da6adb
[4c600bd3]: https://github.com/benredmond/stet/commit/4c600bd350f064683a6c81480c6508c69c604740
[6040da19]: https://github.com/benredmond/stet/commit/6040da19bc01f8e6e8f53bf578f7fb7911ca8665
[b6e280b6]: https://github.com/benredmond/stet/commit/b6e280b65e980663576cdc59e53c60a38260a487
[7ef15ca3]: https://github.com/benredmond/stet/commit/7ef15ca385679538fd17d2a05cf3d540499884a1
[a44f7883]: https://github.com/benredmond/stet/commit/a44f7883609768e7a1adda5ce24841b98daaeef5
[73ce7573]: https://github.com/benredmond/stet/commit/73ce7573e6921f35fa94031f8a33731c74a02374
[f354b569]: https://github.com/benredmond/stet/commit/f354b569b64a8b35dee0eab147fa61bca417f1da
[95325017]: https://github.com/benredmond/stet/commit/953250171ee3b8213db32330fa5e4dfdfc26b02d
[4aa8485d]: https://github.com/benredmond/stet/commit/4aa8485dcb13a22ab4aeb15c8731075e3a93380a
[8c0f1fac]: https://github.com/benredmond/stet/commit/8c0f1facfa933868b2e1463c637398c661627cd6
[380fd72c]: https://github.com/benredmond/stet/commit/380fd72cdec2e545fb1a18bedae6c66d14aafd0e
[9de6d051]: https://github.com/benredmond/stet/commit/9de6d0518879ec1ebf02f6e6f1a6873c6226c5ad
[c879f140]: https://github.com/benredmond/stet/commit/c879f140c36bdb3f3d6ea3c0c8aa58a8d3a52738
[a80b63c0]: https://github.com/benredmond/stet/commit/a80b63c0107b2b21dffa30ea63fb3899280a9eff
[cc6e81d8]: https://github.com/benredmond/stet/commit/cc6e81d8bf4fc128515df03848123fd6d07eeb4b
[8bb784d0]: https://github.com/benredmond/stet/commit/8bb784d01eaa5597d8829e44389c555332a3f81a
[b2e3e382]: https://github.com/benredmond/stet/commit/b2e3e3826a34bb29786f32d6a5d42be95aa87aef
[3a1ec6ca]: https://github.com/benredmond/stet/commit/3a1ec6caf262c4a75c44a7368e4f9eef8673a00a
[c084fa79]: https://github.com/benredmond/stet/commit/c084fa7963a62caf41b874b85cb300cc9ba0fba0
[2ab39e06]: https://github.com/benredmond/stet/commit/2ab39e0642c90eb2ff10143c2e5b2e5d140523dc
[1d382037]: https://github.com/benredmond/stet/commit/1d38203704575b462dd0661781a3fe379a00b703
[e9ab7984]: https://github.com/benredmond/stet/commit/e9ab79847aa457b1ea13347201f1e2a9d07f1d73
[5b563f26]: https://github.com/benredmond/stet/commit/5b563f26c225bff818c05dbb9417835575607e5c

## [v0.5.0-rc.1] - 2026-05-23

Expands Stet's operator surface for customer trials and multi-provider change requests. This release candidate adds GitLab change-request support, auto-update plumbing for installed CLIs, replay-valid suite selection, declarative frozen-baseline reuse in change manifests, and tighter report/plan diagnostics so eval outcomes fail closed instead of drifting into ambiguous states.

### Added
- Add GitLab change-request providers and thread provider identity through dataset and discovery flows ([9de6d051], [8c0f1fac], [a80b63c0])
- Add CLI auto-update support for installed Stet binaries, including runtime identity and dist-update routing ([380fd72c])
- Generate `ai_task` for rev-range and base-head build modes so generated task corpora carry executable task prose ([36e5b5f5])
- Add replay-valid suite selection for rules evals so operators can select tasks whose replay evidence is trustworthy ([8bb784d0])
- Add declarative frozen-baseline reuse in change manifests for rules evals ([e9ab7984])
- Add posture-aware h2h evidence framing for capability-release reads (STET-397) ([73ce7573])
- Add leaderboard AI crawl and private-eval FAQ schema surfaces for search and answer-engine ingestion ([e3fd6c91], [8a3055e1])

### Changed
- Publish beta/customer Stet guide updates and tighten shipped Stet agent guidance for report interpretation and post-run learning capture ([721ebd3f], [50fa0884], [95325017])
- Clarify independent grader-model cost controls, completed compare adequacy caching, disk cleanup boundaries, and GitLab support closeout docs ([4aa8485d], [b6e280b6], [2ab39e06], [c084fa79])

### Fixed
- Detect repaired compare evidence in manifest-backed status and report flows ([6a0bd5a5])
- Add mixed grader-profile diagnostics so compare/report output exposes profile disagreements instead of hiding them in aggregate state ([26cde721])
- Preserve smoke-reuse behavior telemetry and staged-skill activation during `skill_diff` evals ([4c600bd3], [6040da19])
- Tune validation patch guardrails without weakening release-gate semantics ([7ef15ca3])
- Stabilize custom grader metric ordering and preserve custom graders when refreshing regrade decisions ([a44f7883], [f354b569])
- Retry transient replay-validity failures so temporary verifier noise does not become durable eval state ([c879f140])
- Block GitLab merge-request human-patch access in Harbor candidate runs ([cc6e81d8])
- Preserve rules compare report binding and surface Harbor validator disagreement provenance ([b2e3e382], [3a1ec6ca])
- Fail closed when `stet eval rules plan` sees unresolved baseline context ([1d382037])
- Reconcile terminal compare state after finalized eval runs ([5b563f26])

[v0.5.0-rc.1]: https://github.com/benredmond/stet/releases/tag/v0.5.0-rc.1
[721ebd3f]: https://github.com/benredmond/stet/commit/721ebd3fedc7fc1f8819a5d865f9cd1863c25eac
[e3fd6c91]: https://github.com/benredmond/stet/commit/e3fd6c91356cd8c939229716a73b612cca37f31c
[50fa0884]: https://github.com/benredmond/stet/commit/50fa088468c299ede31fd4b73c6dd851ca870d16
[8a3055e1]: https://github.com/benredmond/stet/commit/8a3055e18bc6a48c7f767146ee8e7b004d24740d
[6a0bd5a5]: https://github.com/benredmond/stet/commit/6a0bd5a5b376c6fcfa0b4f2bcd362d01c22831e6
[26cde721]: https://github.com/benredmond/stet/commit/26cde721a83889d7e2ffab3643f73d35879268f8
[36e5b5f5]: https://github.com/benredmond/stet/commit/36e5b5f5ea8ad146728abdb0dd7c37cc40da6adb
[4c600bd3]: https://github.com/benredmond/stet/commit/4c600bd350f064683a6c81480c6508c69c604740
[6040da19]: https://github.com/benredmond/stet/commit/6040da19bc01f8e6e8f53bf578f7fb7911ca8665
[b6e280b6]: https://github.com/benredmond/stet/commit/b6e280b65e980663576cdc59e53c60a38260a487
[7ef15ca3]: https://github.com/benredmond/stet/commit/7ef15ca385679538fd17d2a05cf3d540499884a1
[a44f7883]: https://github.com/benredmond/stet/commit/a44f7883609768e7a1adda5ce24841b98daaeef5
[73ce7573]: https://github.com/benredmond/stet/commit/73ce7573e6921f35fa94031f8a33731c74a02374
[f354b569]: https://github.com/benredmond/stet/commit/f354b569b64a8b35dee0eab147fa61bca417f1da
[95325017]: https://github.com/benredmond/stet/commit/953250171ee3b8213db32330fa5e4dfdfc26b02d
[4aa8485d]: https://github.com/benredmond/stet/commit/4aa8485dcb13a22ab4aeb15c8731075e3a93380a
[8c0f1fac]: https://github.com/benredmond/stet/commit/8c0f1facfa933868b2e1463c637398c661627cd6
[380fd72c]: https://github.com/benredmond/stet/commit/380fd72cdec2e545fb1a18bedae6c66d14aafd0e
[9de6d051]: https://github.com/benredmond/stet/commit/9de6d0518879ec1ebf02f6e6f1a6873c6226c5ad
[c879f140]: https://github.com/benredmond/stet/commit/c879f140c36bdb3f3d6ea3c0c8aa58a8d3a52738
[a80b63c0]: https://github.com/benredmond/stet/commit/a80b63c0107b2b21dffa30ea63fb3899280a9eff
[cc6e81d8]: https://github.com/benredmond/stet/commit/cc6e81d8bf4fc128515df03848123fd6d07eeb4b
[8bb784d0]: https://github.com/benredmond/stet/commit/8bb784d01eaa5597d8829e44389c555332a3f81a
[b2e3e382]: https://github.com/benredmond/stet/commit/b2e3e3826a34bb29786f32d6a5d42be95aa87aef
[3a1ec6ca]: https://github.com/benredmond/stet/commit/3a1ec6caf262c4a75c44a7368e4f9eef8673a00a
[c084fa79]: https://github.com/benredmond/stet/commit/c084fa7963a62caf41b874b85cb300cc9ba0fba0
[2ab39e06]: https://github.com/benredmond/stet/commit/2ab39e0642c90eb2ff10143c2e5b2e5d140523dc
[1d382037]: https://github.com/benredmond/stet/commit/1d38203704575b462dd0661781a3fe379a00b703
[e9ab7984]: https://github.com/benredmond/stet/commit/e9ab79847aa457b1ea13347201f1e2a9d07f1d73
[5b563f26]: https://github.com/benredmond/stet/commit/5b563f26c225bff818c05dbb9417835575607e5c

## [v0.4.3] - 2026-05-19

Hardens Harbor eval isolation for candidate agents. Exported Harbor datasets no longer keep candidate-visible gold patches in fresh or cached task bundles, and the human-patch guard now blocks GitHub pull refs passed through direct git commands, config environment, and included config files.

### Fixed
- Prevent Harbor dataset exports and cache hits from leaving gold/reference patches visible to candidate agents ([f05f41c9])
- Block GitHub pull refs in the human-patch guard so candidate agents cannot fetch target PR heads or merges directly ([3dad80bf])
- Inspect Git config, config-env, and include paths for hidden GitHub pull refs before allowing guarded git operations ([693709b1])

[v0.4.3]: https://github.com/benredmond/stet/releases/tag/v0.4.3
[f05f41c9]: https://github.com/benredmond/stet/commit/f05f41c98595eb57ee5f405e2417a8aa1ffb9376
[3dad80bf]: https://github.com/benredmond/stet/commit/3dad80bf92d545c31185447a1a789c39b40ae930
[693709b1]: https://github.com/benredmond/stet/commit/693709b1179c6b7036fb2209883aaba224bb4546

## [v0.4.2] - 2026-05-18

Blocks Harbor candidate agents from reading public human-patch artifacts during evals. Codex and Claude Code runs now install a guard that prevents direct PR diff/patch, GitHub API, raw head-commit, and downloaded PR-patch access while leaving ordinary package and source lookup available.

### Fixed
- Block public GitHub PR and head-commit artifact access in Harbor Codex and Claude Code agents so candidate evals cannot inspect the target human solution ([7774bac6])

[v0.4.2]: https://github.com/benredmond/stet/releases/tag/v0.4.2
[7774bac6]: https://github.com/benredmond/stet/commit/7774bac6fb8d245c7eefc4624e62c1d20c3d8d44

## [v0.4.1] - 2026-05-18

Prevents Harbor patch capture from retaining harness and gold artifacts as agent output. Operators get cleaner trial results: `.stet/gold.patch`, guidance files, generated directories, and lockfile-only churn no longer leak into captured agent patches, while real source edits and deletions remain visible.

### Fixed
- Prevent gold patch and other harness-generated paths from leaking into captured agent patches; rewrite legacy Harbor artifact sources to the sanitized canonical patch while preserving real source edits and deletions ([4d68d6a])

[v0.4.1]: https://github.com/benredmond/stet/releases/tag/v0.4.1
[4d68d6a]: https://github.com/benredmond/stet/commit/4d68d6a75349992f5e2743601f20b76dc1247f81

## [v0.4.0] - 2026-05-18

Hardens the correctness of cached evidence with a frozen-baseline harness-surface digest gate, adds a `stet eval rules repair` recovery command for interrupted compares, attaches paired-bootstrap confidence intervals and a headline-uncertainty envelope to compare receipts, and reports impl-vs-test-fixture patch surface composition on `footprint_risk`. The CLI gains `--grader` on `stet eval run`, deterministic `--task-order-seed` propagation through `stet eval rules` and monitor reruns, and judge-noise regrade seeding; replay-validity output surfaces typed gold-failure summaries. Adds a Claude Code hook harness surface so hook treatments are first-class compare variants, a `validation_failure.kind` subtype taxonomy that prevents setup blockers from reading as model no-patch behavior, and Linux ARM64 release assets. Returns `stet eval status` in ~2s on finalized compares, restores `--out` dataset reuse in the `stet eval rules` skill wrapper, and corrects the shipped skill docs around `decision_receipt.recommendation` and the `--grader-ai-cmd` / `--grader-ai-model-id` fallback.

### Added
- Publish Linux ARM64 (`linux/arm64`, including aarch64 hosts) CLI release assets and support them in install/update ([9866fe4])
- Accept repeatable `--grader <id|bundle|rubric.yaml>` on `stet eval run` with explicit-wins-merge over repo quality config, mirroring the flag on `stet eval compare` and `stet runs regrade-graders` ([de6c0bc])
- Add `stet eval rules repair` to reuse validation artifacts and resume an interrupted compare or rerun missing/partial arms; `stet eval rules resume` remains accepted as a compatibility alias ([c64393c])
- Plumb `--task-order-seed` through `stet eval rules` and the rules `skill` wrapper so dispatch order replays deterministically against a sorted task selection ([f3e9ee5])
- Honor suite-manifest `eval.task_order_seed` end-to-end through the `stet eval rules` compare path ([6870494])
- Persist `task_order_seed` in monitor rerun config so `stet monitor` reproduces the original dispatch order ([6e07411])
- Add a paired-bootstrap post-pass to `stet eval compare` with `--bootstrap-iterations`, `--bootstrap-seed`, `--ci-level`, and `--no-bootstrap`; receipts gain `aggregate.<metric>.uncertainty` blocks (`baseline_ci`, `candidate_ci`, `delta_ci`, `win_loss_tie`, `bootstrap`) and an `Uncertainty:` text section ([3449973])
- Carry per-metric uncertainty intervals into `decision_receipt`, including `decision_receipt.headline_uncertainty` for the headline metric's CI envelope ([f72da01])
- Report patch surface composition on `footprint_risk` results with a new `surface_breakdown` block (agent vs gold, `implementation` vs `test_fixture` sides, `test`/`fixture`/`expected_output` subkinds, and `test_fixture_added_share`); per-task summaries expose `footprint_surface_breakdown` ([5c5a181])
- Add `--seeds N` to `stet runs regrade-graders` so the operator can bound judge-noise variance during regrades ([ece1165])
- Add a durable arm identity contract so frozen-baseline reuse and arm-level evidence stay bound to a stable identifier across replays ([5f671b3])
- Print typed gold-failure summaries (category/reason plus `harbor_log` path and scrubbed excerpt) in replay-validity terminal output so it matches the JSON diagnostic ([a731873])
- Add a Claude Code hook harness surface — propagate hook-derived signals end-to-end through the rules-runtime artifact, eval-rules check-in, resume, status, runner runtime, and experiment spec so hook treatments are first-class h2h compare variants ([174a94e6])
- Add a no-patch `validation_failure.kind` subtype taxonomy (`empty_patch`, `setup`, `pre_agent`, `verifier`, `sanitized_patch`); propagate counts through h2h task summaries, reports, eval status, smoke preflight, and run validity; classify Harbor no-agent-start artifacts as setup blockers; prefer invalidating subtypes on smoke-preflight tie-breaks while preserving legacy `matrix_status` values for existing consumers ([4939dd3f])

### Changed
- Update the shipped Stet skill docs to point at `decision_receipt.recommendation` as the verdict field (mirrored by `lifecycle.decision`); `decision_receipt` has no top-level `decision` field ([d1374a76])
- Document `--grader-ai-cmd` / `--grader-ai-model-id` as the read-only fixture fallback for LLM-backed graders on `stet eval rules plan` / `launch` / `skill`, and warn that `--no-quality` only drops auto-bundled craft/discipline graders — the default `equivalence` and `code_review` graders remain LLM-backed and still require an evaluator ([d1374a76])

### Fixed
- Gate frozen-baseline reuse on a `harness_surface.baseline_digest`; cache hits whose surface no longer matches the active harness fall back to `cache_status=unknown` rather than replaying stale evidence ([9776d82])
- Include the implicit task list in the `stet eval rules` cache key so cache hits/misses match the realized task set ([36ec2c3])
- Majority-vote non-scored regrade samples when computing aggregate regrade outcomes ([cb77959])
- Harden replay-validity task identity so per-task gold-replay records bind to a stable identity ([4028f8a])
- Close arm identity QA gaps surfaced against the durable-identity contract ([c5caca6])
- Make frozen-baseline trial materialization selective and per-task, preserving trajectory artifacts and avoiding unnecessary copies ([e0d20b9], [f29a6db], [5f0a2fc])
- Document the new compare bootstrap flags in `stet eval compare --help` ([246ee48])
- Honor `--out` dataset reuse in the `stet eval rules` skill wrapper by short-circuiting the `rev_range_buildability` preflight when `dataset/build-summary.json` already exists and `--restart` is not set; the reuse decision is logged to stderr so `--plan` does not silently mask a divergent `--rev-range` ([d1374a76])
- Return `stet eval status` in ~2s on finalized compares by reading the persisted `eval_report.v1.json` sample-adequacy instead of walking `.stet/{eval-rules,leaderboard,archive,baselines}`; the cache binds to the requested compare root and rechecks adequacy inputs for freshness so fail-closed behavior is preserved (STET-387) ([8f439d49])

[v0.4.0]: https://github.com/benredmond/stet/releases/tag/v0.4.0
[de6c0bc]: https://github.com/benredmond/stet/commit/de6c0bc71f8cd69275e9caa9efa9b442e2de0fb5
[c64393c]: https://github.com/benredmond/stet/commit/c64393c6
[f3e9ee5]: https://github.com/benredmond/stet/commit/f3e9ee5f
[6870494]: https://github.com/benredmond/stet/commit/68704944
[6e07411]: https://github.com/benredmond/stet/commit/6e07411b
[3449973]: https://github.com/benredmond/stet/commit/344a9997
[f72da01]: https://github.com/benredmond/stet/commit/f72da01a
[5c5a181]: https://github.com/benredmond/stet/commit/5c5a1812
[ece1165]: https://github.com/benredmond/stet/commit/ece1165e
[5f671b3]: https://github.com/benredmond/stet/commit/5f671b3c
[a731873]: https://github.com/benredmond/stet/commit/a7187351
[9776d82]: https://github.com/benredmond/stet/commit/9776d820
[36ec2c3]: https://github.com/benredmond/stet/commit/36ec2c3c
[cb77959]: https://github.com/benredmond/stet/commit/cb77959a
[4028f8a]: https://github.com/benredmond/stet/commit/4028f8a7
[c5caca6]: https://github.com/benredmond/stet/commit/c5caca63
[e0d20b9]: https://github.com/benredmond/stet/commit/e0d20b96
[f29a6db]: https://github.com/benredmond/stet/commit/f29a6db1
[5f0a2fc]: https://github.com/benredmond/stet/commit/5f0a2fc7
[246ee48]: https://github.com/benredmond/stet/commit/246ee48e
[174a94e6]: https://github.com/benredmond/stet/commit/174a94e6
[4939dd3f]: https://github.com/benredmond/stet/commit/4939dd3f
[d1374a76]: https://github.com/benredmond/stet/commit/d1374a76
[8f439d49]: https://github.com/benredmond/stet/commit/8f439d49
[9866fe4]: https://github.com/benredmond/stet/commit/9866fe4

## [v0.3.1] - 2026-05-15

Enrichment runs natively in Go end-to-end; the Python `enrich_dataset.py` scaffolding is gone and prompts ship without XML fences.

### Changed
- Port `enrich_dataset.py` to Go and drop XML scaffolding from enrichment prompts ([5bb132b])

[v0.3.1]: https://github.com/benredmond/stet/releases/tag/v0.3.1
[5bb132b]: https://github.com/benredmond/stet/commit/5bb132bc872c858889714601c75aff7c93d9b310

## [v0.3.0] - 2026-05-15

Adds operator launch receipts, opus reasoning-curve evidence on the leaderboard, and tightens prompt-shape provenance with fail-closed enforcement when `ai_task` is missing. Smoke preflight is now bypassable for fast iteration, eval status terses on completion, and h2h gains typed grader-failure counters and small-sample directional reads.

### Added
- Surface opus reasoning-curve evidence on the leaderboard ([5e691ba])
- Shift `ai_task` prose to imperative goal-first phrasing during enrichment ([8812b1f])
- Record prompt-shape provenance during build and fail closed when `ai_task` is missing ([7c941bd])
- Add `--prompt-shape` to `stet build` with `self-contained-natural` as the default ([2ef2130])
- Expose `--skip-smoke-preflight` on `stet eval run` for fast candidate iteration ([84214b2])
- Terse `stet eval` status on complete and add `eval report --paths` ([4ae50c7])
- Recognize smoke-preflight runs in the frozen-baseline compare flow ([98df234])
- Polish plan JSON shape and emit an `rc!=0` next-step hint from `stet eval rules` ([b7d3eed])
- Persist smoke-seeded task provenance on the runner runtime artifact ([64653d1])
- Add rules study holdout lanes ([cbccb27])
- Add operator launch receipts to the CLI ([210ee15])
- Add Mandarin blog translations to the leaderboard ([dc16c7d])
- Publish the opus reasoning-curve writeup on the leaderboard ([16f961d])
- Surface typed grader-failure counters on `stet eval` report, status, and the decision receipt (STET-312) ([6e03355])

### Changed
- Reframe the stet-dist README as agent-first and add an onboarding quickstart ([2c02fa7])
- Collapse `TaskMetaConfig` literals and unify prompt-shape resolution across build paths ([b77f10c])
- Unify task-instruction assembly across all build paths ([4b1dcb6])

### Fixed
- Hoist grader-evaluator preflight and gate `activity_state` on resolved backend ([bebf8e1])
- Account for smoke preflight provenance in compare math ([c9711e7])
- Preserve tracked `.stet` contents after repo-bundle bootstrap ([5c8499c])
- Expose limited directional reads for small-sample h2h comparisons ([f217cb0])
- Preflight rules replay validity ([9ef099c])

### Internal
- Refresh dist collateral for v0.3.0 ([cbcab16])
- Drop the tessl MCP server config from codex ([5645ee8])
- Polish ONBOARDING.md voice and content for stet-dist ([20751fa])
- Include ONBOARDING.md in the dist sync CI step ([7cd553c])
- Add ONBOARDING.md explainer for human readers in stet-dist ([1e3eab9])
- Document why terse eval status points at the decision report instead of `--paths` ([8bbd214])
- Reframe the AGENTS guide and refresh design-stet plus QA scenario coverage ([a1e5557])
- Polish opus post presentation and sync copy from the vault ([e49a181], [445d8e7])
- Explain replay-invalid rules slices in the Stet skill docs ([8c624e7])

[v0.3.0]: https://github.com/benredmond/stet/releases/tag/v0.3.0
[cbcab16]: https://github.com/benredmond/stet/commit/cbcab16fcb1aa9af5d24baa4e4fe2e204df86ce8
[5e691ba]: https://github.com/benredmond/stet/commit/5e691bac457b6ca038721ecf20834a0f639be644
[8812b1f]: https://github.com/benredmond/stet/commit/8812b1f152adc533a1cee48df2c0bab449a3fe0d
[7c941bd]: https://github.com/benredmond/stet/commit/7c941bda2a838adec2ced203164a28b008619642
[5645ee8]: https://github.com/benredmond/stet/commit/5645ee8083db3aa8afe3c921905c619bd8d06f5c
[2ef2130]: https://github.com/benredmond/stet/commit/2ef21307d40347f9673e27b03839bdb0bc3f2477
[20751fa]: https://github.com/benredmond/stet/commit/20751fa3c7bdf276e982dd684b1bfc3645df9883
[7cd553c]: https://github.com/benredmond/stet/commit/7cd553cf4c27ce6a1e08cb4ba4f703831510be56
[bebf8e1]: https://github.com/benredmond/stet/commit/bebf8e1c69b1cfe600975b081b9de8e50697866f
[1e3eab9]: https://github.com/benredmond/stet/commit/1e3eab96097ebbd85b799893b147094ff9b2c862
[98df234]: https://github.com/benredmond/stet/commit/98df2349b3621ab179dcd6c6537801f07dfd4e13
[2c02fa7]: https://github.com/benredmond/stet/commit/2c02fa764c19e89b67070547d1d18b016b6347d9
[84214b2]: https://github.com/benredmond/stet/commit/84214b28f08c5f327ec434c99546d973698d8b66
[8bbd214]: https://github.com/benredmond/stet/commit/8bbd2143646dd6fc3684d8164135a90541a29509
[4ae50c7]: https://github.com/benredmond/stet/commit/4ae50c7432cd2d327acb7a25276a616cd0431334
[b77f10c]: https://github.com/benredmond/stet/commit/b77f10cfb5a41c2d7edb38f09313968b7658ad16
[4b1dcb6]: https://github.com/benredmond/stet/commit/4b1dcb690780e7ae9104e25fd77f5a669ce55ec8
[a1e5557]: https://github.com/benredmond/stet/commit/a1e55579cea07f87ecabc4336e78aa7ba9d60590
[5c8499c]: https://github.com/benredmond/stet/commit/5c8499cf4c2ed05eab8e336ab5fc99beb867e007
[b7d3eed]: https://github.com/benredmond/stet/commit/b7d3eedb98c7db80c6767acd96802c3650c7823c
[64653d1]: https://github.com/benredmond/stet/commit/64653d18af0769e8aff18fd83912022254bdd628
[cbccb27]: https://github.com/benredmond/stet/commit/cbccb27408315f9a3e3d6827d08ff865eca547d4
[c9711e7]: https://github.com/benredmond/stet/commit/c9711e7e1a38da3bc6a037e8f28dbb9855dbed9d
[210ee15]: https://github.com/benredmond/stet/commit/210ee1538449a9ccb0fa2f904d3c68e9c0ae0318
[dc16c7d]: https://github.com/benredmond/stet/commit/dc16c7dda56057eadc471dae44d1018ce811d97b
[e49a181]: https://github.com/benredmond/stet/commit/e49a18114a8b96ad79802f3e21f9eba8b06a5b6d
[445d8e7]: https://github.com/benredmond/stet/commit/445d8e75bf423175921d28f559d286ac4116d8e1
[16f961d]: https://github.com/benredmond/stet/commit/16f961d65c75b41f34c695319e6c4317d0bc8495
[f217cb0]: https://github.com/benredmond/stet/commit/f217cb06b02a93333d5dafae55ec767292d3241e
[9ef099c]: https://github.com/benredmond/stet/commit/9ef099cbc0def945bf8ea298705d5d0bf6ed2f41
[8c624e7]: https://github.com/benredmond/stet/commit/8c624e74d966c399735a7e255fe3c2c6fce606b2
[6e03355]: https://github.com/benredmond/stet/commit/6e033556f067387818d7522ec81f7c0b90f7bf65

## [v0.2.0] - 2026-05-11

Hardens the `stet eval rules` flow end-to-end with grader-profile persistence, preflight checks, and surfaced provenance; introduces the GPT-5.5 reasoning-curve leaderboard post and pairwise order-swap judging for custom-grader compares; adds activity-state disambiguation, sample-adequacy reporting, and a stet-qa skill harness for black-box testing the shipped Stet docs. Many small fixes tighten artifact integrity (non-regular file rejection, symlink-escape guards) across the harness.

### Added
- Add `--grader-ai-cmd` / `--grader-ai-model-id` wrapper flags to the eval-rules skill (STET-338) ([9b8c370])
- Surface agent-side exceptions in the `last_error` receipt (STET-332) ([f96da10])
- Improve Stet SEO surfaces on the leaderboard ([7a18f7f])
- Add sticky TOC to the GPT-5.5 reasoning-curve post ([540dcc4])
- Publish the GPT-5.5 reasoning-curve post and add it to model comparisons ([5f890e5], [91c8fa4])
- Preserve explicit `--mode` through stitch and repair ([9cda0af])
- Support optional requested graders and explicit repair evaluators ([9ee0208])
- Centralize structured custom-grader calls ([b9ced48])
- Persist and reuse eval-rules grader profiles, with planning and reported provenance ([893a8df], [dec49c3], [8b377af], [ac48552])
- Add safe stale Docker cleanup to harbor ([fdfc2f5])
- Add eval-rules grading controls ([2a5ee65])
- Persist task outcome history across runs ([8fc26e1])
- Surface eval sample adequacy ([ecd2b60])
- Add order-swap pairwise per-task judging for custom-grader compares ([1d6cbdb])
- Add the stet-linear-tpm skill for Symphony-ready ticket shaping ([d31901f])
- Add `max` as a first-class reasoning-effort tier ([7d47898])
- Make evals quota-aware ([7309948])
- Accept an explicit agent for `stet eval smoke` ([37a7c19])
- Add a default randomized H2H task order ([f9e8320])
- Bake `claude-code` and `codex` into the harbor image ([e766928])
- Route Harbor Codex through `codex-lb` ([498a132])
- Register `gpt-5.5` with pricing and alias ([97bbfbf])
- Add stet-qa scenarios for `claude_md`, `docs_glob`, `model_update`, and `skill_diff` ([98bd7cb])
- Migrate leaderboard datasets to Stet v1 and rewrite ingestion ([1a06b2a])
- Bake `install_config` into per-task Dockerfile and skip node lifecycle scripts during baked install ([1af7972], [8d86967])
- Surface trajectory-derived behavior metrics in eval reports ([0b08059])
- Add artifact-retention compaction ([6d2cb0e])
- Add `--skip-smoke-preflight` to bypass the candidate smoke gate (eval-rules) ([0d446c8])
- Add Opus 4.7 vs 4.6 zod blog item to the leaderboard RSS feed ([b8478f8])
- Add the agents-md-preflight QA scenario and shared 1-task fixture ([fdc0f61], [4819136])
- Add the validate-change-manifest QA scenario and fixture ([b6c477d], [daaddce])
- Add stet-qa SKILL.md scaffolding (skeleton, preamble, report template, fixtures reference, design spec) ([20f7980], [83d0517], [4314d57], [7b29eb8], [8ebc50d])
- Add the stet-qa implementation plan ([ccea8fb])
- Register `eval_rules_plan` as a commercial command ([1e7f44e])
- Publish the Opus 4.7 vs Opus 4.6 Zod writeup with cost and token detail ([cf26998], [77fc7d0])
- Add the GPT-5.5 vs Opus 4.7 blog post and blog SEO scaffolding ([2d9e7da])
- Add an agent setup snippet to `/private` ([cf925a1])

### Changed
- Surface artifact-discrimination diagnostic for any custom-grader compare ([36b923f])
- Honor model-specific AI agents ([d4f33a7])
- Refine GitHub doc-only path classification ([277508b])
- Bound `GRADE_CUSTOM` rubric grader calls with a per-call timeout ([0471faa])
- Stabilize custom-grader no-patch scoring ([8276a9d])
- Update site navigation links and refresh the homepage funnel ([67d401a], [a9ab39c])
- Update the GPT-5.5 vs Opus blog post and methodology data ([8b8d276], [dbe4cf4])
- Overlay current conventions in materialized tasks ([33d8150])
- Improve SEO pages for model comparisons ([a6c36e8])
- Separate grader AI config in eval flows ([a45858f])
- Sort custom-rubric prompt criteria deterministically ([3900957])
- Convert cramped Opus 4.7 tables to bar charts and merge review/discipline into one rubric chart ([1bab40e], [54d58ed])
- Refresh validate-change-manifest dogfood with post-fix run ([8a40b88])
- Stop default Claude Keychain auth lookup ([36eaadc])
- Reduce Vercel compute for inspect routes ([b50c773])

### Fixed
- Add `activity_state` to disambiguate in-flight versus terminal eval status (STET-333) ([83b7ba9])
- Tighten plan/manifest receipts and skill text (rules) (STET-329) ([709295f])
- Reject non-regular pinned dependencies, repo tarballs, validation agent patches, config files, test inference files, score patches, and unsafe cost-usage artifacts and output-root manifests; block git-internals context paths ([ef30ea8], [4c35c65], [bedad3a], [7202b8a], [c812fc2], [a59e904], [e79efe0], [186e25a], [160263b])
- Refresh stale grader coverage from arm summaries ([3611c8c])
- Repair short/non-hex citations, lift nested findings, and add skip-reason-specific refusal text (eval-rules) ([f0e01bc])
- Repair rules QA follow-up flows ([d756cb5])
- Treat nested smoke evidence as pending-compare arm evidence ([d5781c8])
- Share Claude envelope unwrap and refuse empty skill datasets (eval-rules) ([826668f])
- Unwrap Claude `--output-format json` envelope before grader parse ([165f5eb])
- Classify wrong-repo as `repo_not_a_git_repository` and fix QA fixture repo paths ([ed1d4fc])
- Wire grader-ai flags, classify default-branch `launch_error`, and document `--tasks` coupling ([3ae2acb])
- Surface pre-arm failures via `launch_error` and fix baseline path lookup ([400959e])
- Preflight rev-range buildability and document `--rev-range` (STET-331) ([4b9611c])
- Preflight grader provenance in `eval-rules-plan` (STET-330) ([20a1c9c])
- Preflight `--out` dataset and surface build errors in the eval-rules skill ([ab85acf])
- Preflight repo-managed skills root symlinks (STET-327) ([b90aac8])
- Refuse `eval rules` launch when LLM grader credentials are missing (STET-324) ([99fc652])
- Stop recommending resume on terminal rules-arm failure (STET-325) ([5c37fb4])
- Resume resolves treatment paths against the suite repo root ([01433d1])
- Preserve grader and cost evidence on stitch ([55c0cbb])
- Recover rules resume evidence ([9370f05])
- Preserve regrade economics in summaries ([25f5edb])
- Bound frozen-baseline materialization ([cc44270])
- Expose eval report reasoning effort ([896df69])
- Recover trailing custom-grader JSON ([8785d0e])
- Resolve nested sample-adequacy history roots ([dab87b6])
- Detect mixed arm provenance ([c813057])
- Surface rules compare arm status ([73cfd44])
- Preserve frozen-baseline custom graders ([ab5c0b7])
- Reclaim `artifacts/agent.patch` duplicates left by harbor ([fc8cba9])
- Avoid bare 429 quota classification ([9b9b467])
- Copied-patch path classification ([d6688b0])
- Surface repairable custom-grader parse failures ([778891f])
- Enforce grader-evaluator provenance ([db0d690])
- Classify executor failure tail output ([c32f3f8])
- Enforce clean guidance overlays ([c3c8de7])
- Target-pass commit overscan ([0759526])
- Improve blog text contrast ([ee1772e])
- Remove visible SEO duplication from blog posts ([512e9b7])
- Harden review-retry prompt parse errors ([62045c5])
- Repair embedded prompt source loading ([577ecea])
- Reject weekly doctor reports symlink escapes ([966ea35])
- Fix unsafe run-ID artifact lookup ([5fc50b8])
- Fix markdown-bold kv value parsing ([38bd4e3])
- Reject non-executable generated test commands ([08737b5])
- Fix Codex assistant trajectory capture ([ab00275])
- Reject symlinked validation roots ([a19a4a1])
- Reject non-regular gate prompt sources ([6419f9a])
- Validate manifest build numeric flags ([1410ac1])
- Ignore external diff for split patches ([c2f2beb])
- Exclude failed tasks from the weekly denominator gate ([d25e61a])
- Preserve UTF-8 in review-retry prompt ([6e4a324])
- Preserve eval-rules plan launch flags ([f6db705])
- Use per-task cost and time in the GPT-5.5 post ([00b470c])
- Fix frontend audit and Turbopack warnings ([00164b2])
- Prevent convention overlays from polluting agent patches ([96d4090])
- Fix eval-rules runtime evidence locator ([f87d834])
- Fix grader coverage reporting ([53079cd])
- Recover cache tokens when rollup omits them and sum Claude assistant turns ([489ab31])
- Merge experiment report when arms record different dataset paths but identical task slices ([423d581])
- Smoke-preflight liveness classification ([0ba1f41])
- Smoke-gate canonical harbor pass ([9cd6a4b])
- Honor gitignore in harbor patch capture ([edc58f0])
- Preserve evaluator model provenance in grader artifacts ([8a0d747])
- Avoid copying run artifacts during compare staging ([e12bcfb])
- Improve rules-skill wrapper recovery ([a43d462])
- Gate Vercel tracing config so local dev resolves tailwindcss ([5f9f977])

### Internal
- Forbid bespoke leaderboard eval shortcuts in agent docs ([942ac71])
- Refine smoke-preflight provenance and terminal no-patch coverage ([5f07a75])
- Assert h2h repo root by source marker, not basename ([f56a5a6])
- Stabilize stet qa grader preflight ([5006a18])
- Migrate `agents-md-preflight` from sonnet-4.6 to gpt-5.4 (stet-qa) ([32131fe])
- Pin `rev-range-buildability` seeded_from to STET-331 fix SHA ([316efae])
- Sync dist skill snapshot ([718a961], [2520373], [54c1383])
- Roll up failure-path skill drift findings (STET-337) ([8180be2])
- Sync GPT-5.5 reasoning-curve post copy with vault edits ([5aa49ab])
- Ignore claude worktrees, generated leaderboard typings, local launchers, and scheduler lock ([da09121], [fcf22a1])
- Reuse command normalization for task defaults ([e9a1c19])
- Share config value resolution ([7cb5f5d])
- Centralize relevance sorted unique strings ([068040c])
- Centralize Claude auth env lists ([b3952ac])
- Share workbench baseline record loading ([7de8135])
- Centralize path containment checks ([8017b74])
- Share safe path joining ([f0537a0])
- Filter weekly denominator membership ([6d5f68c])
- Preserve task grader rubric scores ([608a249])
- Share local-inspect file traversal ([547133e])
- Clarify leaderboard dogfood eval policy ([5200eb4])
- Refactor leaderboard navigation links ([219ac3e])
- Refactor aicmd explicit option handling ([79809a0])
- Simplify diff path marker parsing ([81d33ac])
- Cover Next config env behavior ([9c5c168])
- Trigger Vercel deployment ([823b32c])
- Record stet-qa dogfood-03 gap-closure verification ([7d133fe])
- Address stet-qa dogfood-02 unclear-receipt gap ([c7eadd9])
- Link the stet-qa skill from the Progressive Disclosure Index ([22dbd82])
- Record stet-qa dogfood: parallel dispatch synthesis ([f338599])
- Record stet-qa dogfood: validate-change-manifest ([61bf64f])
- Rename stet-qa report file to `qa-report.md` ([033f03d])
- Cover `--pairwise` cap and document flags in compare help ([9b5991d])
- Update archived zod evidence paths ([274f59c])
- Add the flu82 graphql xhigh launcher ([778f3b9])
- Merge origin/main and merge the GPT-5.5 reasoning-curve blog ([18b7614], [903f126], [2c12471])

[v0.2.0]: https://github.com/benredmond/stet/releases/tag/v0.2.0
[d5781c8]: https://github.com/benredmond/stet/commit/d5781c841fe0f79b69afe5403d5251064e8be700
[d756cb5]: https://github.com/benredmond/stet/commit/d756cb581b780e1fc1c260c6940182aa0b5bd07d
[5006a18]: https://github.com/benredmond/stet/commit/5006a185fcb88bb6ee4cee84d644e4541a013376
[718a961]: https://github.com/benredmond/stet/commit/718a96182dc8de452a3bffdf2ac8cee1a253d6c7
[da09121]: https://github.com/benredmond/stet/commit/da09121160b569b33e379e2da749a5c013181c3b
[3611c8c]: https://github.com/benredmond/stet/commit/3611c8c04c8f84fdafe483136543a945603cf562
[f0e01bc]: https://github.com/benredmond/stet/commit/f0e01bc16e373acddf4c29b8b2df9e5d271b0632
[498a132]: https://github.com/benredmond/stet/commit/498a13284ef4370dbf5d631d4cfc22dc9b5011ae
[826668f]: https://github.com/benredmond/stet/commit/826668f0be3188e849d5b1e0e171c31fbfcecf21
[2520373]: https://github.com/benredmond/stet/commit/2520373d25bec1866021f6cacc592b956f5127f4
[165f5eb]: https://github.com/benredmond/stet/commit/165f5eb92362e83008bb13855dd75ac47d4744a1
[ed1d4fc]: https://github.com/benredmond/stet/commit/ed1d4fce21b043616b505260f95da00a3a091cf2
[3ae2acb]: https://github.com/benredmond/stet/commit/3ae2acb7b2e9f53a9b184e9921e04a69f35f2c40
[400959e]: https://github.com/benredmond/stet/commit/400959eed17b8e18c0689dbc56297606b82e32cc
[f56a5a6]: https://github.com/benredmond/stet/commit/f56a5a664f94a485c248d5b398f77cdae39706a0
[9b8c370]: https://github.com/benredmond/stet/commit/9b8c370834dc6611c0da6a116e41cbc1d189a25f
[316efae]: https://github.com/benredmond/stet/commit/316efae445d452b4314925af9108c03223d437d7
[4b9611c]: https://github.com/benredmond/stet/commit/4b9611c1f169eb0f710604f884b37362dcc01fbc
[f96da10]: https://github.com/benredmond/stet/commit/f96da10d22407367833b914c5b1232b81a67a5f9
[20a1c9c]: https://github.com/benredmond/stet/commit/20a1c9cd936e51ab30b9f4bbf171b9e666ec2943
[83b7ba9]: https://github.com/benredmond/stet/commit/83b7ba961da3279d6fad0669e2c81c92b2206a45
[8180be2]: https://github.com/benredmond/stet/commit/8180be2778cbcc8056ad60c0174bd24983bf6fcb
[709295f]: https://github.com/benredmond/stet/commit/709295f5b7ce67e28861cc0b56ca88984cc680be
[ab85acf]: https://github.com/benredmond/stet/commit/ab85acf973dc2f09e8f81f14efa955a31b1b7753
[01433d1]: https://github.com/benredmond/stet/commit/01433d139045df51ae169b95ea94d15e9f849588
[b90aac8]: https://github.com/benredmond/stet/commit/b90aac8ee2140fca0d8624847d757c2ddbfcb65b
[99fc652]: https://github.com/benredmond/stet/commit/99fc65246bfaa2d7b713f19616915970b99e6e9a
[5c37fb4]: https://github.com/benredmond/stet/commit/5c37fb479cbb0d19e6cc25a0d12d5e702d009fb8
[2c12471]: https://github.com/benredmond/stet/commit/2c1247190603bd3e78aa7997b1a39b9c01f1b397
[7a18f7f]: https://github.com/benredmond/stet/commit/7a18f7fa01dc294b07b3e4ed9bf471a646c17f70
[55c0cbb]: https://github.com/benredmond/stet/commit/55c0cbbb7cd0ffe5da28579aa653a3e41f0f7432
[9370f05]: https://github.com/benredmond/stet/commit/9370f05a0841beb8df25922c8f655ad0d9236e98
[540dcc4]: https://github.com/benredmond/stet/commit/540dcc48f74aef5c9d587a1c4e75e894e1dd49ab
[91c8fa4]: https://github.com/benredmond/stet/commit/91c8fa4a0487bd39da1133b45bec9516faa63cf5
[5aa49ab]: https://github.com/benredmond/stet/commit/5aa49ab15a27f426b6541fa523d3dfe94c472358
[5f07a75]: https://github.com/benredmond/stet/commit/5f07a7559f2931bffdb1d48b3b2abc5144b71984
[9cda0af]: https://github.com/benredmond/stet/commit/9cda0af27ad4e3b95fc9a5cf1d75e151b2f80ea0
[9ee0208]: https://github.com/benredmond/stet/commit/9ee02089ea341d68196502cec38436abb1ef41ad
[942ac71]: https://github.com/benredmond/stet/commit/942ac711d07322169a08990c3323edf792ecf0d3
[b9ced48]: https://github.com/benredmond/stet/commit/b9ced48a2bed9e9c03fd7d2fd9543ec255f4597e
[18b7614]: https://github.com/benredmond/stet/commit/18b76145759a2f1dfe66da96b258604603d47c02
[903f126]: https://github.com/benredmond/stet/commit/903f1262999c799bdf2ef3f1d84cceb73585c69f
[5f890e5]: https://github.com/benredmond/stet/commit/5f890e5840abd6159373b99ebac6eb3eab6e4dc8
[25f5edb]: https://github.com/benredmond/stet/commit/25f5edb41faf8311cf54041085cf5771570b8a7b
[ac48552]: https://github.com/benredmond/stet/commit/ac485520516eaa06def7905f985e4d5a36613ca6
[8b377af]: https://github.com/benredmond/stet/commit/8b377afc50b67cc7670a24f8d5a97e80ba2df536
[893a8df]: https://github.com/benredmond/stet/commit/893a8dfa54e776f6e37d7d9d7787fc077fef3098
[dec49c3]: https://github.com/benredmond/stet/commit/dec49c3fdf7576442db2fd2e04580113483fb2ff
[cc44270]: https://github.com/benredmond/stet/commit/cc44270f6da92d6c195663281907af444149ff09
[fdfc2f5]: https://github.com/benredmond/stet/commit/fdfc2f5a73a6f1210c870412c920d124c8ab8c91
[778f3b9]: https://github.com/benredmond/stet/commit/778f3b9d6759b90b02904c9ba0df8aa3ca299f28
[274f59c]: https://github.com/benredmond/stet/commit/274f59cbb8e6d4c64fece5a86903836c14be80c3
[2a5ee65]: https://github.com/benredmond/stet/commit/2a5ee659524df4f5d2068f9c49442a0a1b2d0541
[896df69]: https://github.com/benredmond/stet/commit/896df6937952ec938a65754589eefea6504cb3fd
[8785d0e]: https://github.com/benredmond/stet/commit/8785d0ebf2835674cee6f2e3a2f4cffe45cde0fd
[dab87b6]: https://github.com/benredmond/stet/commit/dab87b6d6ed66fcdf4648b9d6e688b0e9f839b1d
[c813057]: https://github.com/benredmond/stet/commit/c8130577e01c792d2375863c9ce2919cd634a09d
[8fc26e1]: https://github.com/benredmond/stet/commit/8fc26e12e8e2bbc71c333c878493e81ff3050d65
[ecd2b60]: https://github.com/benredmond/stet/commit/ecd2b60f0ada535a4332aa22bab13cbdf0d76642
[73cfd44]: https://github.com/benredmond/stet/commit/73cfd44b65237ce896472923ae5f70ec30d29f7b
[36b923f]: https://github.com/benredmond/stet/commit/36b923f022976564c7b0c6333a25f8ffec76db47
[ab5c0b7]: https://github.com/benredmond/stet/commit/ab5c0b71df32a79d40dd02799a7a7fbe4f2469c3
[0471faa]: https://github.com/benredmond/stet/commit/0471faacf2e3ab3ab0acf9e4dece6c14bc11d0d5
[e766928]: https://github.com/benredmond/stet/commit/e766928c75010455d8ebcdfa62de95c2fc51a214
[fc8cba9]: https://github.com/benredmond/stet/commit/fc8cba98053be82a25e8130a13a8a9d5f2dc1da4
[9b5991d]: https://github.com/benredmond/stet/commit/9b5991d56d459652364ef14a82f5cdce3584adb9
[1d6cbdb]: https://github.com/benredmond/stet/commit/1d6cbdb540f63c5be92d5363d77dfffcb542d270
[d31901f]: https://github.com/benredmond/stet/commit/d31901ff60b086e003b9806125b588e04299d84b
[7d47898]: https://github.com/benredmond/stet/commit/7d47898cef069013bce42083b6f8bd265062663a
[8276a9d]: https://github.com/benredmond/stet/commit/8276a9d7fa5864de8bc1baa1440cf6c068816171
[ef30ea8]: https://github.com/benredmond/stet/commit/ef30ea838e3e91f1bce21fae4a3f147863e0ae92
[e9a1c19]: https://github.com/benredmond/stet/commit/e9a1c194e1dd9a9186962c55a4cc699fbdc5c943
[9b9b467]: https://github.com/benredmond/stet/commit/9b9b4676c7625cd9467cc00a4a28c5679a0a5b9f
[e79efe0]: https://github.com/benredmond/stet/commit/e79efe0e5131e06f6c8e6a36c45ad388174500d4
[d6688b0]: https://github.com/benredmond/stet/commit/d6688b0e8d981b6ffc2ddb0aadfbb275170f6a5c
[3900957]: https://github.com/benredmond/stet/commit/39009575b838d1453af8780b61baa3c78f7f8470
[7cb5f5d]: https://github.com/benredmond/stet/commit/7cb5f5d67a6d91be55339d18ecdf650e25177983
[186e25a]: https://github.com/benredmond/stet/commit/186e25a17d64f8ff52cac1bc54274442841a56ad
[277508b]: https://github.com/benredmond/stet/commit/277508ba4f6c173690e37d20a88c372a228e5ee1
[068040c]: https://github.com/benredmond/stet/commit/068040c55a1198a1013e22e1dd19e9d547bb3c4e
[4c35c65]: https://github.com/benredmond/stet/commit/4c35c6565ce42a6fb038df796fe92138e03546a8
[d4f33a7]: https://github.com/benredmond/stet/commit/d4f33a7cd3d1085b5af41cb29a87a2201ac04624
[778891f]: https://github.com/benredmond/stet/commit/778891fa6f8b73b630d7658e5f384ffe53317800
[bedad3a]: https://github.com/benredmond/stet/commit/bedad3a1d3df97b0c7e6f24f9a6d9ddf29961fcd
[db0d690]: https://github.com/benredmond/stet/commit/db0d6900de68a4bf14cd0369fadeca2cbe94fb64
[7202b8a]: https://github.com/benredmond/stet/commit/7202b8a26d66782005489ac74f9163c6f4895749
[b3952ac]: https://github.com/benredmond/stet/commit/b3952ac5af63aa21cf199d2d80bb06c63cea4858
[c32f3f8]: https://github.com/benredmond/stet/commit/c32f3f8ded284573c6e8e0962e4fdf639ca811dc
[c812fc2]: https://github.com/benredmond/stet/commit/c812fc247d5bd4d6441e5686f17c8b07affce413
[a59e904]: https://github.com/benredmond/stet/commit/a59e904f0960a974dea618dbca91ddc261843063
[7de8135]: https://github.com/benredmond/stet/commit/7de81355abb234d71cc4d35630135ff171de4ea3
[160263b]: https://github.com/benredmond/stet/commit/160263b1450d0852af5e04e62adc7b8f1e39cbc1
[6d5f68c]: https://github.com/benredmond/stet/commit/6d5f68cb61cc7fba2d32ea124d80ce37444430b1
[608a249]: https://github.com/benredmond/stet/commit/608a249ad15499f9b951a7cbcf87edf405d2c6dc
[c3c8de7]: https://github.com/benredmond/stet/commit/c3c8de7870324c6ec96ab6b0fb9187d93ee9b9b7
[0759526]: https://github.com/benredmond/stet/commit/0759526a352dbc682c356152cd2a17349a7d7dc6
[547133e]: https://github.com/benredmond/stet/commit/547133e09211641a15716c0da005450e45a25bc1
[5200eb4]: https://github.com/benredmond/stet/commit/5200eb400c20d9b8d1805d39f3372389d6401704
[ee1772e]: https://github.com/benredmond/stet/commit/ee1772ee5fafe1179f209bb430276f17cdc240ea
[512e9b7]: https://github.com/benredmond/stet/commit/512e9b7baa02e0cbe33d8aa9e5ed842bac23c825
[62045c5]: https://github.com/benredmond/stet/commit/62045c5b8e1073c067debf9ab0b404a0d8fa007e
[7309948]: https://github.com/benredmond/stet/commit/730994826c74e9b81b398a165dd6571dad972854
[577ecea]: https://github.com/benredmond/stet/commit/577eceaf36e5d9d9b928ee4b051605cc4539737c
[8017b74]: https://github.com/benredmond/stet/commit/8017b747a0fc5dcf8028fddc98281f721328b3ac
[966ea35]: https://github.com/benredmond/stet/commit/966ea3576e6f3d30ca6c857f9aefa3e5b4bbd74e
[37a7c19]: https://github.com/benredmond/stet/commit/37a7c196c318ec7d2da24702d53e99d344a0f225
[5fc50b8]: https://github.com/benredmond/stet/commit/5fc50b8948db6d8f1b9de87d2247ad83c3e27921
[219ac3e]: https://github.com/benredmond/stet/commit/219ac3e5c74e4aa774b9fecbaa2b7a5a354190e3
[38bd4e3]: https://github.com/benredmond/stet/commit/38bd4e37d5f55c686ba36419d65b1d0ced0fd014
[08737b5]: https://github.com/benredmond/stet/commit/08737b522321e9e3e4dc53d999414422d85a9faf
[ab00275]: https://github.com/benredmond/stet/commit/ab0027509572b35649751ee4b5f44b61c26e4b4c
[a19a4a1]: https://github.com/benredmond/stet/commit/a19a4a14ed76ece8193a0dbc796fbb60d66527f4
[79809a0]: https://github.com/benredmond/stet/commit/79809a0c0200e65f21610ed39bd857f5715d31d6
[6419f9a]: https://github.com/benredmond/stet/commit/6419f9a1b405dba38f1453df2d1bef633160c13f
[a6c36e8]: https://github.com/benredmond/stet/commit/a6c36e860ac852767f6e480fd98b1dd1b84cf062
[1410ac1]: https://github.com/benredmond/stet/commit/1410ac131e80b6ab69759254e299c623746e8e1e
[c2f2beb]: https://github.com/benredmond/stet/commit/c2f2bebafc915e095ddb682e89892e16debd74d7
[d25e61a]: https://github.com/benredmond/stet/commit/d25e61a7e44e570ab05aa915fcf0b6a8a25dacad
[81d33ac]: https://github.com/benredmond/stet/commit/81d33ac3c6bf1a8c6f5e3fa4acfeb5771de8dbec
[6e4a324]: https://github.com/benredmond/stet/commit/6e4a324966604609ad0ea6e86b67d52166931c97
[f9e8320]: https://github.com/benredmond/stet/commit/f9e832075b9b4651bf745ff5fbceade61e99c734
[f0537a0]: https://github.com/benredmond/stet/commit/f0537a01810bd49b1dce4c1099c389040d7478fb
[f6db705]: https://github.com/benredmond/stet/commit/f6db705609cdb333778ad120e7c40b726fb4088d
[00b470c]: https://github.com/benredmond/stet/commit/00b470c00affc460993e27a3c40aff164235f056
[823b32c]: https://github.com/benredmond/stet/commit/823b32c2f7de4fe640566b88690edf5fde54ff30
[a9ab39c]: https://github.com/benredmond/stet/commit/a9ab39c603970a21c5a0d0abf4dbf452cada3d28
[67d401a]: https://github.com/benredmond/stet/commit/67d401ad078d2ca6f1f652f8ba9d8d9e47b294f8
[8b8d276]: https://github.com/benredmond/stet/commit/8b8d276aa4b83761c6ff1e0463220ef92d0da45d
[dbe4cf4]: https://github.com/benredmond/stet/commit/dbe4cf489d28a09c4f22c6490397cc9751e5293f
[00164b2]: https://github.com/benredmond/stet/commit/00164b247b30bf0406ae037b8c4b39c5f671eb06
[2d9e7da]: https://github.com/benredmond/stet/commit/2d9e7da7a4d6a20cf133e2286a984eb7dbaf8ff8
[b50c773]: https://github.com/benredmond/stet/commit/b50c77370fff7113000bb8bbb6ec692b1425974c
[54c1383]: https://github.com/benredmond/stet/commit/54c13832c65e62ede952dd7bf064128641bc9f2b
[cf925a1]: https://github.com/benredmond/stet/commit/cf925a18f11cfb5cb82ca5f32bdfd1e7c64a7d5d
[96d4090]: https://github.com/benredmond/stet/commit/96d4090034d0fa86c39d1a189609157ed62e5432
[f87d834]: https://github.com/benredmond/stet/commit/f87d834a4f4c8ad2475a9752e901ae0fac2832de
[33d8150]: https://github.com/benredmond/stet/commit/33d8150b2146a2f52e6cbdf831e73ee6bb40bd0e
[53079cd]: https://github.com/benredmond/stet/commit/53079cdfcf3fb444db7dd035d53bab0d4a7e6d75
[489ab31]: https://github.com/benredmond/stet/commit/489ab3170dddc65ecc1928fc245aab035f4da04a
[423d581]: https://github.com/benredmond/stet/commit/423d58119db71bbbbd50ac9a822bee6f76fd9045
[0d446c8]: https://github.com/benredmond/stet/commit/0d446c8721ca3da7129dc03b03c59c69af90eb49
[0ba1f41]: https://github.com/benredmond/stet/commit/0ba1f414e8b8670353fff1e8e93b2d05c92dcfc6
[fcf22a1]: https://github.com/benredmond/stet/commit/fcf22a1c28d8befa73c9503303bfc3e2bb934bbb
[8d86967]: https://github.com/benredmond/stet/commit/8d869675932698f01f19054152b743c60e0c8d59
[a45858f]: https://github.com/benredmond/stet/commit/a45858f3342599f96ccaa5ca339f8b29cf6f7481
[9cd6a4b]: https://github.com/benredmond/stet/commit/9cd6a4bf22e7eece42f58e235aa38dc5bc2735e9
[0b08059]: https://github.com/benredmond/stet/commit/0b0805925489e1012fae52d5b743ec16b7b366ac
[6d2cb0e]: https://github.com/benredmond/stet/commit/6d2cb0e584e26c088efc533f1b34a4f674f17f31
[edc58f0]: https://github.com/benredmond/stet/commit/edc58f0533c8df2f7221d806e5d874bb5bfef24d
[1af7972]: https://github.com/benredmond/stet/commit/1af7972f3d2b162ff6bf30c11595a052864e12d9
[8a0d747]: https://github.com/benredmond/stet/commit/8a0d747435bfc0480323548182bc694d270631fd
[e12bcfb]: https://github.com/benredmond/stet/commit/e12bcfbf776a2951b87655733574645143b9f824
[a43d462]: https://github.com/benredmond/stet/commit/a43d462e28856755a2cf726af0f66a2b222cce17
[b8478f8]: https://github.com/benredmond/stet/commit/b8478f81cac67ff4a5864c8d30d9137a35319857
[97bbfbf]: https://github.com/benredmond/stet/commit/97bbfbf6025fb806ebebd9437dcf3ba42c34b204
[32131fe]: https://github.com/benredmond/stet/commit/32131fe3849ba3a56c460a41bc7f560e71eee0f2
[98bd7cb]: https://github.com/benredmond/stet/commit/98bd7cbd2b281aadbf92c80068cd2b24b2d1344d
[1a06b2a]: https://github.com/benredmond/stet/commit/1a06b2adb4b15b232c16e83d2d9b30a942d81138
[9c5c168]: https://github.com/benredmond/stet/commit/9c5c168de815a7bbfae342da52aa3236d0342bba
[7d133fe]: https://github.com/benredmond/stet/commit/7d133fed2cf51dcf963a9acadf854c2c4d96cecd
[c7eadd9]: https://github.com/benredmond/stet/commit/c7eadd9d63644f2873a4846e9b7d1362d14e5a6e
[22dbd82]: https://github.com/benredmond/stet/commit/22dbd82004aa2d018592eaa198f06bc6d6a71e88
[f338599]: https://github.com/benredmond/stet/commit/f338599fd35b899b84929b7b9f21d6482400a8c7
[fdc0f61]: https://github.com/benredmond/stet/commit/fdc0f613e0a7d7cc76e4f88359506d72e7cae920
[4819136]: https://github.com/benredmond/stet/commit/481913697e87c37860ef1bc0a49da6a972ee7596
[8a40b88]: https://github.com/benredmond/stet/commit/8a40b881528b96ff0220d83f9e706c471f661e06
[033f03d]: https://github.com/benredmond/stet/commit/033f03da5ea7fd203f729c7394467a5f5795c578
[61bf64f]: https://github.com/benredmond/stet/commit/61bf64fe154e06d760d80fea37948e05acb82108
[b6c477d]: https://github.com/benredmond/stet/commit/b6c477d563d96239322b16ebcc4d41bf18e63b84
[daaddce]: https://github.com/benredmond/stet/commit/daaddce587e66d3e4634f31acda56d4a1565749d
[36eaadc]: https://github.com/benredmond/stet/commit/36eaadc2fcabf4f29a690295b4a0384fddf8179f
[1e7f44e]: https://github.com/benredmond/stet/commit/1e7f44ec94025b61a53b147a7a35bde0c9d8cc42
[77fc7d0]: https://github.com/benredmond/stet/commit/77fc7d020fe1a378082e9a4950f3bdbe19888458
[7b29eb8]: https://github.com/benredmond/stet/commit/7b29eb84d8b8c8fe60d4396ae97ec2056a923a4f
[4314d57]: https://github.com/benredmond/stet/commit/4314d575cfc3f3b0dd4852d6f2a1664123ba3be1
[83d0517]: https://github.com/benredmond/stet/commit/83d05170c727248e140dd6aebaf062205f2c29a8
[20f7980]: https://github.com/benredmond/stet/commit/20f7980d89ec19bec622e7007105333e9861f7cf
[54d58ed]: https://github.com/benredmond/stet/commit/54d58ed86795a2a610d557b782c402c7416c570a
[ccea8fb]: https://github.com/benredmond/stet/commit/ccea8fb86e23c3ea449da1fd50d7894391108ec4
[1bab40e]: https://github.com/benredmond/stet/commit/1bab40ef0e1df78545d684f8156c4530b219596b
[5f9f977]: https://github.com/benredmond/stet/commit/5f9f977a8a652f5a2371e5b8e48888e025334d99
[cf26998]: https://github.com/benredmond/stet/commit/cf269982658e7667a9cf9594b6f3b5e9c21fa48a
[8ebc50d]: https://github.com/benredmond/stet/commit/8ebc50d7b2cd8babb0d7c9830bc694c509d49020

## [v0.1.0] - 2026-04-17

Initial productized release of the Stet CLI. Stet measures whether an AI coding change is safe to ship, covering the full capability lifecycle: probe and workbench for iterative improvement, gate for promote/hold/rollback, and monitor for scheduled regression detection. v0.1.0 lands the public command surface (`stet build`, `stet eval`, `stet eval rules`, `stet baseline`, `stet monitor`, `stet workbench`, `stet auth`), the canonical `eval_report.v1.json` trial result, a working harbor-backed Docker harness for replayable real-repo task corpora, the Next.js leaderboard frontend, and the stet-cli distribution channel for `pip`-style install.

### Added
- Public, productized CLI surface (`stet build`, `stet eval`, `stet eval rules`, `stet eval workbench`, `stet eval batch-grade`, `stet eval calibrate`, `stet baseline`, `stet monitor`, `stet workbench`, `stet auth`) with versioned model names, gauge-style help output, and a public manifest contract ([e7eef57], [8047f55], [7f7dcef], [11c8b74], [c3a26a4], [8fbd054], [251f33d], [086b59b], [932d07f], [bbe1764], [066e700], [f3e243b])
- Replayable task corpus pipeline: rev-range discovery, materialization, schema-aligned task bundles, repo-managed install configs, and harbor-backed per-task Docker harness for real-repo evaluation ([30d26fe], [0d3cdd4], [5a8763e], [29f4bea], [0ff45d1], [5ef34df])
- `stet eval` validation pipeline with AI-powered offline scoring, equivalence obligations, gate pipeline, and footprint-risk classification ([ab4471a], [3cc728e], [d4b65b0])
- Canonical `eval_report.v1.json` trial result and HTML report rendered alongside it as a sibling artifact (STET-244) ([7685e31], [c59037f])
- Custom YAML rubric graders, scored rubrics on a 0-4 scale (and float-scored 0.0-4.0), compare-gate lifecycle, and `stet eval calibrate` for adversarial rubric calibration ([786cbdd], [b742af7], [d4d0c4d], [1feb8ee], [066e700])
- Head-to-head (h2h) flow with native cutover, instruction treatments, frozen-baseline compare, suite-driven runs, eval-rules skill loop, and capability release tracking via `stet eval batch-grade` (STET-187, STET-166) ([d4b65b0], [2389f34], [c057f69], [1525697], [79773c1], [f3e243b])
- Stet skill packaged in dist and made install-first-class, with hypothesis-driven iteration guidance, comparison workflows, baseline-freeze teaching, and stet-cli (`benredmond/stet-cli`) as the public distribution channel ([ce5840a], [9e004ae], [15d6d7a], [4fa2394], [723a8f6], [a7706a4])
- Leaderboard Next.js frontend with model comparisons, blog posts (Opus 4.7 vs 4.6 Zod), inspect evidence preview, and editorial copy ([280efb6], [d7eb93c], [4033439])
- Reasoning-effort eval arms and Claude Opus 4.7 support with priced model registration ([7ed6f77], [3daf2cb], [feb6691])
- `stet monitor status` and `stet monitor run` for scheduled regression detection (STET-176, STET-178) ([086b59b], [932d07f])
- Workbench mutation-command gating and risk surfacing for the candidate iteration loop (STET-171) ([b14df5f], [bbe1764])

### Changed
- Rename project from Flux to Stet across the codebase, CLI surface, dist artifacts, and public copy ([160c91b])
- Make decision-quality graders the default for `stet eval rules` ([77cde43])
- Gate commercial Stet workflows by entitlement ([9bcf523])
- Reorient the Stet skill to be optimizer-facing (agent-first) ([4e317f6])

### Fixed
- Numerous harness, gate-parsing, grader, leaderboard, baseline, and credential fixes accumulated over the v0.1.0 rcs (auth scoping, OAuth, Harbor harness install skew, smoke preflight, grader repair retry, baseline subset filtering, h2h credential env leaks, decision report wiring)

### Internal
- Migrate task plans into `apex/tasks/` domain layout, add the dist skill mirror sync flow, repo-managed pre-commit hooks, and the QMD-backed task corpus ([af6b5d9], [7c7b197])
- Cache Harbor harness CLI setup, expire stale caches, and rename `tb` args to `harbor` args during the harbor cutover ([915d87a], [e2dfc3a], [af91737])

[v0.1.0]: https://github.com/benredmond/stet/releases/tag/v0.1.0
[30d26fe]: https://github.com/benredmond/stet/commit/30d26fecf816abf5497511b4cd2bb282cc652174
[0d3cdd4]: https://github.com/benredmond/stet/commit/0d3cdd42a58bfeffec51b9ffb8a8e77c379a003d
[5a8763e]: https://github.com/benredmond/stet/commit/5a8763e074ea98ec97662f4bfda6dced8be6406d
[29f4bea]: https://github.com/benredmond/stet/commit/29f4bea3b77f508d3eb3279d636b27d0d9aaee22
[ab4471a]: https://github.com/benredmond/stet/commit/ab4471a056ec272425cde1509079305a19135d4b
[3cc728e]: https://github.com/benredmond/stet/commit/3cc728e5f2ed09d31d32ebdf500b1c0dfc6866c2
[d4b65b0]: https://github.com/benredmond/stet/commit/d4b65b0d21de68331104acd6fa3b15e8e055133e
[160c91b]: https://github.com/benredmond/stet/commit/160c91bf740f37c4b7f6dae256d71fc08b68dc3b
[5ef34df]: https://github.com/benredmond/stet/commit/5ef34dfea318c851c2ca55b0fe1410dfe5bcbf55
[af6b5d9]: https://github.com/benredmond/stet/commit/af6b5d927695a51c0436d7e6abbf867fffe2d5db
[7c7b197]: https://github.com/benredmond/stet/commit/7c7b197478ab138cb6ecc3032146d0662ec8b34c
[2389f34]: https://github.com/benredmond/stet/commit/2389f34cc2a209443f07d45df21564244b0a9550
[c057f69]: https://github.com/benredmond/stet/commit/c057f691a28d886c14bd7e9abf4ba446b5c11d3c
[1525697]: https://github.com/benredmond/stet/commit/1525697678e53d1d2f22d4bbf24c465f07faccff
[79773c1]: https://github.com/benredmond/stet/commit/79773c1048d8871780108bba0b20efaf34c348a9
[7685e31]: https://github.com/benredmond/stet/commit/7685e3131f41499f5d78234890a4db56a04deea8
[c59037f]: https://github.com/benredmond/stet/commit/c59037fab783bca45a2df442f9c13f1e24401b95
[786cbdd]: https://github.com/benredmond/stet/commit/786cbdd555118915aa352e2341ff0b88e207f6e7
[b742af7]: https://github.com/benredmond/stet/commit/b742af789b65ccfe90c9739fffcc1405e23735dc
[d4d0c4d]: https://github.com/benredmond/stet/commit/d4d0c4dbb877fec14c578d2761aef96e0ab83554
[1feb8ee]: https://github.com/benredmond/stet/commit/1feb8eea6f7fa92709961d8625e490101b631d53
[066e700]: https://github.com/benredmond/stet/commit/066e700bbe6afc5f644604ca287ba29c933fab7d
[f3e243b]: https://github.com/benredmond/stet/commit/f3e243b5a8d325ce6d9a7f031c2c6d8e913c3e2d
[e7eef57]: https://github.com/benredmond/stet/commit/e7eef571f395a53aba8d38b81d04b7bfceb414da
[8047f55]: https://github.com/benredmond/stet/commit/8047f55ba8c4db60b5023dbc05101ae49d4b72ed
[7f7dcef]: https://github.com/benredmond/stet/commit/7f7dcef0d83caf0f53f9a2eb093aa8387595a330
[11c8b74]: https://github.com/benredmond/stet/commit/11c8b747ed41f0bcf8484adbadd8d9b615c7facc
[c3a26a4]: https://github.com/benredmond/stet/commit/c3a26a42f2da542f8fc41837296104efed018451
[8fbd054]: https://github.com/benredmond/stet/commit/8fbd05424a130a08b3c75b4c5b32036b3d18c9e5
[251f33d]: https://github.com/benredmond/stet/commit/251f33dd3950e367d7925489aff799bc51083603
[086b59b]: https://github.com/benredmond/stet/commit/086b59b346fa837caa2519f8f1aa3b1f93c50dec
[932d07f]: https://github.com/benredmond/stet/commit/932d07fe688e289344693d68f78e3ff55fbbb81b
[bbe1764]: https://github.com/benredmond/stet/commit/bbe17644b6444ea2f61d53b86cf2e7f91900ea84
[7ed6f77]: https://github.com/benredmond/stet/commit/7ed6f7767ba5bd3c32747fb576b372825a22987f
[3daf2cb]: https://github.com/benredmond/stet/commit/3daf2cb06568d92d23ebe8d3254a2deea16ea923
[feb6691]: https://github.com/benredmond/stet/commit/feb6691eb9ab01c97e050fd45412ab096551d825
[915d87a]: https://github.com/benredmond/stet/commit/915d87aafb3889074bf2220374d23384417f4d93
[e2dfc3a]: https://github.com/benredmond/stet/commit/e2dfc3a24d6b8421f5a1a04ef49af4bb96605728
[af91737]: https://github.com/benredmond/stet/commit/af9173746337f75d486897dc26f9f72d93562686
[ce5840a]: https://github.com/benredmond/stet/commit/ce5840ab8d87bd1d6406e3d2523c0bdc01d9aa3d
[9e004ae]: https://github.com/benredmond/stet/commit/9e004aec3b4a01575d96301a03758ce0d0b35e72
[15d6d7a]: https://github.com/benredmond/stet/commit/15d6d7acf7190c0f3fa45cefec24974b3aabd36e
[4fa2394]: https://github.com/benredmond/stet/commit/4fa2394894f43976d86f4d95c2fe1d1c67f64802
[723a8f6]: https://github.com/benredmond/stet/commit/723a8f6ddf18c706fc86ab5cc5b8e44d02331b2a
[a7706a4]: https://github.com/benredmond/stet/commit/a7706a4a230356cbbc46b584b723164d50afff8e
[280efb6]: https://github.com/benredmond/stet/commit/280efb68dd0bcb7be8bb96e07f3932ddca288757
[d7eb93c]: https://github.com/benredmond/stet/commit/d7eb93c7eb01b3e4afedf422ad42522f273b87a3
[4033439]: https://github.com/benredmond/stet/commit/40334398a97f238e07af457dca28ac8ce8e20ebd
[0ff45d1]: https://github.com/benredmond/stet/commit/0ff45d1daf08837f706e5c5c82d151e48f88f5bc
[9bcf523]: https://github.com/benredmond/stet/commit/9bcf523503fd9678622ea985bc11fe71fe377e2f
[4e317f6]: https://github.com/benredmond/stet/commit/4e317f66e586aea2233fca44f7034921731c332a
[77cde43]: https://github.com/benredmond/stet/commit/77cde4366cdd784221a1c9bc9eb3b1ca0b8de029
[b14df5f]: https://github.com/benredmond/stet/commit/b14df5fc2b1f3363c40743c539080c946dcd4b76
