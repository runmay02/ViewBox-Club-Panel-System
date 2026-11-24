import React, { useState } from "react"
import {
  Copy,
  Check,
  Share2,
  Gift,
  CheckCircle2,
  XCircle,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/Card"
import { mockUserReferrals, mockCurrentUser } from "@/mock/demoData"

export const RespondentReferralsPage: React.FC = () => {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(mockCurrentUser.referral_link)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleWhatsAppShare = () => {
    const text = encodeURIComponent(
      `Join ViewBox Club to participate in paid consumer research surveys! Sign up through my personal link: ${mockCurrentUser.referral_link}`
    )
    window.open(`https://api.whatsapp.com/send?text=${text}`, "_blank")
  }

  const completedCount = mockUserReferrals.filter((r) => r.stage === "COMPLETED").length
  const totalBonusEarned = mockUserReferrals.reduce((sum, r) => sum + r.bonus_amount, 0)

  return (
    <div className="space-y-4">
      {/* Referral Program Hero Card */}
      <div className="bg-gradient-to-tr from-purple-700 via-brand-600 to-indigo-600 rounded-2xl p-4 text-white shadow-sm">
        <div className="flex items-center gap-1.5 text-xs text-purple-200 font-medium mb-1">
          <Gift className="h-3.5 w-3.5" />
          <span>Refer & Earn ₹100 per Survey</span>
        </div>
        <h2 className="text-base font-bold">Invite Friends & Family</h2>
        <p className="text-[11px] text-purple-100 mt-1 leading-relaxed">
          Earn a ₹100 referral bonus for every friend who signs up, qualifies for survey demographics, and successfully completes their study.
        </p>

        {/* Share Link Box */}
        <div className="mt-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-2.5 flex items-center justify-between gap-2">
          <span className="text-[11px] font-mono text-purple-100 truncate">
            {mockCurrentUser.referral_link}
          </span>
          <div className="flex items-center gap-1.5 shrink-0">
            <button
              onClick={handleCopy}
              className="px-2.5 py-1 bg-white text-brand-700 hover:bg-brand-50 rounded-md text-[11px] font-bold shadow-xs flex items-center gap-1 transition-colors"
            >
              {copied ? <Check className="h-3 w-3 text-emerald-600" /> : <Copy className="h-3 w-3" />}
              <span>{copied ? "Copied" : "Copy"}</span>
            </button>
            <button
              onClick={handleWhatsAppShare}
              className="p-1 bg-emerald-500 text-white hover:bg-emerald-600 rounded-md shadow-xs transition-colors"
              title="Share on WhatsApp"
            >
              <Share2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Summary KPI Counters */}
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <p className="text-[10px] text-slate-500 font-medium">Invited</p>
          <p className="text-base font-bold text-slate-900 mt-0.5">
            {mockUserReferrals.length}
          </p>
        </div>
        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <p className="text-[10px] text-slate-500 font-medium">Completed</p>
          <p className="text-base font-bold text-emerald-600 mt-0.5">
            {completedCount}
          </p>
        </div>
        <div className="p-3 bg-white rounded-xl border border-slate-200 shadow-2xs">
          <p className="text-[10px] text-slate-500 font-medium">Bonuses</p>
          <p className="text-base font-bold text-brand-600 mt-0.5">
            ₹{totalBonusEarned}
          </p>
        </div>
      </div>

      {/* Rules Notice */}
      <div className="p-3 rounded-xl bg-slate-100/80 border border-slate-200/60 text-[11px] text-slate-600 leading-relaxed">
        <p className="font-semibold text-slate-800 mb-0.5">Three-Stage Bonus Policy:</p>
        1. <strong>Lead:</strong> Friend registers via your link.<br />
        2. <strong>Fit:</strong> Operations verifies their demographic suitability.<br />
        3. <strong>Completed:</strong> Friend finishes a survey & passes quality checks. (Bonus unlocked!)
      </div>

      {/* Referred Friends Feed */}
      <div className="space-y-2">
        <div className="flex items-center justify-between pt-1">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Referred Friends ({mockUserReferrals.length})
          </h3>
          <span className="text-[10px] text-slate-400">Phones masked for privacy</span>
        </div>

        <div className="space-y-2.5">
          {mockUserReferrals.map((ref) => {
            return (
              <Card key={ref.id} className="border-slate-200 shadow-2xs">
                <CardContent className="p-3.5 space-y-2.5">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-bold text-slate-900">
                          {ref.referred_name}
                        </span>
                        {/* Strictly Masked Phone */}
                        <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">
                          {ref.masked_phone}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        Joined on {ref.registered_on}
                      </p>
                    </div>

                    <div className="text-right">
                      {ref.bonus_status === "EARNED" ? (
                        <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full inline-flex items-center gap-1">
                          <CheckCircle2 className="h-3 w-3" />
                          +₹100
                        </span>
                      ) : ref.stage === "FAILED" ? (
                        <span className="text-[10px] font-semibold text-rose-600 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">
                          Disqualified
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold text-amber-700 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full">
                          In Progress
                        </span>
                      )}
                    </div>
                  </div>

                  {/* 3-Stage Progress Bar */}
                  <div className="pt-1">
                    <div className="grid grid-cols-3 gap-1 text-center text-[9px] font-bold uppercase tracking-wider mb-1">
                      <span className={ref.stage !== "FAILED" ? "text-brand-600" : "text-slate-400"}>
                        1. Lead
                      </span>
                      <span className={ref.stage === "FIT" || ref.stage === "COMPLETED" ? "text-purple-600" : "text-slate-400"}>
                        2. Fit
                      </span>
                      <span className={ref.stage === "COMPLETED" ? "text-emerald-600" : "text-slate-400"}>
                        3. Completed
                      </span>
                    </div>

                    <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden flex">
                      {ref.stage === "FAILED" ? (
                        <div className="h-full w-1/3 bg-rose-400" />
                      ) : (
                        <>
                          <div className="h-full w-1/3 bg-brand-500" />
                          <div
                            className={`h-full w-1/3 ${
                              ref.stage === "FIT" || ref.stage === "COMPLETED"
                                ? "bg-purple-500"
                                : "bg-slate-200"
                            }`}
                          />
                          <div
                            className={`h-full w-1/3 ${
                              ref.stage === "COMPLETED" ? "bg-emerald-500" : "bg-slate-200"
                            }`}
                          />
                        </>
                      )}
                    </div>
                  </div>

                  {/* Operational Failure Explanation if marked Failed */}
                  {ref.stage === "FAILED" && ref.failure_reason && (
                    <div className="p-2 bg-rose-50 border border-rose-200 rounded-lg text-[10px] text-rose-700 flex items-start gap-1.5">
                      <XCircle className="h-3.5 w-3.5 shrink-0 mt-0.5" />
                      <span>{ref.failure_reason}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
