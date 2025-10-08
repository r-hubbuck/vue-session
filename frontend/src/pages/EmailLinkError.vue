<template>
  <div class="container mt-2">
    <img src="/logo_horizontal_blue.png" alt="Logo" class="d-inline-block align-text-top w-50">
    <h1 class="text-danger mt-4 mb-3">Requested Link Is Invalid</h1>
    <p class="mb-4">
      The link you clicked is invalid or has expired. This can happen if:
    </p>
    <div class="mx-auto mb-4" style="max-width: 400px;">
      <ul class="list-unstyled text-start">
        <li class="mb-2"><span class="text-muted">•</span> The link has already been used</li>
        <li class="mb-2"><span class="text-muted">•</span> The link has expired (they expire after a certain time for security)</li>
        <li class="mb-2"><span class="text-muted">•</span> The link was corrupted or incomplete</li>
      </ul>
    </div>
    
    <div class="d-flex flex-column flex-sm-row gap-3 justify-content-center mb-4">
      <RouterLink to="/login" class="btn btn-secondary">
        Back to Login
      </RouterLink>
    </div>
    
    <p class="text-muted small">
      If you continue to have problems, please <a target="_blank" href="mailto:tbp.it@tbp.org">contact support</a>.
    </p>
  </div>
</template>

<script>
export default {
  name: 'EmailLinkError',
  mounted() {
    if (this.$store && this.$store.clearMessage) {
      this.$store.clearMessage();
    }
  },
};
</script>