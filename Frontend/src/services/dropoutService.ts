const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'https://prediccion-de-sismos-facial-v1.onrender.com/api';

// Helper para evitar warning de variable no usada y exponer el base URL si es necesario.
export function getDropoutApiBase(): string {
  return API_BASE_URL;
}
