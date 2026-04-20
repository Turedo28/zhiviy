export const setAuthToken = (token: string) => {
  localStorage.setItem('access_token', token);
  document.cookie = `access_token=${token}; path=/; max-age=86400; SameSite=Strict`;
};

export const getAuthToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const clearAuthToken = () => {
  localStorage.removeItem('access_token');
  document.cookie = 'access_token=; path=/; max-age=0';
};

export const isAuthenticated = (): boolean => {
  return !!getAuthToken();
};

export const logout = () => {
  clearAuthToken();
  window.location.href = '/';
};
