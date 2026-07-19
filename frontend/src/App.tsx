import { Routes, Route, Navigate } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuthStore } from '@/store/authStore'
import { authApi } from '@/lib/api'
import { AppLayout } from '@/components/layout/AppLayout'
import { Dashboard } from '@/pages/Dashboard'
import { Projects } from '@/pages/Projects'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    )
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore()
  return !isAuthenticated ? <>{children}</> : <Navigate to="/" replace />
}

function AuthInitializer({ children }: { children: React.ReactNode }) {
  const { setUser, setLoading } = useAuthStore()

  useEffect(() => {
    const init = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const response = await authApi.me()
          setUser(response.data)
        } catch {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setLoading(false)
    }
    init()
  }, [setUser, setLoading])

  return <>{children}</>
}

export default function App() {
  return (
    <AuthInitializer>
      <Routes>
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
          <Route path="docker" element={<div className="text-muted-foreground">Docker Engine - Coming in Milestone 2</div>} />
          <Route path="kubernetes" element={<div className="text-muted-foreground">Kubernetes - Coming in Milestone 4</div>} />
          <Route path="pipelines" element={<div className="text-muted-foreground">CI/CD Pipelines - Coming in Milestone 6</div>} />
          <Route path="terraform" element={<div className="text-muted-foreground">Terraform - Coming in Milestone 5</div>} />
          <Route path="monitoring" element={<div className="text-muted-foreground">Monitoring - Coming in Milestone 7</div>} />
          <Route path="settings" element={<div className="text-muted-foreground">Settings - Coming soon</div>} />
        </Route>
      </Routes>
    </AuthInitializer>
  )
}
