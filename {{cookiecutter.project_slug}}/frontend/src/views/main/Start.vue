<template>
  <router-view></router-view>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { setLoggedIn, actionCheckLoggedIn } from '@/store/constants';
import { store } from '@/store';

const startRouteGuard = async (to, from, next) => {
  await store.dispatch(actionCheckLoggedIn);
  if (store.state.isLoggedIn) {
    if (to.path === '/login' || to.path === '/') {
      next('/main');
    } else {
      next();
    }
  } else if (store.state.isLoggedIn === false) {
    if (to.path !== '/login') {
      next('/login');
    } else {
      next();
    }
  }
};

@Component
export default class Start extends Vue {
  public beforeRouteEnter(to, from, next) {
    startRouteGuard(to, from, next);
  }

  public beforeRouteUpdate(to, from, next) {
    startRouteGuard(to, from, next);
  }
}
</script>
