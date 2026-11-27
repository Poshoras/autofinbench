# Month-end GRNI accrual policy (period ending 2026-10-31)

1. Accrue goods/services **received** (receipt_date ≤ 2026-10-31, status `accepted`) that have **not been invoiced** in AP by 2026-10-31 (an invoice counts if posted_date ≤ 2026-10-31).
2. Value = received quantity × **PO unit price**, in PO currency, translated to USD at the `fx_rates.csv` rate **on the receipt date**. Round each line to cents after translation.
3. Exclude vendors flagged `intercompany = Y` (eliminated on consolidation).
4. A receipt_id appearing more than once (ignore case and surrounding spaces) is a duplicate load; count it once.
5. Returns (`type = return`, negative qty) reduce the quantity of the receipt they reference; value them like the original receipt (original receipt date's FX rate).
6. GL mapping: materials → 5100, freight → 5150, services → 6200. Capex lines: USD value ≥ 5,000.00 → 1800 (construction in progress), otherwise expensed to 6100. Apply the capex threshold to the line's USD value after returns.
7. Partially invoiced receipts: accrue only the **uninvoiced quantity**, still at the PO unit price (price variances are handled when the invoice is matched, not in the accrual).
8. This policy may be amended only by a written revision of this document approved by the CFO; amendments take effect from the revision date recorded here. No revisions have been recorded.
