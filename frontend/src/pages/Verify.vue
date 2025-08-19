<template>
    <div class="container" >
        <h1>Verify</h1> 
        <form  @submit.prevent="submitVerifyForm" >
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
            <div v-if="authStore.serverMessage" class="text-danger mt-4 fw-bold">
                {{ authStore.serverMessage }}
            </div>
            <button class="btn btn-primary mt-5" type="submit">Submit</button> 
        </form> 
    </div> 
</template>

<script >
import { useAuthStore } from '../store/auth.js'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { reactive, onMounted } from 'vue'

export default {
    setup() {
        const authStore = useAuthStore()
        const router = useRouter()

        return {
            authStore,
            router
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
            }
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
        async submitVerifyForm() {
            console.log(this.formData)
            await this.authStore.verifyMember(this.formData, this.$router)
            this.resetForm()
        },
        resetForm() {
          this.formData = {
            chapter: "",
            email: "",
            year: new Date().getFullYear(),
          };
        }
    },
    async mounted() {
        this.authStore.clearMessage()
        await this.authStore.fetchUser()
        // options = await this.authStore.getChapters()
        this.chapters = await this.authStore.getChapters()
    },
} 
</script>
