"""
Week 4 Capstone Certification & Enterprise E-Invoicing Benchmark Suite.
Audits 100 German B2B & B2G e-invoices across all statutory dimensions:
- European Standard EN 16931-1:2017 & KoSIT XRechnung 3.0
- § 4 E-Rech-VO & ISO 7064 MOD-97-10 Federal Routing Verification
- § 14, § 14a, § 14c, § 13b UStG & § 33 UStDV
- Dual ERP Export: DATEV Format 700 CSV & SAP S/4HANA Finance JSON
- Certified DIN 5008 Master Audit Report PDF Synthesis
"""

import json
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.schemas.erp_export import ChartOfAccounts
from app.services.capstone_audit_engine import capstone_audit_engine
from app.services.capstone_pdf_exporter import generate_capstone_audit_report_pdf


def run_week4_capstone():
    print("=" * 80)
    print("🧾 DOCUNORM AI — WEEK 4 CAPSTONE CERTIFICATION SUITE")
    print("   ZUGFeRD 2027 & XRechnung Enterprise Benchmark (100 German Invoices)")
    print("=" * 80)

    reports_dir = backend_dir / "reports" / "week4_capstone"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print("\n⏳ [1/4] Executing High-Throughput Batch Audit on 100 Invoices...")
    summary = capstone_audit_engine.execute_capstone_audit(chart=ChartOfAccounts.SKR03)

    print(f"✅ [1/4] Ingestion & Audit Completed in {summary.execution_time_ms:.1f} ms!")
    print(f"   Throughput: {summary.throughput_invoices_per_sec:,.0f} invoices/second")
    print(f"   Compliance Rate: {summary.compliance_rate_percent}% ({summary.compliant_count} / {summary.total_invoices})")
    print(f"   Rejected (Fraud/Discrepancy): {summary.rejected_count} invoices")
    print(f"   Total Audited Volume: EUR {summary.total_grand_eur:,.2f} (Net: EUR {summary.total_net_eur:,.2f})")

    print("\n🔍 [2/4] Forensic Anomaly & Rejection Breakdown:")
    for disc in summary.discrepancies:
        print(f"   ❌ [{disc.invoice_number}] {disc.rule_violated} ({disc.risk_level})")
        print(f"      Grund: {disc.rejection_reason[:85]}...")

    print("\n📑 [3/4] Generating Certified 3-Page DIN 5008 Master Capstone Audit PDF...")
    pdf_path = generate_capstone_audit_report_pdf(summary, output_dir=reports_dir)
    print(f"   ✅ Master Audit PDF Created: {pdf_path.name} ({pdf_path.stat().st_size:,} bytes)")

    print("\n💾 [4/4] Writing Archival Export Artifacts...")
    # 1. Summary JSON
    summary_path = reports_dir / "week4_capstone_summary.json"
    summary_path.write_text(summary.model_dump_json(indent=2), encoding="utf-8")
    print(f"   ✅ JSON Summary: {summary_path.name}")

    # 2. DATEV 700 CSV
    datev_path = reports_dir / "DATEV_EXTF_100_INVOICES_SKR03.csv"
    datev_path.write_bytes(b"\xef\xbb\xbf" + summary.datev_csv_content.encode("utf-8"))
    print(f"   ✅ DATEV Format 700 CSV: {datev_path.name} ({datev_path.stat().st_size:,} bytes)")

    # 3. SAP S/4HANA JSON
    sap_path = reports_dir / "SAP_S4HANA_JOURNAL_ENTRIES_100.json"
    sap_path.write_text(summary.sap_json_content, encoding="utf-8")
    print(f"   ✅ SAP S/4HANA Finance JSON: {sap_path.name} ({sap_path.stat().st_size:,} bytes)")

    print("\n" + "=" * 80)
    print("🏆 WEEK 4 CAPSTONE SUCCESSFULLY AUDITED AND CERTIFIED!")
    print(f"   GoBD Batch SHA-256 Digest: {summary.gobd_sha256_batch_hash}")
    print("=" * 80)


if __name__ == "__main__":
    run_week4_capstone()
