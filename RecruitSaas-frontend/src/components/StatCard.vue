<template>
  <div class="bg-white dark:bg-slate-800 p-5 rounded-xl shadow hover:shadow-lg transition">

    <p class="text-sm text-gray-400">{{ title }}</p>

    <div class="flex justify-between items-center mt-2">
      <h3 class="text-2xl font-bold dark:text-white">
        {{ value }}
      </h3>

      <slot />
    </div>

  </div>
</template>

<script setup>
defineProps(["title","value"])
</script>