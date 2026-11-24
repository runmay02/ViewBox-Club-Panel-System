// ViewBox Club — Realistic Mock Data Layer for UI Development
// Separated strictly from API client

export interface RespondentDemo {
  id: string
  member_id: string
  name: string
  phone: string
  email: string
  gender: "Male" | "Female" | "Other"
  date_of_birth: string
  city: string
  income_range: string
  interests: string[]
  source: string
  referred_by?: string
  joined_on: string
  status: "ACTIVE" | "IN_REVIEW" | "SUSPENDED"
}

export interface SurveyDemo {
  id: string
  title: string
  description: string
  survey_url: string
  category: string
  start_date: string
  deadline: string
  days_left: number
  status: "ACTIVE" | "QUOTA_REACHED" | "EXPIRED" | "DRAFT"
  target_quota: number
  completed_count: number
  incentive_amount: number
  referral_bonus_amount: number
  rules: {
    age_min?: number
    age_max?: number
    cities?: string[]
    genders?: string[]
    income_ranges?: string[]
    interests?: string[]
    strictness: "STRICT" | "FLEXIBLE"
  }
}

export interface ReferralDemo {
  id: string
  referrer_id: string
  referred_id: string
  referred_name: string
  masked_phone: string
  registered_on: string
  stage: "LEAD" | "FIT" | "COMPLETED" | "FAILED"
  failure_reason?: string
  bonus_status: "EARNED" | "PENDING_FIT" | "PENDING_COMPLETION" | "INELIGIBLE"
  bonus_amount: number
}

export interface PayoutDemo {
  id: string
  member_id: string
  member_name: string
  type: "SURVEY_COMPLETION" | "REFERRAL_BONUS"
  amount: number
  status: "PENDING_APPROVAL" | "APPROVED" | "PROCESSING" | "PAID" | "FAILED"
  survey_title?: string
  referral_name?: string
  created_at: string
}

export const mockAdminKpis = {
  total_respondents: 189,
  new_signups_7d: 24,
  active_surveys: 4,
  completed_surveys: 142,
  total_referrals: 156,
  successful_referrals: 33,
  pending_ops_tasks: 12,
  total_payouts_disbursed: 45750,
  signup_trend: [
    { date: "18 Nov", signups: 12 },
    { date: "19 Nov", signups: 18 },
    { date: "20 Nov", signups: 15 },
    { date: "21 Nov", signups: 28 },
    { date: "22 Nov", signups: 22 },
    { date: "23 Nov", signups: 34 },
    { date: "24 Nov", signups: 24 },
  ],
  source_distribution: [
    { name: "WhatsApp Pune", count: 32, color: "#4f46e5" },
    { name: "Staff DMs", count: 47, color: "#8b5cf6" },
    { name: "Referrals", count: 33, color: "#10b981" },
    { name: "WhatsApp Mumbai", count: 17, color: "#3b82f6" },
    { name: "Instagram", count: 22, color: "#ec4899" },
    { name: "Facebook", count: 19, color: "#0ea5e9" },
    { name: "Website", count: 19, color: "#f59e0b" },
  ],
  referral_funnel: [
    { stage: "Leads (Signups)", count: 156, fill: "#3b82f6" },
    { stage: "Fit Verified", count: 84, fill: "#8b5cf6" },
    { stage: "Completed & Quality Passed", count: 33, fill: "#10b981" },
  ],
}

export const mockRespondents: RespondentDemo[] = [
  {
    id: "r1",
    member_id: "VB10073",
    name: "Ishaan Singh",
    phone: "9876543210",
    email: "ishaan.41@example.in",
    gender: "Male",
    date_of_birth: "1998-10-22",
    city: "Ahmedabad",
    income_range: "10L-20L",
    interests: ["Auto", "Kids", "Tech"],
    source: "Referral",
    referred_by: "VB10002",
    joined_on: "2025-11-02",
    status: "ACTIVE",
  },
  {
    id: "r2",
    member_id: "VB10166",
    name: "Riya Patil",
    phone: "9021331114",
    email: "riya.8@example.in",
    gender: "Female",
    date_of_birth: "1989-02-25",
    city: "Pune",
    income_range: "6L-10L",
    interests: ["Home", "Travel", "Health"],
    source: "Referral",
    referred_by: "VB10083",
    joined_on: "2026-08-14",
    status: "ACTIVE",
  },
  {
    id: "r3",
    member_id: "VB10169",
    name: "Priya Rao",
    phone: "8728547667",
    email: "priya.63@example.in",
    gender: "Female",
    date_of_birth: "1984-03-01",
    city: "Bengaluru",
    income_range: "10L-20L",
    interests: ["Tech", "Travel", "Kids", "Auto"],
    source: "Referral",
    referred_by: "VB10113",
    joined_on: "2026-08-15",
    status: "ACTIVE",
  },
  {
    id: "r4",
    member_id: "VB10041",
    name: "Neha Chavan",
    phone: "9958519043",
    email: "neha.chavan@example.in",
    gender: "Female",
    date_of_birth: "2000-02-05",
    city: "Navi Mumbai",
    income_range: "Below 3L",
    interests: ["Tech", "Travel", "Fashion", "Auto"],
    source: "WhatsApp Group - Mumbai",
    joined_on: "2026-01-24",
    status: "ACTIVE",
  },
  {
    id: "r5",
    member_id: "VB10085",
    name: "Meera Singh",
    phone: "9921415340",
    email: "meera.singh@example.in",
    gender: "Female",
    date_of_birth: "1989-05-07",
    city: "Thane",
    income_range: "10L-20L",
    interests: ["Auto", "Fashion", "Health", "Beauty"],
    source: "Staff DM - Agent 01",
    joined_on: "2025-08-01",
    status: "ACTIVE",
  },
  {
    id: "r6",
    member_id: "VB10137",
    name: "Tanvi Pawar",
    phone: "8679951794",
    email: "tanvi999@example.com",
    gender: "Female",
    date_of_birth: "1978-03-27",
    city: "Pune",
    income_range: "10L-20L",
    interests: ["Tech", "Fashion", "Food"],
    source: "Instagram",
    joined_on: "2026-09-10",
    status: "ACTIVE",
  },
  {
    id: "r7",
    member_id: "VB10065",
    name: "Meera Reddy",
    phone: "6824460261",
    email: "meera531@example.com",
    gender: "Female",
    date_of_birth: "1983-03-19",
    city: "Mumbai",
    income_range: "Above 20L",
    interests: ["Beauty", "Kids", "Finance"],
    source: "Instagram",
    joined_on: "2026-05-08",
    status: "ACTIVE",
  },
  {
    id: "r8",
    member_id: "VB10050",
    name: "Neha Jadhav",
    phone: "6351619945",
    email: "neha879@example.com",
    gender: "Female",
    date_of_birth: "1974-10-20",
    city: "Mumbai",
    income_range: "10L-20L",
    interests: ["Tech", "Kids", "Fashion"],
    source: "Instagram",
    joined_on: "2025-09-22",
    status: "ACTIVE",
  },
]

export const mockSurveys: SurveyDemo[] = [
  {
    id: "s1",
    title: "Electric Two-Wheeler Consumer Adoption Study",
    description:
      "A comprehensive national consumer study analyzing commuter sentiments, battery charging convenience, and EV scooter adoption drivers across tier-1 Indian metros.",
    survey_url: "https://survey.concaveinsights.com/ev-two-wheeler-2026",
    category: "Automotive & Mobility",
    start_date: "2026-11-20",
    deadline: "2026-12-05",
    days_left: 11,
    status: "ACTIVE",
    target_quota: 50,
    completed_count: 38,
    incentive_amount: 250,
    referral_bonus_amount: 100,
    rules: {
      age_min: 18,
      age_max: 45,
      cities: ["Mumbai", "Pune", "Bengaluru", "Ahmedabad"],
      genders: ["Male", "Female"],
      income_ranges: ["6L-10L", "10L-20L", "Above 20L"],
      interests: ["Auto", "Tech"],
      strictness: "STRICT",
    },
  },
  {
    id: "s2",
    title: "Gen-Z & Millennial Sustainable Fashion Survey",
    description:
      "Understanding retail purchasing choices, thrift shopping attitudes, and eco-friendly apparel preferences among young urban professionals.",
    survey_url: "https://survey.concaveinsights.com/sustainable-fashion-2026",
    category: "Fashion & Lifestyle",
    start_date: "2026-11-18",
    deadline: "2026-12-03",
    days_left: 9,
    status: "ACTIVE",
    target_quota: 75,
    completed_count: 51,
    incentive_amount: 200,
    referral_bonus_amount: 100,
    rules: {
      age_min: 18,
      age_max: 30,
      cities: ["Mumbai", "Pune", "Delhi", "Bengaluru"],
      income_ranges: ["Below 3L", "3L-6L", "6L-10L"],
      interests: ["Fashion", "Beauty"],
      strictness: "FLEXIBLE",
    },
  },
  {
    id: "s3",
    title: "10-Minute Grocery Delivery Habit Tracker",
    description:
      "Evaluating instant grocery quick commerce apps: cart frequency, late-night snacking orders, and delivery fee sensitivity in Western India.",
    survey_url: "https://survey.concaveinsights.com/quick-commerce-2026",
    category: "Consumer Goods & Retail",
    start_date: "2026-11-22",
    deadline: "2026-12-07",
    days_left: 13,
    status: "ACTIVE",
    target_quota: 100,
    completed_count: 88,
    incentive_amount: 150,
    referral_bonus_amount: 100,
    rules: {
      age_min: 20,
      age_max: 55,
      cities: ["Mumbai", "Pune", "Thane", "Navi Mumbai"],
      interests: ["Food", "Home"],
      strictness: "STRICT",
    },
  },
  {
    id: "s4",
    title: "UPI & Digital Credit Lines User Study",
    description:
      "Insights into modern digital banking, RuPay on UPI, Buy-Now-Pay-Later adoption, and micro-loan behaviors.",
    survey_url: "https://survey.concaveinsights.com/fintech-upi-2026",
    category: "Fintech & Banking",
    start_date: "2026-11-10",
    deadline: "2026-11-25",
    days_left: 1,
    status: "ACTIVE",
    target_quota: 40,
    completed_count: 40,
    incentive_amount: 300,
    referral_bonus_amount: 100,
    rules: {
      age_min: 22,
      age_max: 60,
      income_ranges: ["6L-10L", "10L-20L", "Above 20L"],
      interests: ["Finance", "Tech"],
      strictness: "STRICT",
    },
  },
]

export const mockCurrentUser = {
  member_id: "VB10073",
  name: "Ishaan Singh",
  phone: "9876543210",
  email: "ishaan.41@example.in",
  city: "Ahmedabad",
  gender: "Male",
  age: 26,
  date_of_birth: "1998-10-22",
  income_range: "10L-20L",
  interests: ["Auto", "Kids", "Tech"],
  referral_token: "ref_ishaan_vb10073",
  referral_link: "https://viewbox.club/join?ref=VB10073",
  total_earned: 650,
  cool_off_until: null as string | null,
}

export const mockUserReferrals: ReferralDemo[] = [
  {
    id: "ref_1",
    referrer_id: "VB10073",
    referred_id: "VB10166",
    referred_name: "Riya P.",
    masked_phone: "90XXXXXX14",
    registered_on: "2026-08-14",
    stage: "COMPLETED",
    bonus_status: "EARNED",
    bonus_amount: 100,
  },
  {
    id: "ref_2",
    referrer_id: "VB10073",
    referred_id: "VB10117",
    referred_name: "Kabir P.",
    masked_phone: "99XXXXXX16",
    registered_on: "2026-09-02",
    stage: "FIT",
    bonus_status: "PENDING_COMPLETION",
    bonus_amount: 100,
  },
  {
    id: "ref_3",
    referrer_id: "VB10073",
    referred_id: "VB10005",
    referred_name: "Sunita V.",
    masked_phone: "98XXXXXX84",
    registered_on: "2026-11-18",
    stage: "LEAD",
    bonus_status: "PENDING_FIT",
    bonus_amount: 100,
  },
  {
    id: "ref_4",
    referrer_id: "VB10073",
    referred_id: "VB10134",
    referred_name: "Diya S.",
    masked_phone: "06XXXXXX00",
    registered_on: "2026-10-05",
    stage: "FAILED",
    failure_reason: "Did not meet study demographic criteria (Outside target cities)",
    bonus_status: "INELIGIBLE",
    bonus_amount: 0,
  },
]

export const mockOpsQueues = {
  referral_reviews: [
    {
      id: "op_ref_1",
      candidate_id: "VB10142",
      candidate_name: "Arjun Verma",
      phone: "8560349602",
      city: "Navi Mumbai",
      referrer_id: "VB10025",
      referrer_name: "Sunita Bhosale",
      registered_at: "2026-11-22",
      stage: "LEAD",
    },
    {
      id: "op_ref_2",
      candidate_id: "VB10105",
      candidate_name: "Ayesha Nair",
      phone: "6007146555",
      city: "Hyderabad",
      referrer_id: "VB10041",
      referrer_name: "Neha Chavan",
      registered_at: "2026-11-23",
      stage: "LEAD",
    },
    {
      id: "op_ref_3",
      candidate_id: "VB10154",
      candidate_name: "Kabir Sharma",
      phone: "8014861241",
      city: "Hyderabad",
      referrer_id: "VB10104",
      referrer_name: "Pooja Iyer",
      registered_at: "2026-11-20",
      stage: "FIT",
      survey_completed: true,
    },
  ],
  payout_approvals: [
    {
      id: "p1",
      member_id: "VB10073",
      member_name: "Ishaan Singh",
      type: "SURVEY_COMPLETION",
      amount: 250,
      survey_title: "Electric Two-Wheeler Consumer Adoption Study",
      created_at: "2026-11-23",
      status: "PENDING_APPROVAL",
    },
    {
      id: "p2",
      member_id: "VB10073",
      member_name: "Ishaan Singh",
      type: "REFERRAL_BONUS",
      amount: 100,
      referral_name: "Riya Patil (VB10166)",
      created_at: "2026-11-22",
      status: "PENDING_APPROVAL",
    },
    {
      id: "p3",
      member_id: "VB10041",
      member_name: "Neha Chavan",
      type: "SURVEY_COMPLETION",
      amount: 150,
      survey_title: "10-Minute Grocery Delivery Habit Tracker",
      created_at: "2026-11-24",
      status: "PENDING_APPROVAL",
    },
  ] as PayoutDemo[],
}
