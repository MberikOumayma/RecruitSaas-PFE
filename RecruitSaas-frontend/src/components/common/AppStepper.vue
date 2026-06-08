<template>
  <div class="stepper">
    <div
      v-for="(step, index) in steps"
      :key="step.label"
      class="stepper-item"
      :class="{
        'is-active': currentStep === index + 1,
        'is-done': currentStep > index + 1
      }"
    >
      <div class="step-bubble">
        <CheckIcon v-if="currentStep > index + 1" :size="14" />
        <span v-else>{{ index + 1 }}</span>
      </div>
      <span class="step-label">{{ step.label }}</span>

      <!-- Connector line (not after last) -->
      <div v-if="index < steps.length - 1" class="step-connector" />
    </div>
  </div>
</template>

<script>
import { CheckIcon } from 'lucide-vue-next'

export default {
  name: 'AppStepper',
  components: { CheckIcon },
  props: {
    currentStep: {
      type: Number,
      default: 1
    },
    steps: {
      type: Array,
      default: () => [
        { label: 'Informations' },
        { label: 'Configuration' },
        { label: 'Preview' }
      ]
    }
  }
}
</script>

<style scoped>
.stepper {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px 32px;
  gap: 0;
}

.stepper-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 13px;
  font-weight: 500;
}

.stepper-item.is-active {
  color: #1A2B4C;
  font-weight: 700;
}

.stepper-item.is-done {
  color: #22c55e;
}

.step-bubble {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  background: #e2e8f0;
  color: #64748b;
  flex-shrink: 0;
}

.stepper-item.is-active .step-bubble {
  background: #1A2B4C;
  color: #fff;
}

.stepper-item.is-done .step-bubble {
  background: #22c55e;
  color: #fff;
}

.step-label {
  white-space: nowrap;
}

.step-connector {
  flex: 1;
  min-width: 200px;
  height: 1px;
  background: #e2e8f0;
  margin: 0 12px;
}
</style>
