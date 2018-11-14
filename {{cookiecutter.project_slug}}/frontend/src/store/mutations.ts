import { IUserProfile } from '@/interfaces';
import { State, AppNotification } from '.';


export const mutations = {
    setToken(state: State, payload: string) {
        state.token = payload;
    },
    setLoggedIn(state: State, payload: boolean) {
        state.isLoggedIn = payload;
    },
    setLogInError(state: State, payload: boolean) {
        state.logInError = payload;
    },
    setUserProfile(state: State, payload: IUserProfile) {
        state.userProfile = payload;
    },
    setDashboardMiniDrawer(state: State, payload: boolean) {
        state.dashboardMiniDrawer = payload;
    },
    setDashboardShowDrawer(state: State, payload: boolean) {
        state.dashboardShowDrawer = payload;
    },
    setUsers(state: State, payload: IUserProfile[]) {
        state.admin.users = payload;
    },
    setUser(state: State, payload: IUserProfile) {
        const users = state.admin.users.filter((user: IUserProfile) => user.name !== payload.name);
        users.push(payload);
        state.admin.users = users;
    },
    setRoles(state: State, payload: string[]) {
        state.admin.roles = payload;
    },
    addNotification(state: State, payload: AppNotification) {
        state.notifications.push(payload);
    },
    removeNotification(state: State, payload: AppNotification) {
        state.notifications = state.notifications.filter((notification) => notification !== payload);
    },
};
