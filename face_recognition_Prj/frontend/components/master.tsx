"use client"

import { useState, useEffect } from "react"
import { Plus, X } from "lucide-react"

const HOST = "http://127.0.0.1:8080"

interface Plant {
  id: string
  name: string
}

interface Department {
  id: string
  name: string
}

interface Shift {
  id: string
  name: string
  startTime: string
  endTime: string
}

export default function Master() {
  const [plants, setPlants] = useState<Plant[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [shifts, setShifts] = useState<Shift[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [showPlantForm, setShowPlantForm] = useState(false)
  const [showDeptForm, setShowDeptForm] = useState(false)
  const [showShiftForm, setShowShiftForm] = useState(false)

  const [plantName, setPlantName] = useState("")
  const [deptName, setDeptName] = useState("")
  const [shiftName, setShiftName] = useState("")
  const [startTime, setStartTime] = useState("")
  const [endTime, setEndTime] = useState("")

  useEffect(() => {
    fetchAllData()
  }, [])

  const fetchAllData = async () => {
    try {
      setLoading(true)
      // const [plantsRes, deptsRes, shiftsRes] = await Promise.all([
      //   fetch(`${HOST}/api/plants`),
      //   fetch(`${HOST}/api/departments`),
      //   fetch(`${HOST}/api/shifts`),
      // ])

      const res = await fetch(`${HOST}/api/masters`)

      // if (!plantsRes.ok || !deptsRes.ok || !shiftsRes.ok) {
      if (!res.ok) {
        throw new Error("Failed to fetch data")
      }

      // const get_plants = await plantsRes.json()
      // const get_dept = await deptsRes.json()
      // const get_shift = await shiftsRes.json()

      const get_master = await res.json()
      if (get_master.data){
        setPlants(get_master.data.plants)
        setDepartments(get_master.data.depts)
        setShifts(get_master.data.shifts)
      }
      setError(null)
    } catch (err) {
      console.error("[v0] Fetch error:", err)
      setError("Failed to load data")
    } finally {
      setLoading(false)
    }
  }

  const addPlant = async () => {
    if (plantName.trim()) {
      try {
        const res = await fetch(`${HOST}/api/plants`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: plantName }),
        })

        if (!res.ok) throw new Error("Failed to add plant")

        const newPlant = await res.json()
        setPlantName("")
        setPlants(newPlant.data)
        setShowPlantForm(false)
      } catch (err) {
        console.error("[v0] Add plant error:", err)
        setError("Failed to add plant")
      }
    }
  }

  const addDepartment = async () => {
    if (deptName.trim()) {
      try {
        const res = await fetch(`${HOST}/api/departments`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: deptName }),
        })

        if (!res.ok) throw new Error("Failed to add department")

        const newDept = await res.json()
        if (newDept.data){
          setDepartments(newDept.data)
        }
        setDeptName("")
        setShowDeptForm(false)
      } catch (err) {
        console.error("[v0] Add department error:", err)
        setError("Failed to add department")
      }
    }
  }

  const addShift = async () => {
    if (shiftName.trim() && startTime && endTime) {
      try {
        const res = await fetch(`${HOST}/api/shifts`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: shiftName, from_time: startTime, to_time: endTime }),
        })

        if (!res.ok) throw new Error("Failed to add shift")

        const newShift = await res.json()
        setShifts(newShift.data)
        setShiftName("")
        setStartTime("")
        setEndTime("")
        setShowShiftForm(false)
      } catch (err) {
        console.error("[v0] Add shift error:", err)
        setError("Failed to add shift")
      }
    }
  }

  const removePlant = async (name: string) => {
    try {
      const res = await fetch(`${HOST}/api/plants?name=${name}`, { method: "DELETE" })

      if (!res.ok) throw new Error("Failed to delete plant")

      const plantRes = await res.json()
      if (plantRes.data){
        setPlants(plantRes.data)
      }
    } catch (err) {
      console.error("[v0] Delete plant error:", err)
      setError("Failed to delete plant")
    }
  }

  const removeDepartment = async (name: string) => {
    try {
      const res = await fetch(`${HOST}/api/departments?name=${name}`, { method: "DELETE" })

      if (!res.ok) throw new Error("Failed to delete department")

      const deptRes = await res.json()

      if(deptRes.data){
        setDepartments(deptRes.data)
      }
    } catch (err) {
      console.error("[v0] Delete department error:", err)
      setError("Failed to delete department")
    }
  }

  const removeShift = async (name: string) => {
    try {
      const res = await fetch(`${HOST}/api/shifts?name=${name}`, { method: "DELETE" })

      if (!res.ok) throw new Error("Failed to delete shift")

      const shiftRes = await res.json()
      if(shiftRes.data){
        setShifts(shiftRes.data)
      }
    } catch (err) {
      console.error("[v0] Delete shift error:", err)
      setError("Failed to delete shift")
    }
  }

  if (loading) {
    return (
      <div className="p-8">
        <div className="text-center text-slate-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-slate-800 mb-8">Master Configuration</h2>

      {error && <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Plants */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Plants</h3>
          <div className="space-y-2 mb-4 max-h-48 overflow-y-auto">
            {plants.map((plant) => (
              <div key={plant.name} className="flex items-center justify-between bg-slate-50 p-2 rounded">
                <span className="text-slate-700">{plant.name}</span>
                <button onClick={() => removePlant(plant.name)} className="text-red-500 hover:text-red-700">
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
          {!showPlantForm ? (
            <button
              onClick={() => setShowPlantForm(true)}
              className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={18} /> Add Plant
            </button>
          ) : (
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Plant name"
                value={plantName}
                onChange={(e) => setPlantName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex gap-2">
                <button
                  onClick={addPlant}
                  className="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setShowPlantForm(false)
                    setPlantName("")
                  }}
                  className="flex-1 bg-slate-300 text-slate-800 py-2 rounded-lg hover:bg-slate-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Departments */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Departments</h3>
          <div className="space-y-2 mb-4 max-h-48 overflow-y-auto">
            {departments.map((dept) => (
              <div key={dept.name} className="flex items-center justify-between bg-slate-50 p-2 rounded">
                <span className="text-slate-700">{dept.name}</span>
                <button onClick={() => removeDepartment(dept.name)} className="text-red-500 hover:text-red-700">
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
          {!showDeptForm ? (
            <button
              onClick={() => setShowDeptForm(true)}
              className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={18} /> Add Department
            </button>
          ) : (
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Department name"
                value={deptName}
                onChange={(e) => setDeptName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex gap-2">
                <button
                  onClick={addDepartment}
                  className="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setShowDeptForm(false)
                    setDeptName("")
                  }}
                  className="flex-1 bg-slate-300 text-slate-800 py-2 rounded-lg hover:bg-slate-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Shifts */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-slate-800 mb-4">Shifts</h3>
          <div className="space-y-2 mb-4 max-h-48 overflow-y-auto">
            {shifts.map((shift) => (
              <div key={shift.name} className="flex items-center justify-between bg-slate-50 p-2 rounded text-sm">
                <div>
                  <p className="font-medium text-slate-700">{shift.name}</p>
                  <p className="text-slate-500">
                    {shift.startTime} - {shift.endTime}
                  </p>
                </div>
                <button onClick={() => removeShift(shift.name)} className="text-red-500 hover:text-red-700">
                  <X size={18} />
                </button>
              </div>
            ))}
          </div>
          {!showShiftForm ? (
            <button
              onClick={() => setShowShiftForm(true)}
              className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={18} /> Add Shift
            </button>
          ) : (
            <div className="space-y-2">
              <input
                type="text"
                placeholder="Shift name"
                value={shiftName}
                onChange={(e) => setShiftName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="time"
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex gap-2">
                <button
                  onClick={addShift}
                  className="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600"
                >
                  Save
                </button>
                <button
                  onClick={() => {
                    setShowShiftForm(false)
                    setShiftName("")
                    setStartTime("")
                    setEndTime("")
                  }}
                  className="flex-1 bg-slate-300 text-slate-800 py-2 rounded-lg hover:bg-slate-400"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
