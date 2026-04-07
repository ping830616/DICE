# Feature-Level ITC-Study Bridge Analysis

- Workload: `VIDEO_SW`
- Stressor family: `MEMBW`
- Config: `Tier-0/1/2`
- Original anomaly warning: `45.0s`
- Crash-pilot anomaly warning: `62.0s`
- Crash time: `174.6s`
- Lead time: `112.6s`

## ITC-study bridge feature summary

| workload | base_stressor | case_id | mode | feature_name | tier | column_name | reference_warning_s | original_anomaly_warning_s | pilot_warning_s | crash_pilot_anomaly_warning_s | crash_time_s | feature_first_divergence_s | feature_value_at_warning | feature_value_pre_crash | nominal_median | nominal_scale | peak_abs_z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_CONTROL | CONTROL | tier0:uptime_s | tier0 | uptime_s | 45.0 | 45.0 | 62.0 | 62.0 |  | 103.42316699028017 | 406657.5705358982 |  | 406471.62523067 | 90.90475306034088 | 4.055414794283082 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_ABORT | ABORT | tier0:uptime_s | tier0 | uptime_s | 45.0 | 45.0 | 62.0 | 62.0 | 174.566567 | 0.0011157989501953 | 406903.5739991665 | 407011.006303072 | 406471.62523067 | 90.90475306034088 | 6.758927433429513 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_CONTROL | CONTROL | tier1_alt:gpu_temp_c | tier1_alt | gpu_temp_c | 45.0 | 45.0 | 62.0 | 62.0 |  | 0.0 | 59.093299865722656 |  | 56.48534393310547 | 0.250472664642334 | 26.196138550073044 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_ABORT | ABORT | tier1_alt:gpu_temp_c | tier1_alt | gpu_temp_c | 45.0 | 45.0 | 62.0 | 62.0 | 174.566567 | 0.0 | 58.39484405517578 | 63.83685302734375 | 56.48534393310547 | 0.250472664642334 | 202.06573756878137 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_CONTROL | CONTROL | tier0:soft_interrupts | tier0 | soft_interrupts | 45.0 | 45.0 | 62.0 | 62.0 |  | 56.19877910614014 | 2728509898.0 |  | 2723213712.0 | 1746212.2104 | 13.498430408180818 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_ABORT | ABORT | tier0:soft_interrupts | tier0 | soft_interrupts | 45.0 | 45.0 | 62.0 | 62.0 | 174.566567 | 0.0011157989501953 | 2749818162.0 | 2766019805.0 | 2723213712.0 | 1746212.2104 | 25.846592831727687 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_CONTROL | CONTROL | tier0:cpu10_pct | tier0 | cpu10_pct | 45.0 | 45.0 | 62.0 | 62.0 |  |  | 4.5 |  | 18.6 | 27.57636 | 2.262807709211803 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_ABORT | ABORT | tier0:cpu10_pct | tier0 | cpu10_pct | 45.0 | 45.0 | 62.0 | 62.0 | 174.566567 |  | 0.0 | 15.0 | 18.6 | 27.57636 | 2.2265447651539216 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_CONTROL | CONTROL | tier0:cpu_times_system_pct | tier0 | cpu_times_system_pct | 45.0 | 45.0 | 62.0 | 62.0 |  | 0.2070851325988769 | 10.0 |  | 7.7 | 2.52042 | 14.680093000372953 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_ABORT | ABORT | tier0:cpu_times_system_pct | tier0 | cpu_times_system_pct | 45.0 | 45.0 | 62.0 | 62.0 | 174.566567 | 0.2061429023742675 | 11.9 | 9.9 | 7.7 | 2.52042 | 9.998333611064822 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_CONTROL | CONTROL | tier0:cpu9_pct | tier0 | cpu9_pct | 45.0 | 45.0 | 62.0 | 62.0 |  |  | 9.5 |  | 35.0 | 37.065 | 1.367867260218535 |
| VIDEO_SW | MEMBW | VIDEO_SW__MEMBW_ABORT | ABORT | tier0:cpu9_pct | tier0 | cpu9_pct | 45.0 | 45.0 | 62.0 | 62.0 | 174.566567 |  | 23.8 | 20.0 | 35.0 | 37.065 | 1.4838796708485094 |
