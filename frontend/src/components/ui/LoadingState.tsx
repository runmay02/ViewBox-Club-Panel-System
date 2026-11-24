import React from "react"
import { Loader2 } from "lucide-react"
import { cn } from "@/utils/cn"

interface LoadingStateProps {
  message?: string
  description?: string
  className?: string
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading data...",
  description = "Please wait while we retrieve the latest information.",
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-12 text-center rounded-lg border border-dashed border-slate-200 bg-white/50",
        className
      )}
    >
      <div className="h-10 w-10 rounded-full bg-brand-50 flex items-center justify-center mb-3">
        <Loader2 className="h-5 w-5 text-brand-600 animate-spin" />
      </div>
      <h4 className="text-sm font-semibold text-slate-800">{message}</h4>
      {description && (
        <p className="text-xs text-slate-500 mt-1 max-w-sm">{description}</p>
      )}
    </div>
  )
}
