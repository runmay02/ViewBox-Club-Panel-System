import React from "react"
import { AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "./Button"
import { cn } from "@/utils/cn"

interface ErrorStateProps {
  title?: string
  message?: string
  onRetry?: () => void
  className?: string
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title = "Unable to load data",
  message = "An unexpected error occurred while fetching information from the server.",
  onRetry,
  className,
}) => {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center p-8 text-center rounded-lg border border-rose-200 bg-rose-50/50",
        className
      )}
    >
      <div className="h-10 w-10 rounded-full bg-rose-100 flex items-center justify-center mb-3 text-rose-600">
        <AlertCircle className="h-5 w-5" />
      </div>
      <h4 className="text-sm font-semibold text-rose-900">{title}</h4>
      <p className="text-xs text-rose-600 mt-1 max-w-md">{message}</p>
      {onRetry && (
        <Button
          size="sm"
          variant="outline"
          className="mt-4 border-rose-300 text-rose-700 hover:bg-rose-100"
          onClick={onRetry}
        >
          <RefreshCw className="mr-1.5 h-3.5 w-3.5" />
          Retry Request
        </Button>
      )}
    </div>
  )
}
