<template>
  <Transition name="modal">
    <div v-if="modal.show" class="modal-overlay" @click="handleCancel">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">{{ modal.title }}</h3>
          <button class="modal-close" @click="handleCancel">
            <XIcon :size="20" />
          </button>
        </div>
        
        <div class="modal-body">
          <p class="modal-message">{{ modal.message }}</p>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-outline" @click="handleCancel">
            {{ modal.cancelText }}
          </button>
          <button class="btn btn-primary" @click="handleConfirm">
            {{ modal.confirmText }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useNotificationStore } from '../../stores/notification'
import { storeToRefs } from 'pinia'
import { XIcon } from 'lucide-vue-next'

const store = useNotificationStore()
const { modal } = storeToRefs(store)

const handleConfirm = () => {
  store.closeModal(true)
}

const handleCancel = () => {
  store.closeModal(false)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
}

.modal-container {
  background: #fff;
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  animation: modal-pop 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes modal-pop {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #f1f5f9;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.modal-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 4px;
  border-radius: 6px;
  transition: all 0.2s;
  display: flex;
}

.modal-close:hover {
  background: #f1f5f9;
  color: #64748b;
}

.modal-body {
  padding: 24px;
}

.modal-message {
  font-size: 15px;
  color: #475569;
  line-height: 1.6;
  margin: 0;
    white-space: pre-line; 

}

.modal-footer {
  padding: 16px 24px;
  background: #f8fafc;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  border-top: 1px solid #f1f5f9;
}

/* Button styles (matching app design) */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: #454a83;
  color: #fff;
}

.btn-primary:hover {
  background: #363a6a;
}

.btn-outline {
  background: #fff;
  border: 1px solid #e2e8f0;
  color: #475569;
}

.btn-outline:hover {
  background: #f1f5f9;
  border-color: #cbd5e1;
}

/* Transitions */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
