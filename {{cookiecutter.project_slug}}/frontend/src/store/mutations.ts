import { MutationTree } from 'vuex';
import {
    setToken,
    setLoggedIn,
    setLogInError,
    setUserProfile,
    setDashboardMiniDrawer,
    setDashboardShowDrawer,
    setUsers,
    setUser,
    setRoles,
} from './constants';
import { IUserProfile } from '@/interfaces';
import { State } from '.';


export const mutations: MutationTree<State> = {
    [setToken]: (state, payload: string) => {
        state.token = payload;
    },
    [setLoggedIn]: (state, payload: boolean) => {
        state.isLoggedIn = payload;
    },
    [setLogInError]: (state, payload: boolean) => {
        state.logInError = payload;
    },
    [setUserProfile]: (state, payload: IUserProfile) => {
        state.userProfile = payload;
    },
    [setDashboardMiniDrawer]: (state, payload: boolean) => {
        state.dashboardMiniDrawer = payload;
    },
    [setDashboardShowDrawer]: (state, payload: boolean) => {
        state.dashboardShowDrawer = payload;
    },
    [setUsers]: (state, payload: IUserProfile[]) => {
        state.admin.users = payload;
    },
    [setUser]: (state, payload: IUserProfile) => {
        const users = state.admin.users.filter((user: IUserProfile) => user.name !== payload.name);
        users.push(payload);
        state.admin.users = users;
    },
    [setRoles]: (state, payload: string[]) => {
        state.admin.roles = payload;
    },
};
