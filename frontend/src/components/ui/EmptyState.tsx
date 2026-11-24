import React from "react"
import { LucideIcon, Inbox } from "lucide-react"
import { Button } from "./Button"
import { cn } from "@/utils/cn"

interface EmptyStateProps {
  icon?: LucideIcon
  title?: string
  description?: string
  actionLabel?: string
  onAction?: () => void
  className?: string
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = Inbox,
  title = "No data found",
  description = "There are no records matching your current filter criteria.",
  actionLabel,
  onAction,
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-12 text-center rounded-lg border border-dashed border-slate-200 bg-slate-50/50",
        className
      )}
    >
      <div className="h-12 w-12 rounded-full bg-white shadow-sm border border-slate-200 flex items-center justify-center mb-3 text-slate-400">
        <Icon className="h-6 w-6" />
      </div>
      <h4 className="text-sm font-semibold text-slate-900">{title}</h4>
      <p className="text-xs text-slate-500 mt-1 max-w-sm leading-relaxed">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button size="sm" variant="outline" className="mt-4" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  )
}
