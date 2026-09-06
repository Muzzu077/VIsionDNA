import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format, formatDistanceToNow } from 'date-fns';
import type { RiskSeverity } from '../types';

export function classNames(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string | undefined): string {
  if (!dateString) return 'N/A';
  try {
    return format(new Date(dateString), 'PP HH:mm:ss');
  } catch (e) {
    return dateString;
  }
}

export function formatTimeAgo(dateString: string | undefined): string {
  if (!dateString) return 'N/A';
  try {
    return formatDistanceToNow(new Date(dateString), { addSuffix: true });
  } catch (e) {
    return dateString;
  }
}

export function formatRiskLevel(level: RiskSeverity | string): string {
  // Uppercase for safety
  return level.toUpperCase();
}

export function formatConfidence(conf: number): string {
  return `${(conf * 100).toFixed(1)}%`;
}

export function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}m ${s}s`;
}
