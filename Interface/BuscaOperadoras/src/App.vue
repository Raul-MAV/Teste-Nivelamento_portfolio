<script setup>
import { ref } from 'vue';
import axios from 'axios';

const searchTerm = ref('');
const operadoras = ref([]);

async function buscarOperadoras() {
  if (searchTerm.value.length < 3) {
    operadoras.value = [];
    return;
  }
  try {
    const response = await axios.get(`http://localhost:8000/operadoras`, {
      params: { nome: searchTerm.value }
    });
    operadoras.value = response.data;
  } catch (error) {
    console.error("Erro ao buscar operadoras:", error);
  }
}
</script>

<template>
  <div class="p-4 max-w-xl mx-auto">
    <input 
      v-model="searchTerm" 
      @input="buscarOperadoras" 
      placeholder="Digite o nome da operadora" 
      class="border p-2 w-full rounded-lg" 
    />
    <ul v-if="operadoras.length" class="mt-4 border p-2 rounded-lg">
      <li v-for="op in operadoras" :key="op.Registro_ANS" class="py-2 border-b last:border-none">
        <strong>{{ op.Razao_Social || 'Nome não disponível' }}</strong> - 
        {{ op.Cidade || 'Cidade não disponível' }}/{{ op.UF || 'UF não disponível' }}
      </li>
    </ul>
    <p v-else class="mt-4 text-gray-500">Nenhuma operadora encontrada.</p>
  </div>
</template>

<style scoped>
.p-4 {
  padding: 1rem;
}
.max-w-xl {
  max-width: 36rem;
}
.mx-auto {
  margin-left: auto;
  margin-right: auto;
}
.border {
  border: 1px solid #e5e7eb;
}
.p-2 {
  padding: 0.5rem;
}
.w-full {
  width: 100%;
}
.rounded-lg {
  border-radius: 0.5rem;
}
.mt-4 {
  margin-top: 1rem;
}
.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}
.border-b {
  border-bottom: 1px solid #e5e7eb;
}
.last\:border-none:last-child {
  border-bottom: none;
}
.text-gray-500 {
  color: #6b7280;
}
</style>