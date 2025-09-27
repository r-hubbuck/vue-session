<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="">
        <h1 class="text-center mb-4">Set New Password</h1>
        
        <div v-if="tokenError" class="alert alert-danger">
          {{ tokenError }}
          <div class="mt-2">
            <RouterLink to="/password-forgot" class="text-decoration-none">Request a new reset link</RouterLink>
          </div>
        </div>
        
        <div v-else-if="success" class="alert alert-success">
          {{ success }}
        </div>
        
        <form v-else @submit.prevent="resetPassword">
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
            <div v-if="showPasswordReq" class="position-absolute bg-light border rounded shadow-sm p-2 mt-1" style="z-index: 1050; min-width: 320px;">
              <div class="small" :class="passwordLength ? 'text-success' : 'text-danger'">
                <span v-if="passwordLength">✓</span><span v-else>✖</span> At least 8 characters
              </div>
              <div class="small" :class="passwordUpper ? 'text-success' : 'text-danger'">
                <span v-if="passwordUpper">✓</span><span v-else>✖</span> At least one uppercase letter
              </div>
              <div class="small" :class="passwordLower ? 'text-success' : 'text-danger'">
                <span v-if="passwordLower">✓</span><span v-else>✖</span> At least one lowercase letter
              </div>
              <div class="small" :class="passwordNumber ? 'text-success' : 'text-danger'">
                <span v-if="passwordNumber">✓</span><span v-else>✖</span> At least one number
              </div>
              <div class="small" :class="passwordSpecial ? 'text-success' : 'text-danger'">
                <span v-if="passwordSpecial">✓</span><span v-else>✖</span> At least one special character (!@#$%^&*_=+-.)
              </div>
              <div class="small" :class="passwordSafe ? 'text-success' : 'text-danger'">
                <span v-if="passwordSafe">✓</span><span v-else>✖</span> No invalid characters
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
            <div v-if="showPassword2Req" class="position-absolute bg-light border rounded shadow-sm p-2 mt-1" style="z-index: 1050; min-width: 320px;">
              <div class="small" :class="password2Length ? 'text-success' : 'text-danger'">
                <span v-if="password2Length">✓</span><span v-else>✖</span> At least 8 characters
              </div>
              <div class="small" :class="password2Upper ? 'text-success' : 'text-danger'">
                <span v-if="password2Upper">✓</span><span v-else>✖</span> At least one uppercase letter
              </div>
              <div class="small" :class="password2Lower ? 'text-success' : 'text-danger'">
                <span v-if="password2Lower">✓</span><span v-else>✖</span> At least one lowercase letter
              </div>
              <div class="small" :class="password2Number ? 'text-success' : 'text-danger'">
                <span v-if="password2Number">✓</span><span v-else>✖</span> At least one number
              </div>
              <div class="small" :class="password2Special ? 'text-success' : 'text-danger'">
                <span v-if="password2Special">✓</span><span v-else>✖</span> At least one special character (!@#$%^&*_=+-.)
              </div>
              <div class="small" :class="password2Safe ? 'text-success' : 'text-danger'">
                <span v-if="password2Safe">✓</span><span v-else>✖</span> No invalid characters
              </div>
            </div>
            <div v-if="passwordError" class="text-danger mt-2 fw-bold">{{ passwordError }}</div>
          </div>

          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <button 
            type="submit"
            class="btn btn-primary w-100 mb-3"
            :disabled="loading || !isFormValid"
          >
            {{ loading ? 'Updating...' : 'Update Password' }}
          </button>
        </form>

        <div class="text-center">
          <RouterLink to="/login" class="text-decoration-none">Back to Login</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getCSRFToken } from "../store/auth";
const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:9000'

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
        const response = await fetch(
          `${apiUrl}/api/password-reset-confirm/${this.uidb64}/${this.token}/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({
              new_password1: this.newPassword1,
              new_password2: this.newPassword2,
            }),
            credentials: "include",
          }
        );

        const data = await response.json();

        if (response.ok) {
          this.success = data.message || "Password has been reset successfully! You can now log in with your new password.";
          this.newPassword1 = "";
          this.newPassword2 = "";
        } else {
          if (response.status === 400) {
            if (data.error) {
              this.error = data.error;
            } else if (data.new_password1) {
              this.error = data.new_password1[0];
            } else if (data.new_password2) {
              this.error = data.new_password2[0];
            } else {
              this.error = "Invalid password. Please check the requirements.";
            }
          } else {
            this.error = data.error || data.message || "Failed to reset password";
          }
        }
      } catch (err) {
        console.error(err);
        this.error = "An error occurred while resetting your password. Please try again.";
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