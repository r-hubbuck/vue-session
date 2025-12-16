<template>
  <div class="container mt-2">
    <div class="d-flex">
      <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50 mx-auto">
    </div>
    <h1 class="page-title text-center my-4">Login</h1>
    <div>
      <p v-if="hasActivateParam" class="text-success">Your account has been activated!</p>
    </div>
    <form @submit.prevent="login" class="container-md">
      <!-- Email -->
      <div class="form-group">
        <label class="form-label" for="email">Email:</label>
        <input
          class="form-control"
          v-model.trim="email"
          id="email"
          type="text"
          required
          :disabled="loading"
        />
        <div v-if="emailError" class="text-danger mt-4 fw-bold">{{ emailError }}</div>
      </div>

      <!-- Password -->
      <div class="form-group">
        <label class="form-label" for="password">Password:</label>
        <input
          class="form-control"
          v-model="password"
          id="password"
          type="password"
          required
          :disabled="loading"
        />
        <div v-if="passwordError" class="text-danger mt-4 fw-bold">{{ passwordError }}</div>
      </div>

      <div v-if="authStore.serverMessage" class="text-danger mt-4 fw-bold">
        {{ authStore.serverMessage }}
      </div>

      <button 
        class="btn btn-primary mt-5" 
        type="submit" 
        :disabled="loading"
      >
        {{ loading ? 'Please wait...' : 'Login' }}
      </button>
    </form>
    <div class="container-md mt-5">
      <p class="mt-3">
        <RouterLink class="" to="/password-forgot">Forgot your password?</RouterLink>
      </p>
      <p class="mt-3">Don't have an account yet? Please <RouterLink class="" to="/verify">register</RouterLink> now.</p>
    </div>
    
  </div>
</template>

<script>
import { useAuthStore } from "../store/auth";

export default {
  setup() {
    const authStore = useAuthStore();
    return {
      authStore,
    };
  },
  data() {
    return {
      email: "",
      password: "",
      activateParam: null,
      emailError: "",
      passwordError: "",
      loading: false,
    };
  },
  computed: {
    hasActivateParam() {
      return this.activateParam !== null;
    },
  },
  methods: {
    validateEmail() {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.emailError = re.test(this.email)
        ? ""
        : "Please enter a valid email address.";
    },
    validatePassword() {
      if (!this.password) {
        this.passwordError = "Password cannot be empty.";
      } else if (this.password.length < 8) {
        this.passwordError = "Password must be at least 8 characters long.";
      } else {
        this.passwordError = "";
      }
    },
    async login() {
      // Prevent multiple submissions
      if (this.loading) {
        return;
      }

      // Run validations before submitting
      this.validateEmail();
      this.validatePassword();

      if (this.emailError || this.passwordError) {
        return; // stop if there are validation errors
      }

      this.loading = true;

      try {
        await this.authStore.login(this.email, this.password, this.$router);
        this.resetForm();
      } catch (error) {
        console.error('Login error:', error);
      } finally {
        this.loading = false;
      }
    },
    resetForm() {
      this.email = "";
      this.password = "";
      this.emailError = "";
      this.passwordError = "";
    },
  },
  async mounted() {
    this.authStore.clearMessage();
    const urlParams = new URLSearchParams(window.location.search);
    this.activateParam = urlParams.get("activate");
  },
};
</script>