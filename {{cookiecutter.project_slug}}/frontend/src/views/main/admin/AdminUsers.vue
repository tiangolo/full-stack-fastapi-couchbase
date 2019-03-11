<template>
  <div>
    <v-toolbar light>
      <v-toolbar-title>
        Manage Users
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn color="primary" to="/main/admin/users/create">Create User</v-btn>
    </v-toolbar>
    <v-data-table :headers="headers" :items="users">
      <template slot="items" slot-scope="props">
        <td>{{ props.item.username }}</td>
        <td>{{ props.item.email }}</td>
        <td>{{ props.item.full_name }}</td>
        <td><v-icon v-if="props.item.disabled">block</v-icon></td>
        <td>
          <v-chip v-for="role in props.item.admin_roles" :key="role">{{role}}</v-chip>
        </td>
        <td class="justify-center layout px-0">
          <v-tooltip top>
            <span>Edit</span>
            <v-btn slot="activator" flat :to="{name: 'main-admin-users-edit', params: {username: props.item.username}}">
              <v-icon>edit</v-icon>
            </v-btn>
          </v-tooltip>
        </td>
      </template>
    </v-data-table>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Store } from 'vuex';
import { IUserProfile } from '@/interfaces';
import { readAdminUsers } from '@/store/admin/getters';
import { dispatchGetUsers } from '@/store/admin/actions';

@Component
export default class AdminUsers extends Vue {
  public headers = [
    {
      text: 'Username',
      sortable: true,
      value: 'username',
      align: 'left',
    },
    {
      text: 'Email',
      sortable: true,
      value: 'email',
      align: 'left',
    },
    {
      text: 'Full Name',
      sortable: true,
      value: 'full_name',
      align: 'left',
    },
    {
      text: 'Disabled',
      sortable: true,
      value: 'disabled',
      align: 'left',
    },
    {
      text: 'Roles',
      value: 'admin_roles',
      align: 'left',
    },
    {
      text: 'Actions',
      value: 'username',
    },
  ];
  get users() {
    return readAdminUsers(this.$store);
  }

  public async mounted() {
    await dispatchGetUsers(this.$store);
  }
}
</script>
