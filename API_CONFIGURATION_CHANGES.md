# API Configuration Changes - Local Development Setup

## Summary
Updated the frontend to use localhost API endpoints for local development instead of the production Railway URL.

## Changes Made

### 1. Environment Configuration
**File:** `Vendor-frontend/.env.local` (NEW)
- Created environment file with `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api`
- This allows easy switching between local and production environments

### 2. Authentication Utilities
**File:** `Vendor-frontend/utils/auth_fn.ts`
- **Before:** `const API_URL = "https://vendor-backendproduction.up.railway.app/api";`
- **After:** `const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";`
- Now reads from environment variable with localhost as fallback

### 3. Retailer Data Functions
**File:** `Vendor-frontend/components/retailer/data/mockData.ts`
- Added import: `import { API_URL } from "@/utils/auth_fn";`
- Updated `fetchStockFromAPI()`: Changed from `"http://127.0.0.1:8000/api/stock/"` to `${API_URL}/stock/`
- Updated `fetchOrdersFromAPI()`: Changed from `"http://127.0.0.1:8000/api/orders/"` to `${API_URL}/orders/`

### 4. Employee Order Details
**File:** `Vendor-frontend/components/employee/OrderDetails.tsx`
- Added import: `import { API_URL } from "@/utils/auth_fn";`
- Updated `fetchOrdersWithToken()`: Changed to use `${API_URL}/employee_orders/`
- Updated `refreshAccessToken()`: Changed to use `${API_URL}/token/refresh/`

### 5. Configuration Page
**File:** `Vendor-frontend/app/manufacturer/configuration/page.tsx`
- Added import: `import { API_URL } from "@/utils/auth_fn";`
- Updated Odoo credentials endpoint: Changed to use `${API_URL}/odoo/save-credentials/`

## User Groups Setup

### Database Groups Created
Created three user groups in the PostgreSQL database:
1. **Manufacturer** - Company owners/manufacturers who manage products and orders
2. **Retailer** - Retailers who can browse products and place orders
3. **Employee** - Company employees who can manage orders and deliveries

### Management Command
**File:** `Vendor-backend/app/management/commands/setup_groups.py` (NEW)
- Created Django management command to set up default groups
- Run with: `python manage.py setup_groups`

### API Verification
- Groups API endpoint: `http://127.0.0.1:8000/api/groups/`
- Returns: `{"groups":["Manufacturer","Retailer","Employee"]}`
- Signup page now displays all three groups in the dropdown

## How to Use

### For Local Development
1. The `.env.local` file is already configured for localhost
2. Both frontend and backend are running on local ports
3. All API requests will go to `http://127.0.0.1:8000/api`

### For Production Deployment
Edit `.env.local` (or create `.env.production`):
```
NEXT_PUBLIC_API_URL=https://vendor-backendproduction.up.railway.app/api
```

## Current Running Services
- **Backend:** http://127.0.0.1:8000/
- **Frontend:** http://localhost:3000/
- **Cloud SQL Proxy:** Port 5433 (connecting to Google Cloud SQL)
- **Database:** PostgreSQL on Google Cloud SQL

## Testing
The signup page should now display three groups:
- Manufacturer
- Retailer
- Employee

Users can select their role during registration.
