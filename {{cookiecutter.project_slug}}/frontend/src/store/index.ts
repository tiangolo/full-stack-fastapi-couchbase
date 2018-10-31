import Vue from 'vue';
import Vuex from 'vuex';

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

export const store = new Vuex.Store<State>({
  state: defaultState,
  mutations,
  actions,
  getters,
});

export default store;
