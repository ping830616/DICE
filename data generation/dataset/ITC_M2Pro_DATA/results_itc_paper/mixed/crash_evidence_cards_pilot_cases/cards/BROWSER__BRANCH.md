# Crash Evidence Card: BROWSER__BRANCH

![Crash evidence card](../figures/BROWSER__BRANCH.png)

## Summary

- Status: Warning before crash
- Workload: BROWSER
- Stressor: BRANCH
- Warning time: 45.0 s
- Crash time: 167.5 s
- Lead time: 122.5 s
- Warning source: first_persistent_alert
- Crash source: diagnostic_report,screenshot
- Log evidence used: raw pilot collection log

## Primary Crash Evidence

- Diagnostic report: `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_browser_branch/crash_evidence/BROWSER__BRANCH_ABORT/diagnostic_reports/python3.11-2026-03-31-110319.ips`
- System / collection log: `data generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_real_browser_branch/logs/BROWSER__BRANCH_ABORT/tier2_collect.log`

## Diagnostic Report Excerpt

```text
{"app_name":"python3.11","timestamp":"2026-03-31 11:03:19.00
-0700","app_version":"","slice_uuid":"f1fbfc29-e42f-359f-81ae-6730313605a7","build_version":"","platform":1,"share_with_app_devs":0,"is_first_party":1,"bug_type":"309","os_version":"macOS
26.3.1
(25D2128)","roots_installed":0,"incident_id":"623264A4-AE37-4413-9887-141FB816B238","name":"python3.11"}
{
  "uptime" : 170000,
  "procRole" : "Background",
  "version" : 2,
  "userID" : 502,
  "deployVersion" : 210,
```

## System / Collection Log Excerpt

```text
[xctrace record] xcrun xctrace record --template Time Profiler --all-processes --time-limit 240s
--output /Users/hsiaopingni/Documents/New project/DICE/data generation/dataset/I...
[xctrace toc] xcrun xctrace export --input /Users/hsiaopingni/Documents/New project/DICE/data
generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilot_r...
[xctrace export] xcrun xctrace export --input /Users/hsiaopingni/Documents/New project/DICE/data
generation/dataset/ITC_M2Pro_DATA/workload_crash_pilots/data_workload_crash_pilo...
```

## Notes

nan
