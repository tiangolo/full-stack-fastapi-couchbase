import { State, storeOptions } from '.';
import { getStoreAccessors } from 'vuex-typescript';

const {commit, read, dispatch} = getStoreAccessors<State, State>('');

const {getters, mutations, actions} = storeOptions;

export const readAdminOneUser = read(getters.adminOneUser);
export const readAdminRoles = read(getters.adminRoles);
export const readAdminUsers = read(getters.adminUsers);
export const readDashboardMiniDrawer = read(getters.dashboardMiniDrawer);
export const readDashboardShowDrawer = read(getters.dashboardShowDrawer);
export const readHasAdminAccess = read(getters.hasAdminAccess);
export const readIsLoggedIn = read(getters.isLoggedIn);
export const readLoginError = read(getters.loginError);
export const readToken = read(getters.token);
export const readUserProfile = read(getters.userProfile);

export const commitSetDashboardMiniDrawer = commit(mutations.setDashboardMiniDrawer);
export const commitSetDashboardShowDrawer = commit(mutations.setDashboardShowDrawer);
export const commitSetLoggedIn = commit(mutations.setLoggedIn);
export const commitSetLogInError = commit(mutations.setLogInError);
export const commitSetRoles = commit(mutations.setRoles);
export const commitSetToken = commit(mutations.setToken);
export const commitSetUser = commit(mutations.setUser);
export const commitSetUserProfile = commit(mutations.setUserProfile);
export const commitSetUsers = commit(mutations.setUsers);

export const dispatchCheckApiError = dispatch(actions.actionCheckApiError);
export const dispatchCheckLoggedIn = dispatch(actions.actionCheckLoggedIn);
export const dispatchCreateUser = dispatch(actions.actionCreateUser);
export const dispatchGetRoles = dispatch(actions.actionGetRoles);
export const dispatchGetUserProfile = dispatch(actions.actionGetUserProfile);
export const dispatchGetUsers = dispatch(actions.actionGetUsers);
export const dispatchLogIn = dispatch(actions.actionLogIn);
export const dispatchLogOut = dispatch(actions.actionLogOut);
export const dispatchRemoveLogIn = dispatch(actions.actionRemoveLogIn);
export const dispatchRouteLoggedIn = dispatch(actions.actionRouteLoggedIn);
export const dispatchRouteLogOut = dispatch(actions.actionRouteLogOut);
export const dispatchUpdateUser = dispatch(actions.actionUpdateUser);
export const dispatchUpdateUserProfile = dispatch(actions.actionUpdateUserProfile);
