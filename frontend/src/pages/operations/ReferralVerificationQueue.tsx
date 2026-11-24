import React, { useState } from "react"
import {
  CheckCircle2,
  Search,
  Filter,
  Check,
} from "lucide-react"
import { Card } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Modal } from "@/components/ui/Modal"
import { mockOpsQueues } from "@/mock/demoData"

export const OperationsReferralQueue: React.FC = () => {
  const [queue, setQueue] = useState(mockOpsQueues.referral_reviews)
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null)
  const [failModalOpen, setFailModalOpen] = useState(false)
  const [failReason, setFailReason] = useState("Outside Target Geography")
  const [customReason, setCustomReason] = useState("")
  const [notification, setNotification] = useState<string | null>(null)

  const showNotification = (msg: string) => {
    setNotification(msg)
    setTimeout(() => setNotification(null), 3000)
  }

  const handleApproveFit = (id: string, name: string) => {
    setQueue((prev) =>
      prev.map((item) => (item.id === id ? { ...item, stage: "FIT" } : item))
    )
    showNotification(`Candidate ${name} approved as 'FIT'. They can now participate in surveys.`)
  }

  const handleConfirmCompletion = (id: string, name: string) => {
    setQueue((prev) => prev.filter((item) => item.id !== id))
    showNotification(
      `Survey completion verified for ${name}! Referral marked 'COMPLETED' and ₹100 bonus queued for approval.`
    )
  }

  const handleOpenFailModal = (candidate: any) => {
    setSelectedCandidate(candidate)
    setFailReason("Outside Target Geography")
    setCustomReason("")
    setFailModalOpen(true)
  }

  const handleConfirmFail = () => {
    if (!selectedCandidate) return
    const reason = failReason === "Other" ? customReason : failReason
    setQueue((prev) => prev.filter((item) => item.id !== selectedCandidate.id))
    setFailModalOpen(false)
    showNotification(
      `Referral for ${selectedCandidate.candidate_name} marked as FAILED with reason: "${reason}"`
    )
  }

  return (
    <div className="space-y-6">
      {/* Notification Toast */}
      {notification && (
        <div className="p-3 bg-slate-900 text-white rounded-lg text-xs font-medium flex items-center gap-2 shadow-lg animate-in fade-in slide-in-from-top-2">
          <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Header Info */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900">
            Referral Verification Queue
          </h2>
          <p className="text-xs text-slate-500">
            Review respondent suitability and verify survey quality before unlocking referral bonuses.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-md">
            {queue.length} Pending Tasks
          </span>
        </div>
      </div>

      {/* Verification Table Card */}
      <Card className="border-slate-200 shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-white flex items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search candidate by name, phone or referrer..."
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-md border border-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
            />
          </div>

          <div className="flex items-center gap-2">
            <button className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-600 border border-slate-200 rounded-md hover:bg-slate-50 font-medium">
              <Filter className="h-3.5 w-3.5 text-slate-400" /> Filter
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
              <tr>
                <th className="py-3 px-4">Candidate Respondent</th>
                <th className="py-3 px-4">Contact & City</th>
                <th className="py-3 px-4">Referred By (Member)</th>
                <th className="py-3 px-4">Current Stage</th>
                <th className="py-3 px-4">Registered</th>
                <th className="py-3 px-4 text-right">Operational Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {queue.map((row) => (
                <tr key={row.id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3 px-4">
                    <p className="font-bold text-slate-900">{row.candidate_name}</p>
                    <span className="font-mono text-[10px] text-slate-400">
                      {row.candidate_id}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <p className="text-slate-700 font-medium">+91 {row.phone}</p>
                    <p className="text-[10px] text-slate-400">{row.city}</p>
                  </td>
                  <td className="py-3 px-4">
                    <p className="text-slate-800 font-semibold">{row.referrer_name}</p>
                    <span className="font-mono text-[10px] text-brand-600">
                      {row.referrer_id}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <Badge variant={row.stage === "LEAD" ? "lead" : "fit"}>
                      {row.stage}
                    </Badge>
                  </td>
                  <td className="py-3 px-4 text-slate-500">{row.registered_at}</td>
                  <td className="py-3 px-4 text-right space-x-1.5">
                    {row.stage === "LEAD" ? (
                      <>
                        <Button
                          size="sm"
                          variant="brand"
                          onClick={() => handleApproveFit(row.id, row.candidate_name)}
                        >
                          <Check className="h-3 w-3 mr-1" />
                          Approve Fit
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-rose-600 border-rose-200 hover:bg-rose-50"
                          onClick={() => handleOpenFailModal(row)}
                        >
                          Mark Failed
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          size="sm"
                          variant="success"
                          onClick={() => handleConfirmCompletion(row.id, row.candidate_name)}
                        >
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                          Confirm Completion
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-rose-600 border-rose-200 hover:bg-rose-50"
                          onClick={() => handleOpenFailModal(row)}
                        >
                          Disqualify
                        </Button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Mark Failed Modal */}
      {selectedCandidate && (
        <Modal
          isOpen={failModalOpen}
          onClose={() => setFailModalOpen(false)}
          title={`Mark Referral as Failed: ${selectedCandidate.candidate_name}`}
          description="A mandatory failure reason is required. This will update the referrer's dashboard."
          footer={
            <>
              <Button size="sm" variant="outline" onClick={() => setFailModalOpen(false)}>
                Cancel
              </Button>
              <Button size="sm" variant="destructive" onClick={handleConfirmFail}>
                Confirm Disqualification
              </Button>
            </>
          }
        >
          <div className="space-y-3 text-xs">
            <div>
              <label className="font-semibold text-slate-700 block mb-1">
                Select Disqualification Reason:
              </label>
              <select
                value={failReason}
                onChange={(e) => setFailReason(e.target.value)}
                className="w-full border border-slate-200 rounded-md p-2 text-xs focus:ring-1 focus:ring-brand-500"
              >
                <option value="Outside Target Geography">Outside Target Geography</option>
                <option value="Failed Demographic Fit">Failed Demographic Fit (Age/Income)</option>
                <option value="Unreachable or Invalid Phone">Unreachable or Invalid Phone</option>
                <option value="Duplicate Household / Ring Detection">Duplicate Household / Ring Detection</option>
                <option value="Failed Quality & Attention Checks">Failed Quality & Attention Checks</option>
                <option value="Other">Other Custom Reason</option>
              </select>
            </div>

            {failReason === "Other" && (
              <div>
                <label className="font-semibold text-slate-700 block mb-1">
                  Specify Custom Reason:
                </label>
                <textarea
                  rows={3}
                  value={customReason}
                  onChange={(e) => setCustomReason(e.target.value)}
                  placeholder="Explain why this candidate was disqualified..."
                  className="w-full border border-slate-200 rounded-md p-2 text-xs focus:ring-1 focus:ring-brand-500"
                />
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
