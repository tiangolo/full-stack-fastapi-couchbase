import { AdminState } from './state';
import { getStoreAccessors } from 'typesafe-vuex';
import { State } from '../state';

export const getters = {
    adminUsers: (state: AdminState) => state.users,
    adminRoles: (state: AdminState) => state.roles,
    adminOneUser: (state: AdminState) => (username: string) => {
        const filteredUsers = state.users.filter((user) => user.username === username);
        if (filteredUsers.length > 0) {
            return { ...filteredUsers[0] };
        }
    },
};

const { read } = getStoreAccessors<AdminState, State>('');

export const readAdminOneUser = read(getters.adminOneUser);
export const readAdminRoles = read(getters.adminRoles);
export const readAdminUsers = read(getters.adminUsers);
