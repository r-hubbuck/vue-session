<template>
    <div class="container-sm w-100 mt-5">
        <h1>Code Verification</h1> 
        <p class="mt-4 mb-3">Please check your email for a 5-digit verification code.</p>
        <form @submit.prevent="verify" >
            <div class="form-group">
                <label class="form-label" for="code">Code:</label> 
                <input 
                    class="form-control" 
                    v-model="code" 
                    id="code" 
                    type ="text" 
                    required 
                    @input="resetError" 
                    @blur="validateCode"
                />
                
                <div v-if="codeError || error" class="text-danger mt-4 fw-bold">{{ codeError || error }}</div>
            </div> 

            <button class="btn btn-primary mt-5" type="submit">Verify</button> 
        </form> 

    </div> 
</template>

<script >
    import {useAuthStore} from '../store/auth'

    export default {
        setup() {
            const authStore = useAuthStore();
            return {
                authStore,
            };
        },
        data() {
            return {
                code: "",
                error: "",
                codeError: "",
            };
        },
        methods: {
            validateCode() {
                if (this.code.length !== 5) {
                    this.codeError = "Code must be exactly 5 characters long.";
                } else {
                    this.codeError = "";
                }
            },
            async verify() {
                // Run validations before submitting
                this.validateCode();
                if (this.codeError) {
                    return;
                }

                await this.authStore.verify(this.code, this.$router);
                // Show error from authStore if present
                if (this.authStore.error) {
                    this.error = this.authStore.error;
                } else {
                    this.error = "";
                }
            },
            resetError() {
                this.error = "";
                this.codeError = "";
            }
        },
    };
</script>

<style scoped>
.container-sm {
  max-width: 540px !important;
  width: 100%;
}
</style>