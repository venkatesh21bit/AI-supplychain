# 🤖 LOGI-BOT: Autonomous AI Supply Chain Management System

<div align="center">

![LOGI-BOT Logo](frontend/public/logo.png)

**An intelligent, self-healing supply chain management system powered by AI and cross-platform automation**

[![Django](https://img.shields.io/badge/Django-5.1.6-green.svg)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![Composio](https://img.shields.io/badge/Composio-12%20Integrations-blue.svg)](https://composio.dev/)
[![Google Cloud AI](https://img.shields.io/badge/Google%20Cloud-AI%20Enabled-yellow.svg)](https://cloud.google.com/)

[Features](#-key-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Demo](#-demo-instructions) • [API Docs](#-api-documentation)

</div>

---

## 🎯 Problem Statement

Traditional supply chain management systems are **reactive**, requiring manual intervention for:
- ❌ Stock level monitoring and reordering decisions
- ❌ Multi-platform communication (emails, Slack, task managers)
- ❌ Language barriers with international suppliers
- ❌ Document processing and data entry
- ❌ Predictive analytics and forecasting

**Manual processes lead to**: Delayed responses, stockouts, excess inventory, miscommunication, and human errors.

## 💡 Our Solution: LOGI-BOT

**LOGI-BOT** is an **autonomous AI agent** that:

✅ **Proactively detects** low stock levels using demand-based algorithms  
✅ **Automatically executes** multi-platform workflows (Gmail, Slack, Asana, Sheets, etc.)  
✅ **Communicates** in 100+ languages with international suppliers  
✅ **Processes** documents using OCR and NLP  
✅ **Predicts** future stock needs using Google Cloud AI  
✅ **Self-heals** by creating tasks, sending alerts, and logging actions

### 🌟 Why It's Innovative

1. **Autonomous Agent Architecture**: Unlike traditional systems, LOGI-BOT makes decisions and takes actions without human intervention
2. **Cross-Platform Automation**: One trigger → 5 essential platforms (Gmail, Slack, Google Sheets, Calendar, Drive)
3. **AI-Powered Intelligence**: 7 Google Cloud AI features for translation, OCR, speech, NLP, and predictive analytics
4. **Composio Tool Router**: Seamless integration with 881+ business tools via a single API
5. **Real-Time Reactivity**: WebSocket-based notifications and instant workflow triggers
6. **Demand-Based Logic**: Smart algorithms that consider actual demand vs. available stock

---

## 🚀 Key Features

### 🔄 Autonomous Agent System
- **Self-Triggering**: Automatically monitors inventory every 5 seconds
- **Demand-Based Alerts**: Triggers workflows when `available_quantity < total_required_quantity`
- **Batch Processing**: Handles multiple low-stock items simultaneously
- **Execution Tracking**: Complete audit trail of all agent actions

### 🤖 Advanced AI Capabilities
Powered by **Google Cloud AI** (Project ID: `leadership-board-api`):

1. **🌐 Multilingual Translation** - Communicate with suppliers in 100+ languages
2. **👁️ Document Intelligence** - OCR for invoices, receipts, shipping documents
3. **🎤 Voice Commands** - Speech-to-text for hands-free operation
4. **🔊 Text-to-Speech** - Audio alerts and notifications
5. **📊 Natural Language Processing** - Sentiment analysis and entity extraction
6. **📈 Predictive Analytics** - Forecast future stock needs using time-series analysis
7. **📄 Smart Document Generation** - Auto-generate reports and summaries

### ⚡ 5 Essential Composio Integrations
**API Key**: `ak_Ez3L56MGyzV0TIuKcfLY`

| Platform | Use Case | Status |
|----------|----------|--------|
| **Gmail** 📧 | Automated stock alert emails | ✅ **Configured** (Entity: ac_8xS2FGOG-DAD) |
| **Slack** 💬 | Real-time team notifications | 🔌 Connect at [app.composio.dev](https://app.composio.dev) |
| **Google Sheets** 📊 | Inventory data logging | ✅ **Configured** ([View Sheet](https://docs.google.com/spreadsheets/d/1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw/edit)) |
| **Google Calendar** 📅 | Supplier meeting scheduling | 🔌 Connect at [app.composio.dev](https://app.composio.dev) |
| **Google Drive** 💾 | Document & report storage | ✅ **Configured** |

**Note**: Email notifications for password reset/invitations use Django's SMTP (venkatesh.k21062005@gmail.com), while LOGI-BOT stock alerts use Composio Gmail integration.

### 📊 Real-Time Dashboard Features
- **Stock Count Management**: Visual charts, heatmaps, and inventory analytics
- **LOGI-BOT Dashboard**: Live agent status, execution history, animated workflows
- **AI Features Dashboard**: Test all 7 AI capabilities with interactive UI
- **Composio Integrations**: Manage and test all 12 platform integrations
- **Accounting System**: Invoices, bills, customer/vendor management

---

## � How Integrations Work

### **Email System (Two Methods)**

**1. Django SMTP Email** (For User Management)
- **Account**: venkatesh.k21062005@gmail.com  
- **Uses**: Password reset, company invitations, OTP verification
- **Method**: Direct SMTP connection to Gmail servers
- **Config**: `EMAIL_HOST_USER` + `EMAIL_HOST_PASSWORD` in `.env`

**2. Composio Gmail** (For Automated Alerts)
- **Entity ID**: ac_8xS2FGOG-DAD (OAuth authenticated)
- **Uses**: LOGI-BOT stock alerts, supplier notifications
- **Method**: Composio Tool Router API with OAuth
- **Config**: `COMPOSIO_GMAIL_ENTITY_ID` in `.env`
- **Advantage**: Part of multi-platform workflows (email + Slack + Sheets simultaneously)

### **Google Sheets Integration**

📊 **Live Sheet**: [View Inventory Log](https://docs.google.com/spreadsheets/d/1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw/edit)

- **Purpose**: Auto-logs all stock alerts with timestamps
- **Columns**: Product Name, Current Stock, Required Stock, Alert Time, Status
- **Updates**: Real-time when LOGI-BOT detects low stock
- **Access**: Shared with service account email from Google Cloud

### **Google Drive Purpose**

💾 **Use Cases**:
1. Store generated invoices (PDF exports)
2. Upload stock reports for record-keeping
3. Archive supplier documents
4. Backup system data
5. Share documents with external suppliers

### **Google Calendar Recommendations**

📅 **Suggested Automations**:
1. **Auto-schedule restock meetings** when critical stock detected
2. **Create recurring inventory audit reminders** (weekly/monthly)
3. **Schedule supplier review calls** based on order history
4. **Meeting invites** for cross-functional supply chain team

**To Connect**: Visit [app.composio.dev](https://app.composio.dev) → Connect Calendar → Set event triggers

### **Slack Integration (Recommended)**

💬 **Why Connect Slack**:
- Instant notifications to #supply-chain channel
- @mention managers for critical alerts
- Real-time team collaboration
- Mobile push notifications

**Setup**: Visit [app.composio.dev](https://app.composio.dev) → Connect Slack workspace → Set channel preferences

---

## �🛠️ Technology Stack

### Backend
- **Django 5.1.6** + Django REST Framework
- **SQLite** (development) / **PostgreSQL** (production-ready)
- **Google Cloud AI** APIs (Translation, Vision, Speech, NLP)
- **Composio SDK** for cross-platform automation
- **JWT Authentication** for secure API access

### Frontend
- **Next.js 15** with App Router
- **React 18** with TypeScript
- **Tailwind CSS** for responsive dark theme UI
- **Recharts** for data visualization
- **Real-time WebSocket** updates

### AI & Automation
- **Google Cloud AI Platform** (7 services)
- **Composio Tool Router** (881+ app integrations)
- **Custom LOGI-BOT Agent** (autonomous decision engine)

---

## 📋 Prerequisites

Before starting, ensure you have:

- **Node.js** 18+ and npm/pnpm
- **Python** 3.12+
- **Git** for version control

### Required Credentials

#### 1. Google Cloud AI (Required for AI features)
- **Project ID**: `leadership-board-api`
- **API Key**: `AIzaSyA7M0xjkhp866TznL1y7H8gnh1GvynW1F8`
- [Get Google Cloud API Key](https://console.cloud.google.com/apis/credentials)

#### 2. Composio (Required for integrations)
- **API Key**: `ak_Ez3L56MGyzV0TIuKcfLY`
- **Gmail Entity ID**: `ac_8xS2FGOG-DAD` (pre-configured)
- [Get Composio API Key](https://app.composio.dev/settings/api-keys)

#### 3. Google Sheets (Optional - for data logging)
- **Sheet ID**: `1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw`
- [Create Google Sheet](https://sheets.google.com/)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/venkatesh21bit/AI-supplychain.git
cd AI-supplychain
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows:
.\env\Scripts\activate
# On macOS/Linux:
source env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Create .env file with the following:
```

**backend/.env**:
```env
# Database
DATABASE_URL=sqlite:///./db.sqlite3

# Composio API
COMPOSIO_API_KEY=ak_Ez3L56MGyzV0TIuKcfLY
COMPOSIO_GMAIL_ENTITY_ID=ac_8xS2FGOG-DAD

# Google Cloud AI
GOOGLE_CLOUD_API_KEY=AIzaSyA7M0xjkhp866TznL1y7H8gnh1GvynW1F8
GOOGLE_CLOUD_PROJECT_ID=leadership-board-api

# Google Sheets (Optional)
GOOGLE_SHEET_ID=1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw

# Email (Optional - for password reset)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

```bash
# Run database migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Load sample data (optional)
python setup_test_data.py

# Start Django development server
python manage.py runserver
```

Backend will run at: **http://127.0.0.1:8000/**

### 3. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```

Frontend will run at: **http://localhost:3000/**

### 4. Access the Application

- **Frontend**: http://localhost:3000/
- **Backend API**: http://127.0.0.1:8000/api/
- **Django Admin**: http://127.0.0.1:8000/admin/

**Default Test Credentials**:
- Email: `manufacturer@example.com`
- Password: `password123`

---

## 🎭 Demo Instructions (For Testers & Judges)

### A. Testing LOGI-BOT Autonomous Agent

1. **Navigate to LOGI-BOT Dashboard**:
   - Login → Click "LOGI-BOT" in navigation
   - View: Real-time agent status, execution history

2. **Trigger Stock Alert Workflow**:
   ```bash
   # Option 1: Via API
   POST http://127.0.0.1:8000/api/agent/check-all-inventory/
   Authorization: Bearer YOUR_JWT_TOKEN
   
   # Option 2: Via Frontend
   Go to Stock Count → Adjust quantities below demand
   Wait 5 seconds → LOGI-BOT auto-detects and triggers workflow
   ```

3. **Observe Autonomous Actions**:
   - ✅ Alert created in database
   - ✅ Workflow execution logged
   - ✅ Real-time notifications displayed
   - ✅ Status updates in dashboard

### B. Testing AI Features

1. **Navigate to AI Features Dashboard**:
   - Click "🤖 AI Features" in navigation

2. **Test Each Feature**:
   - **Translation**: Enter English text → Get Spanish/French/Chinese translation
   - **Document Analysis**: Upload invoice → Extract text and entities
   - **Voice Command**: Record speech → Convert to text command
   - **Predictive Analytics**: Generate stock forecast reports
   - **Smart Documents**: Auto-generate summary reports

3. **API Key Already Configured**: All AI features work out of the box!

### C. Testing Composio Integrations

1. **Navigate to Integrations Dashboard**:
   - Click "⚡ Integrations" in navigation

2. **View Integration Status**:
   - See 5 essential platforms optimized for supply chain management
   - Pre-configured: Gmail (email alerts), Sheets (data logging), Drive (document storage)

3. **Test Gmail Integration** (Pre-configured):
   ```javascript
   // Fill form:
   To: your-email@example.com
   Subject: "Test from LOGI-BOT"
   Body: "This is an automated test email"
   
   // Click "Send Email"
   // Check your email inbox!
   ```

4. **Connect Additional Platforms** (Optional):
   - Visit: https://app.composio.dev
   - Login with API key: `ak_Ez3L56MGyzV0TIuKcfLY`
   - Connect **Slack** for team notifications
   - Connect **Calendar** for automated meeting scheduling
   - Return to dashboard and test

### D. End-to-End Workflow Demo

**Scenario**: Steel Rods stock drops below demand threshold

1. **Setup**:
   - Go to Stock Count
   - Find "Steel Rods" product
   - Note current stock: 150, Demand: 500

2. **Trigger** (Automatic):
   - LOGI-BOT detects: `150 < 500`
   - Workflow triggers automatically

3. **Actions Executed**:
   - ✅ Alert created: "Low Stock: Steel Rods"
   - ✅ Email sent to manager
   - ✅ Data logged to Google Sheets
   - ✅ Execution record created

4. **Verify**:
   - Check LOGI-BOT dashboard for execution
   - Check email inbox for notification
   - Check Google Sheet for logged data
   - View AI-generated report

---

## 📚 API Documentation

### Core Endpoints

#### Authentication
```bash
# Login
POST /api/token/
{
  "email": "user@example.com",
  "password": "password"
}

# Refresh Token
POST /api/token/refresh/
{
  "refresh": "refresh_token_here"
}
```

#### LOGI-BOT Agent
```bash
# Trigger inventory check
POST /api/agent/check-inventory/

# Check all inventory (batch processing)
POST /api/agent/check-all-inventory/

# Get agent status
GET /api/agent/status/

# Get agent alerts
GET /api/agent/alerts/

# Get execution history
GET /api/agent/executions/
```

#### AI Features (7 Endpoints)
```bash
# Multilingual translation
POST /api/agent/ai/multilingual-alert/

# Document OCR analysis
POST /api/agent/ai/analyze-document/

# Voice command processing
POST /api/agent/ai/voice-command/

# Predictive analytics
POST /api/agent/ai/predictive-analytics/

# Smart document generation
POST /api/agent/ai/generate-document/

# Intelligent workflow creation
POST /api/agent/ai/create-workflow/

# Enhanced agent status
GET /api/agent/ai/enhanced-status/
```

#### Composio Integrations (16 Endpoints)
```bash
# Get integration stats
GET /api/agent/composio/stats/

# Get connected integrations
GET /api/agent/composio/integrations/

# Cross-platform workflow
POST /api/agent/composio/create-workflow/

# Gmail
POST /api/agent/composio/gmail-send/

# Slack
POST /api/agent/composio/slack-notify/

# Asana
POST /api/agent/composio/asana-task/

# Google Sheets
POST /api/agent/composio/sheets-update/

# Calendar
POST /api/agent/composio/calendar-event/

# GitHub
POST /api/agent/composio/github-issue/

# Trello
POST /api/agent/composio/trello-card/

# Discord
POST /api/agent/composio/discord-message/

# Teams
POST /api/agent/composio/teams-message/

# Notion
POST /api/agent/composio/notion-page/

# Google Drive
POST /api/agent/composio/drive-upload/

# Telegram
POST /api/agent/composio/telegram-message/

# Composio status
GET /api/agent/composio/status/
```

#### Inventory Management
```bash
# Get products
GET /api/products/

# Update product quantities
POST /api/update-product-quantities/

# Get categories
GET /api/categories/

# Category stock data
GET /api/category-stock/

# Get counts
GET /api/count/?company={company_id}
```

**Full API Documentation**: See `backend/logibot/API_DOCUMENTATION.md` for detailed specs.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Dashboard   │  │ AI Features  │  │ Integrations │      │
│  │   + Charts   │  │   + OCR      │  │   + Forms    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
│                     REST API / WebSocket                     │
└────────────────────────────┼────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                   BACKEND (Django)                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              LOGI-BOT Agent Core                      │   │
│  │  • Autonomous Monitoring (5s intervals)              │   │
│  │  • Demand-Based Logic (available < required)         │   │
│  │  • Batch Processing (all low-stock items)            │   │
│  │  • Execution Tracking & Audit Trail                  │   │
│  └───────┬──────────────────────────────────┬───────────┘   │
│          │                                   │               │
│  ┌───────▼────────┐                 ┌───────▼────────┐      │
│  │   AI Engine    │                 │   Composio      │      │
│  │  (Google Cloud)│                 │  Tool Router    │      │
│  │ • Translation  │                 │ • 12 Platforms  │      │
│  │ • Vision OCR   │                 │ • 881+ Apps     │      │
│  │ • Speech       │                 │ • Workflows     │      │
│  │ • NLP          │                 │                 │      │
│  │ • Predictive   │                 │                 │      │
│  └────────────────┘                 └─────────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Database (SQLite/PostgreSQL)            │   │
│  │  • Products • Orders • Alerts • Executions           │   │
│  │  • Companies • Users • Invoices • Shipments          │   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   External Integrations       │
              │  • Gmail    • Slack    • Asana│
              │  • Sheets   • Calendar • GitHub│
              │  • Trello   • Discord  • Teams │
              │  • Notion   • Drive    • Telegram│
              └──────────────────────────────┘
```

---

## 🔧 Configuration Guide

### Connecting Additional Composio Tools

1. **Visit Composio Dashboard**:
   ```
   https://app.composio.dev
   ```

2. **Login/Sign Up** using API key: `ak_Ez3L56MGyzV0TIuKcfLY`

3. **Connect Desired Platforms**:
   - Click "Add Integration"
   - Select platform (Slack, Asana, Trello, etc.)
   - Authorize the app
   - Copy the Connection/Entity ID

4. **Update Environment Variable** (if needed):
   ```env
   # Example for Slack
   COMPOSIO_SLACK_ENTITY_ID=your_slack_entity_id
   ```

5. **Test Integration**:
   - Go to http://localhost:3000/manufacturer/composio-integrations
   - Select the platform
   - Fill the form and submit

### Google Cloud AI Setup (If Using Your Own Credentials)

1. **Create Google Cloud Project**:
   - Visit: https://console.cloud.google.com/
   - Create new project

2. **Enable APIs**:
   - Translation API
   - Cloud Vision API
   - Speech-to-Text API
   - Text-to-Speech API
   - Natural Language API

3. **Create API Key**:
   - APIs & Services → Credentials → Create Credentials → API Key

4. **Update .env**:
   ```env
   GOOGLE_CLOUD_API_KEY=your_new_api_key
   GOOGLE_CLOUD_PROJECT_ID=your_project_id
   ```

---

## 📁 Project Structure

```
latest-vendor/
├── backend/                     # Django backend
│   ├── app/                     # Main application
│   │   ├── models.py           # Database models
│   │   ├── views.py            # API endpoints
│   │   ├── serializers.py      # DRF serializers
│   │   ├── ai_views.py         # AI feature endpoints
│   │   ├── composio_views.py   # Composio integrations (core)
│   │   ├── composio_extended_views.py  # Extended integrations
│   │   ├── agent_views.py      # LOGI-BOT agent endpoints
│   │   ├── signals.py          # Auto-trigger signals
│   │   └── urls.py             # URL routing
│   ├── logibot/                # LOGI-BOT agent core
│   │   ├── agent.py            # Main agent logic
│   │   ├── analyzer.py         # Demand analysis
│   │   ├── advanced_features.py  # AI features
│   │   ├── composio_rest_orchestrator.py  # Composio client
│   │   └── enhanced_composio_orchestrator.py
│   ├── main/                   # Django settings
│   ├── manage.py               # Django CLI
│   ├── requirements.txt        # Python dependencies
│   └── db.sqlite3             # SQLite database
│
├── frontend/                   # Next.js frontend
│   ├── app/                    # App router pages
│   │   ├── manufacturer/       # Manufacturer dashboard
│   │   │   ├── page.tsx       # Main dashboard
│   │   │   ├── logibot-dashboard/  # LOGI-BOT UI
│   │   │   ├── ai-features/   # AI features UI
│   │   │   ├── composio-integrations/  # Integrations UI
│   │   │   ├── stockCount/    # Inventory management
│   │   │   └── accounting/    # Accounting system
│   │   ├── retailer/          # Retailer dashboard
│   │   └── authentication/    # Login/signup
│   ├── components/            # React components
│   │   ├── manufacturer/
│   │   │   ├── nav_bar.tsx
│   │   │   ├── ai-features-dashboard.tsx
│   │   │   ├── composio-integrations-dashboard.tsx
│   │   │   ├── animated-workflow.tsx
│   │   │   ├── real-time-notifications.tsx
│   │   │   └── stockcount/    # Stock management components
│   │   └── ui/                # Shadcn UI components
│   ├── package.json           # Node dependencies
│   └── tsconfig.json          # TypeScript config
│
├── COMPOSIO_INTEGRATIONS_GUIDE.md  # Detailed integration docs
└── README.md                  # This file
```

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
python manage.py test

# Test specific features
python test_ai_features.py
python test_composio_api.py
python test_agent_workflow.py
```

### Run Frontend (Manual Testing)
```bash
cd frontend
npm run dev

# Access test pages:
# - http://localhost:3000/manufacturer/logibot-dashboard
# - http://localhost:3000/manufacturer/ai-features
# - http://localhost:3000/manufacturer/composio-integrations
```

### Sample Test Scenarios

**Test 1: Low Stock Alert**
1. Set product stock below demand
2. Wait 5 seconds
3. Verify alert created
4. Check email received
5. View execution in LOGI-BOT dashboard

**Test 2: AI Translation**
1. Navigate to AI Features
2. Enter: "Stock alert: 150 units remaining"
3. Translate to Spanish
4. Verify: "Alerta de stock: quedan 150 unidades"

**Test 3: Composio Gmail**
1. Navigate to Integrations
2. Select Gmail
3. Fill form with test email
4. Submit and check inbox

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Project**: AI Supply Chain Management System  
**Organization**: Amrita Vishwa Vidyapeetham  
**Repository**: https://github.com/venkatesh21bit/AI-supplychain  
**Contact**: venkatesh.k21062005@gmail.com

---

## 🙏 Acknowledgments

- **Composio** - For the amazing Tool Router platform
- **Google Cloud** - For powerful AI APIs
- **Django & Next.js** - For robust frameworks
- **Shadcn/ui** - For beautiful UI components

---

## 📞 Support

For issues, questions, or demo requests:
- 📧 Email: venkatesh.k21062005@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/venkatesh21bit/AI-supplychain/issues)
- 📚 Documentation: See `COMPOSIO_INTEGRATIONS_GUIDE.md`

---

<div align="center">

**⭐ If you find this project useful, please star the repository! ⭐**

Made with ❤️ by the AI Supply Chain Team

</div>
