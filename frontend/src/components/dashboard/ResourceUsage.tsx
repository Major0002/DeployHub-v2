import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Cpu, HardDrive, MemoryStick, Network } from 'lucide-react'

interface ResourceData {
  cpu: number
  memory: number
  disk: number
  network: number
}

interface ResourceUsageProps {
  data: ResourceData
}

export function ResourceUsage({ data }: ResourceUsageProps) {
  const resources = [
    { icon: Cpu, label: 'CPU Usage', value: data.cpu, color: 'bg-deployhub-500', suffix: '%' },
    { icon: MemoryStick, label: 'Memory', value: data.memory, color: 'bg-purple-500', suffix: '%' },
    { icon: HardDrive, label: 'Disk', value: data.disk, color: 'bg-emerald-500', suffix: '%' },
    { icon: Network, label: 'Network', value: data.network, color: 'bg-amber-500', suffix: 'MB/s' },
  ]

  return (
    <Card className="glass">
      <CardHeader>
        <CardTitle className="text-base font-semibold">Resource Usage</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        {resources.map((resource) => {
          const Icon = resource.icon
          return (
            <div key={resource.label} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{resource.label}</span>
                </div>
                <span className="text-sm font-bold">{resource.value}{resource.suffix}</span>
              </div>
              <Progress value={resource.value} className="h-2" />
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}
