<template>
    <div>
        <div class="page-header">
            <div class="page-header-content">
                <h1 class="page-title">Page Not Found</h1>
            </div>
        </div>

        <div class="content-container">
            <div class="section-card text-center py-5">
                <i class="bi bi-exclamation-circle" style="font-size: 3.5rem; color: var(--brand-blue);"></i>
                <h2 class="mt-4">404 — Page Not Found</h2>
                <p class="text-muted mt-2">The page you're looking for doesn't exist or has been moved.</p>
                <router-link to="/" class="btn btn-primary mt-3">Go to Dashboard</router-link>
            </div>
        </div>
    </div>
</template>
