import { api } from './axios'; import type { HealthResponse } from '../types/api'; export const getHealth = async () => (await api.get<HealthResponse>('/health')).data;
