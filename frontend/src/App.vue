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

<style>
.app-wrapper {
  width: 100%;
  min-height: 100vh;
}

.main-content {
  min-height: 100vh;
  width: 100%;
}

.main-content.with-navbar {
  min-height: calc(100vh - 56px);
}
</style>