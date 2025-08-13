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
            <p>Hi there {{ authStore.user?.username }}!</p> 
            <p>You are logged in.</p> 
            <button @click="logout" > Logout </button> 
        </div> 
        <p v-else >You are not logged in. <RouterLink class="" to="/login">Login</RouterLink></p>
    </div>
</template>