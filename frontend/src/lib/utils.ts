import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date));
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const target = new Date(date);
  const diffMs = now.getTime() - target.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(date);
}

export function truncate(str: string, length: number): string {
  if (str.length <= length) return str;
  return str.slice(0, length) + '...';
}

export function severityColor(severity: string): string {
  switch (severity.toLowerCase()) {
    case 'critical': return 'text-on-error-container bg-error-container';
    case 'high': return 'text-on-error-container bg-error-container/70';
    case 'medium': return 'text-on-primary-fixed-variant bg-primary-fixed';
    case 'low': return 'text-on-surface-variant bg-surface-container-high';
    default: return 'text-on-surface-variant bg-surface-container';
  }
}

export function statusColor(status: string): string {
  switch (status.toLowerCase()) {
    case 'active':
    case 'running':
    case 'investigating':
      return 'text-primary bg-primary-fixed';
    case 'resolved':
    case 'completed':
    case 'healthy':
      return 'text-success bg-success-container';
    case 'critical':
    case 'failed':
      return 'text-on-error-container bg-error-container';
    case 'pending':
    case 'review':
      return 'text-on-primary-fixed-variant bg-primary-fixed';
    default:
      return 'text-on-surface-variant bg-surface-container';
  }
}
