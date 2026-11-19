import api from './api';
import type { ApiResponse } from '@/types';

export interface TelemetryLog {
  id: string;
  projectId: string;
  serviceName: string;
  environment: string;
  timestamp: string;
  level: string;
  message: string;
  stackTrace?: string;
  loggerName?: string;
}

export interface TelemetryMetric {
  id: string;
  projectId: string;
  serviceName: string;
  metricName: string;
  value: number;
  unit: string;
  timestamp: string;
  isAnomaly: boolean;
}

export interface TelemetryTrace {
  id: string;
  projectId: string;
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  serviceName: string;
  operationName: string;
  startTime: string;
  durationMs: number;
  statusCode: string;
  errorMessage?: string;
}

export const telemetryService = {
  getLogs: (projectId: string, params?: Record<string, string>) =>
    api.get<TelemetryLog[]>(`/telemetry/${projectId}/logs`, params),

  getMetrics: (projectId: string, params?: Record<string, string>) =>
    api.get<TelemetryMetric[]>(`/telemetry/${projectId}/metrics`, params),

  getTraces: (projectId: string, params?: Record<string, string>) =>
    api.get<TelemetryTrace[]>(`/telemetry/${projectId}/traces`, params),

  ingestLogs: (projectId: string, logs: any[]) =>
    api.post<TelemetryLog[]>(`/telemetry/${projectId}/logs`, logs),

  ingestMetrics: (projectId: string, metrics: any[]) =>
    api.post<TelemetryMetric[]>(`/telemetry/${projectId}/metrics`, metrics),

  ingestTraces: (projectId: string, traces: any[]) =>
    api.post<TelemetryTrace[]>(`/telemetry/${projectId}/traces`, traces),
};
