export interface Project {
  id: string
  name: string
  slug: string
  description: string | null
  repo_url: string | null
  repo_branch: string
  language: string | null
  framework: string | null
  build_command: string | null
  output_directory: string
  env_vars: Record<string, string>
  status: string
  health_status: string
  cpu_limit: string
  memory_limit: string
  owner_id: string
  created_at: string
  updated_at: string
  last_deployed_at: string | null
  deployments?: Deployment[]
}

export interface Deployment {
  id: string
  status: string
  commit_sha: string | null
  commit_message: string | null
  branch: string
  image_tag: string | null
  container_id: string | null
  build_logs: string | null
  runtime_logs: string | null
  build_duration_ms: number | null
  deploy_duration_ms: number | null
  preview_url: string | null
  production_url: string | null
  error_message: string | null
  project_id: string
  triggered_by: string | null
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface ProjectStats {
  total_projects: number
  active_projects: number
  failed_projects: number
  total_deployments: number
  successful_deployments: number
  failed_deployments: number
}

export interface ActivityItem {
  id: string
  type: 'deployment' | 'project' | 'system'
  status: string
  message: string
  project_name: string
  timestamp: string
}
