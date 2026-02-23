# /promotion-report

> If you see unfamiliar placeholders or need to check which tools are connected, see [CONNECTORS.md](../CONNECTORS.md).

Generate marketing performance reports for campaigns and promotions.

## Usage

```
/promotion-report                        # Current month overview
/promotion-report --period weekly         # Period: daily/weekly/monthly/yearly
/promotion-report --campaign <name>       # Specific campaign report
/promotion-report --channel line|social   # Filter by channel
```

## How It Works

```
┌─────────────────────────────────────────────────────┐
│              PROMOTION REPORT                        │
├─────────────────────────────────────────────────────┤
│  STANDALONE (always works)                           │
│  ✓ Define marketing KPIs and metrics framework       │
│  ✓ Create report templates                           │
│  ✓ Suggest optimization strategies                   │
├─────────────────────────────────────────────────────┤
│  SUPERCHARGED (when ~~marketplace-engine connected)  │
│  + Pull broadcast logs from ~~notification           │
│  + Pull order data to measure conversion             │
│  + Calculate ROI per campaign                        │
│  + Show member growth from ~~crm                     │
│  + Generate trend charts data                        │
└─────────────────────────────────────────────────────┘
```

## Key Metrics

| Metric | Source | Description |
|--------|--------|-------------|
| Broadcasts Sent | line.notify.log | Total messages pushed |
| Delivery Rate | LINE API stats | Messages successfully delivered |
| New Followers | line.channel.member | New LINE OA followers |
| Unfollows | line.channel.member | Users who unfollowed |
| Net Growth | Calculated | New followers - unfollows |
| Orders from LINE | sale.order | Orders placed via LIFF |
| Conversion Rate | Calculated | Orders / active users |
| Revenue from LINE | sale.order | Total GMV via LIFF |

## Channel Mix

```
Social Media (YouTube/Facebook/TikTok)
    → Awareness (top of funnel)
LINE OA (Broadcast/Rich Menu)
    → Engagement (middle of funnel)
LIFF Mini App (Marketplace)
    → Conversion (bottom of funnel)
```

## Workflow

1. **Set Period** -- Define report date range
2. **Gather Data** -- Pull from ~~notification, ~~crm, ~~marketplace-engine
3. **Calculate** -- Aggregate metrics, compute rates and trends
4. **Compare** -- Period-over-period comparison
5. **Report** -- Structured performance report with insights

## Output

```markdown
## Promotion Report

**Period:** [start] -- [end]
**Generated:** [timestamp]

### Campaign Performance
| Campaign | Type | Sent | Delivered | Clicks | Conversions | Revenue |
|----------|------|------|-----------|--------|-------------|---------|
| [name] | [broadcast/flash-sale] | [n] | [n] | [n] | [n] | ฿[amt] |
| **Total** | | **[n]** | **[n]** | **[n]** | **[n]** | **฿[amt]** |

### Channel Mix
| Channel | Reach | Engagement | Conversions | Revenue | ROI |
|---------|-------|-----------|-------------|---------|-----|
| LINE Broadcast | [n] | [n] ([%]) | [n] | ฿[amt] | [x] |
| LINE Rich Menu | [n] | [n] ([%]) | [n] | ฿[amt] | [x] |
| Facebook | [n] | [n] ([%]) | [n] | ฿[amt] | [x] |
| YouTube | [n] | [n] ([%]) | [n] | ฿[amt] | [x] |
| TikTok | [n] | [n] ([%]) | [n] | ฿[amt] | [x] |

### Member Growth
| Metric | This Period | Previous | Change |
|--------|------------|----------|--------|
| New Followers | [n] | [prev] | [+/-]% |
| Unfollows | [n] | [prev] | [+/-]% |
| Net Growth | [n] | [prev] | [+/-]% |
| Total Members | [n] | [prev] | [+/-]% |

### Member Distribution
| Type | Count | % of Total |
|------|-------|-----------|
| Buyer | [n] | [%] |
| Seller | [n] | [%] |
| Admin | [n] | [%] |

### Content Ratio Check
| Type | Posts | Target | Actual | Status |
|------|-------|--------|--------|--------|
| Value (80%) | [n] | 80% | [%] | OK/Adjust |
| Selling (20%) | [n] | 20% | [%] | OK/Adjust |

### Top Performing Content
| Content | Channel | Engagement | Conversions |
|---------|---------|-----------|-------------|
| [title] | [channel] | [n] | [n] |

### Recommendations
1. [Insight based on data]
2. [Optimization suggestion]
3. [Content strategy adjustment]
```

## Next Steps

- Want a deeper dive into a specific campaign?
- Should I adjust the content ratio strategy?
- Want to plan next period's campaigns based on these insights?

## Related Skills

- Uses [campaign-analytics](../skills/campaign-analytics/SKILL.md) for metrics
- Uses [content-strategy](../skills/content-strategy/SKILL.md) for 80/20 analysis
- Cross-references [order-management](../../commerce/CONNECTORS.md) for conversion data
- Cross-references [member-management](../../line-platform/CONNECTORS.md) for growth data
