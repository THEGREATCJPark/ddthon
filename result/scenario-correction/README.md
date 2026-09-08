# Scenario correction evidence

- `excel-probe.json`: actual encrypted SaveAs succeeded, subsequent Workbooks.Open timed out. Old failure preserved.
- `real-excel.txt`: retained-open-workbook preparation; actual direct-reader failure + real Excel read-only access, 1 PASS.
- `cold-agent-trace.json`: fresh Claude received only the XLSX analysis request. Actual failure/NO_MATCH, format and application investigation, read-only access, task mapping, forecast and candidate. It encountered insufficient procedure-schema guidance; product validation message was clarified during this diagnostic run. Earlier rejected attempts remain in trace. This is not a claim of a flawless first attempt.
- `cold-trend.png`: actual data 1200,1350,1500 and forecast1650 from the workbook, not an illustrative mockup.
- Exact candidate is awaiting real human approval. No remote publication or Warm completion is claimed here.
- Full regression and minimum-generalization logs retain both initial failures and rerun results. Local Git tests use actual Git and simulated Excel; actual Excel evidence is separate.
