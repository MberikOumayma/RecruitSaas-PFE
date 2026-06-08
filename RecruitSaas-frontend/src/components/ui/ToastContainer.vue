<template>
  <div class="toast-container">
    <transition-group name="toast-list" tag="div" class="toast-list">
      <Toast
        v-for="toast in toasts"
        :key="toast.id"
        :type="toast.type"
        :message="toast.message"
        @close="removeToast(toast.id)"
      />
    </transition-group>
  </div>
</template>

<script setup>
import { useNotificationStore } from '../../stores/notification'
import { storeToRefs } from 'pinia'
import Toast from './Toast.vue'

const store = useNotificationStore()
const { toasts } = storeToRefs(store)
const { removeToast } = store

</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  right: 24px;
  z-index: 9999;
  pointer-events: none;
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: flex-end;
}

/* Animations */
.toast-list-enter-active,
.toast-list-leave-active {
  transition: all 0.3s ease;
}

.toast-list-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.toast-list-leave-to {
  opacity: 0;
  transform: translateX(30px) scale(0.9);
}

.toast-list-move {
  transition: transform 0.3s ease;
}
</style>
