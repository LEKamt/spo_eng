SPORTS ENGINEERING E2 PRESENTATION

Deliverables
- main.pdf: presentation (24 pages, widescreen 16:9).
- main.tex: main source opened in the Codex LaTeX editor.
- slides.tex: 10 rubric-focused main slides plus cover.
- shannon-summary.tex: 2 main slides based on Annex B, after the core findings.
- backup.tex: 7 evidence, reproducibility, contribution and reference slides.
- shannon-detail.tex: 4 detailed Annex B slides at the end.
- presenter-notes.txt: a 4:55 main-talk plan including the 35.2 seconds of original video.
- reference/main-template.tex: unchanged copy of the original template.
- evidence/: reproducible exported calculations, plotting CSVs, results and hash manifest.

Local compilation
From this directory, run twice:
  xelatex -interaction=nonstopmode -halt-on-error main.tex
The theme uses XeLaTeX/fontspec and falls back to Latin Modern Mono when IBM Plex Mono is unavailable, exactly as designed in the supplied theme. No theme file was changed.
Keep slides.tex, backup.tex, shannon-summary.tex, shannon-detail.tex, the theme, images, CSVs, screenshots and clips beside the main project. PDF local-video links may be blocked by a viewer; open the MP4 files manually when needed. They are linked, not embedded.

Source and scope
Cloned from https://github.com/LEKamt/spo_eng.git to the Desktop.
Source revision: 90abbd9f87f20fb2c8a05ab9879a74202d0eaead.
The motion is one recorded trial with three forward-swing peaks. The original main criterion searches all 379 frames. Annex B separately checks three 31-frame windows.
The scene replays Xsens segment CSVs from the same trial processed in OpenSim; it does not load the OpenSim model or .mot file to animate the Vizard skeleton.

Rubric mapping
1. Motion fidelity: main 2–3; backups A–B. Provenance, axes, metres, timing, three frames and numerical discrepancies.
2. Vizard/reproducibility: main 6; backup E. Scene and original clips, controls and launch instructions.
3. Ecological explanation: main 1 and 7–8. Actor-relative possibility, view-dependent information, public environment, touch–posture covariation and visual-only limits.
4. Investigation: main 4–5 and 9; backups C–D. Four ordered conditions, fixed geometric rule, controlled parameter and complete proposed judgment protocol.
5. Report/demonstration: main story and timed notes, references, evidence labels and limitations. The final narrated MP4 and compliant report remain separate Canvas deliverables.
6. Individual contribution: backup F repeats reported roles. Each student must author and verify their own 300–500 word statement.
Optional information theory: main 11–12 and final backups H–K. Entropy, bits/nats, KL, conditional events, mutual information and illustrative Bayes calculations.

Numerical reconciliation with the existing report
Raw exports and source geometry take priority over rounded/manually transcribed report values. The original group report is left untouched.
- f150 OpenSim hand height is 1.12415219 m, not the report's 1.120 m. Difference Vizard minus OpenSim: -0.043489688 m.
- f185 OpenSim hand height is 1.14813630 m. Difference: +0.029325127 m.
- f216 OpenSim elbow flexion is 95.0209 deg in both the CSV and .mot, rather than the report's 94.69 deg.
- f216 OpenSim hand height is 1.22518478 m. Difference: +0.109036391 m (10.9 cm), rather than the reported 10.4 cm.
- Elbow differences use full precision: +3.573, +5.114, -0.385 deg.
- Zero-based frame times are i/60. OpenSim timestamps differ by at most 1 ms at these three rows.
- The elbow export has a duplicate time header and an inDegrees=no metadata flag despite degree-valued entries matching the .mot and reported plots. The script explicitly selects the second time column and third value column.

Important evidence limits to resolve before submission
- Matching OpenSim pose screenshots at the three timestamps are absent. Supplied OpenSim plots and export comparisons should not be presented as newly captured synchronized pose screenshots.
- Vizard GUI playback was not rerun on this Mac. Existing scene screenshots and MP4s were reused. Source calculations were executed independently of the Windows graphics engine.
- The two clips total 35.2 seconds; record a narrated/captioned 3–5 minute demonstration and verify that controls, all conditions and a validation check actually appear.
- Review the existing group report separately against the six-page limit and reconcile its numerical table with these corrected export values.
- The README's separate Python-version claim is not required by this deck. Run the scene inside Vizard's bundled Python environment.
- C4's earliest minimum is a closest approach, not an actual impact. C2's deterministic pass is not evidence of robust physical contact.

Annex B interpretation refinements
- The entropy and KL values describe speed occupancy; temporal ordering is discarded.
- Three windows come from one recorded trial. Do not treat 93 frames or 12 stroke-condition cells as independent sport trials.
- No iid Miller–Madow bias correction is claimed for autocorrelated frames.
- Peak proxy positions have an RMS spread of 0.0680 m. They are not measured racket-ball impacts.
- The main script searches the full trial; the separate Annex B windows yield counts C1=3/3, C2=1/3, C3=C4=0/3.
- The Beta/Bernoulli calculation is illustrative and requires exchangeability assumptions. KL between predictions is not KL between parameter posteriors.
- The assumed observer rates 0.85 and 0.20 are illustrative only. No participant data were fabricated.

Recompute the slide numbers
From repository root:
  python3 group-demostration/evidence/verify_results.py
No Vizard, OpenSim, MATLAB or third-party Python packages are required for this finite export check. The script records input hashes, source revision and non-claims in evidence/manifest.json. It independently checks distances in the original Xsens coordinate system and verifies the mutual-information identity.
