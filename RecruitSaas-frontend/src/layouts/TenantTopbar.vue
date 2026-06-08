<template>
  <header class="bg-white dark:bg-slate-800 shadow px-6 py-4 flex justify-between items-center">

    <input
      v-model="search"
      placeholder="Rechercher un expert..."
      class="px-4 py-2 w-96 rounded-lg border dark:bg-slate-700 dark:text-white"
    />

    <div class="flex items-center gap-4">

      <button
        @click="$emit('toggleDark')"
        class="p-2 rounded hover:bg-gray-200 dark:hover:bg-slate-700">

        <MoonIcon class="w-5"/>
      </button>

      <button
        @click="$emit('invite')"
        class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition">
        Inviter un membre
      </button>

    </div>

  </header>
</template>

<script setup>
import { MoonIcon } from '@heroicons/vue/24/outline'
import { ref } from 'vue'

const search = ref("")
</script>