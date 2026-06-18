"use client"

import { useState, useEffect } from "react"
import { Plus, Trash2 } from "lucide-react"

const HOST = "http://127.0.0.1:8080"

interface AttendanceRecord {
  id: string
  employeeId: string
  employeeName: string
  date: string
  status: "present" | "absent"
}

interface Employee {
  id: string
  name: string
  employeeId: string
  plant: string
  department: string
  shift: string
  photo: string
  photo1: string
  photo2: string
}

export default function Attendance() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [attendance, setAttendance] = useState<AttendanceRecord[]>([])
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0])
  const [showForm, setShowForm] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState("")
  const [selectedStatus, setSelectedStatus] = useState<"present" | "absent">("present")
  const [loading, setLoading] = useState(true)

  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [empRes, attRes] = await Promise.all([
          fetch(`${HOST}/api/enrollments`),
          fetch(`${HOST}/api/attendance-records?date=${selectedDate}`),
        ])

        if (empRes.ok) setEmployees((await empRes.json()).data.employees)
        if (attRes.ok) setAttendance((await attRes.json()).data)
      } catch (error) {
        console.error("Failed to fetch data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [selectedDate])

  const todayRecords = attendance

  const markAttendance = async () => {
    if (!selectedEmployee || !selectedStatus) {
      alert("Please select an employee and status")
      return
    }

    setSubmitting(true)
    try {
      const employee = employees.find((e: any) => e.employeeId === selectedEmployee)
      if (!employee) return

      const response = await fetch(`${HOST}/api/attendance-records`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          employeeId: selectedEmployee,
          employeeName: employee.name,
          date: selectedDate,
          status: selectedStatus,
        }),
      })

      if (response.ok) {
        // const newRecord = await response.json()
        // const existingIndex = attendance.findIndex((a) => a.employeeId === selectedEmployee && a.date === selectedDate)
        // if (existingIndex >= 0) {
        //   const updated = [...attendance]
        //   updated[existingIndex] = newRecord
        //   setAttendance(updated)
        // } else {
        //   setAttendance([...attendance, newRecord])
        // }
        const attRes = await response.json()
        setAttendance(attRes.data)
        setSelectedEmployee("")
        setSelectedStatus("present")
        setShowForm(false)
      }
    } catch (error) {
      console.error("Failed to mark attendance:", error)
      alert("Failed to mark attendance")
    } finally {
      setSubmitting(false)
    }
  }

  const deleteRecord = async (id: string) => {
    try {
      const response = await fetch(`/api/attendance-records?id=${id}`, { method: "DELETE" })
      if (response.ok) {
        setAttendance(attendance.filter((a) => a.id !== id))
      }
    } catch (error) {
      console.error("Failed to delete record:", error)
    }
  }

  const presentCount = todayRecords.filter((a) => a.status === "present").length
  const absentCount = todayRecords.filter((a) => a.status === "absent").length

  if (loading) {
    return <div className="p-8 text-center text-slate-600">Loading...</div>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-slate-800">Attendance Management</h2>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 flex items-center gap-2"
          >
            <Plus size={20} /> Mark Attendance
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <p className="text-slate-600 text-sm font-medium">Total Employees</p>
          <p className="text-3xl font-bold text-slate-800 mt-2">{employees.length}</p>
        </div>
        <div className="bg-green-50 rounded-lg shadow-md p-6 border-l-4 border-green-500">
          <p className="text-slate-600 text-sm font-medium">Present Today</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{presentCount}</p>
        </div>
        <div className="bg-red-50 rounded-lg shadow-md p-6 border-l-4 border-red-500">
          <p className="text-slate-600 text-sm font-medium">Absent Today</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{absentCount}</p>
        </div>
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold text-slate-800 mb-6">Mark Attendance</h3>
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />

              <select
                value={selectedEmployee}
                onChange={(e) => setSelectedEmployee(e.target.value)}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Employee</option>
                {employees.map((emp: any) => (
                  <option key={emp.employeeId} value={emp.employeeId}>
                    {emp.name} ({emp.employeeId})
                  </option>
                ))}
              </select>

              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as "present" | "absent")}
                className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="present">Present</option>
                <option value="absent">Absent</option>
              </select>
            </div>

            <div className="flex gap-4">
              <button
                onClick={markAttendance}
                disabled={submitting}
                className="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 font-semibold disabled:bg-gray-400"
              >
                {submitting ? "Saving..." : "Save Attendance"}
              </button>
              <button
                onClick={() => {
                  setShowForm(false)
                  setSelectedEmployee("")
                }}
                className="flex-1 bg-slate-300 text-slate-800 py-2 rounded-lg hover:bg-slate-400 font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-xl font-semibold text-slate-800">Attendance for {selectedDate}</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-50 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-800">Employee ID</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-800">Name</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-800">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-800">Action</th>
              </tr>
            </thead>
            <tbody>
              {todayRecords.length > 0 ? (
                todayRecords.map((record) => (
                  <tr key={record.employeeId} className="border-b border-slate-200 hover:bg-slate-50">
                    <td className="px-6 py-3 text-sm text-slate-700">{record.employeeId}</td>
                    <td className="px-6 py-3 text-sm text-slate-700">{record.employeeName}</td>
                    <td className="px-6 py-3 text-sm">
                      <span
                        className={`px-3 py-1 rounded-full text-white text-xs font-semibold ${
                          record.status === "present" ? "bg-green-500" : "bg-red-500"
                        }`}
                      >
                        {record.status.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-sm">
                      <button
                        onClick={() => deleteRecord(record.id)}
                        className="text-red-500 hover:text-red-700 flex items-center gap-1"
                      >
                        <Trash2 size={16} /> Delete
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-slate-500">
                    No attendance records for this date
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
