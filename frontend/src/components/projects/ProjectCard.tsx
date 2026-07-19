import { Link } from 'react-router-dom'
import { GitBranch, ExternalLink, MoreVertical, Trash2, Edit } from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { getStatusColor, getStatusDot, formatRelativeTime } from '@/lib/utils'
import type { Project } from '@/types'

interface ProjectCardProps {
  project: Project
  onDelete?: (id: string) => void
}

export function ProjectCard({ project, onDelete }: ProjectCardProps) {
  return (
    <Card className="glass card-hover group">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={cn('h-3 w-3 rounded-full', getStatusDot(project.status))} />
            <div>
              <h3 className="font-semibold text-sm">{project.name}</h3>
              <p className="text-xs text-muted-foreground">{project.slug}</p>
            </div>
          </div>
          <Badge variant="outline" className={cn('text-xs', getStatusColor(project.status))}>
            {project.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <p className="text-sm text-muted-foreground line-clamp-2">
          {project.description || 'No description'}
        </p>

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          {project.language && (
            <span className="flex items-center gap-1">
              <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{project.language}</span>
            </span>
          )}
          {project.framework && (
            <span className="flex items-center gap-1">
              <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px]">{project.framework}</span>
            </span>
          )}
        </div>

        {project.repo_url && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <GitBranch className="h-3 w-3" />
            <span className="truncate">{project.repo_url.replace('https://github.com/', '')}</span>
          </div>
        )}

        <div className="flex items-center justify-between pt-2 border-t border-border/50">
          <span className="text-xs text-muted-foreground">
            {project.last_deployed_at ? formatRelativeTime(project.last_deployed_at) : 'Never deployed'}
          </span>
          <div className="flex items-center gap-1">
            <Button variant="ghost" size="icon" className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity">
              <Edit className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 opacity-0 group-hover:opacity-100 transition-opacity text-destructive hover:text-destructive"
              onClick={() => onDelete?.(project.id)}
            >
              <Trash2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function cn(...classes: (string | undefined | false)[]) {
  return classes.filter(Boolean).join(' ')
}
