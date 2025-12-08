# Authentication System Implementation

## Overview
Complete authentication system with login, registration, user management, and admin dashboard for ShizishanGPT.

## Backend Implementation

### 1. Authentication Schemas (`src/backend/models/auth_schemas.py`)
- **UserRole** enum: USER, ADMIN, SUPERADMIN
- **UserCreate**: Registration schema with password validation
- **UserLogin**: Login credentials schema
- **UserResponse**: User data response (excluding password)
- **UserUpdate**: Optional field updates
- **TokenResponse**: JWT token response with user data
- **UserInDB**: Complete user document with hashed password
- **AdminUserManagement**: Admin action schema

**Password Requirements:**
- Minimum 8 characters
- At least one uppercase letter
- At least one digit

### 2. Authentication Service (`src/backend/services/auth_service.py`)
Complete authentication logic with:
- **JWT Token Management**: HS256 algorithm, 24-hour expiration
- **Password Security**: bcrypt hashing and verification
- **User CRUD Operations**: register, authenticate, get, update, delete
- **Role Management**: grant admin, toggle status
- **Auto-creation**: Superadmin account on first run

**Default Superadmin:**
- Email: `admin@shizishangpt.com`
- Password: `Admin@123456`

### 3. Authentication Router (`src/backend/routers/router_auth.py`)
FastAPI endpoints:

**Public Endpoints:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate user

**Protected Endpoints:**
- `GET /api/auth/me` - Get current user info
- `PUT /api/auth/me` - Update current user

**Admin Endpoints:**
- `GET /api/auth/users` - Get all users (with pagination)
- `GET /api/auth/users/{user_id}` - Get user by ID
- `POST /api/auth/users/{user_id}/manage` - Manage user (activate, deactivate, grant_admin, revoke_admin, delete)
- `DELETE /api/auth/users/{user_id}` - Delete user

### 4. Configuration (`src/backend/config.py`)
Added authentication settings:
```python
JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production-use-env-variable"
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRATION_HOURS: int = 24
```

### 5. Dependencies
Added to `src/backend/requirements.txt`:
```
pyjwt==2.8.0
bcrypt==4.1.2
```

## Middleware Implementation

### 1. Authentication Router (`middleware/routes/authRouter.js`)
Express routes proxying to FastAPI:
- Public routes: `/register`, `/login`
- Protected routes: `/me`, `/users/*`
- Admin routes: User management endpoints

### 2. Authentication Controller (`middleware/controllers/authController.js`)
Controllers for:
- `register()` - User registration
- `login()` - User authentication
- `getCurrentUser()` - Get current user
- `updateCurrentUser()` - Update user profile
- `getAllUsers()` - Get all users (admin)
- `getUserById()` - Get user by ID (admin)
- `manageUser()` - Manage user actions (admin)
- `deleteUser()` - Delete user (admin)

### 3. Server Integration (`middleware/server.js`)
- Registered auth router: `app.use('/api/auth', authRouter)`
- All auth requests forwarded to FastAPI backend

## Frontend Implementation

### 1. Auth Context (`frontend/src/contexts/AuthContext.jsx`)
React context providing:
- **State**: `user`, `token`, `loading`
- **Methods**: 
  - `login(email, password)` - Authenticate user
  - `register(userData)` - Create new account
  - `logout()` - Clear authentication
  - `updateUser(data)` - Update user profile
  - `isAdmin()` - Check admin role
  - `isSuperAdmin()` - Check superadmin role
- **Storage**: Token persisted in localStorage
- **Auto-fetch**: Current user on mount if token exists

### 2. Login Page (`frontend/src/pages/Login.jsx`)
Features:
- Email and password form
- Error display
- Loading state
- Link to registration page
- Responsive design with Tailwind CSS
- Redirects to `/chat` on success

### 3. Register Page (`frontend/src/pages/Register.jsx`)
Features:
- Full registration form (name, email, phone, location, password)
- Password strength indicator (weak/medium/strong)
- Confirm password validation
- Real-time validation feedback
- Password requirements display
- Error handling
- Redirects to `/chat` on success

### 4. Protected Route Component (`frontend/src/components/ProtectedRoute.jsx`)
- Wraps protected pages
- Redirects to `/login` if not authenticated
- Optional `requireAdmin` prop for admin-only pages
- Loading state during auth check

### 5. App Router (`frontend/src/App.js`)
Updated with React Router:
```jsx
<BrowserRouter>
  <AuthProvider>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/chat" element={<ProtectedRoute><AgriChatbot /></ProtectedRoute>} />
      <Route path="/" element={<Navigate to="/login" />} />
    </Routes>
  </AuthProvider>
</BrowserRouter>
```

### 6. AgriChatbot Integration (`frontend/src/components/AgriChatbot.jsx`)
Updated:
- Uses authenticated user ID from `useAuth()`
- Account modal shows user info (name, email, location, role)
- Logout button with redirect to login
- User-specific chat storage

## Database Schema (MongoDB)

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String (unique),
  hashed_password: String,
  full_name: String,
  phone: String (optional),
  location: String (optional),
  role: String (enum: 'user', 'admin', 'superadmin'),
  is_active: Boolean (default: true),
  created_at: DateTime,
  updated_at: DateTime
}
```

**Indexes:**
- `email` - unique index

### Conversations Collection (Updated)
Chat history will be linked to `user_id` field for user-specific storage.

## Security Features

1. **Password Hashing**: bcrypt with salt rounds
2. **JWT Tokens**: Stateless authentication with expiration
3. **Role-Based Access Control (RBAC)**: user, admin, superadmin
4. **Protected Routes**: Backend and frontend route protection
5. **Token Validation**: Automatic token verification on protected endpoints
6. **Self-Action Prevention**: Users cannot delete/deactivate themselves

## Admin Features (To Be Implemented)

Admin dashboard will include:
- User list with search/filter
- View user details
- Activate/deactivate accounts
- Grant/revoke admin privileges
- Delete users
- View user chat counts
- User activity monitoring

**Access:** Superadmin only

## Installation & Setup

### Backend Setup
```bash
cd src/backend
pip install pyjwt==2.8.0 bcrypt==4.1.2
```

### Environment Variables
Add to `.env` (optional - has defaults):
```
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### Start Services

**Backend:**
```bash
cd d:\Ps-3(git)\ShizishanGPT
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Middleware:**
```bash
cd middleware
npm start
```

**Frontend:**
```bash
cd frontend
npm start
```

## API Testing

### Register User
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe",
    "phone": "+1234567890",
    "location": "New York, USA"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Get Current User (Protected)
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Next Steps (Pending)

1. **Admin Dashboard** (`frontend/src/pages/AdminDashboard.jsx`)
   - User list table
   - Search and filter functionality
   - User management actions
   - Chat activity view
   
2. **User-Specific Chat Storage**
   - Update `conversation_service.py` to filter by `user_id`
   - Add `user_id` field to conversation documents
   
3. **Enhanced Security**
   - Refresh tokens
   - Password reset functionality
   - Email verification
   - Rate limiting on auth endpoints
   
4. **Superadmin Override**
   - Environment variables for superadmin credentials
   - Migration script for existing users

## File Structure

```
ShizishanGPT/
├── src/backend/
│   ├── models/
│   │   └── auth_schemas.py          ✅ Created
│   ├── services/
│   │   └── auth_service.py          ✅ Created
│   ├── routers/
│   │   └── router_auth.py           ✅ Created
│   ├── config.py                    ✅ Updated
│   ├── main.py                      ✅ Updated
│   └── requirements.txt             ✅ Updated
├── middleware/
│   ├── routes/
│   │   └── authRouter.js            ✅ Created
│   ├── controllers/
│   │   └── authController.js        ✅ Created
│   └── server.js                    ✅ Updated
└── frontend/
    └── src/
        ├── contexts/
        │   └── AuthContext.jsx      ✅ Created
        ├── pages/
        │   ├── Login.jsx            ✅ Created
        │   └── Register.jsx         ✅ Created
        ├── components/
        │   ├── ProtectedRoute.jsx   ✅ Created
        │   └── AgriChatbot.jsx      ✅ Updated
        └── App.js                   ✅ Updated
```

## Status

### ✅ Completed
- Backend authentication schemas and services
- JWT token management
- Password hashing and validation
- FastAPI auth endpoints
- Middleware proxy routes
- Frontend auth context
- Login and register pages
- Protected routes
- AgriChatbot integration with user info

### ⏳ Pending
- Admin dashboard page
- User-specific chat storage implementation
- Package installation (network issue - run when online)
- Testing authentication flow end-to-end

## Notes

- Network issue prevented package installation. Run `pip install pyjwt==2.8.0 bcrypt==4.1.2` when internet is available.
- Superadmin account auto-created on first backend startup
- All passwords are hashed with bcrypt before storage
- JWT tokens expire after 24 hours
- Frontend stores token in localStorage
- Authenticated user ID used for chat history storage
