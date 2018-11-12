import Vue from 'vue';
import Vuex from 'vuex';
import { getStoreAccessors } from 'vuex-typescript';

import { mutations } from './mutations';
import { actions } from './actions';
import { getters } from './getters';
import { IUserProfile } from '@/interfaces';

export interface AdminState {
  users: IUserProfile[];
  roles: string[];
}

export interface State {
  token: string;
  isLoggedIn: boolean | null;
  logInError: boolean;
  userProfile: IUserProfile | null;
  dashboardMiniDrawer: boolean;
  dashboardShowDrawer: boolean;
  admin: AdminState;
}

Vue.use(Vuex);

const defaultState: State = {
  isLoggedIn: null,
  token: '',
  logInError: false,
  userProfile: null,
  dashboardMiniDrawer: false,
  dashboardShowDrawer: true,
  admin: {
    users: [],
    roles: [],
  },
};

const storeOptions = {
  state: defaultState,
  mutations,
  actions,
  getters,
};

export const store = new Vuex.Store<State>(storeOptions);

export default store;

const {commit, read, dispatch} = getStoreAccessors<State, State>('');

export const readAdminOneUser = read(storeOptions.getters.adminOneUser);
export const readAdminRoles = read(storeOptions.getters.adminRoles);
export const readAdminUsers = read(storeOptions.getters.adminUsers);
export const readDashboardMiniDrawer = read(storeOptions.getters.dashboardMiniDrawer);
export const readDashboardShowDrawer = read(storeOptions.getters.dashboardShowDrawer);
export const readHasAdminAccess = read(storeOptions.getters.hasAdminAccess);
export const readIsLoggedIn = read(storeOptions.getters.isLoggedIn);
export const readLoginError = read(storeOptions.getters.loginError);
export const readToken = read(storeOptions.getters.token);
export const readUserProfile = read(storeOptions.getters.userProfile);

export const commitSetDashboardMiniDrawer = commit(storeOptions.mutations.setDashboardMiniDrawer);
export const commitSetDashboardShowDrawer = commit(storeOptions.mutations.setDashboardShowDrawer);
export const commitSetLoggedIn = commit(storeOptions.mutations.setLoggedIn);
export const commitSetLogInError = commit(storeOptions.mutations.setLogInError);
export const commitSetRoles = commit(storeOptions.mutations.setRoles);
export const commitSetToken = commit(storeOptions.mutations.setToken);
export const commitSetUser = commit(storeOptions.mutations.setUser);
export const commitSetUserProfile = commit(storeOptions.mutations.setUserProfile);
export const commitSetUsers = commit(storeOptions.mutations.setUsers);


export const dispatchCheckApiError = dispatch(storeOptions.actions.actionCheckApiError);
export const dispatchCheckLoggedIn = dispatch(storeOptions.actions.actionCheckLoggedIn);
export const dispatchCreateUser = dispatch(storeOptions.actions.actionCreateUser);
export const dispatchGetRoles = dispatch(storeOptions.actions.actionGetRoles);
export const dispatchGetUserProfile = dispatch(storeOptions.actions.actionGetUserProfile);
export const dispatchGetUsers = dispatch(storeOptions.actions.actionGetUsers);
export const dispatchLogIn = dispatch(storeOptions.actions.actionLogIn);
export const dispatchLogOut = dispatch(storeOptions.actions.actionLogOut);
export const dispatchRemoveLogIn = dispatch(storeOptions.actions.actionRemoveLogIn);
export const dispatchRouteLoggedIn = dispatch(storeOptions.actions.actionRouteLoggedIn);
export const dispatchRouteLogOut = dispatch(storeOptions.actions.actionRouteLogOut);
export const dispatchUpdateUser = dispatch(storeOptions.actions.actionUpdateUser);
export const dispatchUpdateUserProfile = dispatch(storeOptions.actions.actionUpdateUserProfile);
