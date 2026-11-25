import React from "react"
import { BrowserRouter, Routes, Route } from "react-router-dom"
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
import { SurveyApplicationsPage } from "@/pages/operations/SurveyApplicationsPage"

// Admin Pages
import { AdminDashboard } from "@/pages/admin/AdminDashboard"
import { AdminRespondentsGrid } from "@/pages/admin/RespondentsGrid"
import { SourcesPage } from "@/pages/admin/SourcesPage"
import { ImportsPage } from "@/pages/admin/ImportsPage"
import { SurveysAdminPage } from "@/pages/admin/SurveysAdminPage"
import { LoginPage } from "@/pages/LoginPage"
import { OnboardingPage } from "@/pages/OnboardingPage"
import { AuthProvider, useAuth } from "@/contexts/AuthContext"
import { useLocation, Navigate as RouterNavigate } from "react-router-dom"
import { LoadingState } from "@/components/ui/LoadingState"

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
        <AuthProvider><AppRoutes /></AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

function Protected({roles,children}:{roles:string[];children:React.ReactNode}) {
  const {user,loading}=useAuth(); const location=useLocation()
  if(loading)return <LoadingState />
  if(!user)return <RouterNavigate to={`/login?${new URLSearchParams({next:location.pathname+location.search})}`} replace />
  if(!roles.includes(user.role))return <RouterNavigate to={user.role==="ADMIN"?"/admin":user.role==="OPERATIONS"?"/ops":"/portal"} replace />
  if(user.role==="RESPONDENT"&&!user.profile_completed&&location.pathname!=="/onboarding")return <RouterNavigate to="/onboarding" replace />
  return <>{children}</>
}

function AppRoutes(){
 const {user,loading}=useAuth()
 return <Routes>
          <Route path="/login" element={user&&!loading?<RouterNavigate to={user.profile_completed?(user.role==="ADMIN"?"/admin":user.role==="OPERATIONS"?"/ops":"/portal"):"/onboarding"} replace/>:<LoginPage/>} />
          <Route path="/join" element={<RouterNavigate to={`/login${window.location.search}`} replace/>}/>
          <Route path="/onboarding" element={<Protected roles={["RESPONDENT"]}><OnboardingPage/></Protected>} />
          {/* Default redirect to Respondent Portal */}
          <Route path="/" element={<RouterNavigate to={user?(user.role==="ADMIN"?"/admin":user.role==="OPERATIONS"?"/ops":"/portal"):"/login"} replace />} />

          {/* Respondent Portal Routes (Mobile-First) */}
          <Route path="/portal" element={<Protected roles={["RESPONDENT"]}><RespondentLayout /></Protected>}>
            <Route index element={<RespondentSurveysPage />} />
            <Route path="referrals" element={<RespondentReferralsPage />} />
            <Route path="profile" element={<RespondentProfilePage />} />
          </Route>

          {/* Operations Portal Routes (Triage Queues) */}
          <Route path="/ops" element={<Protected roles={["OPERATIONS","ADMIN"]}><OperationsLayout /></Protected>}>
            <Route index element={<OperationsReferralQueue />} />
            <Route path="respondents" element={<AdminRespondentsGrid />} />
            <Route path="payouts" element={<OperationsPayoutQueue />} />
            <Route path="applications" element={<SurveyApplicationsPage />} />
            <Route path="fraud" element={<OperationsReferralQueue />} />
          </Route>

          {/* Admin Portal Routes (Desktop Mission Control) */}
          <Route path="/admin" element={<Protected roles={["ADMIN"]}><AdminLayout /></Protected>}>
            <Route index element={<AdminDashboard />} />
            <Route path="respondents" element={<AdminRespondentsGrid />} />
            <Route path="surveys" element={<SurveysAdminPage />} />
            <Route path="sources" element={<SourcesPage />} />
            <Route path="import" element={<ImportsPage />} />
            <Route path="analytics" element={<AdminDashboard />} />
          </Route>

          {/* Catch-all fallback */}
          <Route path="*" element={<RouterNavigate to="/" replace />} />
        </Routes>
}

export default App
