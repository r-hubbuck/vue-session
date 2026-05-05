<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../store/auth.js'

const authStore = useAuthStore()

onMounted(() => {
  authStore.clearMessage()
})
</script>

<template>
    <div>
        <!-- Page Header -->
        <div class="page-header">
            <div class="page-header-content">
                <h1 class="page-title">Welcome to the Tau Beta Pi Member Portal</h1>
            </div>
        </div>

        <!-- Main Content -->
        <div class="content-container">
            <div v-if="authStore.isAuthenticated">
                <!-- Welcome Section -->
                <div class="section-card">
                    <div class="section-header">
                        <h2 class="section-title">
                            <div class="section-icon">
                                <i class="bi bi-house-door"></i>
                            </div>
                            Dashboard
                        </h2>
                    </div>

                    <div class="info-alert">
                        <i class="bi bi-info-circle-fill"></i>
                        <div class="info-alert-content">
                            Welcome back, <strong>{{ authStore.user?.member?.preferred_first_name || authStore.user?.member?.first_name || authStore.user?.email }}</strong>!
                            You're logged into the Tau Beta Pi Member Portal.
                        </div>
                    </div>

                    <div class="text-center py-4">
                        <img
                            src="/logo_horizontal_blue.png"
                            alt="Tau Beta Pi Logo"
                            class="img-fluid"
                            style="max-width: 400px; width: 100%;"
                        >
                    </div>

                    <div class="row g-4 mt-2">
                        <div v-if="authStore.isAuthenticated" class="col-md-4">
                            <div class="card h-100 text-center p-4" style="border: 1px solid #e2e8f0; border-radius: 12px;">
                                <div class="card-body">
                                    <i class="bi bi-calendar-event" style="font-size: 2.5rem; color: var(--brand-blue);"></i>
                                    <h5 class="mt-3">Convention</h5>
                                    <p class="text-muted">Register for the annual convention</p>
                                    <router-link to="/convention" class="btn btn-primary btn-sm">
                                        Go to Convention
                                    </router-link>
                                </div>
                            </div>
                        </div>

                        <div class="col-md-4">
                            <div class="card h-100 text-center p-4" style="border: 1px solid #e2e8f0; border-radius: 12px;">
                                <div class="card-body">
                                    <i class="bi bi-person-circle" style="font-size: 2.5rem; color: var(--brand-gold);"></i>
                                    <h5 class="mt-3">My Account</h5>
                                    <p class="text-muted">Manage your contact information and account settings</p>
                                    <router-link to="/account" class="btn btn-gold btn-sm">
                                        View Account
                                    </router-link>
                                </div>
                            </div>
                        </div>

                        <div v-if="authStore.isAuthenticated" class="col-md-4">
                            <div class="card h-100 text-center p-4" style="border: 1px solid #e2e8f0; border-radius: 12px;">
                                <div class="card-body">
                                    <i class="bi bi-receipt" style="font-size: 2.5rem; color: var(--brand-blue);"></i>
                                    <h5 class="mt-3">Expense Reports</h5>
                                    <p class="text-muted">Submit and track your travel expenses</p>
                                    <router-link to="/expense-report" class="btn btn-primary btn-sm">
                                        Go to Expense Reports
                                    </router-link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-else class="section-card text-center">
                <h2>You are not logged in</h2>
                <p class="text-muted">Please log in to access the member portal.</p>
                <router-link to="/login" class="btn btn-primary mt-3">
                    Login
                </router-link>
            </div>
        </div>
    </div>
</template>

<style scoped>
.card {
    transition: all 0.3s;
}

.card:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}
</style>
