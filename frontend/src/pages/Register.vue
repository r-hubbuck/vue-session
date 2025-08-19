<template>
  <div class="container">
    <h2>Register</h2>
    <form @submit.prevent="register">
      <!-- Email -->
      <div class="form-group">
        <label class="form-label" for="email">Email:</label>
        <input
          class="form-control"
          v-model.trim="email"
          id="email"
          type="email"
          required
          @blur="validateEmail"
        />
        <div v-if="emailError" class="text-danger mt-4 fw-bold">{{ emailError }}</div>
      </div>

      <!-- Phone -->
      <div class="form-group">
        <label class="form-label" for="phone">Phone:</label>
        <input
          class="form-control"
          v-model.trim="phone"
          id="phone"
          type="text"
          required
          @blur="validatePhone"
        />
        <div v-if="phoneError" class="text-danger mt-4 fw-bold">{{ phoneError }}</div>
      </div>

      <!-- Password -->
      <div class="form-group">
        <label class="form-label" for="password1">Password:</label>
        <input
          class="form-control"
          v-model="password1"
          id="password1"
          type="password"
          required
          @blur="validatePasswords"
        />
      </div>

      <!-- Password Confirm -->
      <div class="form-group">
        <label class="form-label" for="password2">Confirm Password:</label>
        <input
          class="form-control"
          v-model="password2"
          id="password2"
          type="password"
          required
          @blur="validatePasswords"
        />
        <div v-if="passwordError" class="text-danger mt-4 fw-bold">{{ passwordError }}</div>
      </div>

      <button class="btn btn-primary mt-5" type="submit">Register</button>
    </form>

    <!-- Server messages -->
    <div v-if="error" class="text-danger mt-4 fw-bold">{{ error }}</div>
    <div v-if="success" class="text-success mt-4 fw-bold">{{ success }}</div>
  </div>
</template>

<script>
import { getCSRFToken } from "../store/auth";

export default {
  data() {
    return {
      email: "",
      phone: "",
      password1: "",
      password2: "",
      error: "",
      success: "",
      emailError: "",
      phoneError: "",
      passwordError: "",
    };
  },
  methods: {
    validateEmail() {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      this.emailError = re.test(this.email)
        ? ""
        : "Please enter a valid email address.";
    },

    validatePhone() {
      // Remove spaces, dashes, parentheses, and plus signs
      const cleaned = this.phone.replace(/[\s\-\(\)\+]/g, "");
      this.phone = cleaned; // store only digits

      const re = /^[0-9]{10,15}$/;
      this.phoneError = re.test(this.phone)
        ? ""
        : "Phone number must be 10-15 digits.";
    },

    validatePasswords() {
      if (this.password1 && this.password2 && this.password1 !== this.password2) {
        this.passwordError = "Passwords do not match.";
      } else if (this.password1.length < 8) {
        this.passwordError = "Password must be at least 8 characters long.";
      } else {
        this.passwordError = "";
      }
    },

    async register() {
      // Run validations before API call
      this.validateEmail();
      this.validatePhone();
      this.validatePasswords();

      if (this.emailError || this.phoneError || this.passwordError) {
        this.error = "Please fix the highlighted errors before submitting.";
        return;
      }

      try {
        const response = await fetch("http://localhost:9000/api/register", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({
            email: this.email,
            phone: this.phone,
            password1: this.password1,
            password2: this.password2,
          }),
          credentials: "include",
        });

        const data = await response.json();
        if (response.ok) {
          this.success = "Registration successful! Please log in.";
          this.error = "";
          setTimeout(() => {
            this.$router.push("/register-confirmation");
          }, 500);
        } else {
          this.error = data.error || "Registration failed";
        }
      } catch (err) {
        console.error(err);
        this.error = "An error occurred during registration: " + err;
      }
    },
  },
};
</script>
