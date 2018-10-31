import { GetterTree } from 'vuex';
import { State } from '.';

export const getters: GetterTree<State, {}> = {
    hasAdminAccess: (state) => {
        return (
            state.userProfile &&
            state.userProfile.admin_roles.includes('admin') &&
            state.userProfile.admin_roles.includes('superuser'));
    },
};
