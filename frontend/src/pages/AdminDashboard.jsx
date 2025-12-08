import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Users,
  Shield,
  Trash2,
  CheckCircle,
  XCircle,
  Search,
  ArrowLeft,
  Loader,
  AlertCircle,
  MessageSquare,
  Crown,
  UserCheck,
  UserX
} from 'lucide-react';
import axios from 'axios';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const { user, isSuperAdmin, token } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [processingUserId, setProcessingUserId] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  useEffect(() => {
    if (!isSuperAdmin()) {
      navigate('/chat');
    } else {
      fetchUsers();
    }
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/auth/users`, {
        headers: { Authorization: `Bearer ${token}` },
        params: { limit: 1000 }
      });
      setUsers(response.data);
    } catch (err) {
      setError('Failed to load users: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
    }
  };

  const handleManageUser = async (userId, action) => {
    if (processingUserId) return;

    const confirmMessages = {
      activate: 'Are you sure you want to activate this user?',
      deactivate: 'Are you sure you want to deactivate this user?',
      grant_admin: 'Are you sure you want to grant admin privileges?',
      revoke_admin: 'Are you sure you want to revoke admin privileges?',
      delete: 'Are you sure you want to DELETE this user? This action cannot be undone!'
    };

    if (!window.confirm(confirmMessages[action])) {
      return;
    }

    try {
      setProcessingUserId(userId);
      setError('');
      setSuccessMessage('');

      await axios.post(
        `${API_URL}/api/auth/users/${userId}/manage`,
        { action },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setSuccessMessage(`User ${action.replace('_', ' ')} successful!`);
      await fetchUsers();

      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || `Failed to ${action} user`);
    } finally {
      setProcessingUserId(null);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (processingUserId) return;

    if (!window.confirm('⚠️ PERMANENT DELETE - Are you absolutely sure? This cannot be undone!')) {
      return;
    }

    try {
      setProcessingUserId(userId);
      setError('');
      setSuccessMessage('');

      await axios.delete(`${API_URL}/api/auth/users/${userId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setSuccessMessage('User deleted successfully!');
      await fetchUsers();

      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete user');
    } finally {
      setProcessingUserId(null);
    }
  };

  const filteredUsers = users.filter(u =>
    u.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.full_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.role?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'superadmin': return 'bg-purple-600 text-white';
      case 'admin': return 'bg-blue-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  const getRoleIcon = (role) => {
    switch (role) {
      case 'superadmin': return <Crown className="w-4 h-4" />;
      case 'admin': return <Shield className="w-4 h-4" />;
      default: return <Users className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-green-400 mx-auto mb-4" />
          <p className="text-white text-lg">Loading users...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-green-900 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/chat')}
            className="mb-4 flex items-center gap-2 text-green-400 hover:text-green-300 transition"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Chat
          </button>
          
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3 bg-green-700/30 rounded-xl">
                <Shield className="w-8 h-8 text-green-400" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-gray-400">Manage users and permissions</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-400 text-sm">Total Users</p>
              <p className="text-3xl font-bold text-white">{users.length}</p>
            </div>
          </div>
        </div>

        {/* Alerts */}
        {error && (
          <div className="mb-6 p-4 bg-red-900/50 border border-red-700 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-900/50 border border-green-700 rounded-lg flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
            <p className="text-green-200">{successMessage}</p>
          </div>
        )}

        {/* Search */}
        <div className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by name, email, or role..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-gray-800 border border-gray-700 text-white rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Users className="w-8 h-8 text-blue-400" />
              <div>
                <p className="text-gray-400 text-sm">Total Users</p>
                <p className="text-2xl font-bold text-white">{users.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <Shield className="w-8 h-8 text-purple-400" />
              <div>
                <p className="text-gray-400 text-sm">Admins</p>
                <p className="text-2xl font-bold text-white">
                  {users.filter(u => u.role === 'admin' || u.role === 'superadmin').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <UserCheck className="w-8 h-8 text-green-400" />
              <div>
                <p className="text-gray-400 text-sm">Active Users</p>
                <p className="text-2xl font-bold text-white">
                  {users.filter(u => u.is_active).length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <UserX className="w-8 h-8 text-red-400" />
              <div>
                <p className="text-gray-400 text-sm">Inactive Users</p>
                <p className="text-2xl font-bold text-white">
                  {users.filter(u => !u.is_active).length}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Users Table */}
        <div className="bg-gray-800 border border-gray-700 rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900 border-b border-gray-700">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Location
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Joined
                  </th>
                  <th className="px-6 py-4 text-right text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {filteredUsers.length === 0 ? (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-gray-400">
                      No users found
                    </td>
                  </tr>
                ) : (
                  filteredUsers.map((u) => (
                    <tr key={u.id} className="hover:bg-gray-700/50 transition">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-green-700 to-emerald-700 rounded-full flex items-center justify-center text-white font-bold">
                            {u.full_name?.charAt(0).toUpperCase() || 'U'}
                          </div>
                          <div>
                            <p className="font-medium text-white">{u.full_name || 'Unknown'}</p>
                            <p className="text-sm text-gray-400">{u.email}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${getRoleBadgeColor(u.role)}`}>
                          {getRoleIcon(u.role)}
                          {u.role?.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        {u.is_active ? (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-900/50 text-green-400 rounded-full text-xs font-semibold">
                            <CheckCircle className="w-3 h-3" />
                            Active
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-red-900/50 text-red-400 rounded-full text-xs font-semibold">
                            <XCircle className="w-3 h-3" />
                            Inactive
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 text-gray-300 text-sm">
                        {u.location || '-'}
                      </td>
                      <td className="px-6 py-4 text-gray-400 text-sm">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : '-'}
                      </td>
                      <td className="px-6 py-4">
                        {u.id === user?.id ? (
                          <span className="text-xs text-gray-500 italic">You</span>
                        ) : (
                          <div className="flex items-center justify-end gap-2">
                            {/* Activate/Deactivate */}
                            <button
                              onClick={() => handleManageUser(u.id, u.is_active ? 'deactivate' : 'activate')}
                              disabled={processingUserId === u.id}
                              className={`p-2 rounded-lg transition ${
                                u.is_active
                                  ? 'hover:bg-red-900/50 text-red-400'
                                  : 'hover:bg-green-900/50 text-green-400'
                              } disabled:opacity-50`}
                              title={u.is_active ? 'Deactivate' : 'Activate'}
                            >
                              {processingUserId === u.id ? (
                                <Loader className="w-4 h-4 animate-spin" />
                              ) : u.is_active ? (
                                <XCircle className="w-4 h-4" />
                              ) : (
                                <CheckCircle className="w-4 h-4" />
                              )}
                            </button>

                            {/* Grant/Revoke Admin */}
                            {u.role !== 'superadmin' && (
                              <button
                                onClick={() => handleManageUser(u.id, u.role === 'admin' ? 'revoke_admin' : 'grant_admin')}
                                disabled={processingUserId === u.id}
                                className="p-2 hover:bg-blue-900/50 text-blue-400 rounded-lg transition disabled:opacity-50"
                                title={u.role === 'admin' ? 'Revoke Admin' : 'Grant Admin'}
                              >
                                <Shield className="w-4 h-4" />
                              </button>
                            )}

                            {/* Delete */}
                            <button
                              onClick={() => handleDeleteUser(u.id)}
                              disabled={processingUserId === u.id}
                              className="p-2 hover:bg-red-900/50 text-red-400 rounded-lg transition disabled:opacity-50"
                              title="Delete User"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Info Footer */}
        <div className="mt-6 text-center text-gray-500 text-sm">
          <p>Showing {filteredUsers.length} of {users.length} users</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
