import axios from 'axios';
// import { userStore } from '../../state/global';

const api = axios.create({
  headers: {
    'Content-Type': 'application/json',
  },
});

// api.interceptors.request.use((config) => {
//   const { token } = userStore.getState();
//   if (token) {
//     config.headers['Authorization'] = `Bearer ${token}`;
//   }
//   return config;
// });

export default api;