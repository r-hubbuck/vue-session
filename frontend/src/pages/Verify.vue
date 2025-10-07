<template>
    <div class="container mt-5">
        <h1>Verify Tau Beta Pi Membership</h1> 
        <form  @submit.prevent="submitVerifyForm" class="container-md">
            <div class="form-group row">
                <label class="form-label" for="email" type="email">Email:</label> 
                <input class="form-control" v-model="formData.email" id="email" type ="text" required >
            </div> 
            <div class="form-group row">
                <label class="form-label" for="chapter">Chapter:</label>
                <select class="form-control chapter-select" v-model="formData.chapter" id="chapter" required>
                    <option v-for="chapter in chapters" :key="chapter.id" :value="chapter.id">
                        {{ chapter.title }}
                    </option>
            </select>
            </div>
            <div class="form-group row">
                <label class="form-label" for="year">Graduation Year:</label>
                <select class="form-control" id="year" v-model="formData.year" @change="handleYearChange" required>
                    <option v-for="year in years" :key="year" :value="year">
                        {{ year }}
                    </option>
                </select>
            </div> 
            <div v-if="errorMessage" class="text-danger mt-4 fw-bold">
                {{ errorMessage }}
            </div>
            <button class="btn btn-danger mt-5 me-4" type="button" @click="$router.push('/login')">Back</button>
            <button class="btn btn-primary mt-5" type="submit">Submit</button> 
        </form> 
    </div> 
</template>

<script>
import { useAuthStore } from '../store/auth.js'
import api from '../api'

export default {
    setup() {
        const authStore = useAuthStore()
        return {
            authStore
        }
    },
    data() {
        return {
            chapters: [],
            years: this.generateYearRange(1900, new Date().getFullYear()),
            formData: {
                chapter: "",
                email: "",
                year: new Date().getFullYear(),
            },
            errorMessage: ""
        }
    },
    methods: {
        generateYearRange(start, end) {
            const yearRange = [];
            for (let i = end; i >= start; i--) {
                yearRange.push(i);
            }
            return yearRange;
        },
        
        handleYearChange(event) {
            this.formData.year = parseInt(event.target.value);
        },
        
        async fetchChapters() {
            try {
                const response = await api.get('/api/chapter-list')
                this.chapters = Object.values(response.data.chapters)
            } catch (error) {
                console.error('Failed to fetch chapters', error)
                this.errorMessage = 'Failed to load chapters'
            }
        },
        
        async submitVerifyForm() {
            try {
                const response = await api.post('/api/verify-member', this.formData)
                
                if (response.data.message === 'OK') {
                    // Set verification status in store
                    this.authStore.setVerified(this.formData.email)
                    await this.$router.push({ name: 'register' })
                } else {
                    this.errorMessage = response.data.message
                }
            } catch (error) {
                console.error('Verification failed', error)
                this.errorMessage = error.response?.data?.message || 'Verification failed'
            }
        },
        
        resetForm() {
          this.formData = {
            chapter: "",
            email: "",
            year: new Date().getFullYear(),
          }
          this.errorMessage = ""
        }
    },
    
    async mounted() {
        this.authStore.clearMessage()
        await this.authStore.fetchUser()
        await this.fetchChapters()
        
        // Show message if redirected from register page
        if (this.authStore.serverMessage) {
            this.errorMessage = this.authStore.serverMessage
            this.authStore.clearMessage()
        }
    },
} 
</script>