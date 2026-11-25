import React from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { Shield, Users, Smartphone } from "lucide-react"
import { cn } from "@/utils/cn"
import { useAuth } from "@/contexts/AuthContext"

export const RoleSwitcher: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const currentPath = location.pathname
  const {user}=useAuth()

  const roles = [
    {
      id: "respondent",
      label: "Respondent Portal",
      path: "/portal",
      icon: Smartphone,
      active: currentPath.startsWith("/portal") || currentPath === "/",
      badge: "Mobile-First",
    },
    {
      id: "operations",
      label: "Operations Triage",
      path: "/ops",
      icon: Users,
      active: currentPath.startsWith("/ops"),
      badge: "Queue Active",
    },
    {
      id: "admin",
      label: "Admin Mission Control",
      path: "/admin",
      icon: Shield,
      active: currentPath.startsWith("/admin"),
      badge: "Full Control",
    },
  ].filter(r=>user?.role==="ADMIN"||(user?.role==="OPERATIONS"&&r.id!=="admin")||(user?.role==="RESPONDENT"&&r.id==="respondent"))

  return (
    <div className="bg-slate-900 border-b border-slate-800 text-white px-4 py-2 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            ViewBox Club Demo Role Switcher:
          </span>
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto">
          {roles.map((r) => {
            const Icon = r.icon
            return (
              <button
                key={r.id}
                onClick={() => navigate(r.path)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all",
                  r.active
                    ? "bg-brand-600 text-white shadow-sm ring-1 ring-brand-400"
                    : "bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{r.label}</span>
                <span
                  className={cn(
                    "text-[10px] px-1.5 py-0.2 rounded-full font-semibold",
                    r.active
                      ? "bg-brand-700 text-white"
                      : "bg-slate-900 text-slate-400"
                  )}
                >
                  {r.badge}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}
