# FastAir ERP System ✈️

A comprehensive, production-ready airline management system built with modern microservices architecture. FastAir ERP provides complete airline operations management including flight booking, check-in, boarding, and staff management with role-based access control.

## 🚀 Overview

FastAir ERP System is a full-stack airline management solution that demonstrates enterprise-grade architecture patterns and best practices. The system consists of multiple microservices, each responsible for specific business domains, all orchestrated through Docker Compose.

### Key Highlights

- **Dual Frontend Applications**: Separate React apps for customers and staff
- **Microservices Architecture**: Independent FastAPI services for users and staff management
- **Asynchronous Processing**: Celery workers for notifications and background tasks
- **Payment Integration**: Stripe payment processing with webhooks
- **Real-time Operations**: Live seat selection, check-in, and boarding processes
- **Enterprise Security**: JWT authentication with refresh tokens and role-based access

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend Layer                        │
├──────────────────────────┬──────────────────────────────────┤
│    Customer Portal       │        Staff Portal              │
│    (React + Vite)        │        (React + Vite)            │
└──────────────────────────┴──────────────────────────────────┘
                │                            │
                ▼                            ▼
┌─────────────────────────────────────────────────────────────┐
│                         API Gateway                          │
└─────────────────────────────────────────────────────────────┘
                │                            │
┌───────────────┴────────────┬───────────────┴────────────────┐
│     Users Service          │        Staff Service            │
│     (FastAPI)              │        (FastAPI)               │
│  • Authentication          │   • Staff Management           │
│  • Flight Booking          │   • Flight Operations          │
│  • Payment Processing      │   • Check-in & Boarding        │
└────────────────────────────┴──────────────────────────────┘
                │                            │
┌───────────────┴────────────────────────────┴────────────────┐
│              Notification Service (Celery)                   │
│         • Email notifications                                │
│         • Ticket generation with QR codes                    │
│         • Staff synchronization                              │
└──────────────────────────────────────────────────────────────┘
                │                            │
┌───────────────┴────────────┬───────────────┴────────────────┐
│     PostgreSQL (Users)     │     PostgreSQL (Staff)         │
└────────────────────────────┴──────────────────────────────┘
```

## 🌟 Features

### Customer Portal
- **Flight Management**
  - Browse available flights with advanced filtering
  - Real-time seat availability
  - Interactive seat selection
  - Multi-segment flight booking
  
- **Booking System**
  - Shopping cart functionality
  - Guest and registered user checkout
  - Passenger information management
  - Special service requests
  
- **Payment Processing**
  - Secure Stripe integration
  - Payment intent workflow
  - Automatic webhook handling
  - Payment confirmation and receipts
  
- **User Dashboard**
  - Booking history
  - Upcoming flights
  - Digital tickets with QR codes
  - Profile management

### Staff Portal
- **Role-Based Access Control**
  - **Supervisor**: Complete system administration
    - Flight CRUD operations
    - Revenue analytics
    - Staff management
    - System configuration
    
  - **Check-in Manager**: Ground operations
    - Passenger check-in
    - Baggage management
    - Seat reassignment
    - Special service handling
    
  - **Gate Manager**: Boarding operations
    - Boarding pass scanning
    - Passenger verification
    - Flight status updates
    - Gate management

- **Operational Features**
  - Real-time flight status management
  - Passenger manifest handling
  - Revenue reporting and analytics
  - Staff scheduling and assignments

### Platform Features
- **Security**
  - JWT authentication with access/refresh tokens
  - HTTP-only secure cookies
  - Role-based authorization
  - API rate limiting
  
- **Integration**
  - Stripe payment processing
  - Email notifications via SMTP
  - QR code generation for tickets
  - Webhook event processing
  
- **Performance**
  - Asynchronous request handling
  - Database connection pooling
  - Redis caching (optional)
  - Optimized ORM queries

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **SQLAlchemy** - ORM with async support
- **Alembic** - Database migrations
- **Celery** - Distributed task queue
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Stripe API** - Payment processing

### Frontend
- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS framework
- **React Hook Form** - Form management
- **React Query** - Server state management
- **AntDesign** - UI components

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **PostgreSQL** - Primary database
- **Redis** - Caching and session storage (optional)
- **Nginx** - Reverse proxy (production)

## 📋 Prerequisites

- Docker & Docker Compose (v2.0+)
- Node.js 18+ and npm/yarn (for local frontend development)
- Python 3.11+ (for local backend development)
- Stripe CLI (for payment testing)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/FunkyDrama/FastAirERPSystem.git
cd FastAirERPSystem
```

### 2. Environment Setup

Create `.env` files for each service:

**services/users_service/.env**
```env
# Database
POSTGRES_USER=fastair
POSTGRES_PASSWORD=fastair
POSTGRES_DB=fastair_users
POSTGRES_HOST=users_db
POSTGRES_PORT=5432

# JWT
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_FROM=FastAir <noreply@fastair.com>
EMAIL_USE_TLS=true

# Redis (optional)
REDIS_URL=redis://redis:6379/0
```

**services/staff_service/.env**
```env
# Database
POSTGRES_USER=fastair
POSTGRES_PASSWORD=fastair
POSTGRES_DB=fastair_staff
POSTGRES_HOST=staff_db
POSTGRES_PORT=5432

# JWT (same as users service for SSO)
JWT_SECRET=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
```

### 3. Start Services

```bash
# Development mode with hot reload
docker compose --profile dev up

# Production mode
docker compose --profile prod up
```

### 4. Database Setup

```bash
# Run migrations for users service
docker compose --profile dev run --rm users-dev \
  alembic -c services/users_service/app/alembic.ini upgrade head

# Run migrations for staff service  
docker compose --profile dev run --rm staff-dev \
  alembic -c services/staff_service/app/alembic.ini upgrade head

# Seed sample data
docker compose run --rm users-dev \
  python -m scripts.cli seed --db users --flush --flights 60 --days 14
```

### 5. Stripe Webhook Setup (for payments)

```bash
# In a separate terminal
stripe listen --forward-to http://localhost:8001/api/v1/payments/stripe/webhook

# Note the webhook signing secret and update your .env file
```

### 6. Access the Applications

- **Customer Portal**: http://localhost:5173
- **Staff Portal**: http://localhost:5174
- **Users API Docs**: http://localhost:8001/docs
- **Staff API Docs**: http://localhost:8003/docs

## 📖 API Documentation

### Authentication Flow

```javascript
// 1. Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

// Response
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "CUSTOMER"
  }
}

// 2. Use access token in headers
Authorization: Bearer eyJ...

// 3. Refresh token when expired
POST /api/v1/auth/refresh
{
  "refresh_token": "eyJ..."
}
```

### Key Endpoints

#### Users Service
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `GET /api/v1/flights` - List available flights
- `GET /api/v1/flights/{id}` - Flight details
- `POST /api/v1/bookings` - Create booking
- `GET /api/v1/bookings/{id}` - Booking details
- `POST /api/v1/payments/create-intent` - Initialize payment
- `POST /api/v1/payments/stripe/webhook` - Stripe webhook handler

#### Staff Service
- `POST /api/v1/staff/auth/login` - Staff login
- `GET /api/v1/staff/flights` - Manage flights (Supervisor)
- `POST /api/v1/staff/flights` - Create flight (Supervisor)
- `GET /api/v1/staff/checkin/passengers` - Check-in list
- `POST /api/v1/staff/checkin/{booking_id}` - Check in passenger
- `POST /api/v1/staff/boarding/{booking_id}` - Board passenger
- `GET /api/v1/staff/analytics/revenue` - Revenue reports (Supervisor)


## 📦 Deployment

### Production Deployment with Docker

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Run with production configuration
docker compose -f docker-compose.prod.yml up -d

# Scale services
docker compose -f docker-compose.prod.yml up -d --scale users-worker=3
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmaps/
kubectl apply -f k8s/secrets/
kubectl apply -f k8s/deployments/
kubectl apply -f k8s/services/
kubectl apply -f k8s/ingress.yaml
```

### Environment Variables for Production

Ensure all sensitive values are properly configured:
- Use strong JWT secrets
- Configure production database credentials
- Set up production Stripe keys
- Configure email service for production
- Enable HTTPS/TLS
- Set proper CORS origins

## 🛠️ Development

### Local Development Setup

```bash
# Backend development
cd services/users_service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd frontend/customer
npm install
npm run dev
```

### Code Style and Linting

```bash
# Python (Black, Flake8, MyPy)
black services/
flake8 services/
mypy services/

# JavaScript/React (ESLint, Prettier)
npm run lint
npm run format
```

### Database Migrations

```bash
# Create new migration
docker compose run --rm users-dev \
  alembic -c services/users_service/app/alembic.ini revision --autogenerate -m "Description"

# Apply migrations
docker compose run --rm users-dev \
  alembic -c services/users_service/app/alembic.ini upgrade head

# Rollback
docker compose run --rm users-dev \
  alembic -c services/users_service/app/alembic.ini downgrade -1
```

## 🐛 Troubleshooting

### Common Issues

1. **401 Unauthorized after container restart**
   - Cause: Refresh tokens stored in memory are lost
   - Solution: Use persistent Redis with volume mounting

2. **Stripe webhook failures**
   - Ensure webhook secret is correctly configured
   - Check Stripe CLI is running and forwarding to correct URL

3. **Database connection errors**
   - Verify PostgreSQL containers are running
   - Check database credentials in `.env` files
   - Ensure migrations have been applied

### Logs and Debugging

```bash
# View logs for specific service
docker compose logs -f users-service

# Access container shell
docker compose exec users-service /bin/bash

# Database console
docker compose exec users_db psql -U fastair -d fastair_users
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Update documentation
- Follow existing code style
- Add type hints (Python)
- Use conventional commits

## 🙏 Acknowledgments

- FastAPI community for the excellent framework
- Stripe for payment processing capabilities
- Docker for containerization tools
- All open-source contributors

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub Issues](https://github.com/FunkyDrama/FastAirERPSystem/issues)

## 🚦 Project Status

**Current Version**: 1.0.0 (Production Ready)
