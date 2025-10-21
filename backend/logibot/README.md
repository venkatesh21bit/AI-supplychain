# LOGI-BOT: Autonomous Supply Chain Resilience Agent

**Version:** 1.0.0  
**Author:** Vendor Innovation Team  
**License:** MIT

## Overview

LOGI-BOT is a production-ready autonomous agent that proactively detects, diagnoses, and resolves supply chain disruptions in your vendor management system. Unlike traditional reactive systems, LOGI-BOT uses AI-powered analysis and automated workflow orchestration to handle supply chain issues before they impact your business.

## Key Features

### 🎯 Proactive Monitoring
- **Real-time inventory monitoring** across all products
- **Automated alert generation** when stock levels hit critical thresholds
- **Configurable thresholds** per company

### 🔍 Root Cause Analysis
- **Intelligent diagnosis** using historical consumption patterns
- **Demand forecasting comparison** to identify surges
- **Supplier performance analysis** to detect delivery issues
- **Confidence scoring** for all diagnoses

### 🤖 AI-Powered Optimization
- **Emergency replenishment planning** with optimal quantities
- **Sourcing strategy recommendations** (primary, backup, split orders)
- **Timeline calculations** based on lead times and priorities
- **Safety stock adjustments** based on root cause

### 🔄 Autonomous Orchestration
- **Asana project creation** with task assignments
- **Outlook meeting scheduling** for stakeholder briefings
- **Draft order generation** (pending human approval)
- **Complete audit trail** of all actions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      LOGI-BOT AGENT                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Root Cause    │  │ Optimization │  │   Composio       │ │
│  │ Analyzer      │→ │   Engine     │→ │  Orchestrator    │ │
│  └───────────────┘  └──────────────┘  └──────────────────┘ │
│         ↓                   ↓                    ↓          │
│  ┌───────────────────────────────────────────────────────┐ │
│  │           Django REST API Layer                       │ │
│  └───────────────────────────────────────────────────────┘ │
│         ↓                   ↓                    ↓          │
│  ┌───────────┐      ┌──────────┐       ┌─────────────┐   │
│  │ Database  │      │ Frontend │       │  External   │   │
│  │  Models   │      │   UI     │       │   Tools     │   │
│  └───────────┘      └──────────┘       └─────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation & Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+ (Cloud SQL recommended)
- Node.js 18+ (for frontend)
- Composio API Key ([Get one here](https://app.composio.dev))

### Step 1: Install Dependencies

```bash
cd Vendor-backend
pip install -r logibot/requirements.txt
```

Required packages:
- `composio-core>=0.3.0` - For tool orchestration
- `openai>=1.0.0` - For AI optimization engine
- `requests>=2.31.0` - For HTTP requests
- `python-dotenv>=1.0.0` - For environment management

### Step 2: Environment Configuration

Create or update your `.env` file in `Vendor-backend/`:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# Composio Integration
COMPOSIO_API_KEY=your_composio_api_key_here
ASANA_WORKSPACE_ID=your_asana_workspace_id
OUTLOOK_ACCOUNT=your_outlook_email@company.com

# Optional: Additional Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Step 3: Run Database Migrations

```bash
cd Vendor-backend
python manage.py migrate
```

This creates the following tables:
- `app_agentalert` - Tracks all detected alerts
- `app_agentexecution` - Stores execution history
- `app_agentworkflowstep` - Details of workflow steps
- `app_agentconfiguration` - Per-company configuration

### Step 4: Configure Agent for Your Company

Use the Django admin or API to configure:
- Critical inventory level (default: 10 units)
- Warning inventory level (default: 20 units)
- Auto-resolution enabled/disabled
- Notification email addresses

## Usage

### Automated Monitoring

LOGI-BOT can run automated monitoring on a schedule (e.g., every 5 minutes):

```bash
# Add to cron job or task scheduler
python manage.py runscript monitor_inventory
```

Or use the API endpoint:

```bash
curl -X GET http://localhost:8000/api/agent/monitor-inventory/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Manual Trigger

To manually check a specific product:

```bash
curl -X POST http://localhost:8000/api/agent/check-inventory/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 123,
    "company_id": 456
  }'
```

### Monitor Agent Status

```bash
curl -X GET http://localhost:8000/api/agent/status/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

Response:
```json
{
  "agent": "LOGI-BOT",
  "version": "1.0.0",
  "active": true,
  "total_executions": 42,
  "active_workflows": 3,
  "statistics": {
    "total_alerts": 15,
    "active_alerts": 3,
    "successful_executions": 39
  }
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/agent/check-inventory/` | POST | Manually trigger inventory check for a product |
| `/api/agent/monitor-inventory/` | GET | Monitor all products for low inventory |
| `/api/agent/alerts/` | GET | Get all agent alerts with filtering |
| `/api/agent/executions/` | GET | View execution history |
| `/api/agent/status/` | GET | Get current agent status |
| `/api/agent/config/` | POST | Update agent configuration |

See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for detailed API specs.

## Workflow Example: Low Inventory Alert

### Trigger
Product inventory falls below critical threshold (e.g., 10 units)

### Agent Response

1. **Root Cause Analysis** (5-10 seconds)
   - Analyzes consumption rate (last 7 days vs historical)
   - Compares against forecast
   - Checks supplier performance
   - Reviews pending orders
   - **Result**: Identifies "demand_surge" with 85% confidence

2. **Solution Formulation** (2-5 seconds)
   - Calculates optimal replenishment quantity
   - Determines sourcing strategy (primary + backup)
   - Estimates timeline and delivery date
   - Generates action items
   - **Result**: Emergency order for 250 units, 7-day delivery

3. **Autonomous Orchestration** (10-15 seconds)
   - **Asana**: Creates project "EMERGENCY_REPLENISHMENT_LIMESTONE_123"
   - **Asana**: Adds tasks for procurement, logistics, planning teams
   - **Outlook**: Schedules 30-min emergency briefing for next business day
   - **ERP**: Creates draft order (pending manager approval)
   - **Result**: All workflows completed, stakeholders notified

### Total Time: < 30 seconds
### Human Intervention Required: Only for final order approval

## Configuration

### Per-Company Settings

```python
# Via Django Admin or API
AgentConfiguration.objects.create(
    company=company,
    critical_inventory_level=10,    # Trigger alert at this level
    warning_inventory_level=20,     # Warning threshold
    reorder_point=15,               # When to suggest reorder
    safety_stock=5,                 # Minimum safety stock
    auto_resolution_enabled=True,   # Enable autonomous actions
    require_approval=True,          # Require human approval for orders
    check_interval_minutes=5,       # Monitoring frequency
    notification_emails=["manager@company.com"]
)
```

### Alert Types

- `low_inventory` - Stock below critical level
- `delayed_shipment` - Shipment delays detected (coming soon)
- `demand_surge` - Unexpected demand increase (coming soon)
- `supplier_issue` - Supplier performance problems (coming soon)

### Priority Levels

- `critical` - Stock < 10 units, immediate action
- `high` - Stock < 20 units or demand surge
- `medium` - Stock < 30 units
- `low` - General monitoring

## Integration with Composio

LOGI-BOT uses [Composio](https://composio.dev) for all external tool integrations. This provides:

- **Unified authentication** across all tools
- **Tool discovery** and capability checking
- **Error handling** and retry logic
- **Audit logging** of all external actions

### Supported Tools

- **Asana** - Project and task management
- **Microsoft Outlook** - Meeting scheduling
- **ERP System** - Order creation (your internal system)

### Adding New Tools

```python
# In composio_orchestrator.py
def _create_slack_notification(self, data: Dict) -> Dict:
    """Send Slack notification via Composio."""
    payload = {
        "tool": "slack",
        "action": "post_message",
        "parameters": {
            "channel": "#supply-chain",
            "text": f"🚨 Low inventory alert: {data['product_name']}"
        }
    }
    return self._call_composio_api(payload)
```

## Monitoring & Observability

### Logging

LOGI-BOT logs all activities to:
- Console (development)
- File: `logibot.log` (production)
- Database: `AgentExecution` model

Log levels:
```python
DEBUG: Detailed diagnostic information
INFO: General operational messages
WARNING: Non-critical issues
ERROR: Error conditions
CRITICAL: System failures
```

### Metrics

Track agent performance via API:
```bash
GET /api/agent/executions/?status=completed
GET /api/agent/alerts/?priority=critical
```

### Alerting

Configure notifications:
- Email alerts for critical issues
- Slack webhooks for team notifications
- Dashboard view in frontend

## Troubleshooting

### Common Issues

**Agent not detecting alerts:**
- Check `AgentConfiguration` exists for company
- Verify inventory levels in database
- Review `critical_inventory_level` setting

**Composio integration failures:**
- Verify `COMPOSIO_API_KEY` is set
- Check tool authentication in Composio dashboard
- Review `composio_orchestrator.py` logs

**Database connection errors:**
- Ensure Cloud SQL Proxy is running
- Check `DATABASE_URL` environment variable
- Verify network connectivity

### Debug Mode

Enable verbose logging:
```python
# In settings.py
LOGGING = {
    'loggers': {
        'logibot': {
            'level': 'DEBUG',
        }
    }
}
```

## Development

### Running Tests

```bash
pytest logibot/tests/
```

### Adding New Alert Types

1. Add to `AlertType` enum in `config.py`
2. Create handler method in `agent.py`
3. Add API endpoint in `agent_views.py`
4. Update documentation

### Contributing

1. Fork the repository
2. Create feature branch
3. Write tests
4. Submit pull request

## Performance

- **Alert Detection**: < 1 second
- **Root Cause Analysis**: 5-10 seconds
- **Solution Generation**: 2-5 seconds
- **Workflow Orchestration**: 10-15 seconds
- **Total Response Time**: < 30 seconds

## Security

- **Authentication**: JWT tokens required for all API calls
- **Authorization**: Company-level data isolation
- **Audit Trail**: All actions logged with user/timestamp
- **API Keys**: Stored securely in environment variables
- **Data Encryption**: Database connections over SSL/TLS

## Roadmap

### v1.1 (Q1 2025)
- ✅ Low inventory alerts
- ⬜ Delayed shipment detection
- ⬜ Demand forecasting improvements

### v1.2 (Q2 2025)
- ⬜ Supplier performance scoring
- ⬜ Multi-tier approval workflows
- ⬜ Mobile app notifications

### v2.0 (Q3 2025)
- ⬜ Machine learning models
- ⬜ Predictive maintenance
- ⬜ Cost optimization engine

## Support

- **Documentation**: [docs.yourcompany.com/logibot](https://docs.yourcompany.com/logibot)
- **Email**: support@yourcompany.com
- **Slack**: #logibot-support

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built on Django REST Framework
- Powered by Composio Tool Router
- Optimized with OpenAI GPT-4

---

**Made with ❤️ by Vendor Innovation Team**
