import React, { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
  Loader2,
  Languages,
  LogOut,
  Shield,
} from "lucide-react";
import * as api from "../services/api";

export default function AgriChatbot() {
  const { user, logout, isSuperAdmin } = useAuth();
  const navigate = useNavigate();
  
  // Session ID for current conversation
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [userId] = useState(user?.id || "anonymous");
  
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: "bot",
      text: "Hello! 👋 I'm your Agriculture Assistant powered by ShizishanGPT. I can help you with:\n\n• Farming advice and crop management\n• Pest detection from images\n• Yield predictions\n• Weather analysis\n• Translation services\n\nHow can I assist you today?",
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
  const [queryMode, setQueryMode] = useState("agent"); // 'llm', 'rag', 'agent'
  
  // Translation settings
  const [selectedLanguage, setSelectedLanguage] = useState("en"); // User's preferred language
  const [autoTranslateInput, setAutoTranslateInput] = useState(false); // Translate user input to English
  const [autoTranslateOutput, setAutoTranslateOutput] = useState(false); // Translate bot response to user's language
  const [isTranslating, setIsTranslating] = useState(false);
  
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const [previousChats, setPreviousChats] = useState([]); // Will be loaded from MongoDB
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Load conversation history on mount
  useEffect(() => {
    loadConversationHistory();
  }, []);

  // Auto-save conversation when messages change (debounced)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (messages.length > 1) { // Only save if there are user messages
        saveCurrentConversation();
      }
    }, 2000); // Wait 2 seconds after last message before saving

    return () => clearTimeout(timer);
  }, [messages]);

  // Load conversation history from MongoDB
  const loadConversationHistory = async () => {
    try {
      setIsLoadingHistory(true);
      const response = await api.getConversations(userId, 20);
      
      if (response.success && response.data?.conversations) {
        const formattedChats = response.data.conversations.map(conv => ({
          id: conv.session_id,
          session_id: conv.session_id,
          title: conv.title,
          date: formatDate(conv.last_updated),
          message_count: conv.message_count
        }));
        setPreviousChats(formattedChats);
        console.log(`✅ Loaded ${formattedChats.length} conversations from history`);
      }
    } catch (error) {
      console.error("❌ Failed to load conversation history:", error);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Save current conversation to MongoDB
  const saveCurrentConversation = async () => {
    try {
      // Generate title from first user message
      const firstUserMsg = messages.find(m => m.type === 'user');
      const title = firstUserMsg 
        ? firstUserMsg.text.substring(0, 50) + (firstUserMsg.text.length > 50 ? '...' : '')
        : 'New Conversation';
      
      await api.saveConversation(sessionId, title, messages, userId);
      console.log(`💾 Conversation saved: ${title}`);
      
      // Reload history to show updated conversation
      loadConversationHistory();
    } catch (error) {
      console.error("❌ Failed to save conversation:", error);
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 60) return `${diffMins} min ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    
    return date.toLocaleDateString();
  };

  // Load a previous conversation
  const loadPreviousConversation = async (chatSessionId) => {
    try {
      const response = await api.getConversation(chatSessionId, userId);
      
      if (response.success && response.data?.conversation) {
        const conv = response.data.conversation;
        // Convert timestamp strings to Date objects
        const messagesWithDates = (conv.messages || []).map(msg => ({
          ...msg,
          timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date()
        }));
        setMessages(messagesWithDates);
        setSessionId(conv.session_id);
        console.log(`✅ Loaded conversation: ${conv.title}`);
      }
    } catch (error) {
      console.error("❌ Failed to load conversation:", error);
      alert("Failed to load conversation. Please try again.");
    }
  };

  // Check API health on mount
  useEffect(() => {
    api.healthCheck()
      .then((response) => {
        console.log("✅ API health check passed:", response);
      })
      .catch((error) => {
        console.error("❌ API health check failed:", error);
        // Show warning message
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            type: "bot",
            text: "⚠️ Warning: Unable to connect to backend services. Please ensure the Node.js middleware is running on port 5000.",
            timestamp: new Date(),
            isWarning: true,
          },
        ]);
      });
  }, []);

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
      text: "Predict yield for wheat in Punjab with 800mm rainfall",
    },
  ];

  const handleSend = async (text = input) => {
    if (!text.trim() && attachedFiles.length === 0) return;

    let originalText = text.trim();
    let processedText = originalText;
    let translatedInput = null;

    // Auto-translate input if enabled and language is not English
    if (autoTranslateInput && selectedLanguage !== "en" && !attachedFiles.some(f => f.type === "image")) {
      setIsTranslating(true);
      try {
        const translateResponse = await api.translateText(originalText, selectedLanguage, "en");
        if (translateResponse.success && translateResponse.data?.translated_text) {
          processedText = translateResponse.data.translated_text;
          translatedInput = processedText;
          console.log(`🌐 Translated input (${selectedLanguage} → en):`, processedText);
        }
      } catch (error) {
        console.error("Translation failed:", error);
      }
      setIsTranslating(false);
    }

    const userMessage = {
      id: messages.length + 1,
      type: "user",
      text: originalText,
      translatedText: translatedInput,
      files: [...attachedFiles],
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    const currentFiles = [...attachedFiles];
    setAttachedFiles([]);
    setIsTyping(true);

    try {
      let response;

      // Check if image is attached for pest detection
      const imageFile = currentFiles.find((f) => f.type === "image");
      if (imageFile) {
        // Pest detection with ReAct agent (agent processes everything on backend)
        response = await api.detectPest(imageFile.file, 3);
        
        // Backend returns: {top_prediction, confidence, all_predictions, recommendations, agent_analysis, agent_tools_used}
        const topPrediction = response.top_prediction || "Unknown";
        const confidence = response.confidence || 0;
        const allPredictions = response.all_predictions || [];
        const recommendations = response.recommendations || [];
        const agentAnalysis = response.agent_analysis || "";
        const toolsUsed = response.agent_tools_used || [];

        let botText = "🔍 **Plant Disease Detection Results:**\n\n";
        botText += `🌿 **Detected Disease:** ${topPrediction}\n`;
        botText += `📊 **Confidence:** ${(confidence * 100).toFixed(1)}%\n\n`;
        
        if (allPredictions.length > 1) {
          botText += "**Other Possible Diseases:**\n";
          allPredictions.slice(1, 3).forEach((pred, idx) => {
            botText += `${idx + 1}. ${pred.class} - ${(pred.confidence * 100).toFixed(1)}%\n`;
          });
          botText += "\n";
        }
        
        if (recommendations.length > 0) {
          botText += `📋 **Quick Recommendations:**\n`;
          recommendations.forEach((rec, idx) => {
            botText += `${idx + 1}. ${rec}\n`;
          });
          botText += "\n";
        }
        
        // Add agent analysis (comprehensive info from ReAct agent)
        if (agentAnalysis) {
          botText += `🤖 **Detailed Analysis & Treatment:**\n${agentAnalysis}`;
        }
        
        if (toolsUsed.length > 0) {
          botText += `\n\n🔧 **Tools used:** ${toolsUsed.join(", ")}`;
        }

        const botMessage = {
          id: messages.length + 2,
          type: "bot",
          text: botText,
          timestamp: new Date(),
          data: response,
        };
        setMessages((prev) => [...prev, botMessage]);
      } else {
        // Use selected query mode
        if (queryMode === "llm") {
          response = await api.askQuestion(processedText, "direct");
        } else if (queryMode === "rag") {
          response = await api.queryRAG(processedText, 5);
          // Format RAG response
          const documents = response.data?.documents || [];
          let botText = response.data?.answer || "Here are the relevant documents:\n\n";
          if (documents.length > 0) {
            botText += "\n\n📚 **Sources:**\n";
            documents.slice(0, 3).forEach((doc, idx) => {
              botText += `${idx + 1}. ${doc.content.substring(0, 100)}...\n`;
            });
          }
          const botMessage = {
            id: messages.length + 2,
            type: "bot",
            text: botText,
            timestamp: new Date(),
            data: response.data,
          };
          setMessages((prev) => [...prev, botMessage]);
          setIsTyping(false);
          return;
        } else {
          // Default: use agent
          response = await api.queryAgent(processedText, "auto", 5);
        }

        const botText = response.answer || response.data?.answer || response.final_answer || response.data?.final_answer || "I apologize, but I couldn't process your request.";
        const toolsUsed = response.tools_used || response.data?.tools_used || [];

        let displayText = botText;
        if (toolsUsed.length > 0) {
          displayText += `\n\n🔧 **Tools used:** ${toolsUsed.join(", ")}`;
        }

        // Auto-translate output if enabled and language is not English
        let translatedOutput = null;
        console.log(`🔍 Translation check: autoTranslateOutput=${autoTranslateOutput}, selectedLanguage=${selectedLanguage}`);
        
        if (autoTranslateOutput && selectedLanguage !== "en") {
          setIsTranslating(true);
          console.log(`🌐 Starting output translation: ${displayText.substring(0, 50)}...`);
          try {
            const translateResponse = await api.translateText(displayText, "en", selectedLanguage);
            console.log(`🌐 Translation API response:`, translateResponse);
            console.log(`🔍 Response structure:`, JSON.stringify(translateResponse, null, 2));
            console.log(`🔍 Has success?`, translateResponse.success);
            console.log(`🔍 Has data?`, translateResponse.data);
            console.log(`🔍 Has translated_text?`, translateResponse.data?.translated_text);
            
            if (translateResponse.success && translateResponse.data?.translated_text) {
              translatedOutput = translateResponse.data.translated_text;
              console.log(`✅ Translated output (en → ${selectedLanguage}):`, translatedOutput);
              console.log(`📊 Original length: ${displayText.length}, Translated length: ${translatedOutput.length}`);
              console.log(`🔤 First 100 chars of translation:`, translatedOutput.substring(0, 100));
              displayText = translatedOutput; // Use translated text
            } else {
              console.warn(`⚠️ Translation response missing data:`, translateResponse);
              console.warn(`⚠️ Full response:`, JSON.stringify(translateResponse, null, 2));
            }
          } catch (error) {
            console.error("❌ Output translation failed:", error);
          }
          setIsTranslating(false);
        } else {
          console.log(`ℹ️ Skipping output translation (enabled: ${autoTranslateOutput}, lang: ${selectedLanguage})`);
        }

        const botMessage = {
          id: messages.length + 2,
          type: "bot",
          text: displayText,
          originalText: translatedOutput ? botText : null,
          timestamp: new Date(),
          data: response.data,
        };
        setMessages((prev) => [...prev, botMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: messages.length + 2,
        type: "bot",
        text: `❌ Error: ${error.response?.data?.error || error.message || "Unable to process request. Please check if the backend services are running."}`,
        timestamp: new Date(),
        isError: true,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSuggestionClick = (text) => {
    setInput(text);
    setTimeout(() => handleSend(text), 100);
  };

  const startNewChat = () => {
    // Generate new session ID
    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    setSessionId(newSessionId);
    
    // Reset messages to welcome message
    setMessages([
      {
        id: 1,
        type: "bot",
        text: "Hello! 👋 I'm your Agriculture Assistant powered by ShizishanGPT. How can I assist you today?",
        timestamp: new Date(),
      },
    ]);
    
    console.log(`🆕 Started new conversation: ${newSessionId}`);
  };

  const handleFileSelect = (e, type) => {
    const files = Array.from(e.target.files);
    const newFiles = files.map((file) => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      type: type,
      url: URL.createObjectURL(file),
      file: file, // Store actual file for upload
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
                className="p-2 hover:bg-gray-700 rounded-lg transition-all duration-300 text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Query Mode
                </label>
                <select 
                  value={queryMode}
                  onChange={(e) => setQueryMode(e.target.value)}
                  className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                >
                  <option value="agent">Agent (Auto Tool Selection)</option>
                  <option value="llm">Direct LLM</option>
                  <option value="rag">RAG Search</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
                  <Languages className="w-4 h-4 text-green-400" />
                  Preferred Language
                </label>
                <select 
                  value={selectedLanguage}
                  onChange={(e) => setSelectedLanguage(e.target.value)}
                  className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                >
                  <option value="en">English</option>
                  <option value="hi">हिन्दी (Hindi)</option>
                  <option value="te">తెలుగు (Telugu)</option>
                  <option value="ta">தமிழ் (Tamil)</option>
                  <option value="kn">ಕನ್ನಡ (Kannada)</option>
                  <option value="ml">മലയാളം (Malayalam)</option>
                  <option value="mr">मराठी (Marathi)</option>
                  <option value="bn">বাংলা (Bengali)</option>
                  <option value="gu">ગુજરાતી (Gujarati)</option>
                  <option value="pa">ਪੰਜਾਬੀ (Punjabi)</option>
                </select>
              </div>

              {selectedLanguage !== "en" && (
                <>
                  <div className="pt-2 border-t border-green-800">
                    <label className="flex items-center justify-between cursor-pointer">
                      <div>
                        <span className="text-sm font-medium text-gray-300">Auto-translate Input</span>
                        <p className="text-xs text-gray-500 mt-1">Translate your messages to English before sending</p>
                      </div>
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={autoTranslateInput}
                          onChange={(e) => setAutoTranslateInput(e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:bg-green-600 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                      </div>
                    </label>
                  </div>

                  <div>
                    <label className="flex items-center justify-between cursor-pointer">
                      <div>
                        <span className="text-sm font-medium text-gray-300">Auto-translate Output</span>
                        <p className="text-xs text-gray-500 mt-1">Translate bot responses to your language</p>
                      </div>
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={autoTranslateOutput}
                          onChange={(e) => setAutoTranslateOutput(e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:bg-green-600 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all"></div>
                      </div>
                    </label>
                  </div>
                </>
              )}
            </div>
            <div className="p-6 border-t border-green-800">
              <button
                onClick={() => setShowSettings(false)}
                className="w-full bg-gradient-to-r from-green-700 to-emerald-700 text-white py-3 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300 font-medium"
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
                className="p-2 hover:bg-gray-700 rounded-lg transition-all duration-300 text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6">
              <div className="flex flex-col items-center mb-6">
                <div className="w-24 h-24 bg-gradient-to-br from-green-700 to-emerald-700 rounded-full flex items-center justify-center text-white text-3xl font-bold mb-3">
                  {user?.full_name?.charAt(0).toUpperCase() || "U"}
                </div>
                <h3 className="text-xl font-bold text-white">{user?.full_name || "User"}</h3>
                <p className="text-sm text-gray-400">{user?.email || "user@example.com"}</p>
                {user?.role && (
                  <span className="mt-2 px-3 py-1 bg-green-700/30 text-green-400 rounded-full text-xs font-semibold uppercase">
                    {user.role}
                  </span>
                )}
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    value={user?.full_name || ""}
                    readOnly
                    className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    value={user?.email || ""}
                    readOnly
                    className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                  />
                </div>
                {user?.location && (
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      value={user.location}
                      readOnly
                      className="w-full bg-gray-700 border border-green-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:border-green-500"
                    />
                  </div>
                )}
              </div>
            </div>
            <div className="p-6 border-t border-green-800 space-y-2">
              <button
                onClick={() => setShowAccount(false)}
                className="w-full bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-lg transition-all duration-300 font-medium flex items-center justify-center gap-2"
              >
                Close
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
        <div className="p-4 border-b border-green-800">
          <button
            onClick={startNewChat}
            className="w-full flex items-center gap-2 bg-gradient-to-r from-green-700 to-emerald-700 text-white px-4 py-3 rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-300 shadow-lg"
          >
            <Plus className="w-5 h-5" />
            <span className="font-semibold">New Chat</span>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          <div className="flex items-center gap-2 text-green-400 mb-3">
            <History className="w-4 h-4" />
            <h3 className="text-sm font-semibold uppercase tracking-wide">
              Previous Chats
            </h3>
          </div>
          {isLoadingHistory ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 text-green-500 animate-spin" />
            </div>
          ) : previousChats.length === 0 ? (
            <div className="text-center py-8 text-gray-500 text-sm">
              <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No previous conversations</p>
              <p className="text-xs mt-1">Start chatting to save history</p>
            </div>
          ) : (
            <div className="space-y-2">
              {previousChats.map((chat) => (
                <button
                  key={chat.id}
                  onClick={() => loadPreviousConversation(chat.session_id)}
                  className="w-full text-left p-3 rounded-lg bg-gray-700/50 hover:bg-gray-700 transition-all duration-300 border border-gray-700 hover:border-green-700"
                >
                  <div className="flex items-start gap-2">
                    <MessageSquare className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-200 truncate">{chat.title}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-xs text-gray-500">{chat.date}</p>
                        {chat.message_count && (
                          <span className="text-xs text-gray-600">• {chat.message_count} msgs</span>
                        )}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 border-t border-green-800 space-y-2">
          <button
            onClick={() => setShowSettings(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800/50 hover:bg-gradient-to-r hover:from-green-700/20 hover:to-emerald-700/20 border-2 border-transparent hover:border-green-600 transition-all duration-300 text-gray-300 hover:text-green-400"
          >
            <Settings className="w-5 h-5" />
            <span className="text-sm font-medium">Settings</span>
          </button>
          <button
            onClick={() => setShowAccount(true)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-800/50 hover:bg-gradient-to-r hover:from-green-700/20 hover:to-emerald-700/20 border-2 border-transparent hover:border-green-600 transition-all duration-300 text-gray-300 hover:text-green-400"
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
              className="p-2 hover:bg-gray-700 rounded-lg transition-all duration-300"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <div className="bg-green-700/30 p-2 rounded-full">
              <Sprout className="w-6 h-6 text-green-400" />
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold">ShizishanGPT</h1>
              <p className="text-sm text-green-300">Your AI farming companion</p>
            </div>
            {selectedLanguage !== "en" && (
              <div className="flex items-center gap-2 bg-green-700/20 px-3 py-1.5 rounded-lg border border-green-700/50">
                <Languages className="w-4 h-4 text-green-400" />
                <span className="text-xs font-medium text-green-300">
                  {selectedLanguage.toUpperCase()}
                </span>
                {(autoTranslateInput || autoTranslateOutput) && (
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                )}
              </div>
            )}
            
            {/* User Info and Actions */}
            <div className="flex items-center gap-2">
              {user && (
                <div className="text-right mr-2">
                  <p className="text-sm font-medium text-white">{user.full_name}</p>
                  <p className="text-xs text-green-300">{user.email}</p>
                </div>
              )}
              {isSuperAdmin && (
                <button
                  onClick={() => navigate('/admin')}
                  className="p-2 hover:bg-green-700/30 rounded-lg transition-all duration-300 text-green-400"
                  title="Admin Dashboard"
                >
                  <Shield className="w-5 h-5" />
                </button>
              )}
              <button
                onClick={logout}
                className="p-2 hover:bg-red-700/30 rounded-lg transition-all duration-300 text-red-400"
                title="Logout"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl p-4 shadow-lg ${
                    message.type === "user"
                      ? "bg-gradient-to-br from-green-700 to-emerald-700 text-white rounded-br-sm"
                      : message.isError
                      ? "bg-red-900/50 border-2 border-red-700 text-red-100 rounded-bl-sm"
                      : message.isWarning
                      ? "bg-yellow-900/50 border-2 border-yellow-700 text-yellow-100 rounded-bl-sm"
                      : "bg-gray-800 border-2 border-green-800 text-gray-100 rounded-bl-sm"
                  }`}
                >
                  {message.type === "bot" && !message.isError && !message.isWarning && (
                    <div className="flex items-center gap-2 mb-2 text-green-400">
                      <Sprout className="w-4 h-4" />
                      <span className="text-xs font-semibold">ShizishanGPT</span>
                    </div>
                  )}
                  {/* Render Markdown for bot messages, plain text for user messages */}
                  {message.type === "bot" ? (
                    <div className="text-sm">
                      <div className="prose-chatbot">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                          {message.text.split('\n\n🔧')[0]}
                        </ReactMarkdown>
                      </div>
                      {message.text.includes('🔧 **Tools used:**') && (
                        <div className="mt-3 pt-2 border-t border-gray-700/50 text-xs text-gray-400">
                          {message.text.split('\n\n🔧')[1] && `🔧 ${message.text.split('🔧 **Tools used:** ')[1]}`}
                        </div>
                      )}
                    </div>
                  ) : (
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                  )}
                  {message.translatedText && message.type === "user" && (
                    <div className="mt-2 pt-2 border-t border-green-600/30">
                      <div className="flex items-center gap-1 text-xs text-green-300/70">
                        <Languages className="w-3 h-3" />
                        <span>Translated to English</span>
                      </div>
                    </div>
                  )}
                  {message.originalText && message.type === "bot" && (
                    <div className="mt-2 pt-2 border-t border-green-700/30">
                      <div className="flex items-center gap-1 text-xs text-gray-400">
                        <Languages className="w-3 h-3" />
                        <span>Auto-translated</span>
                      </div>
                    </div>
                  )}
                  {message.files && message.files.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {message.files.map((file) => (
                        <div
                          key={file.id}
                          className="flex items-center gap-2 p-2 bg-gray-900/50 rounded-lg border border-green-700/30"
                        >
                          {file.type === "image" && (
                            <>
                              <img
                                src={file.url}
                                alt={file.name}
                                className="w-20 h-20 object-cover rounded"
                              />
                              <div className="flex-1 min-w-0">
                                <p className="text-xs text-gray-300 truncate">{file.name}</p>
                                <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                              </div>
                            </>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                  <span className={`text-xs mt-2 block ${message.type === "user" ? "text-green-200" : "text-gray-500"}`}>
                    {(() => {
                      const timestamp = message.timestamp instanceof Date ? message.timestamp : new Date(message.timestamp);
                      return timestamp.toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      });
                    })()}
                  </span>
                </div>
              </div>
            ))}

            {(isTyping || isTranslating) && (
              <div className="flex justify-start">
                <div className="bg-gray-800 border-2 border-green-800 rounded-2xl rounded-bl-sm p-4 shadow-lg">
                  <div className="flex items-center gap-2 mb-2 text-green-400">
                    {isTranslating ? <Languages className="w-4 h-4 animate-pulse" /> : <Loader2 className="w-4 h-4 animate-spin" />}
                    <span className="text-xs font-semibold">
                      {isTranslating ? "Translating..." : "Processing..."}
                    </span>
                  </div>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }}></div>
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }}></div>
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }}></div>
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
              <p className="text-sm text-gray-400 mb-2 font-medium">Quick suggestions:</p>
              <div className="grid grid-cols-2 gap-2">
                {suggestionPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestionClick(prompt.text)}
                    className="flex items-center gap-2 p-3 bg-gray-800 border-2 border-green-800 rounded-xl hover:bg-gray-700 hover:border-green-600 transition-all duration-300 text-left text-sm text-gray-300"
                  >
                    <div className="text-green-500">{prompt.icon}</div>
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
                    <span className="text-xs text-gray-300 max-w-[150px] truncate">{file.name}</span>
                    <button
                      onClick={() => removeFile(file.id)}
                      className="text-gray-400 hover:text-red-400 transition-all duration-300"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="flex gap-2 relative">
              <div className="relative">
                <button
                  onClick={() => setShowAttachMenu(!showAttachMenu)}
                  className="p-3 rounded-full hover:bg-gray-700 transition-all duration-300 text-gray-400 hover:text-green-400"
                >
                  <Paperclip className="w-5 h-5" />
                </button>

                {showAttachMenu && (
                  <div className="absolute bottom-full left-0 mb-2 bg-gray-700 rounded-lg shadow-xl border border-green-700 overflow-hidden">
                    <button
                      onClick={() => imageInputRef.current?.click()}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-600 transition-all duration-300 text-gray-300 hover:text-green-400 w-full text-left"
                    >
                      <Image className="w-4 h-4" />
                      <span className="text-sm">Upload Image</span>
                    </button>
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="flex items-center gap-3 px-4 py-3 hover:bg-gray-600 transition-all duration-300 text-gray-300 hover:text-green-400 w-full text-left border-t border-gray-600"
                    >
                      <FileText className="w-4 h-4" />
                      <span className="text-sm">Upload File</span>
                    </button>
                  </div>
                )}

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
                onKeyPress={(e) => e.key === "Enter" && !isTyping && handleSend()}
                placeholder="Ask me anything about farming..."
                disabled={isTyping}
                className="flex-1 px-4 py-3 border-2 border-green-800 rounded-full focus:outline-none focus:border-green-600 text-gray-100 placeholder-gray-500 bg-gray-900 disabled:opacity-50"
              />
              <button
                onClick={() => handleSend()}
                disabled={(!input.trim() && attachedFiles.length === 0) || isTyping}
                className="bg-gradient-to-r from-green-700 to-emerald-700 text-white p-3 rounded-full hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 shadow-lg"
              >
                {isTyping ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
