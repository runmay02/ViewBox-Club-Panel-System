import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/utils/cn"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow",
        outline: "text-foreground",
        // Business Status Variants
        approved:
          "border-emerald-200 bg-emerald-50 text-emerald-700 font-medium",
        waitlisted:
          "border-amber-200 bg-amber-50 text-amber-700 font-medium",
        rejected:
          "border-rose-200 bg-rose-50 text-rose-700 font-medium",
        lead:
          "border-blue-200 bg-blue-50 text-blue-700 font-medium",
        fit:
          "border-purple-200 bg-purple-50 text-purple-700 font-medium",
        completed:
          "border-emerald-200 bg-emerald-50 text-emerald-700 font-medium",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
