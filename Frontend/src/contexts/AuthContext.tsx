'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, AuthToken, getToken, setToken, removeToken, getUser, setUser, removeUser } from '@/lib/auth';
import { apiClient } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  register: (email: string, password: string, first_name?: string, last_name?: string, company_name?: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUserState] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated on app load
    const token = getToken();
    const savedUser = getUser();
    
    if (token && savedUser) {
      setUserState(savedUser);
    }
    
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await apiClient.login(email, password);
      
      if (response.access_token) {
        setToken(response.access_token);
        
        // For now, create a user object from the login response
        // In a real app, you might want to fetch user details separately
        const userData: User = {
          id: '1', // This would come from the backend
          email: email,
        };
        
        setUser(userData);
        setUserState(userData);
        return { success: true };
      }
      return { success: false, error: 'Login failed' };
    } catch (error: any) {
      console.error('Login error:', error);
      return { success: false, error: error.message || 'Login failed' };
    }
  };

  const register = async (email: string, password: string, first_name?: string, last_name?: string, company_name?: string): Promise<{ success: boolean; error?: string }> => {
    try {
      const response = await apiClient.register({ 
        email, 
        password,
        first_name: first_name || '',
        last_name: last_name || '',
        company_name: company_name || ''
      });
      
      if (response.id) {
        // After successful registration, log the user in
        const loginResult = await login(email, password);
        return loginResult;
      }
      return { success: false, error: 'Registration failed' };
    } catch (error: any) {
      console.error('Registration error:', error);
      return { success: false, error: error.message || 'Registration failed' };
    }
  };

  const logout = () => {
    removeToken();
    removeUser();
    setUserState(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}; 