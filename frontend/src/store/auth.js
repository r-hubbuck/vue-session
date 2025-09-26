import { defineStore } from 'pinia'

const getStoredState = () => {
    const storedState = localStorage.getItem('authState')

    return storedState
  ? JSON.parse(storedState)
  : {
      user: null,
      isAuthenticated: false,
    }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    storedState: getStoredState(),
    serverMessage: null,
    verified: false
  }),
  actions: {
    clearMessage() {
        this.serverMessage = null;
    },

    async setCsrfToken() {
      await fetch('http://localhost:9000/api/set-csrf-token', {
        method: 'GET',
        credentials: 'include',
      })
    },

    async verifyMember(formData, router = null) {
        console.log(this.formData)
        try {
            const response = await fetch('http://localhost:9000/api/verify-member', {
                method: 'POST',
                body: JSON.stringify(formData),
                headers: {
                    'Content-Type': 'application/json',  
                    'X-CSRFToken': getCSRFToken(),
                },
                credentials: 'include',
            })
            const json = await response.json();
            console.log(json.message)
            this.serverMessage = json.message
            if (json.message == "OK") {
                console.log("OK check")
                if (router) {
                    await router.push({
                      name: 'register',
                    })
                  }
            }
        } catch (error) {
            console.error('Failed', error)
            console.log(response)
            throw error
        }
    },

    async login(email, password, router = null) {
      const response = await fetch('http://localhost:9000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
          email,
          password,
        }),
        credentials: 'include',
      })
      const data = await response.json()
      console.log(data)
      this.serverMessage = data.message
      if (data.success) {
        this.isAuthenticated = true
        this.saveState()
        if (router) {
          await router.push({
            name: 'code-check',
          })
        }
      } else {
        this.user = null
        this.isAuthenticated = false
        this.saveState()
      }
    },

    async verify(code, router = null) {
      console.log("run verify")
      try {
        const response = await fetch('http://localhost:9000/api/code-check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({
                code: code,
            }),
            credentials: 'include'
        })
        const data = await response.json()
        console.log(data)
        if (response.ok) {
            this.success = 'Code is correct.'
            console.log(data.success)
            if (data.success == true) {
              if (router) {
                await router.push({
                  name: 'home',
                })
              }
            }
        } else {
            this.error = data.error || 'Incorrect code'
        }
      } catch (err) {
          console.log(err)
          this.error = 'An error occurred during verification: ' + err
      }
    },

    async requestPasswordReset(email) {
    try {
      const response = await fetch('http://localhost:9000/api/password-reset-request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ email }),
        credentials: 'include',
      })

      const data = await response.json()
      
      if (response.ok) {
        this.serverMessage = data.message || 'Password reset email sent successfully'
        return { success: true, message: data.message }
      } else {
        this.serverMessage = data.error || data.message || 'Failed to send reset email'
        return { success: false, error: data.error || data.message }
      }
    } catch (error) {
      console.error('Password reset request failed', error)
      this.serverMessage = 'An error occurred while sending the reset email'
      return { success: false, error: 'Network error occurred' }
    }
  },

  async confirmPasswordReset(uidb64, token, newPassword1, newPassword2) {
    try {
      const response = await fetch(`http://localhost:9000/api/password-reset-confirm/${uidb64}/${token}/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({
          new_password1: newPassword1,
          new_password2: newPassword2,
        }),
        credentials: 'include',
      })

      const data = await response.json()
      
      if (response.ok) {
        this.serverMessage = data.message || 'Password reset successfully'
        return { success: true, message: data.message }
      } else {
        this.serverMessage = data.error || data.message || 'Failed to reset password'
        return { success: false, error: data.error || data.message || data }
      }
    } catch (error) {
      console.error('Password reset confirmation failed', error)
      this.serverMessage = 'An error occurred while resetting password'
      return { success: false, error: 'Network error occurred' }
    }
  },

    async logout(router = null) {
      try {
        const response = await fetch('http://localhost:9000/api/logout', {
          method: 'POST',
          headers: {
            'X-CSRFToken': getCSRFToken(),
          },
          credentials: 'include',
        })
        if (response.ok) {
          console.log(response)
          this.user = null
          this.isAuthenticated = false
          this.saveState()
          if (router) {
            await router.push({
              name: 'login',
            })
          }
        }
      } catch (error) {
        console.error('Logout failed', error)
        throw error
      }
    },

    async fetchUser() {
      try {
        const response = await fetch('http://localhost:9000/api/user', {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
        })
        if (response.ok) {
          const data = await response.json()
          this.user = data
          this.isAuthenticated = true
        } else {
          this.user = null
          this.isAuthenticated = false
        }
      } catch (error) {
        console.error('Failed to fetch user', error)
        this.user = null
        this.isAuthenticated = false
      }
      this.saveState()
    },

    async getChapters() {
        try {
            const response = await fetch('http://localhost:9000/api/chapter-list', {
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
              },
            })
            if (response.ok) {
              console.log(response)
              const data = await response.json()
              console.log(data.chapters)
              return Object.values(data.chapters)
            } else {
              console.log(response)
            }
          } catch (error) {
            console.error('Failed to fetch user', error)
          }
    },

    saveState() {
      /*
            We save state to local storage to keep the
            state when the user reloads the page.
            This is a simple way to persist state. For a more robust solution,
            use pinia-persistent-state.
             */
      localStorage.setItem(
        'authState',
        JSON.stringify({
          user: this.user,
          isAuthenticated: this.isAuthenticated,
        }),
      )
    },
  },
})

export function getCSRFToken() {
  /*
    We get the CSRF token from the cookie to include in our requests.
    This is necessary for CSRF protection in Django.
     */
  const name = 'csrftoken'
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  if (cookieValue === null) {
    throw 'Missing CSRF cookie.'
  }
  return cookieValue
}