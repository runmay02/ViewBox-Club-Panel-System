import React, { useState } from "react"
import {
  DollarSign,
  CheckCircle2,
  ShieldCheck,
  Check,
} from "lucide-react"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { mockOpsQueues, PayoutDemo } from "@/mock/demoData"

export const OperationsPayoutQueue: React.FC = () => {
  const [payouts, setPayouts] = useState<PayoutDemo[]>(mockOpsQueues.payout_approvals)
  const [notification, setNotification] = useState<string | null>(null)

  const handleApprove = (id: string, name: string, amount: number) => {
    setPayouts((prev) =>
      prev.map((p) => (p.id === id ? { ...p, status: "APPROVED" } : p))
    )
    setNotification(`Payout of ₹${amount} for ${name} authorized! Payout record transitioned to APPROVED.`)
    setTimeout(() => setNotification(null), 3000)
  }

  return (
    <div className="space-y-6">
      {/* Notification Toast */}
      {notification && (
        <div className="p-3 bg-slate-900 text-white rounded-lg text-xs font-medium flex items-center gap-2 shadow-lg animate-in fade-in">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-emerald-600" />
            Payout Authorization Ledger
          </h2>
          <p className="text-xs text-slate-500">
            Operations two-step approval queue for verified survey completions and referral bonuses.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2.5 py-1 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-md">
            ₹500 Pending Sign-Off
          </span>
        </div>
      </div>

      {/* Payouts Table */}
      <Card className="border-slate-200 shadow-xs overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
              <tr>
                <th className="py-3 px-4">Payee Member</th>
                <th className="py-3 px-4">Incentive Type</th>
                <th className="py-3 px-4">Associated Context</th>
                <th className="py-3 px-4">Amount</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Queued On</th>
                <th className="py-3 px-4 text-right">Approval Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {payouts.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4">
                    <p className="font-bold text-slate-900">{p.member_name}</p>
                    <span className="font-mono text-[10px] text-slate-400">
                      {p.member_id}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={p.type === "SURVEY_COMPLETION" ? "default" : "secondary"}>
                      {p.type === "SURVEY_COMPLETION" ? "Survey Reward" : "Referral Bonus"}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-slate-600 max-w-xs truncate">
                    {p.survey_title || p.referral_name}
                  </td>
                  <td className="py-3 px-4 font-bold text-emerald-700">
                    ₹{p.amount}
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                        p.status === "APPROVED"
                          ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                          : "bg-amber-50 text-amber-700 border border-amber-200"
                      }`}
                    >
                      {p.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-400 text-[11px]">{p.created_at}</td>
                  <td className="py-3 px-4 text-right">
                    {p.status === "PENDING_APPROVAL" ? (
                      <Button
                        size="sm"
                        variant="brand"
                        onClick={() => handleApprove(p.id, p.member_name, p.amount)}
                      >
                        <Check className="h-3.5 w-3.5 mr-1" />
                        Authorize Payout
                      </Button>
                    ) : (
                      <span className="text-xs font-semibold text-emerald-600 inline-flex items-center gap-1">
                        <ShieldCheck className="h-4 w-4" /> Ready for Transfer
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  )
}
