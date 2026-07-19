import { GitCommit, Rocket, AlertCircle, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatRelativeTime } from '@/lib/utils'
import type { ActivityItem } from '@/types'

const iconMap = {
  deployment: Rocket,
  project: GitCommit,
  system: AlertCircle,
}

const statusColorMap = {
  success: 'text-emerald-400',
  failed: 'text-red-400',
  pending: 'text-amber-400',
  running: 'text-blue-400',
}

interface ActivityFeedProps {
  activities: ActivityItem[]
}

export function ActivityFeed({ activities }: ActivityFeedProps) {
  return (
    <Card className="glass">
      <CardHeader>
        <CardTitle className="text-base font-semibold">Recent Activity</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {activities.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
            <CheckCircle className="h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          activities.map((activity) => {
            const Icon = iconMap[activity.type] || GitCommit
            return (
              <div key={activity.id} className="flex items-start gap-3 group">
                <div className={cn('mt-0.5', statusColorMap[activity.status as keyof typeof statusColorMap] || 'text-muted-foreground')}>
                  <Icon className="h-4 w-4" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{activity.message}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-muted-foreground">{activity.project_name}</span>
                    <span className="text-xs text-muted-foreground">·</span>
                    <span className="text-xs text-muted-foreground">{formatRelativeTime(activity.timestamp)}</span>
                  </div>
                </div>
                <div className={cn('h-2 w-2 rounded-full mt-2', getStatusDot(activity.status))} />
              </div>
            )
          })
        )}
      </CardContent>
    </Card>
  )
}

function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(' ')
}

function getStatusDot(status: string) {
  const colors: Record<string, string> = {
    success: 'bg-emerald-400',
    failed: 'bg-red-400',
    pending: 'bg-amber-400',
    running: 'bg-blue-400',
  }
  return colors[status] || 'bg-slate-400'
}
