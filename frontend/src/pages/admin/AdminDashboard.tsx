import React from "react"
import {
  Users,
  ClipboardList,
  DollarSign,
  Share2,
  ArrowUpRight,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/Card"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from "recharts"
import { mockAdminKpis } from "@/mock/demoData"

export const AdminDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Title & Mission Statement */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Executive Operations & Business Intelligence
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time panel metrics, acquisition channel attribution, and referral performance.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-3 py-1 bg-brand-50 text-brand-700 border border-brand-200 rounded-lg">
            Active Cycle: Q4 Panel Intake
          </span>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-slate-200 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-slate-500 uppercase">
              Total Respondents
            </CardTitle>
            <div className="h-8 w-8 rounded-lg bg-brand-50 text-brand-600 flex items-center justify-center">
              <Users className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              {mockAdminKpis.total_respondents}
            </div>
            <p className="text-xs text-emerald-600 font-medium flex items-center gap-1 mt-1">
              <ArrowUpRight className="h-3.5 w-3.5" />
              <span>+{mockAdminKpis.new_signups_7d} new this week</span>
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-slate-500 uppercase">
              Active Surveys
            </CardTitle>
            <div className="h-8 w-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <ClipboardList className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              {mockAdminKpis.active_surveys}
            </div>
            <p className="text-xs text-slate-500 font-medium mt-1">
              {mockAdminKpis.completed_surveys} verified completions
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-slate-500 uppercase">
              Referral Conversions
            </CardTitle>
            <div className="h-8 w-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center">
              <Share2 className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              {mockAdminKpis.successful_referrals}
            </div>
            <p className="text-xs text-slate-500 font-medium mt-1">
              Out of {mockAdminKpis.total_referrals} total leads (21% conversion)
            </p>
          </CardContent>
        </Card>

        <Card className="border-slate-200 shadow-xs">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-medium text-slate-500 uppercase">
              Payouts Disbursed
            </CardTitle>
            <div className="h-8 w-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <DollarSign className="h-4 w-4" />
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-slate-900">
              ₹{mockAdminKpis.total_payouts_disbursed.toLocaleString()}
            </div>
            <p className="text-xs text-amber-600 font-medium mt-1">
              12 operations tasks pending sign-off
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Visual Analytics Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Signup Acquisition Timeline Chart */}
        <Card className="border-slate-200 shadow-xs">
          <CardHeader>
            <CardTitle className="text-sm font-bold text-slate-900">
              7-Day Respondent Acquisition Velocity
            </CardTitle>
            <p className="text-xs text-slate-500">
              Daily consumer signups across all acquisition channels
            </p>
          </CardHeader>
          <CardContent className="h-64 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockAdminKpis.signup_trend}>
                <defs>
                  <linearGradient id="signupGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1e293b",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px",
                    border: "none",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="signups"
                  stroke="#4f46e5"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#signupGrad)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Acquisition Channel Breakdown */}
        <Card className="border-slate-200 shadow-xs">
          <CardHeader>
            <CardTitle className="text-sm font-bold text-slate-900">
              Source Attribution Distribution
            </CardTitle>
            <p className="text-xs text-slate-500">
              Respondent volume mapped to dynamic database channels
            </p>
          </CardHeader>
          <CardContent className="h-64 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockAdminKpis.source_distribution}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis
                  dataKey="name"
                  tick={{ fontSize: 10, fill: "#64748b" }}
                  interval={0}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis tick={{ fontSize: 11, fill: "#64748b" }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#1e293b",
                    borderRadius: "8px",
                    color: "#fff",
                    fontSize: "12px",
                    border: "none",
                  }}
                />
                <Bar dataKey="count" radius={[6, 6, 0, 0]}>
                  {mockAdminKpis.source_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Referral Conversion Funnel */}
      <Card className="border-slate-200 shadow-xs">
        <CardHeader>
          <CardTitle className="text-sm font-bold text-slate-900">
            Referral Quality & Conversion Funnel
          </CardTitle>
          <p className="text-xs text-slate-500">
            Three-stage progression: Registered Lead → Operations Fit Approval → Verified Survey Completion
          </p>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {mockAdminKpis.referral_funnel.map((step, idx) => (
              <div
                key={step.stage}
                className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 flex flex-col justify-between"
              >
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    Stage {idx + 1}
                  </span>
                  <h4 className="text-sm font-bold text-slate-900 mt-1">{step.stage}</h4>
                </div>
                <div className="mt-4 flex items-baseline justify-between">
                  <span className="text-3xl font-extrabold text-slate-900">{step.count}</span>
                  <span className="text-xs font-semibold text-slate-500">
                    {idx === 0
                      ? "100%"
                      : idx === 1
                      ? "54% fit rate"
                      : "21% bonus unlocked"}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
