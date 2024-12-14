<template>
  <v-app>
    <v-app-bar color="blue-lighten-5">
      <v-app-bar-title>
        <router-link style="text-decoration: none; color: inherit;" to="/">AI Ticketing</router-link>
      </v-app-bar-title>
    </v-app-bar>
    <v-main class="bg-indigo-lighten-5">

      <v-navigation-drawer permanent>
        <v-list nav>
          <v-list-item prepend-icon="mdi-home" to="/">
            <v-list-item-title>Home</v-list-item-title>
          </v-list-item>
          <v-list-item prepend-icon="mdi-account-circle" to="/account">
            <v-list-item-title>Account</v-list-item-title>
          </v-list-item>
          <v-list-item prepend-icon="mdi-information" to="/about">
            <v-list-item-title>About</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-navigation-drawer>

      <v-container >
        <NuxtPage/>
      </v-container>

    </v-main>

    <v-footer color="purple-lighten-2" style="z-index:1005">
      <span>&copy; 2024 AI Ticketing - 2024952850 - COSE43200 </span>
    </v-footer>  
  </v-app>
</template>
