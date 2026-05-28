import api from '@/api';
import type { User, PageResult } from '@/types';
import type { ApiSuccess } from '@/types/api';

export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  role: User['role'];
  real_name?: string;
}

export interface UserUpdateRequest {
  email?: string;
  role?: User['role'];
  real_name?: string;
  is_active?: boolean;
  password?: string;
}

export function listUsers(
  page = 1,
  pageSize = 20
): Promise<ApiSuccess<PageResult<User>>> {
  return api
    .get('/admin/users', { params: { page, page_size: pageSize } })
    .then((res) => res.data);
}

export function createUser(
  data: UserCreateRequest
): Promise<ApiSuccess<User>> {
  return api.post('/admin/users', data).then((res) => res.data);
}

export function updateUser(
  userId: string,
  data: UserUpdateRequest
): Promise<ApiSuccess<User>> {
  return api.put(`/admin/users/${userId}`, data).then((res) => res.data);
}

export function deleteUser(userId: string): Promise<ApiSuccess<null>> {
  return api.delete(`/admin/users/${userId}`).then((res) => res.data);
}
