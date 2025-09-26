<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="">
        <h1 class="text-center mb-3">Reset Your Password</h1>
        <p class="text-muted text-center mb-4">Enter your email address and we'll send you a link to reset your password.</p>
        
        <div v-if="success" class="alert alert-success">
          {{ success }}
        </div>
        
        <form v-else @submit.prevent="requestPasswordReset">
          <div class="mb-3">
            <label for="email" class="form-label">Email:</label>
            <input
              v-model.trim="email"
              type="email"
              class="form-control"
              id="email"
              required
              :disabled="loading"
              @blur="validateEmail"
              @input="validateEmail"
            />
            <div v-if="emailError" class="text-danger mt-2 fw-bold">{{ emailError }}</div>
          </div>

          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <button 
            type="submit"
            class="btn btn-primary w-100 mb-3"
            :disabled="loading || !!emailError"
          >
            {{ loading ? 'Sending...' : 'Send Reset Link' }}
          </button>
        </form>

        <div class="text-center">
          <RouterLink to="/login" class="text-decoration-none">Back to Login</RouterLink>
        </div>
        
        <div class="text-center mt-3">
          Don't have an account yet? Please <RouterLink to="/verify" class="text-decoration-none">register</RouterLink> now.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCSRFToken } from "../store/auth";

export default {
  name: 'PasswordForgot',
  data() {
    return {
      email: "",
      error: "",
      success: "",
      emailError: "",
      loading: false,
    };
  },
  methods: {
    validateEmail() {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.emailError = re.test(this.email)
        ? ""
        : "Please enter a valid email address.";
    },
    
    async requestPasswordReset() {
      this.validateEmail();

      if (this.emailError) {
        return;
      }

      this.loading = true;
      this.error = "";
      this.success = "";

      try {
        const response = await fetch("http://localhost:9000/api/password-reset-request", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({
            email: this.email,
          }),
          credentials: "include",
        });

        const data = await response.json();
        
        if (response.ok) {
          this.success = data.message || "Password reset email has been sent. Please check your inbox.";
          this.email = "";
        } else {
          this.error = data.error || data.message || "Failed to send reset email";
        }
      } catch (err) {
        console.error(err);
        this.error = "An error occurred while sending the reset email. Please try again.";
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    if (this.$store && this.$store.clearMessage) {
      this.$store.clearMessage();
    }
  },
};
</script>