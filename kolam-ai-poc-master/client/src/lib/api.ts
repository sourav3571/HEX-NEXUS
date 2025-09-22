const BASE_URL = `${import.meta.env.VITE_API_URL}/api`;

// Define the API routes in a structured way
export const API_ROUTES = {
  AUTH: {
    LOGIN: `${BASE_URL}/auth/login`,
    ME: `${BASE_URL}/auth/me`,
  },
  KOLAM: {
    KNOW_YOUR_KOLAM: `${BASE_URL}/know-your-kolam`,
    RENDER: `${BASE_URL}/create_kolam`,
    PREDICT: `${BASE_URL}/predict`,
    SEARCH: `${BASE_URL}/search`,
  }
} as const;

export const localKey = {
  token: `store-app-token`,
}

