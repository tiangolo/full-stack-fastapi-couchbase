import axios from 'axios';
import { apiUrl } from '@/env';
import { IUserProfile, IUserProfileUpdate, IUserProfileCreate } from './interfaces';

const logInGetToken = async (username: string, password: string) => {
  return axios.post(`${apiUrl}/api/v1/login/access-token`, {
    username,
    password,
  });
};

const getMe = async (token: string) => {
  return axios.get<IUserProfile>(`${apiUrl}/api/v1/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

const updateMe = async (token: string, data: IUserProfileUpdate) => {
  return axios.put<IUserProfile>(`${apiUrl}/api/v1/users/me`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

const getUsers = async (token: string) => {
  return axios.get<IUserProfile[]>(`${apiUrl}/api/v1/users/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

const updateUser = async (token: string, name: string, data: IUserProfileUpdate) => {
  return axios.put(`${apiUrl}/api/v1/users/${name}`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

const createUser = async (token: string, data: IUserProfileCreate) => {
  return axios.post(`${apiUrl}/api/v1/users/`, data, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

const getRoles = async (token: string) => {
  return axios.get(`${apiUrl}/api/v1/roles/`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
};

export const api = {
  logInGetToken,
  getMe,
  updateMe,
  getUsers,
  updateUser,
  createUser,
  getRoles,
};
