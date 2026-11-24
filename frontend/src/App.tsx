import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

// Layouts
import { RespondentLayout } from "@/layouts/RespondentLayout"
import { OperationsLayout } from "@/layouts/OperationsLayout"
import { AdminLayout } from "@/layouts/AdminLayout"

// Respondent Pages
import { RespondentSurveysPage } from "@/pages/respondent/SurveysPage"
import { RespondentReferralsPage } from "@/pages/respondent/ReferralsPage"
import { RespondentProfilePage } from "@/pages/respondent/ProfilePage"

// Operations Pages
import { OperationsReferralQueue } from "@/pages/operations/ReferralVerificationQueue"
import { OperationsPayoutQueue } from "@/pages/operations/PayoutApprovalQueue"

// Admin Pages
import { AdminDashboard } from "@/pages/admin/AdminDashboard"
import { AdminRespondentsGrid } from "@/pages/admin/RespondentsGrid"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {/* Default redirect to Respondent Portal */}
          <Route path="/" element={<Navigate to="/portal" replace />} />

          {/* Respondent Portal Routes (Mobile-First) */}
          <Route path="/portal" element={<RespondentLayout />}>
            <Route index element={<RespondentSurveysPage />} />
            <Route path="referrals" element={<RespondentReferralsPage />} />
            <Route path="profile" element={<RespondentProfilePage />} />
          </Route>

          {/* Operations Portal Routes (Triage Queues) */}
          <Route path="/ops" element={<OperationsLayout />}>
            <Route index element={<OperationsReferralQueue />} />
            <Route path="payouts" element={<OperationsPayoutQueue />} />
            <Route path="applications" element={<OperationsReferralQueue />} />
            <Route path="fraud" element={<OperationsReferralQueue />} />
          </Route>

          {/* Admin Portal Routes (Desktop Mission Control) */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="respondents" element={<AdminRespondentsGrid />} />
            <Route path="surveys" element={<AdminDashboard />} />
            <Route path="sources" element={<AdminDashboard />} />
            <Route path="import" element={<AdminRespondentsGrid />} />
            <Route path="analytics" element={<AdminDashboard />} />
          </Route>

          {/* Catch-all fallback */}
          <Route path="*" element={<Navigate to="/portal" replace />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App
