<template>
  <div class="container">
    <h1>Login</h1>
    <div>
      <p v-if="hasActivateParam" class="text-success">Your account has been activated!</p>
    </div>
    <form @submit.prevent="login">
      <!-- Email -->
      <div class="form-group">
        <label class="form-label" for="email">Email:</label>
        <input
          class="form-control"
          v-model.trim="email"
          id="email"
          type="text"
          required
          @blur="validateEmail"
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
          @blur="validatePassword"
        />
        <div v-if="passwordError" class="text-danger mt-4 fw-bold">{{ passwordError }}</div>
      </div>

      <div v-if="authStore.serverMessage" class="text-danger mt-4 fw-bold">
        {{ authStore.serverMessage }}
      </div>

      <button class="btn btn-primary mt-5" type="submit">Login</button>
    </form>

    <p class="mt-3">
      Don't have an account yet? Please
      <RouterLink class="" to="/verify">register</RouterLink> now.
    </p>
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
      // Run validations before submitting
      this.validateEmail();
      this.validatePassword();

      if (this.emailError || this.passwordError) {
        return; // stop if there are validation errors
      }

      await this.authStore.login(this.email, this.password, this.$router);
      this.resetForm();
    },
    resetForm() {
      this.email = "";
      this.password = "";
    },
  },
  async mounted() {
    this.authStore.clearMessage();
    const urlParams = new URLSearchParams(window.location.search);
    this.activateParam = urlParams.get("activate");
  },
};
</script>
