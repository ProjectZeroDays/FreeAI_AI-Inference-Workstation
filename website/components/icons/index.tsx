'use client'

// FreeAI Custom Icon Set — SVG, Tailwind-ready, dark-mode native
// 24x24 viewBox, 1.8px stroke, #22c55e accent by default

interface IconProps {
  className?: string
  stroke?: string
}

const defaultStroke = '#22c55e'

export const IconFreeAI = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="9" />
    <path d="M12 7v10M7 12h10" />
  </svg>
)

export const IconGPU = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="6" width="16" height="12" rx="2" />
    <path d="M8 10h8M8 14h5" />
  </svg>
)

export const IconAgent = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="7" />
    <path d="M9 9h6M9 15h6M12 9v6" />
  </svg>
)

export const IconWorkflow = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="6" height="6" rx="1" />
    <rect x="15" y="4" width="6" height="6" rx="1" />
    <rect x="9" y="14" width="6" height="6" rx="1" />
    <path d="M9 7h6M12 10v4" />
  </svg>
)

export const IconModel = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="5" width="16" height="14" rx="2" />
    <path d="M8 9h8M8 13h5" />
  </svg>
)

export const IconLogs = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M6 4h12v16H6z" />
    <path d="M9 8h6M9 12h6M9 16h4" />
  </svg>
)

export const IconShield = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 3l8 4v5c0 5-4 9-8 9s-8-4-8-9V7z" />
    <path d="M12 11v4" />
  </svg>
)

export const IconCloud = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M7 17h10a4 4 0 0 0 0-8 6 6 0 0 0-11-2 4 4 0 0 0 1 10z" />
  </svg>
)

export const IconDevice = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="4" y="5" width="16" height="12" rx="2" />
    <path d="M8 17h8" />
  </svg>
)

export const IconTerminal = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 5h16v14H4z" />
    <path d="M8 9l3 3-3 3M12 15h4" />
  </svg>
)

export const IconRouting = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 4v16" />
    <path d="M6 8l6 4 6-4" />
    <path d="M6 16l6-4 6 4" />
  </svg>
)

export const IconHealth = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="9" />
    <path d="M8 12h2l2 4 2-8h2" />
  </svg>
)

export const IconPatch = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 12h16" />
    <path d="M12 4v16" />
    <circle cx="12" cy="12" r="3" />
  </svg>
)

export const IconApproval = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14" />
    <path d="M12 5v14" />
    <circle cx="12" cy="12" r="5" />
  </svg>
)

export const IconChat = ({ className, stroke = defaultStroke }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke={stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 5h16v10H7l-3 3z" />
    <path d="M8 9h8M8 12h5" />
  </svg>
)

// Barrel export
export const IconSet = {
  FreeAI: IconFreeAI,
  GPU: IconGPU,
  Agent: IconAgent,
  Workflow: IconWorkflow,
  Model: IconModel,
  Logs: IconLogs,
  Shield: IconShield,
  Cloud: IconCloud,
  Device: IconDevice,
  Terminal: IconTerminal,
  Routing: IconRouting,
  Health: IconHealth,
  Patch: IconPatch,
  Approval: IconApproval,
  Chat: IconChat,
}
