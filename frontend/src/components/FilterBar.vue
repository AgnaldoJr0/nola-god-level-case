<template>
  <el-card class="filter-card">
    <div class="filters">
      <el-date-picker v-model="range" type="daterange" range-separator="a" start-placeholder="Início" end-placeholder="Fim"/>

      <el-select v-model="store" placeholder="Loja" clearable style="width: 220px">
        <el-option v-for="s in stores" :key="s.id" :label="s.name" :value="s.id"/>
      </el-select>

      <el-select v-model="channel" placeholder="Canal" clearable style="width: 180px">
        <el-option v-for="c in channels" :key="c.code" :label="c.name" :value="c.code"/>
      </el-select>

      <el-input-number v-model="limit" :min="1" :max="100" label="limit" style="width:100px"/>

      <el-button type="primary" @click="apply">Aplicar</el-button>
      <el-button @click="reset">Limpar</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getStores, getChannels } from '@/api/summary'

const emit = defineEmits(['update:filters'])

const range = ref([])
const store = ref(null)
const channel = ref(null)
const limit = ref(10)

const stores = ref([])
const channels = ref([])

onMounted(async () => {
  try {
    stores.value = await getStores()
    channels.value = await getChannels()
  } catch (e) {
    console.error('Erro ao buscar stores/channels', e)
  }
})

function apply() {
  const filters = {
    start: range.value[0] ? range.value[0].toISOString().split('T')[0] : null,
    end: range.value[1] ? range.value[1].toISOString().split('T')[0] : null,
    store: store.value,
    channel: channel.value,
    limit: limit.value,
  }
  emit('update:filters', filters)
}

function reset() {
  range.value = []
  store.value = null
  channel.value = null
  limit.value = 10
  emit('update:filters', {})
}
</script>

<style scoped>
.filter-card { margin-bottom: 1rem }
.filters { display:flex; gap: .5rem; align-items:center }
</style>
