"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Navigation from "@/components/navigation"
import Dashboard from "@/components/dashboard"
import Master from "@/components/master"
import EmployeeEnrollment from "@/components/employee-enrollment"
import Attendance from "@/components/attendance"
import Capture from "@/components/capture"

export default function Home() {
  const router = useRouter()
  const [activeMenu, setActiveMenu] = useState("Dashboard")
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) return null

  const renderComponent = () => {
    switch (activeMenu) {
      case "Dashboard":
        return <Dashboard />
      case "Master":
        return <Master />
      case "Employee Enrollment":
        return <EmployeeEnrollment />
      case "Attendance":
        return <Attendance />
      case "Capture":
        return <Capture />
      default:
        return <Dashboard />
    }
  }

  return (
    <div className="flex h-screen bg-slate-50">
      <Navigation activeMenu={activeMenu} setActiveMenu={setActiveMenu} />
      <main className="flex-1 overflow-auto">{renderComponent()}</main>
    </div>
  )
}
