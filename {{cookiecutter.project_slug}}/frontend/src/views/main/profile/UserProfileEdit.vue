<template>
  <v-container fluid>
    <v-card class="ma-3 pa-3">
      <v-card-title primary-title>
        <div class="headline primary--text">Edit User Profile</div>
      </v-card-title>
      <v-card-text>
        <template>
          <div class="my-3">
            <div class="subheading secondary--text text--lighten-2">Username</div>
            <div class="title primary--text text--darken-2" v-if="userProfile.name">{{userProfile.name}}</div>
            <div class="title primary--text text--darken-2" v-else>-----</div>
          </div>
          <v-form v-model="valid" ref="form" lazy-validation>
            <v-text-field label="Full Name" v-model="fullName" required></v-text-field>
            <v-text-field label="E-mail" type="email" v-model="email" v-validate="'required|email'" data-vv-name="email" :error-messages="errors.collect('email')" required></v-text-field>
            <v-btn @click="submit" :disabled="!valid">
              Save
            </v-btn>
            <v-btn @click="reset">Reset</v-btn>
            <v-btn @click="cancel">Cancel</v-btn>
          </v-form>
        </template>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { Store } from "vuex";
import { actionUpdateUserProfile } from '@/store/constants';
import { IUserProfileUpdate } from '@/interfaces';

@Component
export default class UserProfileEdit extends Vue {
  public valid = true;
  public fullName: string = "";
  public email: string = "";

  public created() {
    if (this.$store.state.userProfile) {
      this.fullName = this.$store.state.userProfile.human_name;
      this.email = this.$store.state.userProfile.email;
    }
  }

  get userProfile() {
    return this.$store.state.userProfile;
  }

  public reset() {
    if (this.$store.state.userProfile) {
      this.fullName = this.$store.state.userProfile.human_name;
      this.email = this.$store.state.userProfile.email;
    }
  }

  public cancel() {
    this.$router.back();
  }

  public async submit() {
    if ((this.$refs.form as any).validate()) {
      const updatedProfile: IUserProfileUpdate = {};
      if (this.fullName) {
        updatedProfile.human_name = this.fullName;
      }
      if (this.email) {
        updatedProfile.email = this.email;
      }
      await this.$store.dispatch(actionUpdateUserProfile, updatedProfile);
      this.$router.push("/main/profile");
    }
  }
}
</script>
