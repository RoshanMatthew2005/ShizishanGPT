# 🔐 Authentication System - Quick Start Guide

## Overview
Complete authentication system with JWT tokens, role-based access control, and user management for ShizishanGPT.

## ✅ Installation Complete

All required components have been created and configured:
- ✅ Backend schemas, services, and routes
- ✅ Middleware proxy routes
- ✅ Frontend login, register, and admin pages
- ✅ JWT and bcrypt packages installed

## 🚀 Quick Start

### 1. Start Backend (FastAPI)
```bash
cd D:\Ps-3(git)\ShizishanGPT
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Middleware (Express)
```bash
cd middleware
npm start
```

### 3. Start Frontend (React)
```bash
cd frontend
npm start
```

### 4. Access the Application
Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **Login Page**: http://localhost:3000/login
- **Register Page**: http://localhost:3000/register

## 👤 Default Accounts

### Superadmin Account (Auto-created)
- **Email**: `admin@shizishangpt.com`
- **Password**: `Admin@123456`
- **Role**: Superadmin (full access)

### Create Your Account
1. Go to http://localhost:3000/register
2. Fill in the registration form
3. Click "Create Account"
4. You'll be redirected to the chat interface

## 🔑 Features

### User Authentication
- ✅ Secure registration with password validation
- ✅ Login with JWT token authentication
- ✅ Token stored in localStorage
- ✅ Auto-login on page refresh
- ✅ Logout functionality

### Password Requirements
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 digit
- Password strength indicator on registration

### Role-Based Access Control
- **User**: Default role, access to chat interface
- **Admin**: User management capabilities
- **Superadmin**: Full system access

### Admin Dashboard
Access: http://localhost:3000/admin (Admin/Superadmin only)

**Features:**
- 📊 User statistics (total, active, inactive, admins)
- 🔍 Search users by name, email, or role
- ✅ Activate/deactivate user accounts
- 🛡️ Grant/revoke admin privileges
- 🗑️ Delete users
- 👁️ View user details

**Admin Actions:**
- Activate/Deactivate users
- Grant admin role to users
- Revoke admin role from users
- Delete users (cannot delete self)

### User-Specific Features
- ✅ Chat history linked to user account
- ✅ Personal profile with name, email, location
- ✅ Account information modal
- ✅ Secure logout

## 📡 API Endpoints

### Public Endpoints
```
POST /api/auth/register     - Register new user
POST /api/auth/login        - Authenticate user
```

### Protected Endpoints (Require JWT Token)
```
GET  /api/auth/me           - Get current user info
PUT  /api/auth/me           - Update current user
```

### Admin Endpoints (Admin/Superadmin only)
```
GET    /api/auth/users              - Get all users
GET    /api/auth/users/{id}         - Get user by ID
POST   /api/auth/users/{id}/manage  - Manage user (activate, deactivate, grant_admin, revoke_admin)
DELETE /api/auth/users/{id}         - Delete user
```

## 🧪 Testing the System

### Test Registration
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "FarmerPass123",
    "full_name": "John Farmer",
    "phone": "+1234567890",
    "location": "Punjab, India"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "...",
    "email": "farmer@example.com",
    "full_name": "John Farmer",
    "role": "user",
    "is_active": true
  }
}
```

### Test Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "farmer@example.com",
    "password": "FarmerPass123"
  }'
```

### Test Protected Endpoint
```bash
# Replace YOUR_TOKEN with the access_token from login response
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Admin Endpoint (Superadmin)
```bash
# Login as superadmin first to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@shizishangpt.com",
    "password": "Admin@123456"
  }'

# Then get all users (replace YOUR_ADMIN_TOKEN)
curl -X GET http://localhost:5000/api/auth/users \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## 🎯 User Flow

### New User Registration
1. User visits http://localhost:3000
2. Redirected to `/login`
3. Clicks "Create one" link
4. Fills registration form
5. System creates account with "user" role
6. JWT token generated and stored
7. Redirected to `/chat` interface
8. Can start chatting immediately

### Existing User Login
1. User visits http://localhost:3000/login
2. Enters email and password
3. System validates credentials
4. JWT token generated and stored
5. Redirected to `/chat` interface
6. Previous chat history loaded

### Admin Access
1. Superadmin logs in
2. Sees "Admin Dashboard" button in sidebar
3. Clicks to access `/admin` page
4. Can manage all users
5. Can grant admin role to other users

### Logout
1. Click "Account" in sidebar
2. Click "Sign Out" button
3. Token removed from localStorage
4. Redirected to `/login` page

## 🔒 Security Features

### Password Security
- ✅ bcrypt hashing with salt
- ✅ No plain-text password storage
- ✅ Password strength validation
- ✅ Minimum complexity requirements

### Token Security
- ✅ JWT with HS256 algorithm
- ✅ 24-hour expiration
- ✅ Stateless authentication
- ✅ Bearer token authorization

### Route Protection
- ✅ Backend middleware validates JWT
- ✅ Frontend ProtectedRoute component
- ✅ Admin-only routes
- ✅ Auto-redirect on unauthorized access

### MongoDB Security
- ✅ Unique email index
- ✅ No password exposure in responses
- ✅ User-specific data isolation

## 📁 File Structure

```
ShizishanGPT/
├── src/backend/
│   ├── models/
│   │   └── auth_schemas.py          # Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py          # Authentication logic
│   │   └── conversation_service.py  # Already supports user_id
│   ├── routers/
│   │   ├── router_auth.py           # Auth endpoints
│   │   └── router_conversations.py  # Already supports user_id
│   ├── config.py                    # JWT settings
│   └── main.py                      # Router registration
│
├── middleware/
│   ├── routes/
│   │   └── authRouter.js            # Express auth routes
│   ├── controllers/
│   │   └── authController.js        # Auth request handlers
│   └── server.js                    # Router registration
│
└── frontend/
    └── src/
        ├── contexts/
        │   └── AuthContext.jsx      # Auth state management
        ├── pages/
        │   ├── Login.jsx            # Login page
        │   ├── Register.jsx         # Registration page
        │   └── AdminDashboard.jsx   # User management
        ├── components/
        │   ├── ProtectedRoute.jsx   # Route guard
        │   └── AgriChatbot.jsx      # Updated with user info
        └── App.js                   # Router setup
```

## ⚙️ Configuration

### Backend (.env or config.py)
```python
JWT_SECRET_KEY = "your-secret-key-here"  # Change in production!
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
MONGODB_URL = "mongodb://localhost:27017"
MONGODB_DB_NAME = "shizishangpt"
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000
```

## 🐛 Troubleshooting

### Issue: Cannot login with superadmin
**Solution**: Backend auto-creates superadmin on first startup. Restart backend:
```bash
python -m uvicorn src.backend.main:app --reload
```

### Issue: "Authorization token required"
**Solution**: Token expired or not stored. Login again.

### Issue: MongoDB connection error
**Solution**: Ensure MongoDB is running:
```bash
mongod --dbpath /path/to/data
```

### Issue: CORS errors
**Solution**: Ensure middleware is running and CORS is configured in server.js

### Issue: "User not found" after login
**Solution**: Clear localStorage and login again:
```javascript
// In browser console
localStorage.clear()
```

## 📊 Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  hashed_password: String,
  full_name: String,
  phone: String,
  location: String,
  role: "user" | "admin" | "superadmin",
  is_active: Boolean,
  created_at: DateTime,
  updated_at: DateTime
}
```

### Conversations Collection
```javascript
{
  _id: ObjectId,
  session_id: String,
  user_id: String,              // Links to user
  title: String,
  messages: Array,
  message_count: Number,
  created_at: DateTime,
  last_updated: DateTime
}
```

## 🎨 UI Screenshots

### Login Page
- Clean, professional design
- Email and password inputs
- Error display
- Link to registration

### Register Page
- Full name, email, phone, location
- Password strength indicator
- Confirm password validation
- Real-time validation feedback

### Chat Interface
- User name in account modal
- Role badge display
- Admin Dashboard button (admins only)
- Logout button

### Admin Dashboard
- User statistics cards
- Search functionality
- User table with actions
- Role badges and status indicators

## 🔄 Next Steps

### Recommended Enhancements
1. **Password Reset**: Email-based password recovery
2. **Email Verification**: Verify email on registration
3. **Refresh Tokens**: Long-lived sessions
4. **Rate Limiting**: Prevent brute force attacks
5. **Audit Log**: Track admin actions
6. **User Activity**: Last login, activity tracking
7. **Profile Updates**: Allow users to edit their info
8. **Avatar Upload**: User profile pictures

### Production Checklist
- [ ] Change JWT_SECRET_KEY to strong random value
- [ ] Enable HTTPS/SSL
- [ ] Configure proper CORS origins
- [ ] Set up rate limiting
- [ ] Add password reset functionality
- [ ] Implement email verification
- [ ] Add session timeout warnings
- [ ] Set up monitoring/logging
- [ ] Create backup strategy for MongoDB
- [ ] Add environment-specific configs

## 📚 Additional Resources

- **FastAPI Security**: https://fastapi.tiangolo.com/tutorial/security/
- **JWT.io**: https://jwt.io/
- **bcrypt**: https://github.com/pyca/bcrypt/
- **React Router**: https://reactrouter.com/

## ✅ System Status

All authentication components are **FULLY IMPLEMENTED** and **READY TO USE**:

- ✅ Backend authentication system
- ✅ Middleware proxy routes
- ✅ Frontend UI components
- ✅ Admin dashboard
- ✅ User-specific chat storage support
- ✅ JWT tokens configured
- ✅ Password security enabled
- ✅ Role-based access control
- ✅ Protected routes
- ✅ All packages installed

**You can now start all services and use the authentication system!** 🎉
