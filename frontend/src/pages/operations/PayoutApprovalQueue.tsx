import React from "react"
import {useMutation,useQuery,useQueryClient} from "@tanstack/react-query"
import {DollarSign,ShieldCheck,Check} from "lucide-react"
import {Card} from "@/components/ui/Card"
import {Badge} from "@/components/ui/Badge"
import {Button} from "@/components/ui/Button"
import {LoadingState} from "@/components/ui/LoadingState"
import {ErrorState} from "@/components/ui/ErrorState"
import api from "@/utils/api"
type Payout={id:string;member_id:string;member_name:string;type:string;amount:number;status:string;survey_title?:string|null;referral_name?:string|null;created_at:string}
export const OperationsPayoutQueue:React.FC=()=>{
 const qc=useQueryClient();const q=useQuery({queryKey:["payouts"],queryFn:async()=> (await api.get<Payout[]>("/operations/payouts")).data});const approve=useMutation({mutationFn:async(id:string)=>(await api.post(`/operations/payouts/${id}/approve`)).data,onSuccess:()=>void qc.invalidateQueries({queryKey:["payouts"]})})
 if(q.isLoading)return <LoadingState/>;if(q.error)return <ErrorState title="Could not load payouts" message={q.error.message} onRetry={()=>void q.refetch()}/>;const payouts=q.data||[];const pending=payouts.filter(p=>p.status==="PENDING_APPROVAL").reduce((n,p)=>n+p.amount,0)
 return <div className="space-y-5"><div><h2 className="text-lg font-bold flex gap-2"><DollarSign className="h-5 w-5 text-emerald-600"/>Payout Authorization Ledger</h2><p className="text-xs text-slate-500">Authorize verified survey completions and referral bonuses.</p><b className="text-xs text-emerald-700">₹{pending.toLocaleString()} pending sign-off</b></div>{approve.isError&&<p role="alert" className="text-sm text-rose-700">{approve.error.message}</p>}<Card className="overflow-x-auto"><table className="w-full text-xs text-left"><thead className="bg-slate-50 uppercase text-[10px]"><tr>{["Payee","Type","Context","Amount","Status","Queued","Action"].map(x=><th key={x} className="p-3">{x}</th>)}</tr></thead><tbody className="divide-y">{payouts.map(p=><tr key={p.id}><td className="p-3"><b>{p.member_name}</b><div className="text-slate-400">{p.member_id}</div></td><td className="p-3"><Badge variant={p.type==="SURVEY_COMPLETION"?"default":"secondary"}>{p.type.replace("_"," ")}</Badge></td><td className="p-3">{p.survey_title||p.referral_name||"—"}</td><td className="p-3 font-bold text-emerald-700">₹{p.amount}</td><td className="p-3">{p.status}</td><td className="p-3">{new Date(p.created_at).toLocaleDateString()}</td><td className="p-3">{p.status==="PENDING_APPROVAL"?<Button size="sm" variant="brand" disabled={approve.isPending} onClick={()=>approve.mutate(p.id)}><Check className="h-3 w-3 mr-1"/>Authorize</Button>:<span className="text-emerald-700"><ShieldCheck className="inline h-4 w-4"/> Ready</span>}</td></tr>)}</tbody></table>{payouts.length===0&&<p className="p-5 text-sm text-slate-500">No payouts are in the ledger.</p>}</Card></div>
}
