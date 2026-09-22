# ITC-Study Crash Bridge Report

- Feature profile: `mixed`
- Original ITC cases: `24`
- Matched crash-pilot cases: `4`
- Matched workloads: `BROWSER, PY_AI, PY_STATS, VIDEO_SW`

Pilot warning evidence uses exact abort-case records; original-run warnings are separate references.
The CSV records timing provenance and conflicts. Legacy peak features cover the whole recording unless `crash_peak_scope` is `pre_crash`.

## Matched ITC-study bridge cases

| original_case_id | original_anomaly_warning_s | crash_pilot_anomaly_warning_s | crash_time_s | lead_time_s | original_top_feature_1 | crash_pilot_warning_top_feature_1 | crash_peak_feature_1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BROWSER__BRANCH | 45.0 | 62.0 | 167.478639 | 105.478639 | tier0:swap_sout_bytes | tier0:swap_total_bytes | tier0:swap_free_bytes |
| VIDEO_SW__MEMBW | 45.0 | 62.0 | 174.566567 | 112.566567 | tier0:uptime_s | tier0:uptime_s | tier1_alt:gpu_temp_c |
| PY_AI__CACHE | 45.0 | 62.0 | 214.779384 | 152.779384 | tier1_alt:gpu_avg_freq_mhz | tier0:soft_interrupts | tier0:swap_sout_bytes |
| PY_STATS__ATOMIC | 45.0 | 62.0 | 196.682946 | 134.682946 | tier0:uptime_s | tier0:swap_total_bytes | tier0:swap_total_bytes |
