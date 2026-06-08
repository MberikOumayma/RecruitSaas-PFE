import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    toasts: [],
    modal: {
      show: false,
      title: '',
      message: '',
      confirmText: 'Confirm',
      cancelText: 'Cancel',
      resolve: null,
      reject: null
    }
  }),

  actions: {
    addToast({ type = 'info', message, duration = 4000 }) {
      const id = Date.now()
      this.toasts.push({ id, type, message })

      if (duration > 0) {
        setTimeout(() => {
          this.removeToast(id)
        }, duration)
      }
    },

    removeToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },

    confirm({ title, message, confirmText = 'Confirm', cancelText = 'Cancel' }) {
      this.modal = {
        show: true,
        title,
        message,
        confirmText,
        cancelText,
        resolve: null,
        reject: null
      }

      return new Promise((resolve, reject) => {
        this.modal.resolve = resolve
        this.modal.reject = reject
      })
    },

    closeModal(result) {
      if (result && this.modal.resolve) {
        this.modal.resolve(true)
      } else if (this.modal.reject) {
        this.modal.resolve(false)
      }
      
      this.modal.show = false
      this.modal.resolve = null
      this.modal.reject = null
    }
  }
})
