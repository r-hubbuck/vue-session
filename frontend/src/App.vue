<script setup>
import { RouterView } from 'vue-router'
import Navbar from './components/Navbar.vue'
import { useAuthStore } from './store/auth'

const authStore = useAuthStore()
</script>

<template>
  <div class="app-wrapper">
    <!-- Show navbar only when user is authenticated - positioned outside container -->
    <Navbar v-if="authStore.isAuthenticated" />
    
    <!-- Main content with centered container -->
    <div class="main-content" :class="{ 'with-navbar': authStore.isAuthenticated }">
      <div class="content-container">
        <RouterView />
      </div>
    </div>
  </div>
</template>
