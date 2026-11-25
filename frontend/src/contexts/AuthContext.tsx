import React, { createContext, useContext, useEffect, useMemo, useState } from "react"
import api from "@/utils/api"
export type AuthUser = { id:string; phone:string; role:"ADMIN"|"OPERATIONS"|"RESPONDENT"; is_active:boolean; profile_completed:boolean }
type AuthValue = { user:AuthUser|null; loading:boolean; refresh:()=>Promise<void>; logout:()=>void }
const AuthContext=createContext<AuthValue|undefined>(undefined)
export const AuthProvider:React.FC<{children:React.ReactNode}> = ({children}) => {
  const [user,setUser]=useState<AuthUser|null>(null); const [loading,setLoading]=useState(true)
  const refresh=async()=>{ if(!localStorage.getItem("access_token")){setUser(null);setLoading(false);return} try{const res=await api.get<AuthUser>("/auth/me");setUser(res.data)}catch{localStorage.removeItem("access_token");localStorage.removeItem("refresh_token");setUser(null)}finally{setLoading(false)} }
  useEffect(()=>{void refresh()},[])
  const logout=()=>{localStorage.removeItem("access_token");localStorage.removeItem("refresh_token");setUser(null)}
  const value=useMemo(()=>({user,loading,refresh,logout}),[user,loading])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
export function useAuth(){const value=useContext(AuthContext);if(!value)throw new Error("useAuth must be inside AuthProvider");return value}
