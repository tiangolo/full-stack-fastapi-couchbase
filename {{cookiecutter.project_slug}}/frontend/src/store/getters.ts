import { State } from '.';

export const getters = {
    hasAdminAccess: (state: State) => {
        return (
            state.userProfile &&
            state.userProfile.admin_roles.includes('superuser'));
    },
    loginError: (state: State) => state.logInError,
    dashboardShowDrawer: (state: State) => state.dashboardShowDrawer,
    dashboardMiniDrawer: (state: State) => state.dashboardMiniDrawer,
    userProfile: (state: State) => state.userProfile,
    token: (state: State) => state.token,
    isLoggedIn: (state: State) => state.isLoggedIn,
    adminUsers: (state: State) => state.admin.users,
    adminRoles: (state: State) => state.admin.roles,
    adminOneUser: (state: State) => (name: string) => {
        const filteredUsers = state.admin.users.filter((user) => user.name === name);
        if (filteredUsers.length > 0) {
            return { ...filteredUsers[0] };
        }
    },
};
