<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, postJSON } from '../api'
import BoxUnfold from '../components/BoxUnfold.vue'

const boxes = ref([])
const papers = ref([])
const bid = ref(null)
const pid = ref(null)
const out = ref(null)
const err = ref('')
const busy = ref(false)

onMounted(async () => {
  try {
    boxes.value = (await getJSON('/api/boxes')).items.filter((b) => b.data_quality === 'clean')
    if (boxes.value.length) bid.value = boxes.value[0].id
    papers.value = (await getJSON('/api/papers')).items
    if (papers.value.length) pid.value = papers.value[0].id
  } catch (e) {
    err.value = String(e.message || e)
  }
})

async function go(save) {
  err.value = ''
  if (!pid.value) {
    err.value = '请先选纸卷：算纸必须按整卷标称托底'
    return
  }
  busy.value = true
  try {
    out.value = save
      ? await postJSON('/api/estimate', { box_id: bid.value, paper_id: pid.value, save: true })
      : await getJSON(`/api/estimate?box_id=${bid.value}&paper_id=${pid.value}`)
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>算纸</h1>
    <p class="lede">选盒选卷先试算：按卷宽折下料长，不够一卷按整卷倍数托底订货米，确认后再写入用纸档。</p>
    <div class="row">
      <select v-model.number="bid">
        <option v-for="b in boxes" :key="b.id" :value="b.id">{{ b.name }}</option>
      </select>
      <select v-model.number="pid">
        <option :value="null" disabled>选纸卷（必选）</option>
        <option v-for="p in papers" :key="p.id" :value="p.id">
          {{ p.name }}（卷宽 {{ p.roll_width }} m / 卷长 {{ p.stock_len ?? '—' }} m）
        </option>
      </select>
      <button :disabled="busy" @click="go(false)">试算</button>
      <button class="ribbon" :disabled="busy" @click="go(true)">写入用纸档</button>
    </div>
    <p v-if="err" class="bad">{{ err }}</p>
    <div v-if="out" class="result-board">
      <div class="figure">{{ out.paper_m2 }}<span>m²</span></div>
      <p class="stat-line">
        下料长 <strong>{{ out.sheet_len }}</strong> m
        · 标称卷长 {{ out.stock_len }} m
        · 订货米 <strong>{{ out.order_m }}</strong> m
      </p>
      <p class="stat-line" v-if="out.ribbon">
        十字丝带约 {{ out.ribbon.ribbon_m ?? out.ribbon }} m
      </p>
      <p v-if="out.run_id" class="stat-line">
        已写入用纸档 #{{ out.run_id }}，订货米以落库值为准
      </p>
      <BoxUnfold
        :l="out.box.length"
        :w="out.box.width"
        :h="out.box.height"
        :paper-m2="out.paper_m2"
      />
    </div>
  </div>
</template>
