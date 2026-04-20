import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== Import CSV ====================

export const importFieldCharacteristics = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/import/field', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const importYearFieldData = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/import/year-field', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const importRainfallData = (file, datasetName = 'default') => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post(`/import/rainfall?dataset_name=${encodeURIComponent(datasetName)}`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const importFertilizationData = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/import/fertilization', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// ==================== Fields ====================

export const getFields = () => api.get('/fields/');
export const getField = (id) => api.get(`/fields/${id}`);
export const deleteField = (id) => api.delete(`/fields/${id}`);

// ==================== Parameters ====================

export const getFertilizers = () => api.get('/parameters/fertilizers');
export const createFertilizer = (data) => api.post('/parameters/fertilizers', data);
export const updateFertilizer = (id, data) => api.put(`/parameters/fertilizers/${id}`, data);
export const deleteFertilizer = (id) => api.delete(`/parameters/fertilizers/${id}`);

export const getEmissionFactors = () => api.get('/parameters/emission-factors');
export const createEmissionFactor = (data) => api.post('/parameters/emission-factors', data);
export const updateEmissionFactor = (id, data) => api.put(`/parameters/emission-factors/${id}`, data);

export const getVolatilizationParams = () => api.get('/parameters/volatilization');
export const createVolatilizationParam = (data) => api.post('/parameters/volatilization', data);
export const updateVolatilizationParam = (id, data) => api.put(`/parameters/volatilization/${id}`, data);

export const getLeachingParams = () => api.get('/parameters/leaching');
export const createLeachingParam = (data) => api.post('/parameters/leaching', data);
export const updateLeachingParam = (id, data) => api.put(`/parameters/leaching/${id}`, data);

export const getFuzzyModules = () => api.get('/parameters/fuzzy/modules');

export const getFuzzyFactors = (moduleCode) =>
  api.get('/parameters/fuzzy/factors' + (moduleCode ? `?module_code=${moduleCode}` : ''));
export const updateFuzzyFactor = (id, data) => api.put(`/parameters/fuzzy/factors/${id}`, data);

export const getFuzzyRules = (moduleCode) =>
  api.get('/parameters/fuzzy/rules' + (moduleCode ? `?module_code=${moduleCode}` : ''));
export const updateFuzzyRule = (id, data) => api.put(`/parameters/fuzzy/rules/${id}`, data);

export const getFuzzyNominalConversions = (moduleCode) =>
  api.get('/parameters/fuzzy/nominal-conversions' + (moduleCode ? `?module_code=${moduleCode}` : ''));
export const updateFuzzyNominalConversion = (id, data) =>
  api.put(`/parameters/fuzzy/nominal-conversions/${id}`, data);

export const getPalmUptakeParams = () => api.get('/parameters/palm-uptake');
export const createPalmUptakeParam = (data) => api.post('/parameters/palm-uptake', data);
export const updatePalmUptakeParam = (id, data) => api.put(`/parameters/palm-uptake/${id}`, data);

export const getMethods = () => api.get('/parameters/methods');
export const createMethod = (data) => api.post('/parameters/methods', data);

// ==================== Simulations ====================

export const getSimulations = () => api.get('/simulations/');
export const createSimulation = (data) => api.post('/simulations/', data);
export const getSimulation = (id) => api.get(`/simulations/${id}`);
export const getSimulationResults = (id) => api.get(`/simulations/${id}/results`);
export const deleteSimulation = (id) => api.delete(`/simulations/${id}`);

export default api;
