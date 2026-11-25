import React, { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Card } from "@/components/ui/Card"
import { LoadingState } from "@/components/ui/LoadingState"
import { ErrorState } from "@/components/ui/ErrorState"
import api from "@/utils/api"

type Survey = { id: string; title: string; status: string; deadline: string; completed_count: number; target_quota: number; incentive_amount: number }
type Rule = { rule_type: string; rule_value: string; strictness: "STRICT" | "FLEXIBLE" }
const blankRule = (): Rule => ({ rule_type: "CITY", rule_value: "", strictness: "STRICT" })

export const SurveysAdminPage: React.FC = () => {
  const qc = useQueryClient()
  const [form, setForm] = useState({ title: "", description: "", survey_url: "", start_date: new Date().toISOString().slice(0, 10), deadline: "", target_quota: 50, max_applications: 60, incentive_amount: 250 })
  const [rules, setRules] = useState<Rule[]>([])
  const q = useQuery({ queryKey: ["surveys"], queryFn: async () => (await api.get<Survey[]>("/surveys")).data })
  const create = useMutation({ mutationFn: async () => (await api.post("/surveys", { ...form, rules: rules.filter(rule => rule.rule_value.trim()) })).data, onSuccess: () => { void qc.invalidateQueries({ queryKey: ["surveys"] }); setForm({ ...form, title: "", description: "", survey_url: "" }); setRules([]) } })
  if (q.isLoading) return <LoadingState />
  if (q.error) return <ErrorState title="Could not load surveys" message={q.error.message} onRetry={() => void q.refetch()} />
  return <div className="space-y-4"><h2 className="text-xl font-bold">Survey Projects</h2><Card className="p-4"><form onSubmit={e => { e.preventDefault(); create.mutate() }} className="grid sm:grid-cols-2 gap-3">
    <input required placeholder="Survey title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} className="border rounded p-2 text-sm" />
    <input type="url" placeholder="External survey URL" value={form.survey_url} onChange={e => setForm({ ...form, survey_url: e.target.value })} className="border rounded p-2 text-sm" />
    <textarea required placeholder="Description" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} className="border rounded p-2 text-sm sm:col-span-2" />
    <label className="text-xs">Start date<input type="date" required value={form.start_date} onChange={e => setForm({ ...form, start_date: e.target.value })} className="block border rounded p-2" /></label>
    <label className="text-xs">Deadline<input type="date" required value={form.deadline} onChange={e => setForm({ ...form, deadline: e.target.value })} className="block border rounded p-2" /></label>
    <input type="number" min="1" aria-label="Target quota" value={form.target_quota} onChange={e => setForm({ ...form, target_quota: +e.target.value })} className="border rounded p-2 text-sm" />
    <input type="number" min="1" aria-label="Application limit" value={form.max_applications} onChange={e => setForm({ ...form, max_applications: +e.target.value })} className="border rounded p-2 text-sm" />
    <input type="number" min="0" aria-label="Incentive amount" value={form.incentive_amount} onChange={e => setForm({ ...form, incentive_amount: +e.target.value })} className="border rounded p-2 text-sm" />
    <section className="sm:col-span-2 space-y-2"><div className="flex justify-between items-center"><h3 className="font-medium text-sm">Eligibility rules</h3><button type="button" className="text-sm text-brand-700" onClick={() => setRules([...rules, blankRule()])}>Add rule</button></div>
      {rules.map((rule, index) => <div className="grid grid-cols-1 sm:grid-cols-3 gap-2" key={index}>
        <select aria-label="Rule type" value={rule.rule_type} onChange={e => setRules(rules.map((r, i) => i === index ? { ...r, rule_type: e.target.value } : r))} className="border rounded p-2 text-sm">{["AGE_MIN", "AGE_MAX", "CITY", "GENDER", "INCOME_RANGE", "INTEREST"].map(type => <option key={type}>{type}</option>)}</select>
        <input aria-label="Rule value" required placeholder="Rule value" value={rule.rule_value} onChange={e => setRules(rules.map((r, i) => i === index ? { ...r, rule_value: e.target.value } : r))} className="border rounded p-2 text-sm" />
        <div className="flex gap-2"><select aria-label="Rule strictness" value={rule.strictness} onChange={e => setRules(rules.map((r, i) => i === index ? { ...r, strictness: e.target.value as Rule["strictness"] } : r))} className="border rounded p-2 text-sm flex-1"><option>STRICT</option><option>FLEXIBLE</option></select><button type="button" aria-label="Remove rule" onClick={() => setRules(rules.filter((_, i) => i !== index))} className="text-rose-700">Remove</button></div>
      </div>)}
    </section>
    <button disabled={create.isPending} className="rounded bg-brand-600 text-white p-2 text-sm">Create active survey</button>
  </form>{create.isError && <p role="alert" className="text-rose-700 mt-2 text-sm">{create.error.message}</p>}</Card>
    <Card className="overflow-x-auto"><table className="w-full text-xs text-left"><thead className="bg-slate-50"><tr>{["Survey", "Status", "Deadline", "Quota", "Reward"].map(x => <th key={x} className="p-3">{x}</th>)}</tr></thead><tbody className="divide-y">{q.data?.map(s => <tr key={s.id}><td className="p-3">{s.title}</td><td className="p-3">{s.status}</td><td className="p-3">{s.deadline}</td><td className="p-3">{s.completed_count}/{s.target_quota}</td><td className="p-3">₹{s.incentive_amount}</td></tr>)}</tbody></table>{q.data?.length === 0 && <p className="p-4 text-sm text-slate-500">No surveys created yet.</p>}</Card>
  </div>
}
