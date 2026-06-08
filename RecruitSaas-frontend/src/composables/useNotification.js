import { useNotificationStore } from '../stores/notification'

export function useNotification() {
  const store = useNotificationStore()

  const toast = {
    success: (message, duration) => store.addToast({ type: 'success', message, duration }),
    error: (message, duration) => store.addToast({ type: 'error', message, duration }),
    info: (message, duration) => store.addToast({ type: 'info', message, duration }),
    warning: (message, duration) => store.addToast({ type: 'warning', message, duration }),
    remove: (id) => store.removeToast(id)
  }

  const confirm = (options) => {
    return store.confirm(options)
  }

  return {
    toast,
    confirm,
    toasts: store.toasts,
    modal: store.modal
  }
}
