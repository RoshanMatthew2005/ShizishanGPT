# Chat History with MongoDB Integration

## Overview

This feature adds **persistent chat history** to the ShizishanGPT frontend, storing all conversations in MongoDB and allowing users to view and resume previous chats.

## What Was Changed

### 🔧 Backend Changes (FastAPI)

#### 1. **Enabled MongoDB** (`src/backend/config.py`)
```python
MONGODB_ENABLED: bool = True  # Changed from False
MONGODB_CONVERSATIONS_COLLECTION: str = "conversations"  # New collection
```

#### 2. **Created Conversation Service** (`src/backend/services/conversation_service.py`)
- **New service** for managing conversation history
- Methods:
  - `save_conversation()` - Save/update conversations
  - `get_conversations()` - Get user's conversation list
  - `get_conversation()` - Get specific conversation with all messages
  - `delete_conversation()` - Delete a conversation

#### 3. **Created Conversation Router** (`src/backend/routers/router_conversations.py`)
- **New API endpoints**:
  - `POST /conversations/save` - Save conversation
  - `POST /conversations/list` - Get conversation list
  - `POST /conversations/get` - Get specific conversation
  - `POST /conversations/delete` - Delete conversation

#### 4. **Updated Main App** (`src/backend/main.py`)
- Initialize MongoDB on startup
- Register conversation service
- Include conversation router

### 🌐 Middleware Changes (Node.js)

#### 1. **Created Conversation Router** (`middleware/routes/conversationRouter.js`)
- Forwards conversation requests to FastAPI backend
- Validates requests using Joi schemas
- Handles errors gracefully

#### 2. **Updated Server** (`middleware/server.js`)
- Added conversation router
- Updated endpoints list

### 💻 Frontend Changes (React)

#### 1. **Updated API Service** (`frontend/src/services/api.js`)
- Added 4 new methods:
  - `saveConversation(sessionId, title, messages, userId)`
  - `getConversations(userId, limit)`
  - `getConversation(sessionId, userId)`
  - `deleteConversation(sessionId, userId)`

#### 2. **Updated AgriChatbot Component** (`frontend/src/components/AgriChatbot.jsx`)

**Key Changes:**
- ❌ **Removed** dummy data for `previousChats`
- ✅ **Added** session ID tracking for each conversation
- ✅ **Added** auto-save functionality (saves 2 seconds after last message)
- ✅ **Added** `loadConversationHistory()` - Loads from MongoDB on mount
- ✅ **Added** `saveCurrentConversation()` - Auto-saves to MongoDB
- ✅ **Added** `loadPreviousConversation()` - Loads a specific chat
- ✅ **Added** loading states and empty states for sidebar
- ✅ **Added** click handlers to load previous conversations
- ✅ **Added** smart date formatting (e.g., "2h ago", "Yesterday")

## How It Works

### 📝 Saving Conversations

1. User sends a message
2. Message added to state
3. After 2-second delay, conversation auto-saves to MongoDB
4. Title generated from first user message
5. Sidebar refreshes to show updated conversation

### 📖 Loading Conversations

1. On app mount, fetch user's conversation list from MongoDB
2. Display in sidebar with title, date, and message count
3. Click a conversation → load all messages from MongoDB
4. Session ID switches to loaded conversation

### 🆕 Starting New Conversation

1. Click "New Conversation" button
2. Generate new unique session ID
3. Reset messages to welcome message
4. New messages will be saved under new session ID

## MongoDB Collections

### `conversations` Collection Structure

```json
{
  "session_id": "session_1701436800000_abc123",
  "user_id": "anonymous",
  "title": "Best crops for monsoon season",
  "messages": [
    {
      "id": 1,
      "type": "bot",
      "text": "Hello! How can I assist you?",
      "timestamp": "2025-12-01T10:00:00.000Z"
    },
    {
      "id": 2,
      "type": "user",
      "text": "Best crops for monsoon season",
      "timestamp": "2025-12-01T10:00:15.000Z"
    }
  ],
  "message_count": 4,
  "last_updated": "2025-12-01T10:05:30.000Z",
  "created_at": "2025-12-01T10:00:00.000Z"
}
```

## Testing the Feature

### Prerequisites

1. **Install MongoDB**:
   ```powershell
   # Download from: https://www.mongodb.com/try/download/community
   # Or use Docker:
   docker run -d -p 27017:27017 --name mongodb mongo
   ```

2. **Install Python dependencies**:
   ```powershell
   pip install pymongo
   ```

3. **Ensure all services are running**:
   - MongoDB on port 27017
   - FastAPI backend on port 8000
   - Node.js middleware on port 5000
   - React frontend on port 3000

### Test Steps

1. **Start a conversation**:
   - Open http://localhost:3000
   - Send a message: "What crops grow in monsoon?"
   - Wait 2 seconds (auto-save)
   - Check browser console: "💾 Conversation saved: What crops grow in monsoon?"

2. **View in MongoDB**:
   ```javascript
   // MongoDB shell
   use shizishangpt
   db.conversations.find()
   ```

3. **Refresh page**:
   - Reload browser
   - Sidebar should show your previous conversation
   - Click it to reload messages

4. **Start new conversation**:
   - Click "New Conversation" button
   - Send new messages
   - Both conversations appear in sidebar

## API Endpoints

### Save Conversation
```http
POST /api/conversations/save
Content-Type: application/json

{
  "session_id": "session_123",
  "title": "Crop advice",
  "messages": [...],
  "user_id": "anonymous"
}
```

### Get Conversation List
```http
POST /api/conversations/list
Content-Type: application/json

{
  "user_id": "anonymous",
  "limit": 20
}
```

### Get Specific Conversation
```http
POST /api/conversations/get
Content-Type: application/json

{
  "session_id": "session_123",
  "user_id": "anonymous"
}
```

### Delete Conversation
```http
POST /api/conversations/delete
Content-Type: application/json

{
  "session_id": "session_123",
  "user_id": "anonymous"
}
```

## User Experience Improvements

### Before (Dummy Data)
- ❌ Sidebar showed fake conversations
- ❌ Data lost on page refresh
- ❌ No way to resume previous chats
- ❌ Conversations not saved

### After (MongoDB Integration)
- ✅ Sidebar shows real conversation history
- ✅ Data persists across sessions
- ✅ Click to load any previous conversation
- ✅ Auto-saves as you chat
- ✅ See message count and last updated time
- ✅ Smart date formatting ("2h ago")
- ✅ Loading states and empty states
- ✅ Unique session IDs for each conversation

## Future Enhancements

- [ ] User authentication (replace "anonymous" with real user IDs)
- [ ] Edit conversation titles
- [ ] Delete conversations from UI
- [ ] Search conversation history
- [ ] Export conversations
- [ ] Conversation folders/tags
- [ ] Share conversations
- [ ] Conversation analytics

## Troubleshooting

### MongoDB Connection Failed
```
Solution: Ensure MongoDB is running on localhost:27017
```

### Conversations Not Saving
```
Check browser console for errors
Verify MongoDB is enabled in backend config
Check backend logs for MongoDB connection status
```

### Sidebar Shows Empty
```
Check if MongoDB has data: db.conversations.find()
Verify API endpoints are responding
Check network tab in browser DevTools
```

## Files Changed

### Created (8 files)
- `src/backend/services/conversation_service.py`
- `src/backend/routers/router_conversations.py`
- `middleware/routes/conversationRouter.js`
- `docs/CHAT_HISTORY_FEATURE.md`

### Modified (5 files)
- `src/backend/config.py`
- `src/backend/main.py`
- `middleware/server.js`
- `frontend/src/services/api.js`
- `frontend/src/components/AgriChatbot.jsx`

## Summary

This feature transforms the frontend from a **stateless chat interface** to a **persistent conversation manager**, giving users the ability to:
- 💾 Save all conversations automatically
- 📖 View conversation history in sidebar
- 🔄 Resume previous conversations
- 🆕 Start new conversations
- 📊 See conversation metadata (date, message count)

All data is stored in **MongoDB** with a clean three-tier architecture:
```
React → Node.js Middleware → FastAPI Backend → MongoDB
```
