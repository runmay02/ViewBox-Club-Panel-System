import React, { useState } from "react"
import {
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  ExternalLink,
  ChevronRight,
  Sparkles,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Modal } from "@/components/ui/Modal"
import { mockSurveys, mockCurrentUser, SurveyDemo } from "@/mock/demoData"

export const RespondentSurveysPage: React.FC = () => {
  const [selectedSurvey, setSelectedSurvey] = useState<SurveyDemo | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [applicationSuccess, setApplicationSuccess] = useState(false)

  // Eligibility evaluation logic (reusable client view for mock)
  const getEligibility = (survey: SurveyDemo) => {
    // Check 3-month cool-off
    if (mockCurrentUser.cool_off_until) {
      return {
        status: "REJECTED" as const,
        badgeVariant: "rejected" as const,
        label: "Cool-off Active",
        reason: `In cool-off until ${mockCurrentUser.cool_off_until}. You cannot join a survey for 3 months following prior completion.`,
      }
    }

    // Check strict rules
    const userCityMatch = !survey.rules.cities || survey.rules.cities.includes(mockCurrentUser.city)
    const userAgeMatch =
      (!survey.rules.age_min || mockCurrentUser.age >= survey.rules.age_min) &&
      (!survey.rules.age_max || mockCurrentUser.age <= survey.rules.age_max)
    const userIncomeMatch =
      !survey.rules.income_ranges || survey.rules.income_ranges.includes(mockCurrentUser.income_range)

    if (survey.rules.strictness === "STRICT") {
      if (!userCityMatch) {
        return {
          status: "REJECTED" as const,
          badgeVariant: "rejected" as const,
          label: "Not Eligible",
          reason: `Target geography restricted to ${survey.rules.cities?.join(", ")}. Your registered city is ${mockCurrentUser.city}.`,
        }
      }
      if (!userAgeMatch) {
        return {
          status: "REJECTED" as const,
          badgeVariant: "rejected" as const,
          label: "Not Eligible",
          reason: `Requires age ${survey.rules.age_min} to ${survey.rules.age_max}. Your age is ${mockCurrentUser.age}.`,
        }
      }
      if (!userIncomeMatch) {
        return {
          status: "REJECTED" as const,
          badgeVariant: "rejected" as const,
          label: "Not Eligible",
          reason: `Target income bracket is ${survey.rules.income_ranges?.join(", ")}.`,
        }
      }
    } else {
      // Flexible rule mismatch produces waitlist
      if (!userIncomeMatch || !userCityMatch) {
        return {
          status: "WAITLISTED" as const,
          badgeVariant: "waitlisted" as const,
          label: "Waitlisted",
          reason: "You meet primary criteria but belong to a secondary demographic bracket. You are waitlisted for quota expansion.",
        }
      }
    }

    return {
      status: "APPROVED" as const,
      badgeVariant: "approved" as const,
      label: "You Qualify",
      reason: "You meet all research demographics and quota criteria for this study.",
    }
  }

  const handleOpenModal = (survey: SurveyDemo) => {
    setSelectedSurvey(survey)
    setApplicationSuccess(false)
    setIsModalOpen(true)
  }

  const handleApply = () => {
    setApplicationSuccess(true)
  }

  return (
    <div className="space-y-4">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-brand-600 to-indigo-700 rounded-2xl p-4 text-white shadow-sm">
        <div className="flex items-center gap-1.5 text-xs text-brand-200 font-medium mb-1">
          <Sparkles className="h-3.5 w-3.5" />
          <span>Available Research Opportunities</span>
        </div>
        <h2 className="text-base font-bold">Earn Cash for Market Insights</h2>
        <p className="text-[11px] text-brand-100 mt-1 leading-relaxed">
          Surveys strictly enforce a 15-day lifecycle. Payments are credited upon complete participation.
        </p>
      </div>

      {/* Cool-off Alert banner (if active) */}
      {mockCurrentUser.cool_off_until && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-3 text-amber-900 text-xs flex items-start gap-2.5">
          <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold">3-Month Cool-off Active:</strong> You completed a study recently. To ensure unbiased data, you can take another survey starting {mockCurrentUser.cool_off_until}. You can still refer friends!
          </div>
        </div>
      )}

      {/* Survey Feed Header */}
      <div className="flex items-center justify-between pt-1">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
          Live Survey Projects ({mockSurveys.length})
        </h3>
        <span className="text-[10px] text-slate-400 font-medium">Updated just now</span>
      </div>

      {/* Survey Cards */}
      <div className="space-y-3">
        {mockSurveys.map((survey) => {
          const eligibility = getEligibility(survey)
          const matchesInterest = survey.rules.interests?.some((i) =>
            mockCurrentUser.interests.includes(i)
          )

          return (
            <Card
              key={survey.id}
              onClick={() => handleOpenModal(survey)}
              className="hover:border-brand-300 hover:shadow-md cursor-pointer transition-all border-slate-200"
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <Badge variant={eligibility.badgeVariant}>
                    {eligibility.label}
                  </Badge>

                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                    ₹{survey.incentive_amount}
                  </span>
                </div>

                <h4 className="text-sm font-bold text-slate-900 line-clamp-2 leading-snug">
                  {survey.title}
                </h4>

                <p className="text-[11px] text-slate-500 line-clamp-2 mt-1 leading-relaxed">
                  {survey.description}
                </p>

                {/* Tags & Deadline Footer */}
                <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-3 w-3 text-slate-400" />
                    <span>Ends in {survey.days_left}d</span>
                    {matchesInterest && (
                      <span className="bg-brand-50 text-brand-700 font-semibold px-1.5 py-0.2 rounded">
                        Matches Profile
                      </span>
                    )}
                  </div>

                  <span className="text-brand-600 font-semibold flex items-center gap-0.5">
                    Details <ChevronRight className="h-3 w-3" />
                  </span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Eligibility & Application Modal */}
      {selectedSurvey && (
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title={selectedSurvey.title}
          description={selectedSurvey.category}
          footer={
            getEligibility(selectedSurvey).status === "APPROVED" ? (
              <div className="w-full flex items-center justify-between">
                <div className="text-left">
                  <p className="text-[10px] text-slate-400">Verified Payout</p>
                  <p className="text-sm font-bold text-emerald-600">
                    ₹{selectedSurvey.incentive_amount}
                  </p>
                </div>
                {!applicationSuccess ? (
                  <Button size="sm" variant="brand" onClick={handleApply}>
                    <ExternalLink className="mr-1.5 h-3.5 w-3.5" />
                    Take Survey Now
                  </Button>
                ) : (
                  <a
                    href={selectedSurvey.survey_url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center justify-center rounded-md text-xs font-semibold h-8 px-4 bg-emerald-600 text-white hover:bg-emerald-700 shadow-sm"
                  >
                    Open Survey Link <ExternalLink className="ml-1.5 h-3.5 w-3.5" />
                  </a>
                )}
              </div>
            ) : (
              <Button size="sm" variant="outline" onClick={() => setIsModalOpen(false)}>
                Close
              </Button>
            )
          }
        >
          <div className="space-y-4 text-xs">
            {/* Reward & Quota pill */}
            <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
              <div>
                <p className="text-[10px] text-slate-500">Survey Reward</p>
                <p className="text-base font-bold text-slate-900">
                  ₹{selectedSurvey.incentive_amount}
                </p>
              </div>
              <div className="text-right">
                <p className="text-[10px] text-slate-500">Remaining Quota</p>
                <p className="text-sm font-semibold text-slate-800">
                  {selectedSurvey.target_quota - selectedSurvey.completed_count} / {selectedSurvey.target_quota}
                </p>
              </div>
            </div>

            {/* Eligibility Evaluation Banner */}
            {(() => {
              const el = getEligibility(selectedSurvey)
              return (
                <div
                  className={`p-3 rounded-lg border text-xs leading-relaxed flex items-start gap-2.5 ${
                    el.status === "APPROVED"
                      ? "bg-emerald-50 border-emerald-200 text-emerald-900"
                      : el.status === "WAITLISTED"
                      ? "bg-amber-50 border-amber-200 text-amber-900"
                      : "bg-rose-50 border-rose-200 text-rose-900"
                  }`}
                >
                  {el.status === "APPROVED" ? (
                    <CheckCircle2 className="h-4 w-4 text-emerald-600 shrink-0 mt-0.5" />
                  ) : el.status === "WAITLISTED" ? (
                    <AlertCircle className="h-4 w-4 text-amber-600 shrink-0 mt-0.5" />
                  ) : (
                    <XCircle className="h-4 w-4 text-rose-600 shrink-0 mt-0.5" />
                  )}
                  <div>
                    <p className="font-bold">{el.label}</p>
                    <p className="mt-0.5 text-[11px] opacity-90">{el.reason}</p>
                  </div>
                </div>
              )
            })()}

            {/* Full Demographic Rule Checklist */}
            <div className="space-y-2 pt-1">
              <h5 className="font-bold text-[11px] uppercase tracking-wider text-slate-500">
                Rule Evaluation Breakdown
              </h5>

              <div className="space-y-1.5 text-[11px]">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Age Range:</span>
                  <span className="font-medium text-slate-800">
                    {selectedSurvey.rules.age_min || 18} - {selectedSurvey.rules.age_max || 60} yrs (Your age: {mockCurrentUser.age})
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Target Cities:</span>
                  <span className="font-medium text-slate-800 text-right">
                    {selectedSurvey.rules.cities?.join(", ") || "All Cities"}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-500">Income Brackets:</span>
                  <span className="font-medium text-slate-800 text-right">
                    {selectedSurvey.rules.income_ranges?.join(", ") || "All Brackets"}
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-500">Survey Lifecycle:</span>
                  <span className="font-medium text-slate-800">
                    Max 15-day strict window (Ends {selectedSurvey.deadline})
                  </span>
                </div>
              </div>
            </div>

            {applicationSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-lg text-center animate-in fade-in">
                <CheckCircle2 className="h-5 w-5 text-emerald-600 mx-auto mb-1" />
                <p className="font-bold text-xs">Application Confirmed!</p>
                <p className="text-[11px] text-emerald-700 mt-0.5">
                  Your spot has been reserved. Please complete the survey using the link below to qualify for ₹{selectedSurvey.incentive_amount}.
                </p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  )
}
