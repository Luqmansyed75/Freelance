import { useState } from 'react'
import { Outlet, Link, useLocation } from 'react-router-dom'
import { Briefcase, LayoutDashboard, LogOut, Loader2, Sparkles } from 'lucide-react'
import useAuthStore from '../../store/useAuthStore'
import AuthModal from '../auth/AuthModal'

const Layout = () => {
  const { user, isAuthenticated, logout } = useAuthStore()
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const location = useLocation()

  const handleTriggerScraper = async () => {
    // API logic to trigger scraper
    alert('Scraper synchronization triggered!');
  };

  const navItemClass = (path) => `
    flex items-center space-x-2 px-3 py-2 rounded-md transition-colors
    ${location.pathname === path ? 'bg-primary/20 text-primary' : 'hover:bg-white/5 text-muted-foreground hover:text-foreground'}
  `

  return (
    <div className="min-h-screen flex flex-col relative w-full overflow-hidden">
      {/* Premium Glassmorphic Navbar */}
      <header className="sticky top-0 z-50 w-full border-b border-white/10 glass">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-primary to-purple-500 flex items-center justify-center">
                <Briefcase className="w-5 h-5 text-white" />
              </div>
              <span className="font-bold text-lg tracking-tight text-glow hidden sm:inline-block">
                Freelance Matcher
              </span>
            </Link>

            <nav className="flex items-center space-x-2">
              <Link to="/" className={navItemClass('/')}>
                <LayoutDashboard className="w-4 h-4" />
                <span>Job Board</span>
              </Link>
              {isAuthenticated && (
                <Link to="/crm" className={navItemClass('/crm')}>
                  <Briefcase className="w-4 h-4" />
                  <span>My CRM</span>
                </Link>
              )}
            </nav>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <div className="flex items-center space-x-4">
                {user?.is_admin && (
                  <button 
                    onClick={handleTriggerScraper}
                    className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-accent/50 hover:bg-accent text-accent-foreground text-sm font-medium transition-colors border border-white/10"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Trigger Scraper</span>
                  </button>
                )}
                <div className="flex items-center space-x-3 pl-4 border-l border-white/10">
                  <div className="flex flex-col items-end hidden sm:flex">
                    <span className="text-sm font-medium leading-none">{user?.email}</span>
                    {user?.is_admin && <span className="text-xs text-muted-foreground">Admin</span>}
                  </div>
                  <div className="w-8 h-8 rounded-full bg-secondary border border-white/10 flex items-center justify-center text-sm font-bold text-primary">
                    {user?.email?.charAt(0).toUpperCase()}
                  </div>
                  <button
                    onClick={logout}
                    className="p-1.5 rounded-md text-muted-foreground hover:bg-white/5 hover:text-destructive transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ) : (
              <button
                onClick={() => setIsAuthModalOpen(true)}
                className="px-4 py-2 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-medium transition-all shadow-[0_0_15px_rgba(80,40,250,0.5)] hover:shadow-[0_0_25px_rgba(80,40,250,0.7)]"
              >
                Login / Sign Up
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 container mx-auto px-4 py-8">
        <Outlet />
      </main>

      {/* Auth Modal Portal */}
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </div>
  )
}

export default Layout
