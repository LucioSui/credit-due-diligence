import api from '@/api';
import type { LoginRequest, TokenPayload, User } from '@/types';
import type { ApiSuccess } from '@/types/api';

/** Login with username and password */
export function login(req: LoginRequest): Promise<ApiSuccess<TokenPayload>> {
  return api.post('/auth/login', req).then((res) => res.data);
}

/** Get current user info */
export function getMe(): Promise<ApiSuccess<User>> {
  return api.get('/auth/me').then((res) => res.data);
}

/** Change password */
export function changePassword(oldPassword: string, newPassword: string): Promise<ApiSuccess<null>> {
  return api.put('/auth/password', { old_password: oldPassword, new_password: newPassword }).then((res) => res.data);
}
