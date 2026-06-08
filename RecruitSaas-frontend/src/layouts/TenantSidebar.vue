<template>
  <aside class="w-64 bg-slate-900 text-white flex flex-col">

    <div class="p-6 text-xl font-bold tracking-wide">
      tenant
    </div>

    <nav class="flex-1 px-4 space-y-2">

      <router-link
        to="/experts"
        class="flex items-center gap-3 px-4 py-3 rounded-lg bg-slate-800">

        <UsersIcon class="w-5"/>
        Évaluateurs
      </router-link>

    </nav>

    <div class="p-4 border-t border-slate-700 text-sm text-gray-400">
      Tenant Panel
    </div>

  </aside>
</template>

<script setup>
import { UsersIcon } from '@heroicons/vue/24/outline'
</script>