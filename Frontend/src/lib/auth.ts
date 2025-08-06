// Authentication utilities

export interface User {
  id: string; // UUID as string
  email: string;
  first_name?: string;
  last_name?: string;
  company_name?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

// Token management
export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
};

export const setToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('auth_token', token);
};

export const removeToken = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('auth_token');
};

export const getUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const setUser = (user: User): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem('user', JSON.stringify(user));
};

export const removeUser = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('user');
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  const token = getToken();
  return !!token;
};

// Logout function
export const logout = (): void => {
  removeToken();
  removeUser();
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}; 