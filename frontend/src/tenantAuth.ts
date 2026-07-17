const TOKEN_KEY = 'tenant_token';

export function getTenantToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setTenantToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearTenantToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export function isTenantAuthenticated(): boolean {
  return !!getTenantToken();
}
