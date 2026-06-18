"use client"

import { BarChart3, Settings, Users, Clock, Camera } from "lucide-react"

interface NavigationProps {
  activeMenu: string
  setActiveMenu: (menu: string) => void
}

export default function Navigation({ activeMenu, setActiveMenu }: NavigationProps) {
  const menuItems = [
    { label: "Dashboard", icon: BarChart3 },
    { label: "Master", icon: Settings },
    { label: "Employee Enrollment", icon: Users },
    { label: "Attendance", icon: Clock },
    { label: "Capture", icon: Camera },
  ]

  return (
    <nav className="w-64 bg-gradient-to-b from-slate-800 to-slate-900 text-white shadow-lg">
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-2xl font-bold text-blue-400">Attendance</h1>
        <p className="text-sm text-slate-400 mt-1">System</p>
      </div>
      <div className="p-4 space-y-2">
        {menuItems.map((item) => {
          const Icon = item.icon
          return (
            <button
              key={item.label}
              onClick={() => setActiveMenu(item.label)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeMenu === item.label
                  ? "bg-blue-600 text-white shadow-lg"
                  : "text-slate-300 hover:bg-slate-700 hover:text-white"
              }`}
            >
              <Icon size={20} />
              <span className="font-medium">{item.label}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
