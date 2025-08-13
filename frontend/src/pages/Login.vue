<template>
    <div class="container" >
        <h1>Login</h1> 
        <div>
            <p v-if="hasActivateParam" class="text-danger">Your account has been activated!</p>
        </div>
        <form @submit.prevent="login" >
            <div class="form-group">
                <label class="form-label" for="email">Email:</label> 
                <input class="form-control" v-model="email" id="email" type ="text" required>
            </div> 
            <div class="form-group">
                <label class="form-label" for="password">Password:</label> 
                <input class="form-control" v-model="password" id="password" type="password" required>
            </div> 
            <div v-if="authStore.serverMessage" class="text-danger mt-4 fw-bold">
                {{ authStore.serverMessage }}
            </div>
            <button class="btn btn-primary mt-5" type="submit">Login</button> 
        </form> 
        <p class="mt-3">Don't have an account yet? Please <RouterLink class="" to="/verify">register</RouterLink> now.</p>
    </div> 
</template>

<script >
    import {useAuthStore} from '../store/auth'

export default {
    setup() {
        const authStore = useAuthStore()
        return {
            authStore
        }
    },
    data() {
        return {
            email: "",
            password: "",
            activateParam: null,
        }
    },
    computed: {
        hasActivateParam() {
            return this.activateParam !== null;
        },
    },
    methods: {
        async login() {
            await this.authStore.login(this.email, this.password, this.$router)
            this.resetForm()
        },
        resetForm() {
            this.email = "",
            this.password = ""
        //   this.formData = {
        //     selectedChapter: "",
        //     email: "",
        //     selectedYear: new Date().getFullYear(),
        //   };
        }
    },
    async mounted() {
        this.authStore.clearMessage()
        const urlParams = new URLSearchParams(window.location.search);
        this.activateParam = urlParams.get('activate');
    },
} 
</script>