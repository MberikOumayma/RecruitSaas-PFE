<template>
  <router-view />
  <ToastContainer />
  <AppModal />
</template>

<script setup>
import ToastContainer from './components/ui/ToastContainer.vue'
import AppModal from './components/ui/AppModal.vue'
</script>

<style>
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  width: 100%;
  height: 100%;
  overflow-x: hidden;
}

body {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  background: #f0f2f5;
}

#app {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

</style>