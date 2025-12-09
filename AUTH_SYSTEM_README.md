# 🔐 ShizishanGPT Authentication System

Complete user authentication with login, registration, and super admin dashboard.

## ✨ Features

### User Features
- ✅ **User Registration** - Create account with email, name, phone, location, farm size
- ✅ **User Login** - Secure JWT-based authentication
- ✅ **Profile Management** - Update user information
- ✅ **Multi-language Support** - Integrated with translation system
- ✅ **Conversation History** - Personalized chat history per user

### Super Admin Features  
- ✅ **Admin Dashboard** - Comprehensive user management interface
- ✅ **User Statistics** - Total users, active users, new registrations, query counts
- ✅ **User Management** - View, search, filter all users
- ✅ **Account Control** - Activate/deactivate user accounts
- ✅ **User Deletion** - Remove users (except super admin)
- ✅ **Create Users** - Admin can create accounts

### Security
- ✅ **Password Hashing** - BCrypt encryption
- ✅ **JWT Tokens** - 7-day expiration
- ✅ **Protected Routes** - Frontend and backend authorization
- ✅ **Role-Based Access** - User, Admin, Super Admin roles
- ✅ **MongoDB Storage** - Secure database with indexes

## 🚀 Quick Start

### 1. Install Dependencies

**Backend:**
```bash
pip install passlib[bcrypt] pyjwt pymongo
```

**Frontend:**
Already included (react-router-dom, axios)

### 2. Start Services

**MongoDB** (if not running):
```bash
mongod
```

**Backend** (Port 8000):
```bash
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Middleware** (Port 5000):
```bash
cd middleware
node server.js
```

**Frontend** (Port 3000):
```bash
cd frontend
npm start
```

### 3. Access the Application

- **Login Page**: http://localhost:3000/login
- **Main Chat**: http://localhost:3000 (requires login)
- **Admin Dashboard**: http://localhost:3000/admin (super admin only)

## 👤 Default Super Admin

The system automatically creates a super admin account:

**Email**: `admin@shizishangpt.com`  
**Password**: `admin123`

⚠️ **Change this password in production!**

## 📁 File Structure

```
src/backend/
├── models/
│   └── user_model.py          # Pydantic schemas
├── services/
│   └── auth_service.py        # JWT & password hashing (existing)
├── db/
│   └── user_db.py             # MongoDB user operations
└── routers/
    └── router_auth.py         # Auth endpoints (existing)

frontend/src/
├── contexts/
│   └── AuthContext.js         # Auth state management
├── pages/
│   ├── LoginPage.js           # Login/Register UI
│   └── AdminDashboard.js      # Admin panel
└── App.js                     # Routes & protection
```

## 🔌 API Endpoints

### Public Endpoints

**POST** `/api/auth/register`
```json
{
  "username": "farmer1",
  "email": "farmer@example.com",
  "password": "securepass123",
  "full_name": "Ravi Kumar",
  "phone": "+91 9876543210",
  "location": "Telangana",
  "farm_size": "5 acres"
}
```

**POST** `/api/auth/login`
```json
{
  "email": "farmer@example.com",
  "password": "securepass123"
}
```

### Protected Endpoints (Require Bearer Token)

**GET** `/api/auth/me` - Get current user profile  
**PUT** `/api/auth/me` - Update profile

### Admin Endpoints (Super Admin Only)

**GET** `/api/auth/admin/users` - List all users  
**GET** `/api/auth/admin/stats` - Get statistics  
**POST** `/api/auth/admin/users` - Create user  
**DELETE** `/api/auth/admin/users/{id}` - Delete user  
**PUT** `/api/auth/admin/users/{id}/toggle-active` - Activate/deactivate

## 🎨 UI Design

### Login Page
- Agricultural green theme with wheat/plant patterns
- Toggle between Login/Register
- Form validation with error messages
- Responsive design for mobile

### Admin Dashboard
- Statistics cards (Total Users, Active, New Today, Queries)
- User table with search and filter
- Actions: Activate/Deactivate, Delete
- Real-time updates

### Chatbot Integration
- User info in header (name, email)
- Admin dashboard button (for super admin)
- Logout button
- Protected chat access

## 🔒 Security Best Practices

1. **Environment Variables**:
```bash
JWT_SECRET_KEY=your-super-secret-key-change-in-production
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=shizishangpt
```

2. **Password Requirements**:
- Minimum 6 characters
- BCrypt hashing with salt
- Never stored in plain text

3. **JWT Tokens**:
- 7-day expiration
- Stored in localStorage
- Sent in Authorization header

4. **Database Indexes**:
- Unique index on email
- Unique index on username
- Auto-created on startup

## 📊 Database Schema

```javascript
{
  "_id": ObjectId,
  "username": "farmer1",
  "email": "farmer@example.com",
  "hashed_password": "$2b$12$...",
  "full_name": "Ravi Kumar",
  "role": "user",  // "user" | "admin" | "super_admin"
  "phone": "+91 9876543210",
  "location": "Telangana",
  "farm_size": "5 acres",
  "created_at": ISODate,
  "last_login": ISODate,
  "is_active": true,
  "login_count": 15,
  "query_count": 42
}
```

## 🧪 Testing

### Create Test User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testfarmer",
    "email": "test@farmer.com",
    "password": "test123",
    "full_name": "Test Farmer",
    "location": "Karnataka"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@farmer.com",
    "password": "test123"
  }'
```

### Get Profile (with token)
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐛 Troubleshooting

### Issue: "Module not found: passlib"
```bash
pip install passlib[bcrypt]
```

### Issue: "MongoDB connection failed"
- Ensure MongoDB is running: `mongod`
- Check connection string in .env file

### Issue: "Cannot access admin dashboard"
- Use super admin credentials: `admin@shizishangpt.com / admin123`
- Check user role in database

### Issue: "Token expired"
- Tokens expire after 7 days
- Logout and login again

## 🎯 Usage Examples

### Register a New Farmer
1. Open http://localhost:3000/login
2. Click "Register" tab
3. Fill in details (username, email, password, name, location, farm size)
4. Click "Create Account"
5. Automatically logged in and redirected to chat

### Admin Tasks
1. Login as super admin
2. Click Shield icon in header → Admin Dashboard
3. View user statistics
4. Search for users
5. Deactivate/Delete accounts as needed

## 🔄 Integration with Existing Features

✅ **Translation**: Auth integrated with language preferences  
✅ **Chat History**: Per-user conversation storage  
✅ **Query Tracking**: Counts saved per user  
✅ **Profile**: Farm size, location used for personalization

## 📈 Future Enhancements

- [ ] Email verification
- [ ] Password reset via email
- [ ] Two-factor authentication
- [ ] User roles (Farmer, Agronomist, etc.)
- [ ] Farm management features
- [ ] User analytics dashboard
- [ ] Export user data

## 🌟 Agricultural Theme

The UI uses a beautiful green agricultural theme:
- Primary: Green (#059669, #10B981)
- Background: Gradient from green to teal
- Icons: Sprout, Wheat, Farm-related symbols
- Patterns: Wheat/plant SVG backgrounds
- Responsive and mobile-friendly

---

**Built with ❤️ for farmers** 🌾
