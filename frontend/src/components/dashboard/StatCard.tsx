import { LucideIcon } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { cn } from '@/lib/utils'

interface StatCardProps {
  title: string
  value: string | number
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  icon: LucideIcon
  iconColor?: string
  iconBg?: string
}

export function StatCard({ title, value, change, changeType = 'neutral', icon: Icon, iconColor, iconBg }: StatCardProps) {
  return (
    <Card className="glass">
      <CardContent className="p-6">
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-3xl font-bold tracking-tight">{value}</p>
            {change && (
              <p className={cn(
                'text-xs font-medium',
                changeType === 'positive' && 'text-emerald-400',
                changeType === 'negative' && 'text-red-400',
                changeType === 'neutral' && 'text-muted-foreground'
              )}>
                {change}
              </p>
            )}
          </div>
          <div className={cn('rounded-xl p-3', iconBg || 'bg-primary/10')}>
            <Icon className={cn('h-5 w-5', iconColor || 'text-primary')} />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
