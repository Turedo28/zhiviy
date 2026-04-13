export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const clearAuthToken = () => {
  localStorage.removeItem('access_token');
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

export const logout = () => {
  clearAuthToken();
  window.location.href = '/';
};
