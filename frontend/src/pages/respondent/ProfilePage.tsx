import React from "react"
import {
  User,
  MapPin,
  Calendar,
  Briefcase,
  Heart,
  ShieldCheck,
  Award,
  History,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { mockCurrentUser } from "@/mock/demoData"

export const RespondentProfilePage: React.FC = () => {
  return (
    <div className="space-y-4">
      {/* Profile Header Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-4 shadow-xs flex items-center gap-3.5">
        <div className="h-14 w-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-500 text-white flex items-center justify-center font-bold text-lg shadow-sm">
          IS
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <h3 className="text-sm font-bold text-slate-900">{mockCurrentUser.name}</h3>
            <span className="text-[10px] bg-brand-50 text-brand-700 font-mono px-1.5 py-0.2 rounded font-semibold border border-brand-200">
              {mockCurrentUser.member_id}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{mockCurrentUser.email}</p>
          <span className="inline-flex items-center gap-1 text-[10px] text-emerald-700 font-semibold mt-1">
            <ShieldCheck className="h-3 w-3" /> Phone Verified: +91 {mockCurrentUser.phone}
          </span>
        </div>
      </div>

      {/* Demographics Card */}
      <Card className="border-slate-200 shadow-2xs">
        <CardContent className="p-4 space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <User className="h-3.5 w-3.5" />
            Demographic Information
          </h4>

          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5 text-slate-400" /> City:
              </span>
              <span className="font-semibold text-slate-800">{mockCurrentUser.city}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5 text-slate-400" /> Date of Birth:
              </span>
              <span className="font-semibold text-slate-800">
                {mockCurrentUser.date_of_birth} ({mockCurrentUser.age} years)
              </span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-100">
              <span className="text-slate-500 flex items-center gap-1">
                <Briefcase className="h-3.5 w-3.5 text-slate-400" /> Income Range:
              </span>
              <span className="font-semibold text-slate-800">{mockCurrentUser.income_range}</span>
            </div>
            <div className="py-1">
              <span className="text-slate-500 flex items-center gap-1 mb-1.5">
                <Heart className="h-3.5 w-3.5 text-slate-400" /> Stated Interests:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {mockCurrentUser.interests.map((interest) => (
                  <Badge key={interest} variant="secondary" className="text-[10px]">
                    {interest}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Study Participation Status */}
      <Card className="border-slate-200 shadow-2xs">
        <CardContent className="p-4 space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Award className="h-3.5 w-3.5" />
            Panel Participation Status
          </h4>

          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-900 flex items-center justify-between">
            <div>
              <p className="font-bold">Next Survey Eligibility</p>
              <p className="text-[11px] text-emerald-700">Eligible immediately (No active cool-off)</p>
            </div>
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse" />
          </div>

          <div className="pt-2 text-[11px] text-slate-500 flex items-center gap-1">
            <History className="h-3.5 w-3.5 text-slate-400" />
            <span>Completed Surveys to Date: <strong>2 studies</strong> (₹500 earned)</span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
