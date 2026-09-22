# Historical draft package

This writing package predates the corrected evidence interpretation. Its numerical recommendations and descriptions of diagnosis coverage and crash lead time are not authoritative. Use [paper evidence notes](paper-evidence-notes.md) and regenerated exports when preparing the final paper.

# ITC Results Section Package

This note distills the strongest draft-aligned claims already supported by the released DICE results, proposes a cleaner section structure, and provides a revised Results draft aligned with the current manuscript tone.

## Strongest Defensible Claims

Use these as the main paper headline results because they are both strong and honest.

1. The mixed `Tier-0/1/2` profile is the best practical deployment profile.
   It reaches `ROC-AUC = 0.8500`, `PR-AUC = 0.9620`, detects `85%` of anomalous runs, raises `0%` benign run alerts, and reaches a median detection time of `72 s`.

2. The full `Tier-0/1/2` profile is the higher-observability upper-bound result.
   It reaches `ROC-AUC = 0.9625`, `PR-AUC = 0.9925`, detects `95%` of anomalous runs, raises `0%` benign run alerts, and reaches a median detection time of `60 s`.

3. The mixed profile is the stronger anomaly-category and subsystem-path result.
   It achieves exact `Top-2 = 0.80`, confidence-gated `Top-2 = 0.8889` at `45%` coverage, and anomaly-category `Top-3` coverage of `0.8846`.

4. The mixed profile is also the stronger transfer result.
   Under cross-workload transfer it reaches mean and worst-case `PR-AUC` of `0.8867` and `0.8100`, respectively, versus `0.8075` and `0.7100` for the full profile.

5. The subsystem-path story is practical and hardware-relevant.
   The strongest recurring evidence concentrates in the unified-memory and swap path plus the Neural Engine rather than diffusing across many weak cues.

6. The LLM-based triage layer is useful because it is grounded, not because it improves detection.
   The saved scored baseline preserves the dominant tier in all summaries, preserves the dominant anomaly category in `90%` of mixed-profile summaries and `100%` of full-profile summaries, and shows `0%` hallucinated claims in both profiles.

## Recommended Main-Paper Structure

Keep the main Results section focused on the deployment story. Move extra sweep detail to the appendix.

### Suggested subsection titles

1. Run-Level Monitoring Performance
2. Detection Timing and First Sustained Alert Windows
3. Diagnosis and Subsystem-Path Evidence
4. Robustness Under Workload Shift and Feature Budgets
5. LLM-Based Triage Layer
6. Crash-Aware Early-Warning Extension

### What belongs in the main paper

- mixed versus full `Tier-0/1/2` monitoring scorecard
- first sustained alert-window timing and one representative subsystem-path figure
- anomaly-category and subsystem-path hotspot evidence
- cross-workload transfer summary
- one compact LLM-based triage grounding scorecard

### What should move to the appendix

- full tier-by-tier sweep tables
- extended feature-budget plots
- all confusion matrices
- complete per-case subsystem-path tables
- implementation detail for the scored LLM-based triage pipeline

## Suggested Table and Figure Order

### Main paper

1. `Table IV`: Run-level monitoring scorecard across telemetry settings.
   Caption: "Run-level monitoring performance across mixed and full telemetry profiles. The mixed `Tier-0/1/2` setting is the preferred practical deployment point because it removes benign run alerts while retaining strong anomaly ranking and timely detection."

2. `Figure 4`: Run-level monitoring quality across observability settings.
   Caption: "Run-level anomaly ranking improves as DICE moves from Tier-0 to Tier-0/1/2, with the full profile defining the strongest upper bound and the mixed profile defining the preferred deployment tradeoff."

3. `Figure 5`: Time to the first sustained alert window by stressor and profile.
   Caption: "First sustained alert-window timing by stressor. DICE behaves as a time-sensitive monitor: some anomalies surface almost immediately, whereas others require a longer observation window."

4. `Figure 6`: Representative subsystem-path traces.
   Caption: "Representative mixed-profile traces showing the first sustained anomalous interval. The highlighted windows illustrate that DICE responds to compact clusters of anomaly evidence rather than isolated score spikes."

5. `Table V`: Anomaly-category and subsystem-path summary for the selected `Tier-0/1/2` configurations.
   Caption: "Diagnosis quality at the selected operating points. The mixed profile is the stronger deployment-facing diagnosis setting, while both profiles retain strong anomaly-category guidance and subsystem-path evidence."

6. `Figure 8`: Subsystem-path hotspot summary.
   Caption: "Most visible subsystem-path hotspots in the final DICE head. Evidence concentrates in the unified-memory and swap path and, secondarily, the Neural Engine, which makes the alerts interpretable for real systems."

7. Transfer summary table or compact paragraph with values from `industry_paper_scorecard_profiles.csv`.
   Caption: "Cross-workload transfer summary. The mixed profile retains stronger workload-shift robustness than the full profile."

8. LLM grounding scorecard.
   Caption: "LLM-based triage summary. The language model improves interpretability by summarizing structured DICE evidence without adding unsupported claims."

### Appendix or extension

1. Feature-budget figure
2. Ternary tier-contribution figure
3. Top recurring localized features figure
4. Crash-aware early-warning timeline and lead-time plots when a crash manifest is available

## Revised Results Draft

### V. RESULTS AND ANALYSIS

#### A. Run-Level Monitoring Performance

We begin with the primary question for in-field silicon lifecycle monitoring: can DICE distinguish benign runs from anomalous runs under deployment-realistic tiered telemetry? Table IV and Fig. 4 show that it can. The mixed profile improves monotonically as additional telemetry tiers are added, rising from `ROC-AUC = 0.8000` and `PR-AUC = 0.9319` at Tier-0 to `ROC-AUC = 0.8500` and `PR-AUC = 0.9620` at Tier-0/1/2. At the selected mixed Tier-0/1/2 operating point, DICE detects `85%` of anomalous runs, raises no benign run alerts, and reaches a median detection time of `72 s`. This is the strongest practical deployment result in the study because it combines strong anomaly ranking, zero benign run alerts, and a moderate feature budget.

The full profile defines the higher-observability upper bound. At Tier-0/1/2 it reaches `ROC-AUC = 0.9625` and `PR-AUC = 0.9925`, detects `95%` of anomalous runs, raises no benign run alerts, and reaches a median detection time of `60 s`. We therefore use the full profile to show the best achievable monitoring accuracy when richer telemetry is available, but we use the mixed profile as the main practical result because it offers the cleaner deployment tradeoff.

#### B. Detection Timing and First Sustained Alert Windows

Accurate run-level detection is necessary but not sufficient for in-field use. A useful digital twin must also show when anomalous behavior first becomes visible. Figure 5 shows that DICE is time-sensitive rather than purely end-of-run. In the mixed profile, several stressors become visible almost immediately, whereas others emerge only after a much longer observation interval. Figure 6 makes this behavior concrete at the case level. The first sustained alert windows appear as compact intervals of anomaly evidence above the calibrated threshold, not as isolated score spikes, which makes the alerts easier to interpret and more suitable for downstream diagnosis.

This timing result matters for real systems. In practice, operators need both a detection decision and a warning time. DICE provides that second quantity directly through the first sustained alert window, which creates a natural bridge from anomaly detection to predictive maintenance and crash-aware early warning.

#### C. Diagnosis and Subsystem-Path Evidence

Once DICE detects an anomalous run, the next question is whether the anomaly evidence is specific enough to guide triage. Table V shows that the mixed Tier-0/1/2 configuration is again the strongest practical deployment point. It achieves exact `Top-1 = 0.50` and exact `Top-2 = 0.80`. When DICE abstains on low-confidence cases, the confidence-gated `Top-2` accuracy rises to `0.8889` at `45%` coverage. At the broader anomaly-category level, the mixed profile reaches `Top-3` coverage of `0.8846`, indicating that even when exact stressor ranking is difficult, DICE still maps the anomaly to a useful subsystem path.

The hardware interpretation is equally important. The recurring hotspot analysis shows that the strongest evidence is concentrated in the unified-memory and swap path and, secondarily, the Neural Engine. This concentration is a practical result: the alert is not a diffuse statistical artifact spread across hundreds of weak features. Instead, DICE consistently points to a small set of deployment-visible subsystem paths that an engineer can inspect.

#### D. Robustness Under Workload Shift and Feature Budgets

The mixed profile is also the stronger robustness result. Under cross-workload transfer, it reaches mean and worst-case `PR-AUC` values of `0.8867` and `0.8100`, compared with `0.8075` and `0.7100` for the full profile. This result is important for industry use because workload drift is unavoidable after deployment. The mixed-profile digital twin retains useful anomaly sensitivity even when evaluated on held-out workload families.

The feature-budget study reinforces the same conclusion. DICE degrades gracefully as the active feature set is reduced, which supports lightweight host-side deployment. This result is best used as supporting evidence for feasibility rather than as the headline result; the core message is that the practical-deployment mixed profile remains strong even when telemetry and budget are constrained.

#### E. LLM-Based Triage Layer

The LLM-based triage layer is not part of the detector. It does not alter anomaly scores, thresholds, or alerts. Its value lies in interpretation. Using only structured DICE evidence, the saved scored baseline preserves the dominant telemetry tier in all summaries, preserves the dominant anomaly category in `90%` of mixed-profile summaries and `100%` of full-profile summaries, and shows no hallucinated claims in either profile. These results show that DICE produces evidence that is structured enough to support concise and faithful grounded case summaries, which strengthens usability for monitoring, triage, and field debugging.

#### F. Crash-Aware Early-Warning Extension

The current released dataset supports first-warning timing but does not include a ground-truth crash manifest. For that reason, the main paper should not claim quantitative crash prediction from the released data alone. Instead, the correct statement is that DICE already computes the key precursor signal needed for such a study: the first sustained alert window. The repository now includes a crash-aware extension that records reproducible crash evidence and pairs it with this first-warning timestamp to measure warning precision, recall before crash, lead-time distribution, and false alarms per monitored hour. Once recollection with crash evidence is complete, this extension can support a rigorous predictive-maintenance result without changing the core DICE detector.

## Writing Notes

- Prefer `detect` or `identify` for the current released dataset. Reserve `predict crash` for the crash-aware extension once crash evidence exists.
- Use `practical deployment profile` for the mixed profile and `higher-observability upper bound` for the full profile. This distinction is clear and consistent with the current method section.
- Keep the anomaly-category and subsystem-path story concrete. Mention the unified-memory and swap path, the Neural Engine, and the first sustained alert window.
- Keep the LLM-based triage paragraph short. Its role is interpretability, not detector improvement.
