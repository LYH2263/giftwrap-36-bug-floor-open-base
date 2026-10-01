<script setup>
import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const items = ref([])
const err = ref('')

onMounted(async () => {
  try {
    items.value = (await getJSON('/api/runs')).items
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <h1>用纸档</h1>
    <p class="hint">列表与详情同钉写入值（order_m / stock）。</p>
    <p class="lede">算纸页「写入用纸档」后的落库结果；订货米以写入时标称为准，改标称不回填。</p>
    <p v-if="err" class="bad">{{ err }}</p>
    <p v-else-if="!items.length" class="empty">还没有写入过。先去算纸试一单。</p>
    <ul v-else class="item-list">
      <li v-for="r in items" :key="r.id">
        <router-link :to="`/history/${r.id}`">#{{ r.id }} {{ r.box_name }}</router-link>
        <span class="meta">
          {{ r.result?.paper_m2 ?? '—' }} m²
          · 订货米 {{ r.result?.order_m ?? '—' }} m
          · {{ r.result?.paper_name ?? '—' }}
        </span>
      </li>
    </ul>
  </div>
</template>
