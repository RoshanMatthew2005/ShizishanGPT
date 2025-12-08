import React, { useState, useRef, useEffect } from "react";
import {
  Send,
  Sprout,
  Sun,
  Droplets,
  Bug,
  Menu,
  X,
  MessageSquare,
  Settings,
  User,
  History,
  Plus,
  Paperclip,
  Image,
  FileText,
} from "lucide-react";

export default function AgriChatbot() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      text: "Hello! 👋 I'm your Agriculture Assistant. I'm here to help you with farming advice, crop management, pest control, irrigation tips, and more. How can I assist you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [attachedFiles, setAttachedFiles] = useState([]);
  const [showAttachMenu, setShowAttachMenu] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAccount, setShowAccount] = useState(false);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const [previousChats, setPreviousChats] = useState([
    { id: 1, title: "Monsoon crop suggestions", date: "Today" },
    { id: 2, title: "Organic pest control", date: "Yesterday" },
    { id: 3, title: "Soil pH management", date: "Nov 8" },
    { id: 4, title: "Drip irrigation setup", date: "Nov 7" },
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const suggestionPrompts = [
    {
      icon: <Sprout className="w-4 h-4" />,
      text: "Best crops for monsoon season",
    },
    {
      icon: <Droplets className="w-4 h-4" />,
      text: "How to improve soil irrigation?",
    },
    { icon: <Bug className="w-4 h-4" />, text: "Organic pest control methods" },
    {
      icon: <Sun className="w-4 h-4" />,
      text: "Dealing with drought conditions",
    },
  ];

  const handleSend = async (text = input) => {
    if (!text.trim() && attachedFiles.length === 0) return;

    const userMessage = {
      id: messages.length + 1,
      type: "user",
      text: text.trim(),
      files: [...attachedFiles],
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setAttachedFiles([]);
    setIsTyping(true);

    setTimeout(() => {
      const botMessage = {
        id: messages.length + 2,
        type: "bot",
        text: getBotResponse(text.trim()),
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1500);
  };

  const getBotResponse = (query) => {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes("monsoon") || lowerQuery.includes("rainy")) {
      return "Great question! For monsoon season, I'd recommend crops like rice, maize, millets, pulses, and vegetables like okra and bottle gourd. These thrive in wet conditions. Make sure to ensure proper drainage to prevent waterlogging. Would you like specific tips for any of these crops?";
    } else if (
      lowerQuery.includes("irrigation") ||
      lowerQuery.includes("water")
    ) {
      return "Efficient irrigation is key! Consider drip irrigation systems - they save up to 60% water and deliver it directly to roots. For traditional methods, water early morning or evening to minimize evaporation. Check soil moisture regularly. What's your current irrigation setup?";
    } else if (lowerQuery.includes("pest") || lowerQuery.includes("insect")) {
      return "For organic pest control, try neem oil spray, companion planting with marigolds, or introducing beneficial insects like ladybugs. Crop rotation also helps break pest cycles. Avoid chemical pesticides if possible. What specific pest issues are you facing?";
    } else if (lowerQuery.includes("drought") || lowerQuery.includes("dry")) {
      return "Drought management tips: Use mulching to retain soil moisture, choose drought-resistant varieties, practice conservation tillage, and collect rainwater when possible. Drip irrigation is most efficient. Consider crops like millets, sorghum, or pulses that need less water. Need more specific advice?";
    } else {
      return "I'm here to help with all your farming questions! I can assist with crop selection, soil health, pest management, irrigation, weather planning, and sustainable farming practices. Feel free to ask me anything specific about your farm or crops.";
    }
  };

  const handleSuggestionClick = (text) => {
    handleSend(text);
  };

  const startNewChat = () => {
    setMessages([
      {
        id: 1,
        type: "bot",
        text: "Hello! 👋 I'm your Agriculture Assistant. I'm here to help you with farming advice, crop management, pest control, irrigation tips, and more. How can I assist you today?",
        timestamp: new Date(),
      },
    ]);
  };

  const handleFileSelect = (e, type) => {
    const files = Array.from(e.target.files);
    const newFiles = files.map((file) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: type,
      url: URL.createObjectURL(file),
    }));
    setAttachedFiles((prev) => [...prev, ...newFiles]);
    setShowAttachMenu(false);
  };

  const removeFile = (fileId) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-900 via-green-900 to-gray-900">
      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-2xl border-2 border-green-700 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between p-6 border-b border-green-800">
              <div className="flex items-center gap-3">
                <Settings className="w-6 h-6 text-green-400" />
                <h2 className="text-xl font-bold text-white">Settings</h2>
              </div>
              <button
                onClick={() => setShowSettings(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-all duration-300 text-gray-400 hover:text-white hover:shadow-lg hover:shadow-green-900/30 transform hover:scale-110"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Language
                </label>
                <select className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500">
                  <option>English</option>
                  <option>Hindi</option>
                  <option>Telugu</option>
                  <option>Tamil</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Response Detail
                </label>
                <select className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500">
                  <option>Detailed</option>
                  <option>Moderate</option>
                  <option>Brief</option>
                </select>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Dark Mode</span>
                <div className="bg-green-700 w-12 h-6 rounded-full flex items-center px-1">
                  <div className="bg-white w-4 h-4 rounded-full ml-auto"></div>
                </div>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Notifications</span>
                <div className="bg-gray-600 w-12 h-6 rounded-full flex items-center px-1">
                  <div className="bg-white w-4 h-4 rounded-full"></div>
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-green-800">
              <button
                onClick={() => setShowSettings(false)}
                className="w-full bg-gradient-to-r from-green-700 to-emerald-700 text-white py-3 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-medium hover:shadow-xl hover:shadow-green-900/50 transform hover:scale-105 active:scale-95"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Account Modal */}
      {showAccount && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-2xl border-2 border-green-700 max-w-md w-full shadow-2xl">
            <div className="flex items-center justify-between p-6 border-b border-green-800">
              <div className="flex items-center gap-3">
                <User className="w-6 h-6 text-green-400" />
                <h2 className="text-xl font-bold text-white">Account</h2>
              </div>
              <button
                onClick={() => setShowAccount(false)}
                className="p-2 hover:bg-gray-700 rounded-lg transition-all duration-300 text-gray-400 hover:text-white hover:shadow-lg hover:shadow-green-900/30 transform hover:scale-110"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <div className="flex flex-col items-center mb-6">
                <div className="w-24 h-24 bg-gradient-to-br from-green-700 to-emerald-700 rounded-full flex items-center justify-center text-white text-3xl font-bold mb-3">
                  FA
                </div>
                <h3 className="text-xl font-bold text-white">Farmer Account</h3>
                <p className="text-sm text-gray-400">farmer@example.com</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    defaultValue="Farmer Account"
                    className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    defaultValue="farmer@example.com"
                    className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Farm Location
                  </label>
                  <input
                    type="text"
                    placeholder="Enter your location"
                    className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-green-800 space-y-2">
              <button
                onClick={() => setShowAccount(false)}
                className="w-full bg-gradient-to-r from-green-700 to-emerald-700 text-white py-3 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-medium hover:shadow-xl hover:shadow-green-900/50 transform hover:scale-105 active:scale-95"
              >
                Update Profile
              </button>
              <button className="w-full bg-gray-700 text-gray-300 py-3 rounded-lg hover:bg-gray-600 transition-all duration-300 font-medium hover:shadow-lg transform hover:scale-105 active:scale-95">
                Sign Out
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? "w-72" : "w-0"
        } bg-gray-800 border-r border-green-800 transition-all duration-300 overflow-hidden flex flex-col`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-green-800">
          <button
            onClick={startNewChat}
            className="w-full flex items-center gap-2 bg-gradient-to-r from-green-700 to-emerald-700 text-white px-4 py-3 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-green-900/50 transform hover:scale-105"
          >
            <Plus className="w-5 h-5" />
            <span className="font-semibold">New Chat</span>
          </button>
        </div>

        {/* Previous Queries */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center gap-2 text-green-400 mb-3">
            <History className="w-4 h-4" />
            <h3 className="text-sm font-semibold uppercase tracking-wide">
              Previous Chats
            </h3>
          </div>
          <div className="space-y-2">
            {previousChats.map((chat) => (
              <button
                key={chat.id}
                className="w-full text-left p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-all duration-300 border border-gray-700 hover:border-green-700 group transform hover:scale-105 hover:shadow-lg hover:shadow-green-900/30"
              >
                <div className="flex items-start gap-2">
                  <MessageSquare className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0 group-hover:text-green-400 transition-colors duration-300" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-200 truncate group-hover:text-green-300 transition-colors duration-300">
                      {chat.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{chat.date}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-4 border-t border-green-800 space-y-2">
          <button
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800/50 hover:bg-gradient-to-r hover:from-green-700/20 hover:to-emerald-700/20 border-2 border-transparent hover:border-green-600 transition-all duration-300 text-gray-300 hover:text-green-400 hover:shadow-lg hover:shadow-green-900/50 transform hover:scale-105"
          >
            <Settings className="w-5 h-5 transition-transform duration-300 group-hover:rotate-90" />
            <span className="text-sm font-medium">Settings</span>
          </button>
          <button
            onClick={() => setShowAccount(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800/50 hover:bg-gradient-to-r hover:from-green-700/20 hover:to-emerald-700/20 border-2 border-transparent hover:border-green-600 transition-all duration-300 text-gray-300 hover:text-green-400 hover:shadow-lg hover:shadow-green-900/50 transform hover:scale-105"
          >
            <User className="w-5 h-5" />
            <span className="text-sm font-medium">Account</span>
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-800 border-b border-green-800 text-white p-4 shadow-lg">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-gray-700 rounded-lg transition-all duration-300 hover:shadow-lg hover:shadow-green-900/30 transform hover:scale-110"
            >
              {sidebarOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
            <div className="bg-green-700/30 p-2 rounded-full">
              <Sprout className="w-6 h-6 text-green-400" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Agriculture Assistant</h1>
              <p className="text-sm text-green-300">Your farming companion</p>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.type === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-4 shadow-lg ${
                    message.type === "user"
                      ? "bg-gradient-to-br from-green-700 to-emerald-700 text-white rounded-br-sm"
                      : "bg-gray-800 border-2 border-green-800 text-gray-100 rounded-bl-sm"
                  }`}
                >
                  {message.type === "bot" && (
                    <div className="flex items-center gap-2 mb-2 text-green-400">
                      <Sprout className="w-4 h-4" />
                      <span className="text-xs font-semibold">
                        Agri Assistant
                      </span>
                    </div>
                  )}
                  <p className="text-sm leading-relaxed whitespace-pre-wrap">
                    {message.text}
                  </p>
                  {message.files && message.files.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {message.files.map((file) => (
                        <div
                          key={file.id}
                          className="flex items-center gap-2 p-2 bg-gray-900/50 rounded-lg border border-green-700/30"
                        >
                          {file.type === "image" ? (
                            <>
                              <Image className="w-4 h-4 text-green-400" />
                              <img
                                src={file.url}
                                alt={file.name}
                                className="w-20 h-20 object-cover rounded"
                              />
                              <div className="flex-1 min-w-0">
                                <p className="text-xs text-gray-300 truncate">
                                  {file.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {formatFileSize(file.size)}
                                </p>
                              </div>
                            </>
                          ) : (
                            <>
                              <FileText className="w-4 h-4 text-green-400" />
                              <div className="flex-1 min-w-0">
                                <p className="text-xs text-gray-300 truncate">
                                  {file.name}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {formatFileSize(file.size)}
                                </p>
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  <span
                    className={`text-xs mt-2 block ${
                      message.type === "user"
                        ? "text-green-200"
                        : "text-gray-500"
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </span>
                </div>
              </div>
            ))}

            {isTyping && (
              <div className="flex justify-start">
                <div className="bg-gray-800 border-2 border-green-800 rounded-2xl rounded-bl-sm p-4 shadow-lg">
                  <div className="flex items-center gap-2 mb-2 text-green-400">
                    <Sprout className="w-4 h-4" />
                    <span className="text-xs font-semibold">
                      Agri Assistant
                    </span>
                  </div>
                  <div className="flex gap-1">
                    <div
                      className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                      style={{ animationDelay: "0ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    ></div>
                    <div
                      className="w-2 h-2 bg-green-500 rounded-full animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    ></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Suggestion Prompts */}
        {messages.length <= 2 && (
          <div className="px-4 pb-2">
            <div className="max-w-4xl mx-auto">
              <p className="text-sm text-gray-400 mb-2 font-medium">
                Quick suggestions:
              </p>
              <div className="grid grid-cols-2 gap-2">
                {suggestionPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestionClick(prompt.text)}
                    className="flex items-center gap-2 p-3 bg-gray-800 border-2 border-green-800 rounded-xl hover:bg-gray-700 hover:border-green-600 transition-all duration-300 text-left text-sm text-gray-300 shadow-lg hover:shadow-xl hover:shadow-green-900/50 transform hover:scale-105 hover:text-green-400 group"
                  >
                    <div className="text-green-500 group-hover:text-green-400 transition-colors duration-300">
                      {prompt.icon}
                    </div>
                    <span>{prompt.text}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-gray-800 border-t-2 border-green-800 p-4 shadow-lg">
          <div className="max-w-4xl mx-auto">
            {/* Attached Files Preview */}
            {attachedFiles.length > 0 && (
              <div className="mb-3 flex flex-wrap gap-2">
                {attachedFiles.map((file) => (
                  <div
                    key={file.id}
                    className="flex items-center gap-2 bg-gray-700 px-3 py-2 rounded-lg border border-green-700"
                  >
                    {file.type === "image" ? (
                      <Image className="w-4 h-4 text-green-400" />
                    ) : (
                      <FileText className="w-4 h-4 text-green-400" />
                    )}
                    <span className="text-xs text-gray-300 max-w-[150px] truncate">
                      {file.name}
                    </span>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-gray-400 hover:text-red-400 transition-all duration-300 hover:scale-125"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            {/* Input Row */}
            <div className="flex gap-2 relative">
              {/* Attachment Button */}
              <div className="relative">
                <button
                  onClick={() => setShowAttachMenu(!showAttachMenu)}
                  className="p-3 rounded-full hover:bg-gray-700 transition-all duration-300 text-gray-400 hover:text-green-400 hover:shadow-lg hover:shadow-green-900/30 transform hover:scale-110"
                >
                  <Paperclip className="w-5 h-5" />
                </button>

                {/* Attachment Menu */}
                {showAttachMenu && (
                  <div className="absolute bottom-full left-0 mb-2 bg-gray-700 rounded-lg shadow-xl border border-green-700 overflow-hidden">
                    <button
                      onClick={() => imageInputRef.current?.click()}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-600 transition-all duration-300 text-gray-300 hover:text-green-400 w-full text-left transform hover:scale-105"
                    >
                      <Image className="w-4 h-4" />
                      <span className="text-sm">Upload Image</span>
                    </button>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-600 transition-all duration-300 text-gray-300 hover:text-green-400 w-full text-left border-t border-gray-600 transform hover:scale-105"
                    >
                      <FileText className="w-4 h-4" />
                      <span className="text-sm">Upload File</span>
                    </button>
                  </div>
                )}

                {/* Hidden File Inputs */}
                <input
                  ref={imageInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={(e) => handleFileSelect(e, "image")}
                  className="hidden"
                />
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  multiple
                  onChange={(e) => handleFileSelect(e, "document")}
                  className="hidden"
                />
              </div>

              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleSend()}
                placeholder="Ask me anything about farming..."
                className="flex-1 px-4 py-3 border-2 border-green-800 rounded-full focus:outline-none focus:border-green-600 text-gray-100 placeholder-gray-500 bg-gray-900"
              />
              <button
                onClick={() => handleSend()}
                disabled={!input.trim() && attachedFiles.length === 0}
                className="bg-gradient-to-r from-green-700 to-emerald-700 text-white p-3 rounded-full hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl hover:shadow-green-900/50 transform hover:scale-110 active:scale-95"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
