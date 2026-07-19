import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  FolderKanban,
  Rocket,
  AlertTriangle,
  Container,
  TrendingUp,
  TrendingDown,
} from 'lucide-react'
import { StatCard } from '@/components/dashboard/StatCard'
import { ActivityFeed } from '@/components/dashboard/ActivityFeed'
import { DeploymentChart } from '@/components/dashboard/DeploymentChart'
import { ResourceUsage } from '@/components/dashboard/ResourceUsage'
import { projectApi } from '@/lib/api'
import type { ActivityItem } from '@/types'

// Demo data for initial view
const demoActivities: ActivityItem[] = [
  { id: '1', type: 'deployment', status: 'success', message: 'Deployed v2.1.0 to production', project_name: 'api-gateway', timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString() },
  { id: '2', type: 'deployment', status: 'failed', message: 'Build failed: dependency resolution error', project_name: 'frontend-app', timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString() },
  { id: '3', type: 'project', status: 'success', message: 'Created new project "auth-service"', project_name: 'auth-service', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() },
  { id: '4', type: 'deployment', status: 'success', message: 'Auto-deployed from main branch', project_name: 'web-dashboard', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString() },
  { id: '5', type: 'system', status: 'success', message: 'System maintenance completed', project_name: 'System', timestamp: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString() },
]

const chartData = [
  { name: 'Mon', deployments: 12, successful: 10, failed: 2 },
  { name: 'Tue', deployments: 18, successful: 16, failed: 2 },
  { name: 'Wed', deployments: 8, successful: 7, failed: 1 },
  { name: 'Thu', deployments: 24, successful: 22, failed: 2 },
  { name: 'Fri', deployments: 15, successful: 14, failed: 1 },
  { name: 'Sat', deployments: 5, successful: 5, failed: 0 },
  { name: 'Sun', deployments: 3, successful: 3, failed: 0 },
]

const resourceData = {
  cpu: 42,
  memory: 68,
  disk: 35,
  network: 12.5,
}

export function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['project-stats'],
    queryFn: () => projectApi.stats().then((r) => r.data),
    refetchInterval: 30000,
  })

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Overview of your deployments and infrastructure
          </p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Projects"
          value={stats?.total_projects ?? 12}
          change="+2 this week"
          changeType="positive"
          icon={FolderKanban}
          iconColor="text-blue-400"
          iconBg="bg-blue-400/10"
        />
        <StatCard
          title="Running Deployments"
          value={stats?.active_projects ?? 8}
          change="All systems operational"
          changeType="positive"
          icon={Rocket}
          iconColor="text-emerald-400"
          iconBg="bg-emerald-400/10"
        />
        <StatCard
          title="Failed Deployments"
          value={stats?.failed_deployments ?? 1}
          change="-50% from last week"
          changeType="positive"
          icon={AlertTriangle}
          iconColor="text-red-400"
          iconBg="bg-red-400/10"
        />
        <StatCard
          title="Active Containers"
          value={18}
          change="+3 containers"
          changeType="neutral"
          icon={Container}
          iconColor="text-purple-400"
          iconBg="bg-purple-400/10"
        />
      </div>

      {/* Charts & Activity */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <DeploymentChart data={chartData} />
        </div>
        <div>
          <ActivityFeed activities={demoActivities} />
        </div>
      </div>

      {/* Resource Usage */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <ResourceUsage data={resourceData} />
        </div>
        <div className="lg:col-span-2">
          <div className="glass rounded-xl p-6">
            <h3 className="text-base font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: 'New Project', desc: 'Create deployment', color: 'from-deployhub-500 to-deployhub-600' },
                { label: 'Deploy Now', desc: 'Quick deploy', color: 'from-emerald-500 to-emerald-600' },
                { label: 'View Logs', desc: 'System logs', color: 'from-purple-500 to-purple-600' },
                { label: 'Settings', desc: 'Configure', color: 'from-amber-500 to-amber-600' },
              ].map((action) => (
                <button
                  key={action.label}
                  className="group relative overflow-hidden rounded-xl bg-gradient-to-br p-4 text-left transition-all hover:scale-[1.02]"
                  style={{ backgroundImage: `linear-gradient(135deg, var(--tw-gradient-stops))` }}
                >
                  <div className={cn('absolute inset-0 bg-gradient-to-br opacity-20', action.color)} />
                  <div className="relative">
                    <p className="font-semibold text-sm">{action.label}</p>
                    <p className="text-xs text-white/70 mt-1">{action.desc}</p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(' ')
}
