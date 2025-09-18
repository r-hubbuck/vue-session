<script>
import { useAuthStore } from '../store/auth.js'
import { useRouter } from 'vue-router'

export default {
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()

        return {
            authStore,
            router
        }
    },
    methods: {
        async logout() {
            try {
                await this.authStore.logout(this.$router)
            } catch (error) {
                console.error(error)
            }
        },
    },
    async mounted() {
        this.authStore.clearMessage()
        await this.authStore.fetchUser()
    },
}
</script>

<template>
    <div>
        <h1>Welcome to the home page</h1>  
        <div v-if="authStore.isAuthenticated">
            <p>Hi there {{ authStore.user?.email }}!</p> 
            <p>You are logged in.</p> 
            <div class="button-group">
                <button @click="$router.push('/addresses')" class="btn-addresses">View My Addresses</button>
                <button @click="logout" class="btn-logout">Logout</button>
            </div>
        </div> 
        <p v-else >You are not logged in. <RouterLink class="" to="/login">Login</RouterLink></p>
    </div>
</template>

<style scoped>
.button-group {
    display: flex;
    gap: 15px;
    margin-top: 20px;
    justify-content: center;
}

.btn-addresses, .btn-logout {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    transition: background-color 0.2s ease;
}

.btn-addresses {
    background-color: #28a745;
    color: white;
}

.btn-addresses:hover {
    background-color: #218838;
}

.btn-logout {
    background-color: #dc3545;
    color: white;
}

.btn-logout:hover {
    background-color: #c82333;
}
</style>