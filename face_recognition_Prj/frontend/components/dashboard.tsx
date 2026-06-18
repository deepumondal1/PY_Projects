"use client"

import { useEffect, useState } from "react"
import { Users, UserCheck, UserX, Building2, Layers } from "lucide-react"

const HOST = "http://127.0.0.1:8080"

interface DashboardData {
  totalEmployees: number
  totalPresent: number
  totalAbsent: number
  totalPlants: number
  totalDepartments: number
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData>({
    totalEmployees: 0,
    totalPresent: 0,
    totalAbsent: 0,
    totalPlants: 0,
    totalDepartments: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${HOST}/api/dashboard`)
      if (!response.ok) {
        throw new Error("Failed to fetch dashboard data")
      }
      const dashboardData = await response.json()
      setData(dashboardData.data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred")
      console.error("[v0] Dashboard fetch error:", err)
    } finally {
      setLoading(false)
    }
  }

  const cards = [
    { label: "Total Employees", value: data.totalEmployees, icon: Users, color: "bg-blue-500" },
    { label: "Present Today", value: data.totalPresent, icon: UserCheck, color: "bg-green-500" },
    { label: "Absent Today", value: data.totalAbsent, icon: UserX, color: "bg-red-500" },
    { label: "Plants", value: data.totalPlants, icon: Building2, color: "bg-purple-500" },
    { label: "Departments", value: data.totalDepartments, icon: Layers, color: "bg-orange-500" },
  ]

  if (loading) {
    return (
      <div className="p-8">
        <h2 className="text-3xl font-bold text-slate-800 mb-8">Dashboard</h2>
        <div className="flex items-center justify-center h-64">
          <p className="text-slate-600">Loading dashboard data...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-slate-800 mb-8">Dashboard</h2>
      {error && <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">{error}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        {cards.map((card, idx) => {
          const Icon = card.icon
          return (
            <div key={idx} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className={`${card.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                <Icon size={24} className="text-white" />
              </div>
              <p className="text-slate-600 text-sm font-medium">{card.label}</p>
              <p className="text-3xl font-bold text-slate-800 mt-2">
                {/* {data[card.label.toLowerCase().replace(/\s/g, "") as keyof DashboardData] || 0} */}
                {card.value}
              </p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
