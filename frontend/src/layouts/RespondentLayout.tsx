import React, { useState } from "react"
import { Outlet, Link, useLocation } from "react-router-dom"
import {
  Compass,
  Users,
  User,
  Copy,
  Check,
  Smartphone,
  Monitor,
} from "lucide-react"
import { RoleSwitcher } from "@/components/navigation/RoleSwitcher"
import { cn } from "@/utils/cn"
import { useQuery } from "@tanstack/react-query"
import api from "@/utils/api"
import { useAuth } from "@/contexts/AuthContext"

export const RespondentLayout: React.FC = () => {
  const location = useLocation()
  const [copied, setCopied] = useState(false)
  const [isMobilePreview, setIsMobilePreview] = useState(true)
  const { logout } = useAuth()
  const {data:profile}=useQuery({queryKey:["profile"],queryFn:async()=> (await api.get<{full_name:string;referral_link:string;total_earned:number}>("/members/me")).data})

  const handleCopyLink = () => {
    if(profile?.referral_link) void navigator.clipboard.writeText(new URL(profile.referral_link,window.location.origin).toString())
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const bottomNavItems = [
    { label: "Surveys", path: "/portal", icon: Compass },
    { label: "My Referrals", path: "/portal/referrals", icon: Users },
    { label: "My Profile", path: "/portal/profile", icon: User },
  ]

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-sans">
      <RoleSwitcher />

      {/* Viewport Mode Bar */}
      <div className="bg-slate-900 border-b border-slate-800 text-slate-400 py-1.5 px-4 text-xs flex items-center justify-between">
        <span className="text-[11px] font-medium text-slate-400 hidden sm:inline">
          📱 <strong>Mobile-First Respondent Portal</strong> (Optimized for Android / iOS)
        </span>
        <div className="flex items-center gap-2 ml-auto">
          <button
            onClick={() => setIsMobilePreview(true)}
            className={cn(
              "flex items-center gap-1 px-2.5 py-1 rounded text-[11px] transition-colors",
              isMobilePreview
                ? "bg-brand-600 text-white font-semibold shadow-xs"
                : "hover:text-slate-200"
            )}
          >
            <Smartphone className="h-3 w-3" />
            <span>Mobile Device Frame</span>
          </button>
          <button
            onClick={() => setIsMobilePreview(false)}
            className={cn(
              "flex items-center gap-1 px-2.5 py-1 rounded text-[11px] transition-colors",
              !isMobilePreview
                ? "bg-brand-600 text-white font-semibold shadow-xs"
                : "hover:text-slate-200"
            )}
          >
            <Monitor className="h-3 w-3" />
            <span>Fullscreen</span>
          </button>
        </div>
      </div>

      {/* Outer Centering Canvas */}
      <div className="flex-1 flex items-start justify-center p-0 sm:py-6">
        <div
          className={cn(
            "w-full bg-slate-50 text-slate-900 flex flex-col transition-all min-h-screen sm:min-h-[820px]",
            isMobilePreview
              ? "sm:max-w-[430px] sm:rounded-3xl sm:border-[8px] sm:border-slate-800 sm:shadow-2xl sm:overflow-hidden relative"
              : "max-w-2xl sm:rounded-xl shadow-lg border border-slate-200"
          )}
        >
          {/* Respondent Mobile Sticky Header */}
          <header className="bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-20 shadow-xs">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-brand-600 text-white flex items-center justify-center font-bold text-xs shadow-xs">
                  VB
                </div>
                <div>
                  <h2 className="text-xs font-bold text-slate-900 leading-tight">
                    ViewBox Club
                  </h2>
                  <p className="text-[10px] text-slate-500">
                    Welcome, {profile?.full_name.split(" ")[0] || "Member"}
                  </p>
                </div>
              </div>

              {/* Earnings & Referral Quick Button */}
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-xs">
                  ₹{profile?.total_earned || 0}
                </span>

                <button
                  onClick={handleCopyLink}
                  title="Copy My Referral Link"
                  className="flex items-center gap-1 px-2 py-1 rounded-md text-xs font-medium bg-brand-50 text-brand-700 border border-brand-200 hover:bg-brand-100 transition-colors shadow-xs"
                >
                  {copied ? (
                    <Check className="h-3.5 w-3.5 text-emerald-600" />
                  ) : (
                    <Copy className="h-3.5 w-3.5" />
                  )}
                  <span className="text-[10px] font-semibold">
                    {copied ? "Copied!" : "Refer"}
                  </span>
                </button>
                <button onClick={logout} className="text-[10px] text-slate-500 hover:text-rose-600" aria-label="Sign out">Log out</button>
              </div>
            </div>
          </header>

          {/* Scrollable Viewport Body */}
          <div className="flex-1 p-4 pb-20 overflow-y-auto">
            <Outlet />
          </div>

          {/* Sticky Bottom Navigation Bar */}
          <nav className="absolute bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md border-t border-slate-200 py-1.5 px-6 flex items-center justify-around z-20 shadow-lg">
            {bottomNavItems.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.path

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={cn(
                    "flex flex-col items-center gap-1 py-1 px-3 rounded-lg text-[10px] font-semibold transition-colors",
                    isActive
                      ? "text-brand-600 font-bold"
                      : "text-slate-400 hover:text-slate-700"
                  )}
                >
                  <Icon
                    className={cn(
                      "h-5 w-5 transition-transform",
                      isActive && "scale-110"
                    )}
                  />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </div>
    </div>
  )
}
