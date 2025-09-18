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
      <div class="form-group position-relative">
        <label class="form-label" for="password1">Password:</label>
        <input
          class="form-control"
          v-model="password1"
          id="password1"
          type="password"
          required
          @focus="showPasswordReq = true"
          @blur="onPasswordBlur"
          @input="validatePasswords"
          autocomplete="new-password"
          pattern="[A-Za-z0-9!@#$%^&*_=+\-.]{8,}"
        />
  <div v-if="showPasswordReq" class="password-req-box bg-light border rounded p-2" style="z-index:100; position:absolute; left:0; top:100%; min-width:320px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <div :class="{'text-success': passwordLength, 'text-danger': !passwordLength}">
            <span v-if="passwordLength">✔</span><span v-else>✖</span> At least 8 characters
          </div>
          <div :class="{'text-success': passwordUpper, 'text-danger': !passwordUpper}">
            <span v-if="passwordUpper">✔</span><span v-else>✖</span> At least one uppercase letter
          </div>
          <div :class="{'text-success': passwordLower, 'text-danger': !passwordLower}">
            <span v-if="passwordLower">✔</span><span v-else>✖</span> At least one lowercase letter
          </div>
          <div :class="{'text-success': passwordNumber, 'text-danger': !passwordNumber}">
            <span v-if="passwordNumber">✔</span><span v-else>✖</span> At least one number
          </div>
          <div :class="{'text-success': passwordSpecial, 'text-danger': !passwordSpecial}">
            <span v-if="passwordSpecial">✔</span><span v-else>✖</span> At least one special character (!@#$%^&*_=+-.)
          </div>
          <div :class="{'text-success': passwordSafe, 'text-danger': !passwordSafe}">
            <span v-if="passwordSafe">✔</span><span v-else>✖</span> No invalid characters
          </div>
        </div>
      </div>

      <!-- Password Confirm -->
      <div class="form-group position-relative">
        <label class="form-label" for="password2">Confirm Password:</label>
        <input
          class="form-control"
          v-model="password2"
          id="password2"
          type="password"
          required
          @focus="showPassword2Req = true"
          @blur="onPassword2Blur"
          @input="validatePasswords"
          autocomplete="new-password"
          pattern="[A-Za-z0-9!@#$%^&*_=+\-.]{8,}"
        />
  <div v-if="showPassword2Req" class="password-req-box bg-light border rounded p-2" style="z-index:100; position:absolute; left:0; top:100%; min-width:320px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <div :class="{'text-success': password2Length, 'text-danger': !password2Length}">
            <span v-if="password2Length">✔</span><span v-else>✖</span> At least 8 characters
          </div>
          <div :class="{'text-success': password2Upper, 'text-danger': !password2Upper}">
            <span v-if="password2Upper">✔</span><span v-else>✖</span> At least one uppercase letter
          </div>
          <div :class="{'text-success': password2Lower, 'text-danger': !password2Lower}">
            <span v-if="password2Lower">✔</span><span v-else>✖</span> At least one lowercase letter
          </div>
          <div :class="{'text-success': password2Number, 'text-danger': !password2Number}">
            <span v-if="password2Number">✔</span><span v-else>✖</span> At least one number
          </div>
          <div :class="{'text-success': password2Special, 'text-danger': !password2Special}">
            <span v-if="password2Special">✔</span><span v-else>✖</span> At least one special character (!@#$%^&*_=+-.)
          </div>
          <div :class="{'text-success': password2Safe, 'text-danger': !password2Safe}">
            <span v-if="password2Safe">✔</span><span v-else>✖</span> No invalid characters
          </div>
        </div>
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
      showPasswordReq: false,
      showPassword2Req: false,
    };
  },
  computed: {
    passwordLength() {
      return this.password1.length >= 8;
    },
    passwordUpper() {
      return /[A-Z]/.test(this.password1);
    },
    passwordLower() {
      return /[a-z]/.test(this.password1);
    },
    passwordNumber() {
      return /[0-9]/.test(this.password1);
    },
    passwordSpecial() {
      return /[!@#$%^&*_=+\-.]/.test(this.password1);
    },
    passwordSafe() {
      return !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(this.password1);
    },
     password2Length() {
      return this.password2.length >= 8;
    },
    password2Upper() {
      return /[A-Z]/.test(this.password2);
    },
    password2Lower() {
      return /[a-z]/.test(this.password2);
    },
    password2Number() {
      return /[0-9]/.test(this.password2);
    },
    password2Special() {
      return /[!@#$%^&*_=+\-.]/.test(this.password2);
    },
    password2Safe() {
      return !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(this.password2);
    },
  },
  methods: {
     onPasswordBlur() {
      // Hide requirements box only if not focusing confirm field
      setTimeout(() => {
        this.showPasswordReq = false;
      }, 200);
    },

     onPassword2Blur() {
      setTimeout(() => {
        this.showPassword2Req = false;
      }, 200);
    },

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
      // Enforce all requirements for blocking, but only show error if passwords do not match
      const allowedSpecial = /[!@#$%^&*_=+\-.]/;
      const forbidden = /[^A-Za-z0-9!@#$%^&*_=+\-.]/;
      if (this.password1 && this.password2 && this.password1 !== this.password2) {
        this.passwordError = "Passwords do not match.";
      } else {
        this.passwordError = "";
      }
      // Return true if all requirements are met
      return (
        this.password1.length >= 8 &&
        /[A-Z]/.test(this.password1) &&
        /[a-z]/.test(this.password1) &&
        /[0-9]/.test(this.password1) &&
        allowedSpecial.test(this.password1) &&
        !forbidden.test(this.password1)
      );
    },

    async register() {
      // Run validations before API call
      this.validateEmail();
      this.validatePhone();
      const passwordsValid = this.validatePasswords();

      if (
        this.emailError ||
        this.phoneError ||
        this.passwordError ||
        !passwordsValid
      ) {
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
