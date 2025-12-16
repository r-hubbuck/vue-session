<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { useAuthStore } from './store/auth'

const authStore = useAuthStore()
</script>

<template>
  <div id="app">
    <!-- Show navbar when user is authenticated -->
    <Navbar v-if="authStore.isAuthenticated" />
    
    <!-- Main content area -->
    <div class="main-content" :class="{ 'with-navbar': authStore.isAuthenticated }">
      <RouterView />
    </div>
  </div>
</template>

<style>
/* Global styles are in style.css */
</style>
