import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRelativeTime(date: string | Date): string {
  const now = new Date()
  const then = new Date(date)
  const diffMs = now.getTime() - then.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) return 'just now'
  if (diffMin < 60) return `${diffMin}m ago`
  if (diffHour < 24) return `${diffHour}h ago`
  if (diffDay < 7) return `${diffDay}d ago`
  return formatDate(date)
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    healthy: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    running: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    success: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    deployed: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20',
    active: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    idle: 'text-slate-400 bg-slate-400/10 border-slate-400/20',
    pending: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    building: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
    failed: 'text-red-400 bg-red-400/10 border-red-400/20',
    error: 'text-red-400 bg-red-400/10 border-red-400/20',
    unknown: 'text-slate-400 bg-slate-400/10 border-slate-400/20',
    cancelled: 'text-slate-400 bg-slate-400/10 border-slate-400/20',
  }
  return colors[status.toLowerCase()] || colors.unknown
}

export function getStatusDot(status: string): string {
  const colors: Record<string, string> = {
    healthy: 'bg-emerald-400',
    running: 'bg-blue-400',
    success: 'bg-emerald-400',
    deployed: 'bg-emerald-400',
    active: 'bg-blue-400',
    idle: 'bg-slate-400',
    pending: 'bg-amber-400',
    building: 'bg-amber-400',
    failed: 'bg-red-400',
    error: 'bg-red-400',
    unknown: 'bg-slate-400',
  }
  return colors[status.toLowerCase()] || colors.unknown
}
