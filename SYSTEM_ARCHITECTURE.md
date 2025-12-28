# World Coder - System Architecture

> **Last Updated**: 2025-12-28
> **Version**: 1.0

---

## 1. System Overview

```
                                    +------------------+
                                    |   Cloudflare     |
                                    |     Pages        |
                                    +--------+---------+
                                             |
        +------------------------------------+------------------------------------+
        |                                    |                                    |
+-------v-------+                   +--------v--------+                  +--------v--------+
|  tg_admin_web |                   |   tg_kds_web    |                  |   tg_web_pos    |
| (Admin Panel) |                   | (Kitchen Display)|                 |   (Web POS)     |
+-------+-------+                   +--------+--------+                  +--------+--------+
        |                                    |                                    |
        +------------------------------------+------------------------------------+
                                             |
                                    +--------v--------+
                                    |   API Gateway   |
                                    | (AWS API GW)    |
                                    +--------+--------+
                                             |
                                    +--------v--------+
                                    |   AWS Lambda    |
                                    | (Python/FastAPI)|
                                    +--------+--------+
                                             |
                              +--------------+--------------+
                              |                             |
                     +--------v--------+           +--------v--------+
                     |   DynamoDB      |           |      S3         |
                     | (Main Database) |           | (Static Assets) |
                     +-----------------+           +-----------------+


              +------------------+
              |   tg_pos_app     |
              | (Flutter Mobile/ |
              |   Desktop App)   |
              +--------+---------+
                       |
                       v
              (Same API Gateway)
```

---

## 2. Component Details

### 2.1 Backend (AWS)

| Component | Service | Description |
|-----------|---------|-------------|
| **API Server** | AWS Lambda | Python FastAPI (Mangum adapter) |
| **Database** | DynamoDB | NoSQL, auto-scaling |
| **File Storage** | S3 | Images, static assets |
| **API Routing** | API Gateway | REST API endpoints |
| **Authentication** | Lambda + JWT | Custom JWT auth |

**Current Development**: `development/` folder (SQLite for local dev)

**Production Migration**:
- SQLAlchemy ORM → DynamoDB (boto3)
- SQLite → DynamoDB tables
- File uploads → S3 presigned URLs

### 2.2 Frontend Web (Cloudflare Pages)

| App | Folder | Domain (Example) | Description |
|-----|--------|------------------|-------------|
| **Admin Panel** | `tg_admin_web/` | admin.tgcommerce.io | Store management dashboard |
| **KDS** | `tg_kds_web/` | kds.tgcommerce.io | Kitchen display system |
| **Web POS** | `tg_web_pos/` | pos.tgcommerce.io | Browser-based POS |

**Deployment**: Cloudflare Pages (auto-deploy from Git)

**Features**:
- Static HTML + Vue.js/vanilla JS
- API calls to AWS Lambda backend
- Environment-based API_BASE configuration

### 2.3 Mobile/Desktop App (Flutter)

| App | Folder | Platforms | Description |
|-----|--------|-----------|-------------|
| **POS App** | `tg_pos_app/` | Android, iOS, Windows, macOS | Native POS application |

**Deployment**:
- Android: Google Play Store
- iOS: Apple App Store
- Windows/macOS: Direct download / Microsoft Store

---

## 3. API Endpoints (Production)

### Base URL
```
Production: https://api.tgcommerce.io/v1
Development: http://localhost:8001
```

### Endpoint Groups

| Prefix | Description | Auth Required |
|--------|-------------|---------------|
| `/auth` | Authentication | No (login) |
| `/products` | Product management | Yes |
| `/orders` | Order processing | Yes |
| `/inventory` | Stock management | Yes |
| `/stats` | Sales analytics | Yes |
| `/membership` | Loyalty program | Yes |
| `/store` | Store configuration | Yes |
| `/sync` | External integrations | Yes + HMAC |
| `/receipt` | Receipt generation | Yes |

---

## 4. Database Schema (DynamoDB)

### Tables

| Table | Partition Key | Sort Key | GSI |
|-------|--------------|----------|-----|
| `tg_stores` | store_id | - | - |
| `tg_users` | user_id | - | username-index |
| `tg_products` | store_id | product_id | category-index |
| `tg_orders` | store_id | order_id | status-index, date-index |
| `tg_payments` | order_id | payment_id | - |
| `tg_inventory` | store_id | item_id | - |
| `tg_members` | store_id | member_id | phone-index |

---

## 5. Environment Configuration

### Frontend (tg_*_web)

Each frontend folder contains `config.js`:

```javascript
// config.js
const CONFIG = {
    API_BASE: 'https://api.tgcommerce.io/v1',  // Production
    // API_BASE: 'http://localhost:8001',      // Development
};
```

### Backend (Lambda)

Environment variables in AWS Lambda:

| Variable | Description |
|----------|-------------|
| `DYNAMODB_TABLE_PREFIX` | Table name prefix (e.g., `prod_`) |
| `JWT_SECRET` | JWT signing key |
| `WEBHOOK_SECRET` | HMAC signature key |
| `S3_BUCKET` | Asset storage bucket |
| `TGMAIN_WEBHOOK_URL` | TgMain integration URL |

---

## 6. Deployment Pipeline

### Backend (AWS Lambda)

```bash
# Package and deploy
cd development
pip install -r requirements.txt -t package/
cp -r src package/
cd package && zip -r ../lambda.zip .
aws lambda update-function-code --function-name tg-commerce-api --zip-file fileb://lambda.zip
```

### Frontend (Cloudflare Pages)

```bash
# Auto-deploy on git push
git push origin main

# Or manual deploy
cd tg_admin_web
npx wrangler pages publish . --project-name=tg-admin
```

### Mobile App (Flutter)

```bash
# Android
flutter build apk --release

# iOS
flutter build ios --release

# Windows
flutter build windows --release
```

---

## 7. Security

| Layer | Implementation |
|-------|----------------|
| **Transport** | HTTPS only (Cloudflare SSL) |
| **Authentication** | JWT tokens (short-lived) |
| **Authorization** | Role-based (owner, admin, staff) |
| **API Protection** | Rate limiting (API Gateway) |
| **Webhook Security** | HMAC-SHA256 signatures |
| **Data Encryption** | DynamoDB encryption at rest |

---

## 8. Monitoring & Logging

| Component | Service |
|-----------|---------|
| **API Logs** | CloudWatch Logs |
| **Metrics** | CloudWatch Metrics |
| **Alerts** | CloudWatch Alarms |
| **Frontend Analytics** | Cloudflare Analytics |
| **Error Tracking** | (Recommended: Sentry) |

---

## 9. Cost Optimization

| Strategy | Description |
|----------|-------------|
| **Lambda** | Pay-per-request, auto-scaling |
| **DynamoDB** | On-demand capacity mode |
| **Cloudflare** | Free tier for Pages |
| **S3** | Lifecycle policies for old data |

---

## 10. Future Considerations

- [ ] Redis/ElastiCache for session caching
- [ ] CloudFront CDN for API caching
- [ ] Multi-region deployment
- [ ] WebSocket for real-time updates (IoT Hub)
- [ ] Cognito for federated auth
