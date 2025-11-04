<template>
  <el-card class="metric-card">
    <h4>Horários de pico (últimos 30 dias)</h4>

    <el-skeleton v-if="loading" rows="8" animated />

    <el-table v-else :data="hours" stripe style="width: 100%">
      <el-table-column prop="hour" label="Hora" width="80" />
      <el-table-column prop="count" label="Vendas" />
    </el-table>
  </el-card>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { getPeakHours } from "@/api/summary";

const props = defineProps({ filters: { type: Object, default: () => ({}) } });

const hours = ref([]);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    const data = await getPeakHours(props.filters || {});
    // Normaliza: garante que todas as 24 horas existam (0‑23)
    const map = new Map(data.map(d => [d.hour, d.count]));
    const full = Array.from({ length: 24 }, (_, i) => ({
      hour: i,
      count: map.get(i) ?? 0,
    }));
    hours.value = full;
  } catch (e) {
    console.error("Erro ao buscar horário de pico:", e);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => props.filters, load, { deep: true });
</script>

<style scoped>
.metric-card {
  width: 100%;
}
</style>
