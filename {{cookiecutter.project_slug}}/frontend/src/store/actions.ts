import {
    actionLogIn,
    setToken,
    setLoggedIn,
    setLogInError,
    actionGetUserProfile,
    actionRouteLoggedIn,
    actionLogOut,
    setUserProfile,
    actionUpdateUserProfile,
    actionCheckLoggedIn,
    actionRemoveLogIn,
    actionRouteLogOut,
    actionGetUsers,
    actionCheckApiError,
    setUsers,
    actionUpdateUser,
    setUser,
    actionGetRoles,
    setRoles,
    actionCreateUser,
} from './constants';
import { api } from '@/api';
import { saveLocalToken, getLocalToken, removeLocalToken } from '@/utils';
import router from '@/router';
import { ActionTree } from 'vuex';
import { State } from '.';
import { AxiosError } from 'axios';
import { IUserProfileUpdate, IUserProfileCreate } from '@/interfaces';

export const actions: ActionTree<State, {}> = {
    [actionLogIn]: async (context, payload) => {
        try {
            const response = await api.logInGetToken(payload.username, payload.password);
            const token = response.data.access_token;
            if (token) {
                saveLocalToken(token);
                context.commit(setToken, token);
                context.commit(setLoggedIn, true);
                context.commit(setLogInError, false);
                await context.dispatch(actionGetUserProfile);
                await context.dispatch(actionRouteLoggedIn);
            } else {
                await context.dispatch(actionLogOut);
            }
        } catch (err) {
            context.commit(setLogInError, true);
            await context.dispatch(actionLogOut);
        }
    },
    [actionGetUserProfile]: async (context) => {
        try {
            const response = await api.getMe(context.state.token);
            if (response.data) {
                context.commit(setUserProfile, response.data);
            }
        } catch (error) {
            await context.dispatch(actionCheckApiError, error);
        }
    },
    [actionUpdateUserProfile]: async (context, payload) => {
        try {
            const response = await api.updateMe(context.state.token, payload);
            if (response.data) {
                context.commit(setUserProfile, response.data);
            }
        } catch (error) {
            await context.dispatch(actionCheckApiError, error);
        }
    },
    [actionCheckLoggedIn]: async (context) => {
        if (!context.state.isLoggedIn) {
            let token = context.state.token;
            if (!token) {
                const localToken = getLocalToken();
                if (localToken) {
                    context.commit(setToken, localToken);
                    token = localToken;
                }
            }
            if (token) {
                try {
                    const response = await api.getMe(token);
                    context.commit(setLoggedIn, true);
                    context.commit(setUserProfile, response.data);
                } catch (error) {
                    await context.dispatch(actionRemoveLogIn);
                }
            } else {
                await context.dispatch(actionRemoveLogIn);
            }
        }
    },
    [actionRemoveLogIn]: async (context) => {
        removeLocalToken();
        context.commit(setToken, '');
        context.commit(setLoggedIn, false);
    },
    [actionLogOut]: async (context) => {
        await context.dispatch(actionRemoveLogIn);
        await context.dispatch(actionRouteLogOut);
    },
    [actionRouteLogOut]: (context) => {
        if (router.currentRoute.path !== '/login') {
            router.push('/login');
        }
    },
    [actionCheckApiError]: async (context, payload: AxiosError) => {
        if (payload.response!.status === 401) {
            await context.dispatch(actionLogOut);
        }
    },
    [actionRouteLoggedIn]: (context) => {
        if (router.currentRoute.path === '/login' || router.currentRoute.path === '/') {
            router.push('/main');
        }
    },
    [actionGetUsers]: async (context) => {
        try {
            const response = await api.getUsers(context.state.token);
            if (response) {
                context.commit(setUsers, response.data);
            }
        } catch (error) {
            await context.dispatch(actionCheckApiError, error);
        }
    },
    [actionUpdateUser]: async (context, payload: {name: string, user: IUserProfileUpdate}) => {
        try {
            const response = await api.updateUser(context.state.token, payload.name, payload.user);
            context.commit(setUser, response.data);
        } catch (error) {
            context.dispatch(actionCheckApiError, error);
        }
    },
    [actionCreateUser]: async (context, payload: IUserProfileCreate) => {
        try {
            const response = await api.createUser(context.state.token, payload);
            context.commit(setUser, response.data);
        } catch (error) {
            context.dispatch(actionCheckApiError, error);
        }
    },
    [actionGetRoles]: async (context) => {
        try {
            const response = await api.getRoles(context.state.token);
            context.commit(setRoles, response.data.roles);
        } catch (error) {
            context.dispatch(actionCheckApiError, error);
        }
    },
};
