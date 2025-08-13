<template>
    <div class="container">
        <h2>Register</h2> 
        <form @submit.prevent = "register" >
            <div class="form-group">
                <label class="form-label" for="email"> Email: </label> 
                <input class="form-control" v-model="email" id="email" type="email" required >
            </div> 
            <div class="form-group">
                <label class="form-label" for="phone"> Phone: </label> 
                <input class="form-control" v-model="phone" id="phone" type="text" required >
            </div> 
            <div>
                <label class="form-label" for="password1"> Password: </label> 
                <input class="form-control" v-model="password1" id="password1" type="password" required >
            </div> 
            <div>
                <label class="form-label" for="password"> Password Confirm: </label> 
                <input class="form-control" v-model="password2" id="password2" type="password" required >
            </div>
            <button class="btn btn-primary mt-5" type="submit">Register</button> 
        </form> 
        <p v-if = "error" > {{error}} </p> 
        <p v-if = "success" > {{success}} </p> 
    </div> 
</template>

<script>
    import {getCSRFToken} from '../store/auth'

export default {
    data() {
        return {
            email: '',
            phone: '',
            password1: '',
            password2: '',
            error: '',
            success: ''
        }
    },
    methods: {
        async register() {
            try {
                const response = await fetch('http://localhost:8000/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        email: this.email,
                        phone: this.phone,
                        password1: this.password1,
                        password2: this.password2
                    }),
                    credentials: 'include'
                })
                const data = await response.json()
                if (response.ok) {
                    this.success = 'Registration successful! Please log in.'
                    setTimeout(() => {
                        this.$router.push('/register-confirmation')
                    }, 500)
                } else {
                    this.error = data.error || 'Registration failed'
                }
            } catch (err) {
                console.log(err)
                this.error = 'An error occurred during registration: ' + err
            }
        }
    }
} 
</script>