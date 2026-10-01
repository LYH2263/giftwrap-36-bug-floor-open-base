<script setup>
import { onMounted, ref } from 'vue'
import { getJSON, putJSON } from '../api'

const items = ref([])
const err = ref('')
const editId = ref(null)
const form = ref({ name: '', roll_width: 0, stock_len: 0 })
const busy = ref(false)

async function load() {
  items.value = (await getJSON('/api/papers')).items
}

onMounted(async () => {
  try {
    await load()
  } catch (e) {
    err.value = String(e.message || e)
  }
})

function startEdit(p) {
  err.value = ''
  editId.value = p.id
  form.value = { name: p.name, roll_width: p.roll_width, stock_len: p.stock_len }
}

async function save(pid) {
  err.value = ''
  busy.value = true
  try {
    await putJSON(`/api/papers/${pid}`, {
      name: form.value.name,
      roll_width: Number(form.value.roll_width),
      stock_len: Number(form.value.stock_len),
    })
    editId.value = null
    await load()
  } catch (e) {
    err.value = String(e.message || e)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="page">
    <h1>包装纸</h1>
    <p class="lede">
      卷宽折出下料长，标称卷长用于整卷起订托底；这里只改标称，已写入的用纸档保持原值不回填。
    </p>
    <p v-if="err" class="bad">{{ err }}</p>
    <div class="paper-grid">
      <div v-for="p in items" :key="p.id" class="paper-tile">
        <template v-if="editId !== p.id">
          <strong>{{ p.name }}</strong>
          <span class="meta">卷宽 {{ p.roll_width }} m · 标称卷长 {{ p.stock_len ?? '—' }} m</span>
          <span v-if="p.data_quality === 'dirty'" class="pill warn">脏数据</span>
          <div class="tile-actions">
            <button class="ghost" @click="startEdit(p)">改标称</button>
          </div>
        </template>
        <template v-else>
          <label class="field">
            名称
            <input v-model="form.name" type="text" />
          </label>
          <label class="field">
            卷宽 (m)
            <input v-model.number="form.roll_width" type="number" step="0.01" min="0" />
          </label>
          <label class="field">
            标称卷长 (m)
            <input v-model.number="form.stock_len" type="number" step="0.1" min="0" />
          </label>
          <div class="tile-actions">
            <button :disabled="busy" @click="save(p.id)">保存标称</button>
            <button class="ghost" :disabled="busy" @click="editId = null">取消</button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
