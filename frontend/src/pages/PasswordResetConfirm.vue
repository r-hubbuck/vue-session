<template>
  <div class="container mt-2">
    <!-- <div class="row justify-content-center">
      <div class=""> -->
        <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50">
        <h1 class="mt-4 mb-3">Set New Password</h1>
        <div v-if="tokenError" class="alert alert-danger">
          {{ tokenError }}
          <div class="mt-2">
            <RouterLink to="/password-forgot" class="text-decoration-none">Request a new reset link</RouterLink>
          </div>
        </div>
        
        <div v-else-if="success" class="alert alert-success">
          {{ success }}
        </div>
        
        <form v-else @submit.prevent="resetPassword" class="container-md">
          <div class="mb-3 position-relative">
            <label for="newPassword1" class="form-label">New Password:</label>
            <input
              v-model="newPassword1"
              type="password"
              class="form-control"
              id="newPassword1"
              required
              :disabled="loading"
              @focus="showPasswordReq = true"
              @blur="onPasswordBlur"
              @input="validatePasswords"
              autocomplete="new-password"
            />
            <div v-if="showPasswordReq" class="position-absolute bg-light border rounded shadow-sm p-2 mt-1" style="text-align: left; z-index: 1050; min-width: 320px;">
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

          <div class="mb-3 position-relative">
            <label for="newPassword2" class="form-label">Confirm New Password:</label>
            <input
              v-model="newPassword2"
              type="password"
              class="form-control"
              id="newPassword2"
              required
              :disabled="loading"
              @focus="showPassword2Req = true"
              @blur="onPassword2Blur"
              @input="validatePasswords"
              autocomplete="new-password"
            />
            <div v-if="showPassword2Req" class="position-absolute bg-light border rounded shadow-sm p-2 mt-1" style="text-align: left; z-index: 1050; min-width: 320px;">
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
            <div v-if="passwordError" class="text-danger mt-2 fw-bold">{{ passwordError }}</div>
          </div>

          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <button 
            type="submit"
            class="btn btn-primary mt-5"
            :disabled="loading || !isFormValid"
          >
            {{ loading ? 'Updating...' : 'Update Password' }}
          </button>
        </form>

        <p class="text-center mt-3">
          <RouterLink to="/login" class="text-decoration-none">Back to Login</RouterLink>
        </p>
      </div>
    <!-- </div>
  </div> -->
</template>

<script>
import api from '../api'

export default {
  name: 'PasswordResetConfirm',
  data() {
    return {
      newPassword1: "",
      newPassword2: "",
      error: "",
      success: "",
      tokenError: "",
      passwordError: "",
      loading: false,
      showPasswordReq: false,
      showPassword2Req: false,
      uidb64: "",
      token: "",
    };
  },
  computed: {
    passwordLength() {
      return this.newPassword1.length >= 8;
    },
    passwordUpper() {
      return /[A-Z]/.test(this.newPassword1);
    },
    passwordLower() {
      return /[a-z]/.test(this.newPassword1);
    },
    passwordNumber() {
      return /[0-9]/.test(this.newPassword1);
    },
    passwordSpecial() {
      return /[!@#$%^&*_=+\-.]/.test(this.newPassword1);
    },
    passwordSafe() {
      return !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(this.newPassword1);
    },
    password2Length() {
      return this.newPassword2.length >= 8;
    },
    password2Upper() {
      return /[A-Z]/.test(this.newPassword2);
    },
    password2Lower() {
      return /[a-z]/.test(this.newPassword2);
    },
    password2Number() {
      return /[0-9]/.test(this.newPassword2);
    },
    password2Special() {
      return /[!@#$%^&*_=+\-.]/.test(this.newPassword2);
    },
    password2Safe() {
      return !/[^A-Za-z0-9!@#$%^&*_=+\-.]/.test(this.newPassword2);
    },
    isFormValid() {
      return (
        this.passwordLength &&
        this.passwordUpper &&
        this.passwordLower &&
        this.passwordNumber &&
        this.passwordSpecial &&
        this.passwordSafe &&
        this.password2Length &&
        this.password2Upper &&
        this.password2Lower &&
        this.password2Number &&
        this.password2Special &&
        this.password2Safe &&
        this.newPassword1 === this.newPassword2 &&
        !this.passwordError
      );
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

    validatePasswords() {
      if (this.newPassword1 && this.newPassword2 && this.newPassword1 !== this.newPassword2) {
        this.passwordError = "Passwords do not match.";
      } else {
        this.passwordError = "";
      }
    },

    async resetPassword() {
      this.validatePasswords();

      if (!this.isFormValid) {
        this.error = "Please fix the highlighted errors before submitting.";
        return;
      }

      this.loading = true;
      this.error = "";

      try {
        const response = await api.post(
          `/api/password-reset-confirm/${this.uidb64}/${this.token}/`,
          {
            new_password1: this.newPassword1,
            new_password2: this.newPassword2,
          }
        );

        this.success = response.data.message || "Password has been reset successfully! You can now log in with your new password.";
        this.newPassword1 = "";
        this.newPassword2 = "";
      } catch (err) {
        console.error(err);
        const data = err.response?.data;
        
        if (err.response?.status === 400) {
          if (data?.error) {
            this.error = data.error;
          } else if (data?.new_password1) {
            this.error = data.new_password1[0];
          } else if (data?.new_password2) {
            this.error = data.new_password2[0];
          } else {
            this.error = "Invalid password. Please check the requirements.";
          }
        } else {
          this.error = data?.error || data?.message || "Failed to reset password";
        }
      } finally {
        this.loading = false;
      }
    },
  },
  mounted() {
    this.uidb64 = this.$route.params.uidb64;
    this.token = this.$route.params.token;

    if (!this.uidb64 || !this.token) {
      this.tokenError = "Invalid reset link. Please request a new password reset.";
      return;
    }

    if (this.$store && this.$store.clearMessage) {
      this.$store.clearMessage();
    }
  },
};
</script>