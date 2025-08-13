<template>
    <div class="container" >
        <h1>Code Verification</h1> 
        <form @submit.prevent="verify" >
            <div class="form-group">
                <label class="form-label" for="code">Code:</label> 
                <input class="form-control" v-model="code" id="code" type ="text" required @input="resetError" >
            </div> 
            <button class="btn btn-primary mt-5" type="submit">Verify</button> 
        </form> 
        <p v-if= "error" class="error">{{error}}</p> 
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
            code: "",
            error: "",
        }
    },
    methods: {
        async verify() {
            await this.authStore.verify(this.code, this.$router)
        },
        resetError() {
            this.error = ""
        }
    },
} 
</script>