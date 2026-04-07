# Feature-Level ITC-Study Bridge Analysis

- Workload: `PY_STATS`
- Stressor family: `ATOMIC`
- Config: `Tier-0/1/2`
- Original anomaly warning: `45.0s`
- Crash-pilot anomaly warning: `62.0s`
- Crash time: `196.7s`
- Lead time: `134.7s`

## ITC-study bridge feature summary

| workload | base_stressor | case_id | mode | feature_name | tier | column_name | reference_warning_s | original_anomaly_warning_s | pilot_warning_s | crash_pilot_anomaly_warning_s | crash_time_s | feature_first_divergence_s | feature_value_at_warning | feature_value_pre_crash | nominal_median | nominal_scale | peak_abs_z |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_CONTROL | CONTROL | tier0:swap_sout_bytes | tier0 | swap_sout_bytes | 45.0 | 45.0 | 62.0 | 62.0 |  | 0.8190658092498779 | 100580114432.0 |  | 100577558528.0 | 472.7682305551233 | 54617.003282307756 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_ABORT | ABORT | tier0:swap_sout_bytes | tier0 | swap_sout_bytes | 45.0 | 45.0 | 62.0 | 62.0 | 196.682946 | 0.0010640621185302 | 100606951424.0 | 100612308992.0 | 100577558528.0 | 472.7682305551233 | 73608.19477894777 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_CONTROL | CONTROL | tier0:swap_total_bytes | tier0 | swap_total_bytes | 45.0 | 45.0 | 62.0 | 62.0 |  |  | 10737418240.0 |  | 10737418240.0 | 1.0 | 0.0 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_ABORT | ABORT | tier0:swap_total_bytes | tier0 | swap_total_bytes | 45.0 | 45.0 | 62.0 | 62.0 | 196.682946 | 15.59043788909912 | 9663676416.0 | 9663676416.0 | 10737418240.0 | 1.0 | 1073741824.0 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_CONTROL | CONTROL | tier0:soft_interrupts | tier0 | soft_interrupts | 45.0 | 45.0 | 62.0 | 62.0 |  | 107.6613118648529 | 3158646376.0 |  | 3155792377.0 | 1403656.7391 | 4.126250270927082 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_ABORT | ABORT | tier0:soft_interrupts | tier0 | soft_interrupts | 45.0 | 45.0 | 62.0 | 62.0 | 196.682946 | 0.0010640621185302 | 3162658257.0 | 3164465224.0 | 3155792377.0 | 1403656.7391 | 6.793676640710826 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_CONTROL | CONTROL | tier2:max_core_id | tier2 | max_core_id | 45.0 | 45.0 | 62.0 | 62.0 |  | 206.0 | 11.0 |  | 10.0 | 1.4826 | 2.697963037906381 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_ABORT | ABORT | tier2:max_core_id | tier2 | max_core_id | 45.0 | 45.0 | 62.0 | 62.0 | 196.682946 | 192.2 | 11.0 | 8.0 | 10.0 | 1.4826 | 4.721435316336167 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_CONTROL | CONTROL | tier0:swap_sin_bytes | tier0 | swap_sin_bytes | 45.0 | 45.0 | 62.0 | 62.0 |  | 78.81006288528442 | 2245457854464.0 |  | 2243803758592.0 | 719922094.0799999 | 5.455438292971135 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_ABORT | ABORT | tier0:swap_sin_bytes | tier0 | swap_sin_bytes | 45.0 | 45.0 | 62.0 | 62.0 | 196.682946 | 0.0010640621185302 | 2248554430464.0 | 2249482747904.0 | 2243803758592.0 | 719922094.0799999 | 8.795518809701038 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_CONTROL | CONTROL | tier0:mem_used_bytes | tier0 | mem_used_bytes | 45.0 | 45.0 | 62.0 | 62.0 |  | 1.430839776992798 | 7492665344.0 |  | 7462846464.0 | 193052073.984 | 3.3344752362171026 |
| PY_STATS | ATOMIC | PY_STATS__ATOMIC_ABORT | ABORT | tier0:mem_used_bytes | tier0 | mem_used_bytes | 45.0 | 45.0 | 62.0 | 62.0 | 196.682946 | 1.2403998374938965 | 7087570944.0 | 7346634752.0 | 7462846464.0 | 193052073.984 | 6.181636733407517 |
