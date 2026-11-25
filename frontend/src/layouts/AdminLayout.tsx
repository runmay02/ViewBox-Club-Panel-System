import React from "react"
import { Outlet, Link, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  Users,
  ClipboardList,
  Share2,
  FileSpreadsheet,
  BarChart3,
  LogOut,
  Sparkles,
} from "lucide-react"
import { RoleSwitcher } from "@/components/navigation/RoleSwitcher"
import { cn } from "@/utils/cn"
import {useAuth} from "@/contexts/AuthContext"

export const AdminLayout: React.FC = () => {
  const location = useLocation()
  const {user,logout}=useAuth()

  const navItems = [
    { label: "Dashboard & KPIs", path: "/admin", icon: LayoutDashboard },
    { label: "Respondents Grid", path: "/admin/respondents", icon: Users },
    { label: "Survey Projects", path: "/admin/surveys", icon: ClipboardList },
    { label: "Acquisition Sources", path: "/admin/sources", icon: Share2 },
    { label: "Bulk CSV Ingestion", path: "/admin/import", icon: FileSpreadsheet },
    { label: "Analytics & BI", path: "/admin/analytics", icon: BarChart3 },
  ]

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <RoleSwitcher />

      <div className="flex-1 flex">
        {/* Persistent Admin Sidebar */}
        <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-200 flex flex-col">
          {/* Brand Header */}
          <div className="p-5 border-b border-slate-800">
            <div className="flex items-center gap-2.5">
              <div className="h-9 w-9 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center text-white font-bold shadow-md">
                VB
              </div>
              <div>
                <h1 className="font-bold text-sm tracking-tight text-white flex items-center gap-1.5">
                  ViewBox Club
                  <span className="text-[10px] bg-brand-500/20 text-brand-300 px-1.5 py-0.5 rounded font-mono">
                    ADMIN
                  </span>
                </h1>
                <p className="text-[11px] text-slate-400">Concave Insights Ops</p>
              </div>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive =
                item.path === "/admin"
                  ? location.pathname === "/admin"
                  : location.pathname.startsWith(item.path)

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/60"
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>

          {/* Sidebar Footer User Info */}
          <div className="p-4 border-t border-slate-800 bg-slate-950/40">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="h-8 w-8 rounded-full bg-slate-700 flex items-center justify-center font-semibold text-xs text-slate-200">
                  AD
                </div>
                <div>
                  <p className="text-xs font-semibold text-white">Administrator</p>
                  <p className="text-[10px] text-slate-400">+91 {user?.phone}</p>
                </div>
              </div>
              <button
                title="Logout"
                onClick={logout}
                className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800 transition-colors"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content Pane */}
        <main className="flex-1 flex flex-col overflow-y-auto max-h-[calc(100vh-41px)]">
          {/* Top Bar */}
          <header className="h-14 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-10 shadow-xs">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                System Administration
              </span>
              <span className="text-slate-300">/</span>
              <span className="text-xs font-medium text-slate-700">
                {navItems.find(
                  (n) =>
                    n.path === location.pathname ||
                    (n.path !== "/admin" && location.pathname.startsWith(n.path))
                )?.label || "Overview"}
              </span>
            </div>

            <div className="flex items-center gap-3">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                <Sparkles className="h-3 w-3" />
                Live Database Active
              </span>
            </div>
          </header>

          <div className="p-8 flex-1">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
