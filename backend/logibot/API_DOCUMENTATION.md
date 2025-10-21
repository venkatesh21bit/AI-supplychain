# LOGI-BOT API Documentation

## Base URL
```
http://localhost:8000/api
```

## Authentication

All API endpoints require JWT authentication. Include the token in the `Authorization` header:

```
Authorization: Bearer YOUR_JWT_TOKEN
```

To obtain a token:
```bash
POST /api/token/
{
    "username": "your_username",
    "password": "your_password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLC...",
    "refresh": "eyJ0eXAiOiJKV1QiLC..."
}
```

---

## Endpoints

### 1. Check Inventory (Manual Trigger)

**Endpoint**: `POST /api/agent/check-inventory/`

**Description**: Manually trigger an inventory check for a specific product. If inventory is below critical threshold, LOGI-BOT will initiate the full response workflow.

**Request Body**:
```json
{
    "product_id": 123,
    "company_id": 456
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | integer | Yes | ID of the product to check |
| `company_id` | integer | Yes | ID of the company that owns the product |

**Response** (200 OK):
```json
{
    "status": "success",
    "alert_generated": true,
    "message": "Low inventory detected for LIMESTONE. Alert created and agent initiated response.",
    "alert": {
        "id": 42,
        "alert_type": "low_inventory",
        "priority": "critical",
        "product_id": 123,
        "product_name": "LIMESTONE",
        "current_inventory": 8,
        "threshold": 10,
        "created_at": "2025-01-15T10:30:00Z",
        "status": "active"
    },
    "execution": {
        "id": 15,
        "status": "completed",
        "started_at": "2025-01-15T10:30:01Z",
        "completed_at": "2025-01-15T10:30:28Z",
        "duration_seconds": 27,
        "root_cause": "demand_surge",
        "confidence": 0.85,
        "actions_taken": [
            "Created Asana project EMERGENCY_REPLENISHMENT_LIMESTONE_123",
            "Scheduled emergency briefing for 2025-01-16 at 09:00",
            "Created draft order for 250 units (pending approval)"
        ]
    }
}
```

**Response** (200 OK - No Alert):
```json
{
    "status": "success",
    "alert_generated": false,
    "message": "Inventory level is adequate. Current: 45 units, Threshold: 10 units",
    "product": {
        "id": 123,
        "name": "LIMESTONE",
        "current_inventory": 45
    }
}
```

**Error Responses**:

400 Bad Request:
```json
{
    "error": "Missing required fields: product_id and company_id"
}
```

404 Not Found:
```json
{
    "error": "Product not found"
}
```

500 Internal Server Error:
```json
{
    "error": "Failed to execute agent workflow",
    "details": "Connection to Composio API timed out"
}
```

---

### 2. Monitor All Inventory

**Endpoint**: `GET /api/agent/monitor-inventory/`

**Description**: Monitors all products for low inventory across all companies or a specific company. This is typically called by a scheduled job.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | integer | No | Filter by specific company |
| `auto_resolve` | boolean | No | Whether to automatically trigger agent response (default: true) |

**Example Request**:
```bash
GET /api/agent/monitor-inventory/?company_id=456&auto_resolve=true
```

**Response** (200 OK):
```json
{
    "status": "success",
    "timestamp": "2025-01-15T10:45:00Z",
    "products_checked": 127,
    "alerts_generated": 3,
    "alerts": [
        {
            "alert_id": 42,
            "product_id": 123,
            "product_name": "LIMESTONE",
            "company_id": 456,
            "current_inventory": 8,
            "threshold": 10,
            "priority": "critical",
            "execution_initiated": true,
            "execution_id": 15
        },
        {
            "alert_id": 43,
            "product_id": 456,
            "product_name": "CEMENT",
            "company_id": 456,
            "current_inventory": 15,
            "threshold": 20,
            "priority": "high",
            "execution_initiated": true,
            "execution_id": 16
        },
        {
            "alert_id": 44,
            "product_id": 789,
            "product_name": "SAND",
            "company_id": 457,
            "current_inventory": 12,
            "threshold": 15,
            "priority": "medium",
            "execution_initiated": false,
            "reason": "Auto-resolution disabled for company 457"
        }
    ],
    "summary": {
        "critical_alerts": 1,
        "high_priority_alerts": 1,
        "medium_priority_alerts": 1,
        "executions_started": 2
    }
}
```

---

### 3. Get Alerts

**Endpoint**: `GET /api/agent/alerts/`

**Description**: Retrieve all alerts with optional filtering.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | integer | No | Filter by company |
| `product_id` | integer | No | Filter by product |
| `alert_type` | string | No | Filter by type: `low_inventory`, `delayed_shipment`, etc. |
| `priority` | string | No | Filter by priority: `critical`, `high`, `medium`, `low` |
| `status` | string | No | Filter by status: `active`, `acknowledged`, `resolved`, `ignored` |
| `start_date` | datetime | No | Filter alerts created after this date (ISO 8601) |
| `end_date` | datetime | No | Filter alerts created before this date (ISO 8601) |
| `limit` | integer | No | Number of results per page (default: 50, max: 200) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Example Request**:
```bash
GET /api/agent/alerts/?company_id=456&priority=critical&status=active&limit=10
```

**Response** (200 OK):
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 42,
            "alert_type": "low_inventory",
            "priority": "critical",
            "status": "active",
            "product": {
                "id": 123,
                "name": "LIMESTONE",
                "sku": "LM-001",
                "category": "Raw Materials"
            },
            "company": {
                "id": 456,
                "name": "Acme Manufacturing"
            },
            "current_inventory": 8,
            "threshold": 10,
            "details": {
                "consumption_rate": "12 units/day",
                "days_until_stockout": 0.67,
                "pending_orders": 0,
                "last_restock": "2025-01-10T14:00:00Z"
            },
            "created_at": "2025-01-15T10:30:00Z",
            "acknowledged_at": null,
            "acknowledged_by": null,
            "resolved_at": null,
            "execution_id": 15
        }
    ]
}
```

---

### 4. Get Executions

**Endpoint**: `GET /api/agent/executions/`

**Description**: Retrieve agent execution history with details of all workflow steps.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `company_id` | integer | No | Filter by company |
| `alert_id` | integer | No | Filter by specific alert |
| `status` | string | No | Filter by status: `running`, `completed`, `failed` |
| `start_date` | datetime | No | Filter executions started after this date |
| `end_date` | datetime | No | Filter executions started before this date |
| `limit` | integer | No | Number of results per page (default: 20, max: 100) |
| `offset` | integer | No | Pagination offset (default: 0) |

**Example Request**:
```bash
GET /api/agent/executions/?status=completed&limit=5
```

**Response** (200 OK):
```json
{
    "count": 42,
    "next": "/api/agent/executions/?offset=5&limit=5",
    "previous": null,
    "results": [
        {
            "id": 15,
            "alert": {
                "id": 42,
                "alert_type": "low_inventory",
                "priority": "critical",
                "product_name": "LIMESTONE"
            },
            "company": {
                "id": 456,
                "name": "Acme Manufacturing"
            },
            "status": "completed",
            "started_at": "2025-01-15T10:30:01Z",
            "completed_at": "2025-01-15T10:30:28Z",
            "duration_seconds": 27,
            "workflow_steps": [
                {
                    "id": 45,
                    "step_name": "root_cause_analysis",
                    "step_number": 1,
                    "status": "completed",
                    "started_at": "2025-01-15T10:30:01Z",
                    "completed_at": "2025-01-15T10:30:09Z",
                    "duration_seconds": 8,
                    "output": {
                        "root_cause": "demand_surge",
                        "confidence": 0.85,
                        "analysis": {
                            "consumption_rate_increase": 0.45,
                            "forecast_deviation": 0.38,
                            "supplier_delays": false
                        }
                    },
                    "error": null
                },
                {
                    "id": 46,
                    "step_name": "optimization",
                    "step_number": 2,
                    "status": "completed",
                    "started_at": "2025-01-15T10:30:09Z",
                    "completed_at": "2025-01-15T10:30:13Z",
                    "duration_seconds": 4,
                    "output": {
                        "recommended_quantity": 250,
                        "sourcing_strategy": "primary_with_backup",
                        "primary_supplier": "Supplier A (200 units)",
                        "backup_supplier": "Supplier B (50 units)",
                        "estimated_delivery": "2025-01-22",
                        "safety_stock_adjustment": 20
                    },
                    "error": null
                },
                {
                    "id": 47,
                    "step_name": "orchestration",
                    "step_number": 3,
                    "status": "completed",
                    "started_at": "2025-01-15T10:30:13Z",
                    "completed_at": "2025-01-15T10:30:28Z",
                    "duration_seconds": 15,
                    "output": {
                        "asana_project": {
                            "id": "1234567890",
                            "name": "EMERGENCY_REPLENISHMENT_LIMESTONE_123",
                            "url": "https://app.asana.com/0/1234567890",
                            "tasks_created": 6
                        },
                        "outlook_meeting": {
                            "id": "AAMkAG...",
                            "subject": "Emergency: LIMESTONE Stock Shortage",
                            "start_time": "2025-01-16T09:00:00Z",
                            "attendees": 8
                        },
                        "draft_orders": [
                            {
                                "supplier": "Supplier A",
                                "quantity": 200,
                                "estimated_cost": 5000,
                                "status": "pending_approval"
                            },
                            {
                                "supplier": "Supplier B",
                                "quantity": 50,
                                "estimated_cost": 1350,
                                "status": "pending_approval"
                            }
                        ]
                    },
                    "error": null
                }
            ],
            "summary": "Successfully resolved low inventory for LIMESTONE through demand surge mitigation. Created emergency replenishment plan with dual-supplier strategy.",
            "error": null
        }
    ]
}
```

---

### 5. Get Agent Status

**Endpoint**: `GET /api/agent/status/`

**Description**: Get the current health and operational status of LOGI-BOT.

**Query Parameters**: None

**Example Request**:
```bash
GET /api/agent/status/
```

**Response** (200 OK):
```json
{
    "agent": "LOGI-BOT",
    "version": "1.0.0",
    "status": "active",
    "uptime_hours": 72.5,
    "last_check": "2025-01-15T10:45:00Z",
    "statistics": {
        "total_executions": 42,
        "successful_executions": 39,
        "failed_executions": 3,
        "success_rate": 0.929,
        "active_workflows": 2,
        "total_alerts": 58,
        "active_alerts": 5,
        "resolved_alerts": 51,
        "ignored_alerts": 2,
        "avg_response_time_seconds": 24.3
    },
    "health_checks": {
        "database_connection": "ok",
        "composio_api": "ok",
        "last_successful_execution": "2025-01-15T10:30:28Z",
        "configuration_loaded": true
    },
    "recent_activity": [
        {
            "timestamp": "2025-01-15T10:30:00Z",
            "event": "execution_completed",
            "alert_id": 42,
            "execution_id": 15,
            "duration_seconds": 27
        },
        {
            "timestamp": "2025-01-15T10:25:00Z",
            "event": "execution_completed",
            "alert_id": 41,
            "execution_id": 14,
            "duration_seconds": 31
        }
    ]
}
```

---

### 6. Update Agent Configuration

**Endpoint**: `POST /api/agent/config/`

**Description**: Update agent configuration for a company.

**Request Body**:
```json
{
    "company_id": 456,
    "critical_inventory_level": 10,
    "warning_inventory_level": 20,
    "reorder_point": 15,
    "safety_stock": 5,
    "auto_resolution_enabled": true,
    "require_approval": true,
    "check_interval_minutes": 5,
    "notification_emails": ["manager@acme.com", "procurement@acme.com"],
    "notification_slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
}
```

**Parameters**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `company_id` | integer | Yes | ID of the company |
| `critical_inventory_level` | integer | No | Units at which critical alert is triggered |
| `warning_inventory_level` | integer | No | Units at which warning alert is triggered |
| `reorder_point` | integer | No | Recommended reorder point |
| `safety_stock` | integer | No | Minimum safety stock to maintain |
| `auto_resolution_enabled` | boolean | No | Enable autonomous agent response |
| `require_approval` | boolean | No | Require human approval for orders |
| `check_interval_minutes` | integer | No | Monitoring frequency (5-60 minutes) |
| `notification_emails` | array | No | List of email addresses for notifications |
| `notification_slack_webhook` | string | No | Slack webhook URL for notifications |

**Response** (200 OK):
```json
{
    "status": "success",
    "message": "Agent configuration updated successfully",
    "configuration": {
        "id": 789,
        "company_id": 456,
        "company_name": "Acme Manufacturing",
        "critical_inventory_level": 10,
        "warning_inventory_level": 20,
        "reorder_point": 15,
        "safety_stock": 5,
        "auto_resolution_enabled": true,
        "require_approval": true,
        "check_interval_minutes": 5,
        "notification_emails": ["manager@acme.com", "procurement@acme.com"],
        "notification_slack_webhook": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
        "created_at": "2025-01-10T08:00:00Z",
        "updated_at": "2025-01-15T10:50:00Z"
    }
}
```

**Error Responses**:

400 Bad Request:
```json
{
    "error": "Invalid configuration",
    "details": {
        "check_interval_minutes": ["Value must be between 5 and 60"]
    }
}
```

---

## Error Codes

| HTTP Status | Error Code | Description |
|-------------|-----------|-------------|
| 400 | `INVALID_REQUEST` | Missing or invalid request parameters |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication token |
| 403 | `FORBIDDEN` | User doesn't have permission to access resource |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error during processing |
| 502 | `EXTERNAL_SERVICE_ERROR` | Error communicating with external service (Composio, etc.) |
| 503 | `SERVICE_UNAVAILABLE` | Agent is temporarily unavailable |

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Monitoring endpoints**: 100 requests per minute
- **Manual triggers**: 20 requests per minute
- **Configuration updates**: 10 requests per minute

Rate limit headers are included in all responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## Webhooks (Coming Soon)

Subscribe to agent events:
- `alert.created` - New alert generated
- `execution.started` - Agent workflow started
- `execution.completed` - Agent workflow completed
- `execution.failed` - Agent workflow failed

## Best Practices

1. **Use monitoring endpoint for scheduled jobs**: Call `/api/agent/monitor-inventory/` every 5-10 minutes
2. **Manual triggers for specific products**: Use `/api/agent/check-inventory/` when user reports an issue
3. **Pagination for large datasets**: Always use `limit` and `offset` for alerts and executions
4. **Filter by company**: For multi-tenant applications, always include `company_id` filter
5. **Check agent status periodically**: Monitor `/api/agent/status/` to ensure agent is healthy
6. **Handle errors gracefully**: Implement retry logic for 502/503 errors

## Code Examples

### Python
```python
import requests

API_URL = "http://localhost:8000/api"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Check inventory
response = requests.post(
    f"{API_URL}/agent/check-inventory/",
    headers=headers,
    json={"product_id": 123, "company_id": 456}
)
print(response.json())

# Get alerts
response = requests.get(
    f"{API_URL}/agent/alerts/?priority=critical&status=active",
    headers=headers
)
alerts = response.json()["results"]
```

### JavaScript (Frontend)
```javascript
const API_URL = process.env.NEXT_PUBLIC_API_URL;
const token = localStorage.getItem('access_token');

// Monitor inventory
const response = await fetch(`${API_URL}/agent/monitor-inventory/`, {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
const data = await response.json();
console.log(`Generated ${data.alerts_generated} alerts`);
```

### cURL
```bash
# Check status
curl -X GET http://localhost:8000/api/agent/status/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Trigger inventory check
curl -X POST http://localhost:8000/api/agent/check-inventory/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 123, "company_id": 456}'
```

---

**Last Updated**: 2025-01-15  
**API Version**: v1.0.0
