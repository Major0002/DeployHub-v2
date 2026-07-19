import { useState } from 'react'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Project } from '@/types'

interface ProjectFormProps {
  project?: Project | null
  onSubmit: (data: any) => void
  onCancel: () => void
}

export function ProjectForm({ project, onSubmit, onCancel }: ProjectFormProps) {
  const [formData, setFormData] = useState({
    name: project?.name || '',
    description: project?.description || '',
    repo_url: project?.repo_url || '',
    repo_branch: project?.repo_branch || 'main',
    language: project?.language || '',
    framework: project?.framework || '',
    build_command: project?.build_command || '',
    output_directory: project?.output_directory || 'dist',
    cpu_limit: project?.cpu_limit || '1',
    memory_limit: project?.memory_limit || '512Mi',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit(formData)
  }

  return (
    <Card className="glass">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-base font-semibold">
          {project ? 'Edit Project' : 'Create Project'}
        </CardTitle>
        <Button variant="ghost" size="icon" onClick={onCancel}>
          <X className="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Project Name *</label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="my-awesome-app"
                required
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Repository URL</label>
              <Input
                value={formData.repo_url}
                onChange={(e) => setFormData({ ...formData, repo_url: e.target.value })}
                placeholder="https://github.com/user/repo"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Description</label>
            <Input
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Brief description of your project"
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Language</label>
              <Input
                value={formData.language}
                onChange={(e) => setFormData({ ...formData, language: e.target.value })}
                placeholder="node, python, go..."
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Framework</label>
              <Input
                value={formData.framework}
                onChange={(e) => setFormData({ ...formData, framework: e.target.value })}
                placeholder="nextjs, fastapi..."
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Branch</label>
              <Input
                value={formData.repo_branch}
                onChange={(e) => setFormData({ ...formData, repo_branch: e.target.value })}
                placeholder="main"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Build Command</label>
              <Input
                value={formData.build_command}
                onChange={(e) => setFormData({ ...formData, build_command: e.target.value })}
                placeholder="npm run build"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Output Directory</label>
              <Input
                value={formData.output_directory}
                onChange={(e) => setFormData({ ...formData, output_directory: e.target.value })}
                placeholder="dist"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">CPU Limit</label>
              <Input
                value={formData.cpu_limit}
                onChange={(e) => setFormData({ ...formData, cpu_limit: e.target.value })}
                placeholder="1"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Memory Limit</label>
              <Input
                value={formData.memory_limit}
                onChange={(e) => setFormData({ ...formData, memory_limit: e.target.value })}
                placeholder="512Mi"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit">
              {project ? 'Update Project' : 'Create Project'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
