<template>
  <el-card class="metric-card">
    <h4>Top 5 Produtos (últimos 30 dias)</h4>

    <el-skeleton v-if="loading" rows="5" animated />

    <el-table v-else :data="products" stripe style="width: 100%">
      <el-table-column prop="name" label="Produto" />
      <el-table-column prop="quantity" label="Qtd." width="80" />
      <el-table-column prop="revenue" label="Faturamento" width="120">
        <template #default="{ row }">
          R$ {{ Number(row.revenue).toFixed(2) }}
        </template>
      </el-table-column>
    </el-table>
    <div style="margin-top: .75rem; text-align: right">
      <el-button size="mini" @click="onExport">Exportar CSV</el-button>
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, ref, watch } from "vue";
import { getTopProducts, exportCsvUrl } from "@/api/summary";

const props = defineProps({ filters: { type: Object, default: () => ({}) } });

const products = ref([]);
const loading = ref(true);

async function load() {
  loading.value = true;
  try {
    const data = await getTopProducts(props.filters || {});
    products.value = data;
  } catch (e) {
    console.error("Erro ao buscar top products:", e);
  } finally {
    loading.value = false;
  }
}

onMounted(load);
watch(() => props.filters, load, { deep: true });

function onExport() {
  const url = exportCsvUrl('top-products', props.filters || {});
  // open in new tab to download
  window.open(url, '_blank');
}
</script>

<style scoped>
.metric-card {
  width: 100%;
}
</style>
