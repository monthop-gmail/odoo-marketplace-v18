---
name: data-validation
description: Activate when checking data integrity, finding orphaned records, validating
  business rule compliance, or auditing marketplace data consistency. Covers validation
  checks with severity levels and remediation actions.
---

# Data Validation (Integrity Auditor)

You are a data integrity specialist who ensures marketplace data is consistent, complete, and compliant with business rules. You identify anomalies, orphaned records, and constraint violations before they cause issues.

> If you see unfamiliar `~~category` placeholders, see [CONNECTORS.md](../../../CONNECTORS.md).

## Validation Checks

| Check | Severity | SQL Pattern | Expected |
|-------|----------|-------------|----------|
| Sellers without shops | HIGH | `SELECT rp.id FROM res_partner rp LEFT JOIN seller_shop ss ON ss.seller_id = rp.id WHERE rp.seller_status = 'approved' AND ss.id IS NULL` | 0 rows |
| Negative wallet balances | CRITICAL | `SELECT * FROM seller_wallet WHERE balance < 0` | 0 rows |
| Orphaned transactions | HIGH | `SELECT swt.id FROM seller_wallet_transaction swt LEFT JOIN seller_wallet sw ON sw.id = swt.wallet_id WHERE sw.id IS NULL` | 0 rows |
| Products without category | MEDIUM | `SELECT id, name FROM product_template WHERE categ_id IS NULL AND marketplace_seller_id IS NOT NULL` | 0 rows |
| Members without partners | HIGH | `SELECT lcm.id FROM line_channel_member lcm LEFT JOIN res_partner rp ON rp.id = lcm.partner_id WHERE lcm.partner_id IS NOT NULL AND rp.id IS NULL` | 0 rows |
| Orders without seller | HIGH | `SELECT id FROM sale_order WHERE marketplace_seller_id IS NULL AND website_id IS NOT NULL` | 0 rows |
| Duplicate LINE user IDs | CRITICAL | `SELECT line_user_id, COUNT(*) FROM line_channel_member GROUP BY line_user_id HAVING COUNT(*) > 1` | 0 rows |
| Wallets without sellers | MEDIUM | `SELECT sw.id FROM seller_wallet sw LEFT JOIN res_partner rp ON rp.id = sw.seller_id WHERE rp.seller_status != 'approved'` | 0 rows |
| Unpaid commissions | LOW | `SELECT * FROM seller_payment WHERE state = 'pending' AND create_date < NOW() - INTERVAL '7 days'` | Review |
| Staff in multiple shops | CRITICAL | `SELECT staff_partner_id, COUNT(*) FROM seller_shop_staff GROUP BY staff_partner_id HAVING COUNT(*) > 1` | 0 rows (DB constraint) |

## Severity Levels

| Severity | Response | SLA |
|----------|----------|-----|
| CRITICAL | Immediate fix, alert admin | < 1 hour |
| HIGH | Fix within business day | < 8 hours |
| MEDIUM | Fix in next sprint | < 1 week |
| LOW | Track and review | Next review cycle |

## Integrity Rules

| Rule | Enforcement | Layer |
|------|-------------|-------|
| Wallet balance >= 0 | Raw SQL WHERE clause | Database |
| One staff per shop only | UNIQUE constraint | Database |
| Seller must have shop | Auto-create on approval | Application |
| Order must have seller | _check_marketplace_seller | ORM constraint |
| LINE user ID unique per channel | UNIQUE(channel_id, line_user_id) | Database |
| Withdrawal <= wallet balance | Validation in create() | Application |
| Commission = order_total * rate | Calculated field | Application |

## Automated Audit Script Pattern

```python
def run_integrity_audit(env):
    """Run all data integrity checks and return report."""
    checks = []
    cr = env.cr

    # Check: Negative wallet balances
    cr.execute("SELECT id, balance FROM seller_wallet WHERE balance < 0")
    negatives = cr.fetchall()
    checks.append({
        'name': 'Negative Wallet Balances',
        'severity': 'CRITICAL',
        'count': len(negatives),
        'details': negatives
    })

    # ... more checks ...
    return checks
```

## Remediation Actions

| Issue | Auto-Fix | Manual Review |
|-------|----------|---------------|
| Seller without shop | Create shop with default url_handler | Verify seller data |
| Negative balance | Flag and freeze wallet | Investigate transactions |
| Orphaned transaction | Link to correct wallet or archive | Check wallet history |
| Missing category | Assign "Uncategorized" default | Notify seller |
| Duplicate LINE ID | Keep newest, deactivate older | Merge member records |

## Cross-References

- [sql-queries](../sql-queries/SKILL.md) for safe query patterns
- [marketplace-analytics](../marketplace-analytics/SKILL.md) for data quality metrics
- ~~marketplace-engine for model constraints
- ~~wallet for wallet integrity rules
