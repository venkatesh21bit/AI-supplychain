from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.urlpatterns import format_suffix_patterns  # ✅ For better API format handling
from rest_framework.routers import DefaultRouter
from .views import (
    CustomAuthToken, ProductViewSet,CategoryViewSet,add_retailer,get_employee_id,logout_view, get_employees, get_retailers,get_counts,
    get_orders,get_users,get_employee_orders,recent_actions,get_employee_shipments,update_shipment_status,get_logged_in_user,allocate_order, get_trucks, get_shipments,category_stock_data,store_qr_code,
    save_odoo_credentials,register_user,get_available_employees_for_order, get_available_groups, InvoiceViewSet, CompanyViewSet, shipment_stats, invoice_count, approve_order,
    forgot_password, verify_otp, reset_password, resend_otp, update_product_quantities,
    retailer_companies, public_companies, send_company_invite, join_by_code, request_company_approval,
    retailer_counts, retailer_companies_count, retailer_orders, retailer_products, retailer_profile,
    generate_invite_code, get_company_invites, get_retailer_requests, accept_retailer_request,
    get_company_connections, update_connection_status, create_retailer_profile, check_retailer_profile
)
from .agent_views import (
    trigger_inventory_check, monitor_all_inventory, get_agent_alerts,
    get_agent_executions, get_agent_status, update_agent_config, check_all_inventory
)
# Advanced AI features (optional import)
try:
    from .ai_views import (
        process_voice_command, analyze_document, send_multilingual_alert,
        generate_predictive_report, generate_smart_document, create_intelligent_workflow,
        get_enhanced_agent_status
    )
    AI_FEATURES_AVAILABLE = True
except ImportError:
    AI_FEATURES_AVAILABLE = False

# Enhanced Composio integration (optional import)
try:
    from .composio_views import (
        create_cross_platform_workflow, send_slack_notification, create_asana_task,
        send_email_notification, update_tracking_sheet, schedule_meeting,
        create_github_issue, get_composio_status
    )
    from .composio_extended_views import (
        get_connected_integrations, create_trello_card, send_discord_message,
        send_teams_message, create_notion_page, create_github_issue as create_github_issue_ext,
        upload_to_google_drive, send_telegram_message, get_integration_stats
    )
    COMPOSIO_FEATURES_AVAILABLE = True
except ImportError:
    COMPOSIO_FEATURES_AVAILABLE = False
# Add the router for InvoiceViewSet
router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # Registration Endpoint
    path('register/', register_user, name='register_user'),

    # ✅ Authentication Endpoints
    path("token/", CustomAuthToken.as_view(), name="api_token_auth"),  # Login (Returns JWT tokens)
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # Refresh JWT token
    path("logout/", logout_view, name="api_logout"),  # Logout (Blacklist refresh token)

    # ✅ API Endpoints (Protected)
    path('retailers/add/', add_retailer, name='add_retailer'),
    path("employees/", get_employees, name="get_employees"),  # Admin Only
    path("retailers/", get_retailers, name="get_retailers"),  # Admin Only
    path("orders/", get_orders, name="get_orders"),  # Admin & Employees
    path("allocate-order/", allocate_order, name="allocate_orders"),  # Employees Only
    path("trucks/", get_trucks, name="get_trucks"),  # Admin Only
    path("shipments/", get_shipments, name="get_shipments"),  # Admin & Employees.
    path('category-stock/', category_stock_data, name='category-stock-data'),
    path('store_qr/', store_qr_code, name='store_qr'),
    
    #count
    path('approve_order/', approve_order),
    path('get_available_employees_for_order/', get_available_employees_for_order),
    path('invoices/count/', invoice_count, name='invoice-count'),
    path('shipment-stats/', shipment_stats, name='shipment_stats'),
    path('count/', get_counts, name='count'),   
    path('users/', get_users, name='get_users'), 
    path('user_detail/', get_logged_in_user, name='get_logged_in_user'),
    path('employee_shipments/', get_employee_shipments, name='employee_shipments'),
    path('update_shipment_status/', update_shipment_status, name='update-shipment-status'),
    path('employee_orders/', get_employee_orders, name='get_employee_orders'),
    path('recent_actions/', recent_actions, name='recent_actions'),
    path('employee_id/', get_employee_id, name='get_employee_id'),
    path('odoo/save-credentials/', save_odoo_credentials, name='save_odoo_credentials'),
    path('groups/', get_available_groups, name='get_available_groups'),
    
    # Password Reset Endpoints
    path('forgot-password/', forgot_password, name='forgot_password'),
    path('verify-otp/', verify_otp, name='verify_otp'),
    path('reset-password/', reset_password, name='reset_password'),
    path('resend-otp/', resend_otp, name='resend_otp'),
    
    # Product Quantity Update Endpoint
    path('update-product-quantities/', update_product_quantities, name='update_product_quantities'),
    
    # Retailer API Endpoints
    path('retailer/check-profile/', check_retailer_profile, name='check_retailer_profile'),
    path('retailer/companies/', retailer_companies, name='retailer_companies'),
    path('companies/public/', public_companies, name='public_companies'),
    path('retailer/join-by-invite/', send_company_invite, name='send_company_invite'),
    path('retailer/join-by-code/', join_by_code, name='join_by_code'),
    path('retailer/request-approval/', request_company_approval, name='request_company_approval'),
    path('retailer/count/', retailer_counts, name='retailer_counts'),
    path('retailer/companies/count/', retailer_companies_count, name='retailer_companies_count'),
    path('retailer/orders/', retailer_orders, name='retailer_orders'),
    path('retailer/products/', retailer_products, name='retailer_products'),
    path('retailer/profile/', retailer_profile, name='retailer_profile'),
    
    # Company Management API Endpoints
    path('company/generate-invite-code/', generate_invite_code, name='generate_invite_code'),
    path('company/invites/', get_company_invites, name='get_company_invites'),
    path('company/retailer-requests/', get_retailer_requests, name='get_retailer_requests'),
    path('company/accept-request/', accept_retailer_request, name='accept_retailer_request'),
    path('company/connections/', get_company_connections, name='get_company_connections'),
    path('company/update-connection/', update_connection_status, name='update_connection_status'),
    
    # LOGI-BOT Agent endpoints (Core)
    path('agent/check-inventory/', trigger_inventory_check, name='agent_check_inventory'),
    path('agent/check-all-inventory/', check_all_inventory, name='agent_check_all_inventory'),
    path('agent/monitor-inventory/', monitor_all_inventory, name='agent_monitor_inventory'),
    path('agent/alerts/', get_agent_alerts, name='agent_alerts'),
    path('agent/executions/', get_agent_executions, name='agent_executions'),
    path('agent/status/', get_agent_status, name='agent_status'),
    path('agent/config/', update_agent_config, name='agent_config'),
    
     # Add router URLs here
    path('', include(router.urls)),
]

# ===================== ADVANCED AI FEATURES (Google Cloud Integration) =====================
# Add AI endpoints only if advanced features are available
if AI_FEATURES_AVAILABLE:
    ai_urlpatterns = [
        # Voice Command Processing
        path('agent/ai/voice-command/', process_voice_command, name='ai_voice_command'),
        
        # Document Intelligence & OCR  
        path('agent/ai/analyze-document/', analyze_document, name='ai_analyze_document'),
        
        # Multilingual Supplier Communication
        path('agent/ai/multilingual-alert/', send_multilingual_alert, name='ai_multilingual_alert'),
        
        # Predictive Analytics
        path('agent/ai/predictive-analytics/', generate_predictive_report, name='ai_predictive_analytics'),
        
        # Smart Document Generation
        path('agent/ai/generate-document/', generate_smart_document, name='ai_generate_document'),
        
        # Intelligent Workflow Creation
        path('agent/ai/create-workflow/', create_intelligent_workflow, name='ai_create_workflow'),
        
        # Enhanced Agent Status with AI Features
        path('agent/ai/enhanced-status/', get_enhanced_agent_status, name='ai_enhanced_status'),
    ]
    
    # Add AI endpoints to main urlpatterns
    urlpatterns.extend(ai_urlpatterns)

# ===================== ENHANCED COMPOSIO AUTOMATION =====================
# Add Composio endpoints for cross-platform automation
if COMPOSIO_FEATURES_AVAILABLE:
    composio_urlpatterns = [
        # Cross-Platform Workflow Automation
        path('agent/composio/create-workflow/', create_cross_platform_workflow, name='composio_create_workflow'),
        
        # Slack Integration
        path('agent/composio/slack-notify/', send_slack_notification, name='composio_slack_notify'),
        
        # Asana Task Management
        path('agent/composio/asana-task/', create_asana_task, name='composio_asana_task'),
        
        # Gmail Notifications
        path('agent/composio/gmail-send/', send_email_notification, name='composio_email_notify'),
        
        # Google Sheets Tracking
        path('agent/composio/sheets-update/', update_tracking_sheet, name='composio_update_sheet'),
        
        # Calendar Scheduling
        path('agent/composio/calendar-event/', schedule_meeting, name='composio_schedule_meeting'),
        
        # GitHub Issue Tracking
        path('agent/composio/github-issue/', create_github_issue, name='composio_github_issue'),
        
        # Composio Status and Integration Info
        path('agent/composio/status/', get_composio_status, name='composio_status'),
        
        # ========= EXTENDED INTEGRATIONS =========
        # Get All Connected Integrations
        path('agent/composio/integrations/', get_connected_integrations, name='composio_integrations'),
        
        # Trello Integration
        path('agent/composio/trello-card/', create_trello_card, name='composio_trello_card'),
        
        # Discord Integration
        path('agent/composio/discord-message/', send_discord_message, name='composio_discord_message'),
        
        # Microsoft Teams Integration
        path('agent/composio/teams-message/', send_teams_message, name='composio_teams_message'),
        
        # Notion Integration
        path('agent/composio/notion-page/', create_notion_page, name='composio_notion_page'),
        
        # Google Drive Integration
        path('agent/composio/drive-upload/', upload_to_google_drive, name='composio_drive_upload'),
        
        # Telegram Integration
        path('agent/composio/telegram-message/', send_telegram_message, name='composio_telegram_message'),
        
        # Integration Statistics
        path('agent/composio/stats/', get_integration_stats, name='composio_stats'),
    ]
    
    # Add Composio endpoints to main urlpatterns
    urlpatterns.extend(composio_urlpatterns)

# Integration Management Endpoints
try:
    from .integration_views import (
        IntegrationConfigViewSet,
        get_integration_logs,
        get_available_integrations
    )
    from rest_framework.routers import DefaultRouter
    
    # Create router for ViewSet
    integration_router = DefaultRouter()
    integration_router.register(r'integrations/config', IntegrationConfigViewSet, basename='integration-config')
    
    integration_urlpatterns = [
        # Integration Management
        path('integrations/available/', get_available_integrations, name='available_integrations'),
        path('integrations/logs/', get_integration_logs, name='integration_logs'),
    ]
    
    # Add integration endpoints to main urlpatterns
    urlpatterns.extend(integration_urlpatterns)
    urlpatterns.extend(integration_router.urls)

except ImportError as e:
    print(f"⚠️ Integration views not loaded: {str(e)}")

# ✅ Support API requests with format suffixes (e.g., /orders.json, /orders.xml)
#urlpatterns = format_suffix_patterns(urlpatterns, allowed=["json", "html"])


