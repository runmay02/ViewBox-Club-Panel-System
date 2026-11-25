import React from "react"
import { Outlet, Link, useLocation } from "react-router-dom"
import {
  Users,
  CheckCircle2,
  DollarSign,
  AlertTriangle,
  ClipboardList,
} from "lucide-react"
import { RoleSwitcher } from "@/components/navigation/RoleSwitcher"
import { cn } from "@/utils/cn"
import {useAuth} from "@/contexts/AuthContext"

export const OperationsLayout: React.FC = () => {
  const location = useLocation()
  const {user}=useAuth()

  const tabs = [
    {
      label: "Referral Verification Queue",
      path: "/ops",
      icon: Users,
      badge: "",
    },
    {
      label: "Respondents",
      path: "/ops/respondents",
      icon: Users,
      badge: "",
    },
    {
      label: "Survey Applications",
      path: "/ops/applications",
      icon: ClipboardList,
      badge: "",
    },
    {
      label: "Payout Authorization",
      path: "/ops/payouts",
      icon: DollarSign,
      badge: "",
    },
    {
      label: "Fraud Review Queue",
      path: "/ops/fraud",
      icon: AlertTriangle,
      badge: "",
    },
  ]

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <RoleSwitcher />

      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 shadow-xs">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-amber-500 flex items-center justify-center text-white font-bold shadow-sm">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold text-slate-900">
                  Operations Triage Portal
                </h1>
                <span className="text-[10px] font-semibold bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full">
                  Ops Lead
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Respondent suitability reviews, referral verifications & payout authorizations
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div className="text-right">
              <p className="text-xs font-semibold text-slate-800">Operations</p>
              <p className="text-[10px] text-slate-500">+91 {user?.phone}</p>
            </div>
            <div className="h-8 w-8 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-xs">
              FA
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="max-w-7xl mx-auto mt-4 flex items-center gap-1 border-t border-slate-100 pt-3 overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = location.pathname === tab.path

            return (
              <Link
                key={tab.path}
                to={tab.path}
                className={cn(
                  "flex items-center gap-2 px-3.5 py-2 rounded-md text-xs font-medium transition-all whitespace-nowrap",
                  isActive
                    ? "bg-slate-900 text-white shadow-xs"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-100"
                )}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    className={cn(
                      "text-[10px] px-1.5 py-0.2 rounded-full font-bold",
                      isActive
                        ? "bg-brand-500 text-white"
                        : "bg-slate-200 text-slate-700"
                    )}
                  >
                    {tab.badge}
                  </span>
                )}
              </Link>
            )
          })}
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-6">
        <Outlet />
      </main>
    </div>
  )
}
