<template>
  <el-card class="metric-card">
    <h4>Faturamento (últimos 30 dias)</h4>

    <el-skeleton v-if="loading" :rows="2" animated />

    <div v-else>
      <p><strong>Bruto:</strong> R$ {{ revenue.gross.toFixed(2) }}</p>
      <p><strong>Líquido:</strong> R$ {{ revenue.net.toFixed(2) }}</p>
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { getRevenue } from "@/api/summary";

const props = defineProps({ filters: { type: Object, default: () => ({}) } });

const revenue = ref({ gross: 0, net: 0 });
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    const data = await getRevenue(props.filters || {});
    revenue.value = data;
  } catch (e) {
    console.error("Erro ao buscar faturamento:", e);
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
