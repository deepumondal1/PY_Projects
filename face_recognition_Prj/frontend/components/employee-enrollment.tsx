"use client"

import { useState, useRef, useEffect } from "react"
import { Plus, Camera, Edit2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from '@/components/ui/label'
import { useToast } from "@/hooks/use-toast"

const HOST = "http://127.0.0.1:8080"

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

export default function EmployeeEnrollment() {
  const [employees, setEmployees] = useState<Employee[]>([])
  const [plants, setPlants] = useState([])
  const [departments, setDepartments] = useState([])
  const [shifts, setShifts] = useState([])
  const [loading, setLoading] = useState(true)

  const [submitting, setSubmitting] = useState(false)

  const [showForm, setShowForm] = useState(false)
  const [showCamera, setShowCamera] = useState(false)
  const [testPhotoCamera, setTestPhotoCamera] = useState(false)
  const [captureState, setCaptureState] = useState(true)
  const [photoData, setPhotoData] = useState<string | null>(null)
  const [testPhotoData, setTestPhotoData] = useState<string | undefined>(undefined)
  const [editingId, setEditingId] = useState<string | null>(null)  
  
  const { toast } = useToast()

  const [formData, setFormData] = useState({
    name: "",
    employeeId: "",
    plant: "",
    department: "",
    shift: "",
  })

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const reader = useRef<ReadableStreamDefaultReader<Uint8Array<ArrayBuffer>> | undefined>(undefined)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // const [empRes, plantRes, deptRes, shiftRes] = await Promise.all([
        //   fetch("/api/enrollments"),
        //   fetch("/api/plants"),
        //   fetch("/api/departments"),
        //   fetch("/api/shifts"),
        // ])

        const res = await fetch(`${HOST}/api/enrollments`)        

        // if (empRes.ok) setEmployees(await empRes.json())
        // if (plantRes.ok) setPlants(await plantRes.json())
        // if (deptRes.ok) setDepartments(await deptRes.json())
        // if (shiftRes.ok) setShifts(await shiftRes.json())
        if(res.ok){
          const data = (await res.json()).data
          setEmployees(data.employees)
          setPlants(data.plants)
          setDepartments(data.depts)
          setShifts(data.shifts)
        }
      } catch (error) {
        console.error("Failed to fetch data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const resetForm = () => {
    setFormData({ name: "", employeeId: "", plant: "", department: "", shift: "" })
    setPhotoData(null)
    setShowForm(false)
    setEditingId(null)
  }

  const startCamera = async () => {
    try {
      // const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
      const stream = await navigator.mediaDevices.getUserMedia({ video: true })
      console.log('start stream',stream)
      console.log('videoRef',videoRef)
      if (videoRef.current) {
        videoRef.current.srcObject = stream
      }
    } catch (error) {
      console.error("Camera access denied:", error)
      alert("Unable to access camera")
    } finally{
      setCaptureState(false)
    }
  }

  const capturePhoto = () => {
    if (canvasRef.current && videoRef.current) {
      const context = canvasRef.current.getContext("2d")
      if (context) {
        context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height)
        const imageData = canvasRef.current.toDataURL("image/jpeg")
        setPhotoData(imageData)
      }
    }
    stopCamera()
  }

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream
      console.log('stop stream',stream)
      stream.getTracks().forEach((track) => track.stop())
    }
    setShowCamera(false)
    setCaptureState(true)
  }

  const handleTestPhoto = async () => {
    console.log(reader)
    setShowCamera(true)
    setTestPhotoCamera(true)
    try{
      const form = new FormData()
      if (!photoData){
        throw Error("Photo is not captured yet.")
      }
      form.append('src_img', photoData || '')

      const resp = await fetch(`${HOST}/api/matching_captured`,{
        method: "POST",
        body: form
      })
      if(!resp.ok){
        throw Error("Invalid Response Generated")
      }
      reader.current = await resp.body?.getReader()
      const textDecoder = new TextDecoder()
      let chunk = ''
      try{
        if(reader.current){
          while(true){
            const {done, value} = await reader.current.read()
            if(done){
              console.log('job done')
              break
            }
            chunk = chunk + textDecoder.decode(value)
            if(!chunk.includes("|")) {
                continue
            }
            const lines = chunk.split("|")
            chunk = ''
            for (const line of lines){
              if (line.includes("data")) {
                try {
                  let data = JSON.parse(line)
                  data=data.data
                  setTestPhotoData(data.base64img)
                  console.log(data)
                  if (data.isFaceCaptured){
                    (data.isMatched) ? 
                      toast({
                        title: "Testing Capture Image",
                        description: <>
                          <br/>
                          <Label>MATCH FOUND!</Label>
                          <img src={data.base64img} alt="Found Image"/>
                        </>,
                        variant:'success'
                      }) : 
                      toast({
                        title: "Testing Capture Image",
                        description: <>
                          <br/>
                          <Label>NO MATCH FOUND!</Label>
                          <img src={data.base64img} alt="Found Image"/>
                        </>,
                        variant:'destructive'
                      }) 
                    break
                  }
                } catch (parseError) {
                  // console.error("Error parsing SSE data:", parseError)
                    // toast({
                    //   title: "File processed Failed",
                    //   description: `${parseError}`,
                    //   // variant: "destructive",
                    // })
                }
                
              }
            }
            // if(chunk.includes("|")){
            //   chunk = chunk.replace("}{","}|{")
            //   const ch = chunk.split("|")
            //   console.log(ch)
            //   const data = JSON.parse(ch[0])
            //   if (data.isMatched){
            //     toast({
            //       title: "Testing Capture Image",
            //       description: "MATCH FOUND!",
            //       variant:'success'
            //     })
            //     console.log("Match Found")
            //     break
            //   }
            //   setTestPhotoData(data.base64img)
            //   chunk = ch[1] || ''
            // }
          }
        }
      }catch(err){
        console.log('err2', err)
        toast({
          title: "Error Found-2",
          description: `${err}`,
          variant: 'destructive'
        })
      }finally{
        reader.current?.releaseLock()
      }

    }catch(err){
      console.log('err1', err)
    }finally{
      setTestPhotoCamera(false)
      setShowCamera(false)
      setTestPhotoData(undefined)
      reader.current = undefined
    }
  }

  const releaseTestCamera = async () => {
    try{
      console.log('releaseTestCamera',reader.current)
      if (reader.current){
        await reader.current?.cancel('Force Stop Camera')
        setTestPhotoCamera(false)
        setShowCamera(false)
        setTestPhotoData(undefined)
      }
    }catch(err){
      console.log('Error - releaseTestCamera',err)
    }finally{
      reader.current = undefined
    }
  }

  const saveEmployee = async () => {
    if (
      !formData.name ||
      !formData.employeeId ||
      !formData.plant ||
      !formData.department ||
      !formData.shift ||
      !photoData
    ) {
      alert("Please fill all fields and capture a photo")
      return
    }

    setSubmitting(true)
    try {
      if (editingId) {
        const response = await fetch(`${HOST}/api/enrollments`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...formData, photo: photoData }),
        })
        if (response.ok) {
          const updated = await response.json()
          setEmployees(employees.map((emp) => (emp.id === editingId ? updated : emp)))
        }
      } else {
        const response = await fetch(`${HOST}/api/enrollments`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ ...formData, photo: photoData }),
        })
        if (response.ok) {
          const newEmployee = await response.json()
          setEmployees(newEmployee.data)
        }
      }
      resetForm()
    } catch (error) {
      console.error("Failed to save employee:", error)
      alert("Failed to save employee")
    } finally {
      setSubmitting(false)
    }
  }

  const deleteEmployee = async (empId: string) => {
    try {
      const response = await fetch(`${HOST}/api/enrollments?empId=${empId}`, { method: "DELETE" })
      if (response.ok) {
        const empRes = await response.json()
        setEmployees(empRes.data)
      }
    } catch (error) {
      console.error("Failed to delete employee:", error)
    }
  }

  const startEdit = (employee: Employee) => {
    setFormData({
      name: employee.name,
      employeeId: employee.employeeId,
      plant: employee.plant,
      department: employee.department,
      shift: employee.shift,
    })
    setPhotoData(employee.photo)
    setEditingId(employee.id)
    setShowForm(true)
  }

  if (loading) {
    return <div className="p-8 text-center text-slate-600">Loading...</div>
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-8">
        <h2 className="text-3xl font-bold text-slate-800">Employee Enrollment</h2>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 flex items-center gap-2"
          >
            <Plus size={20} /> Add Employee
          </button>
        )}
      </div>

      {showForm && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h3 className="text-xl font-semibold text-slate-800 mb-6">{editingId ? "Edit" : "Add"} Employee</h3>

          {!showCamera ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Employee Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="text"
                  placeholder="Employee ID"
                  value={formData.employeeId}
                  onChange={(e) => setFormData({ ...formData, employeeId: e.target.value })}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <select
                  value={formData.plant}
                  onChange={(e) => setFormData({ ...formData, plant: e.target.value })}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Plant</option>
                  {plants.map((p: any) => (
                    <option key={p.name} value={p.name}>
                      {p.name}
                    </option>
                  ))}
                </select>

                <select
                  value={formData.department}
                  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Department</option>
                  {departments.map((d: any) => (
                    <option key={d.name} value={d.name}>
                      {d.name}
                    </option>
                  ))}
                </select>

                <select
                  value={formData.shift}
                  onChange={(e) => setFormData({ ...formData, shift: e.target.value })}
                  className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Shift</option>
                  {shifts.map((s: any) => (
                    <option key={s.name} value={s.name}>
                      {s.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center gap-4">
                {photoData && (
                  <img
                    src={photoData || "/placeholder.svg"}
                    alt="Captured"
                    className="w-20 h-20 rounded-lg object-cover"
                  />
                )}
                <button
                  onClick={()=>setShowCamera(true)}
                  className="bg-orange-500 text-white px-6 py-2 rounded-lg hover:bg-orange-600 flex items-center gap-2"
                >
                  <Camera size={20} /> Capture Photo
                </button>
                <button
                  onClick={handleTestPhoto}
                  className="bg-red-500 text-white px-6 py-2 rounded-lg hover:bg-red-600 flex items-center gap-2"
                >
                  <Camera size={20} /> Test Photo
                </button>
              </div>

              <div className="flex gap-4">
                <button
                  onClick={saveEmployee}
                  disabled={submitting}
                  className="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 font-semibold disabled:bg-gray-400"
                >
                  {submitting ? "Saving..." : "Save Employee"}
                </button>
                <button
                  onClick={resetForm}
                  className="flex-1 bg-slate-300 text-slate-800 py-2 rounded-lg hover:bg-slate-400 font-semibold"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
                {testPhotoCamera ? (
                  <>
                    <Button
                      onClick={releaseTestCamera}
                      disabled={reader.current == undefined}
                      className="flex-1 bg-red-500 text-white py-2 rounded-lg hover:bg-red-600 font-semibold"
                    >
                      Stop Testing Camera
                    </Button>
                    {reader.current != undefined ? (
                      <div className="relative">
                        <img 
                          src={testPhotoData} 
                          alt='Test Photo Camera' 
                          className="rounded-lg object-cover"
                        />
                      </div>
                    ):(
                      <div>
                        <Label>
                          Please wait for camera to load...
                        </Label>
                      </div>
                    )}
                  </>
                ) : (
                  <>
                    <div className="relative">
                      <video ref={videoRef} autoPlay playsInline className="w-full rounded-lg bg-slate-900" />
                      <canvas ref={canvasRef} width={320} height={240} className="hidden" />
                    </div>
                    <div className="flex gap-4">
                      <Button
                        onClick={startCamera}
                        className="flex-1 bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 font-semibold"
                      >
                        Start Camera
                      </Button>
                      <Button
                        onClick={capturePhoto}
                        disabled={captureState}
                        className="flex-1 bg-red-500 text-white py-2 rounded-lg hover:bg-red-600 font-semibold disabled:cursor-not-allowed disabled:pointer-events-auto"
                      >
                        Capture
                      </Button>
                      <Button
                        onClick={stopCamera}
                        className="flex-1 bg-slate-300 text-slate-800 py-2 rounded-lg hover:bg-slate-400 font-semibold"
                      >
                        Close Camera
                      </Button>
                    </div>
                  </>
                )}
            </div>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {employees.map((emp) => (
          <div key={emp.employeeId} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
            <img src={emp.photo || "/placeholder.svg"} alt={emp.name} className="w-full h-48 object-cover" />
            <div className="p-4">
              <h3 className="font-bold text-slate-800">{emp.name}</h3>
              <p className="text-sm text-slate-600">ID: {emp.employeeId}</p>
              <p className="text-sm text-slate-600">Plant: {emp.plant}</p>
              <p className="text-sm text-slate-600">Department: {emp.department}</p>
              <p className="text-sm text-slate-600">Shift: {emp.shift}</p>
              <div className="flex gap-2 mt-4">
                <button
                  onClick={() => startEdit(emp)}
                  className="flex-1 bg-blue-500 text-white py-1 rounded flex items-center justify-center gap-1 hover:bg-blue-600 text-sm"
                >
                  <Edit2 size={16} /> Edit
                </button>
                <button
                  onClick={() => deleteEmployee(emp.employeeId)}
                  className="flex-1 bg-red-500 text-white py-1 rounded hover:bg-red-600 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
