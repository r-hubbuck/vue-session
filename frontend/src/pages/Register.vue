<template>
  <div class="container mt-5">
    <h2>Register</h2>
    <form @submit.prevent="register" class="container-md">
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
      <!-- <div class="form-group">
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
      </div> -->

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
  <div v-if="showPasswordReq" class="password-req-box bg-light border rounded p-2" style="text-align:left; z-index:100; position:absolute; left:0; top:100%; min-width:320px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <div class="small">
            <span v-if="passwordLength" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': passwordLength, 'text-danger': !passwordLength}"> At least 8 characters</span>
          </div>
          <div class="small">
            <span v-if="passwordUpper" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': passwordUpper, 'text-danger': !passwordUpper}"> At least one uppercase letter</span>
          </div>
          <div class="small">
            <span v-if="passwordLower" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': passwordLower, 'text-danger': !passwordLower}"> At least one lowercase letter</span>
          </div>
          <div class="small">
            <span v-if="passwordNumber" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': passwordNumber, 'text-danger': !passwordNumber}"> At least one number</span>
          </div>
          <div class="small">
            <span v-if="passwordSpecial" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': passwordSpecial, 'text-danger': !passwordSpecial}"> At least one special character (!@#$%^&*_=+-.)</span>
          </div>
          <div class="small">
            <span v-if="passwordSafe" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': passwordSafe, 'text-danger': !passwordSafe}"> No invalid characters</span>
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
  <div v-if="showPassword2Req" class="password-req-box bg-light border rounded p-2" style="text-align:left; z-index:100; position:absolute; left:0; top:100%; min-width:320px; box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          <div class="small">
            <span v-if="password2Length" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': password2Length, 'text-danger': !password2Length}"> At least 8 characters</span>
          </div>
          <div class="small">
            <span v-if="password2Upper" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': password2Upper, 'text-danger': !password2Upper}"> At least one uppercase letter</span>
          </div>
          <div class="small">
            <span v-if="password2Lower" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': password2Lower, 'text-danger': !password2Lower}"> At least one lowercase letter</span>
          </div>
          <div class="small">
            <span v-if="password2Number" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': password2Number, 'text-danger': !password2Number}"> At least one number</span>
          </div>
          <div class="small">
            <span v-if="password2Special" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': password2Special, 'text-danger': !password2Special}"> At least one special character (!@#$%^&*_=+-.)</span>
          </div>
          <div class="small">
            <span v-if="password2Safe" style="color: #28a745; font-weight: bold;">✓</span>
            <span v-else style="color: red !important; margin-right: 5px;">✗</span>
            <span :class="{'text-success': password2Safe, 'text-danger': !password2Safe}"> No invalid characters</span>
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
import api from '../api'
import { useAuthStore } from '../store/auth'

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
      // phone: "",
      password1: "",
      password2: "",
      error: "",
      success: "",
      emailError: "",
      // phoneError: "",
      passwordError: "",
      showPasswordReq: false,
      showPassword2Req: false,
    };
  },
  mounted() {
    // Pre-fill email if user came from verification
    if (this.authStore.verificationEmail) {
      this.email = this.authStore.verificationEmail
    }
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

    // validatePhone() {
    //   const cleaned = this.phone.replace(/[\s\-\(\)\+]/g, "");
    //   this.phone = cleaned;

    //   const re = /^[0-9]{10,15}$/;
    //   this.phoneError = re.test(this.phone)
    //     ? ""
    //     : "Phone number must be 10-15 digits.";
    // },

    validatePasswords() {
      const allowedSpecial = /[!@#$%^&*_=+\-.]/;
      const forbidden = /[^A-Za-z0-9!@#$%^&*_=+\-.]/;
      
      if (this.password1 && this.password2 && this.password1 !== this.password2) {
        this.passwordError = "Passwords do not match.";
      } else {
        this.passwordError = "";
      }
      
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
      this.validateEmail();
      // this.validatePhone();
      const passwordsValid = this.validatePasswords();

      if (
        this.emailError ||
        // this.phoneError ||
        this.passwordError ||
        !passwordsValid
      ) {
        this.error = "Please fix the highlighted errors before submitting.";
        return;
      }

      try {
        const response = await api.post('/api/register', {
          email: this.email,
          // phone: this.phone,
          password1: this.password1,
          password2: this.password2,
        });

        this.success = "Registration successful! Please log in.";
        this.error = "";
        
        // Clear verification after successful registration
        this.authStore.clearVerification()
        
        setTimeout(() => {
          this.$router.push("/email-confirmation");
        }, 500);
      } catch (err) {
        console.error(err);
        this.error = err.response?.data?.error || "Registration failed";
      }
    },
  },
};
</script>