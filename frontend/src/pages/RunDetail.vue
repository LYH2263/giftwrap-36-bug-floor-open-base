<script setup>
// 详情订货米：与列表一致，钉落库时的托升值；改标称不回填。

import { onMounted, ref } from 'vue'
import { getJSON } from '../api'

const props = defineProps({ id: String })
const run = ref(null)
const err = ref('')

onMounted(async () => {
  try {
    run.value = await getJSON(`/api/runs/${props.id}`)
  } catch (e) {
    err.value = String(e.message || e)
  }
})
</script>

<template>
  <div class="page">
    <p v-if="err" class="bad">{{ err }}</p>
    <template v-else-if="run">
      <h1>用纸档 #{{ run.id }}</h1>
      <p class="lede">落库时的钉住值；纸张标称后续改动不影响本单。</p>
      <div class="result-board">
        <div class="figure">{{ run.result?.order_m ?? '—' }}<span>m 订货米</span></div>
        <ul class="item-list detail-list">
          <li><span>礼盒</span><span class="meta">{{ run.box_name }}</span></li>
          <li><span>纸卷</span><span class="meta">{{ run.result?.paper_name ?? '—' }}</span></li>
          <li><span>用纸面积</span><span class="meta">{{ run.result?.paper_m2 ?? '—' }} m²</span></li>
          <li><span>下料长</span><span class="meta">{{ run.result?.sheet_len ?? '—' }} m</span></li>
          <li><span>标称卷长</span><span class="meta">{{ run.result?.stock_len ?? '—' }} m</span></li>
          <li><span>折边系数</span><span class="meta">× {{ run.overlap }}</span></li>
          <li><span>写入时间</span><span class="meta">{{ run.created_at }}</span></li>
        </ul>
      </div>
      <div class="row" style="margin-top: 1.25rem">
        <router-link class="btn ghost" to="/history">返回用纸档</router-link>
      </div>
    </template>
  </div>
</template>
