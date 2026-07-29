import csv, tempfile, unittest
from pathlib import Path
from training.backtest_result import build_results, generate_manifest, metrics, validate_manifest, validate_results

def write(path, rows):
    fields=["record_id","decision_id","symbol","timestamp","event_type","side","price","quantity","exit_reason"]
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n"); w.writeheader(); w.writerows(rows)

class BacktestResultTests(unittest.TestCase):
    META={"cost_configuration_hash":"c1","validation_report_id":"v1","git_commit":"g1","environment_id":"e1","generation_command":"cmd","acceptance_status":"DRAFT","storage_location":"offline","backup_status":"PENDING"}
    def test_closed_trade_metrics_and_manifest(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root); events=base/"events.csv"; results=base/"results.csv"; manifest=base/"manifest.json"
            common={"record_id":"r1","decision_id":"d1","symbol":"XAUUSD","side":"BUY","quantity":"2"}
            second=dict(common,record_id="r2",decision_id="d2")
            write(events,[dict(common,timestamp="2026-01-01T00:00:00Z",event_type="ENTRY",price="100",exit_reason=""),dict(common,timestamp="2026-01-01T00:01:00Z",event_type="EXIT",price="101",exit_reason="TARGET"),dict(second,timestamp="2026-01-01T00:02:00Z",event_type="ENTRY",price="100",exit_reason=""),dict(second,timestamp="2026-01-01T00:03:00Z",event_type="EXIT",price="99",exit_reason="STOP")])
            build_results(events,results,cost=0.5); self.assertEqual(metrics(results)["net_pnl"],"-1.0000000000")
            generate_manifest(results,manifest,{"events":"e1"},self.META); self.assertEqual(validate_manifest(results,manifest,{"events":"e1"}),[])

    def test_open_trade_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"events.csv"; common={"record_id":"r1","decision_id":"d1","symbol":"XAUUSD","side":"BUY","quantity":"1"}
            write(p,[dict(common,timestamp="2026-01-01T00:00:00Z",event_type="ENTRY",price="100",exit_reason="")])
            with self.assertRaises(ValueError): build_results(p,Path(root)/"out.csv")

    def test_noncausal_exit_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"events.csv"; common={"record_id":"r1","decision_id":"d1","symbol":"XAUUSD","side":"SELL","quantity":"1"}
            write(p,[dict(common,timestamp="2026-01-01T00:01:00Z",event_type="ENTRY",price="100",exit_reason=""),dict(common,timestamp="2026-01-01T00:00:00Z",event_type="EXIT",price="99",exit_reason="STOP")])
            with self.assertRaises(ValueError): build_results(p,Path(root)/"out.csv", cost=0.0)

    def test_explicit_cost_and_result_validation(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root); events=base/"events.csv"; results=base/"results.csv"
            common={"record_id":"r1","decision_id":"d1","symbol":"XAUUSD","side":"BUY","quantity":"1"}
            write(events,[dict(common,timestamp="2026-01-01T00:00:00Z",event_type="ENTRY",price="100",exit_reason=""),dict(common,timestamp="2026-01-01T00:01:00Z",event_type="EXIT",price="101",exit_reason="TARGET")])
            build_results(events,results,cost=0.1); self.assertEqual(validate_results(results),[])

    def test_manifest_requires_governance_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            base=Path(root); events=base/"events.csv"; results=base/"results.csv"
            common={"record_id":"r1","decision_id":"d1","symbol":"XAUUSD","side":"BUY","quantity":"1"}
            write(events,[dict(common,timestamp="2026-01-01T00:00:00Z",event_type="ENTRY",price="100",exit_reason=""),dict(common,timestamp="2026-01-01T00:01:00Z",event_type="EXIT",price="101",exit_reason="TARGET")])
            build_results(events,results,cost=0.1)
            with self.assertRaises(ValueError): generate_manifest(results,base/"m.json",{})

if __name__ == "__main__": unittest.main()
