<template>
  <div class="toast" :class="`toast-${type}`">
    <div class="toast-icon">
      <CheckCircleIcon v-if="type === 'success'" :size="20" />
      <XCircleIcon v-else-if="type === 'error'" :size="20" />
      <AlertTriangleIcon v-else-if="type === 'warning'" :size="20" />
      <InfoIcon v-else :size="20" />
    </div>
    <div class="toast-content">
      <p class="toast-message">{{ message }}</p>
    </div>
    <button class="toast-close" @click="$emit('close')">
      <XIcon :size="16" />
    </button>
  </div>
</template>

<script setup>
import { 
  CheckCircleIcon, 
  XCircleIcon, 
  AlertTriangleIcon, 
  InfoIcon,
  XIcon
} from 'lucide-vue-next'

defineProps({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info'
  }
})

defineEmits(['close'])
</script>

<style scoped>
.toast {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
  max-width: 320px;
  min-width: 280px;
  pointer-events: auto;
  position: relative;
  overflow: hidden;
  animation: slide-in 0.3s ease-out;
}

@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.toast-content {
  flex: 1;
}

.toast-message {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin: 0;
  line-height: 1.5;
}

.toast-close {
  flex-shrink: 0;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 2px;
  border-radius: 4px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast-close:hover {
  background: #f1f5f9;
  color: #64748b;
}

/* Types */
.toast-success .toast-icon { color: #10b981; }
.toast-error .toast-icon { color: #ef4444; }
.toast-warning .toast-icon { color: #f59e0b; }
.toast-info .toast-icon { color: #3b82f6; }

/* Theme */
.toast-success { border-left: 4px solid #10b981; }
.toast-error { border-left: 4px solid #ef4444; }
.toast-warning { border-left: 4px solid #f59e0b; }
.toast-info { border-left: 4px solid #3b82f6; }
</style>
