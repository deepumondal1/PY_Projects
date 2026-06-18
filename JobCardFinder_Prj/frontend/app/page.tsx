"use client"

import { FormEvent, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/hooks/use-toast"
import DataTable from "@/components/data-table"
import { Loader2, Upload, CheckCircle, X } from "lucide-react"

interface JobCard {
  id: string
  jobId: string
  jobTitle: string
  company: string
  location: string
  salary: string
  status: string
  datePosted: string
  description: string
}

// Mock database of job cards
const JOB_CARD_DATABASE: { [key: string]: JobCard } = {
  "JC-001": {
    id: "1",
    jobId: "JC-001",
    jobTitle: "Senior Frontend Developer",
    company: "Tech Corp",
    location: "San Francisco, CA",
    salary: "$120,000 - $150,000",
    status: "Active",
    datePosted: "2024-10-20",
    description: "Looking for experienced frontend developer with React expertise",
  },
  "JC-002": {
    id: "2",
    jobId: "JC-002",
    jobTitle: "Full Stack Engineer",
    company: "StartUp Inc",
    location: "New York, NY",
    salary: "$100,000 - $130,000",
    status: "Active",
    datePosted: "2024-10-18",
    description: "Build scalable web applications using modern tech stack",
  },
  "JC-003": {
    id: "3",
    jobId: "JC-003",
    jobTitle: "Backend Developer",
    company: "Cloud Systems",
    location: "Remote",
    salary: "$110,000 - $140,000",
    status: "Closed",
    datePosted: "2024-10-15",
    description: "Develop robust backend services and APIs",
  },
  "JC-004": {
    id: "4",
    jobId: "JC-004",
    jobTitle: "DevOps Engineer",
    company: "Enterprise Solutions",
    location: "Austin, TX",
    salary: "$130,000 - $160,000",
    status: "Active",
    datePosted: "2024-10-22",
    description: "Manage infrastructure and deployment pipelines",
  },
  "JC-005": {
    id: "5",
    jobId: "JC-005",
    jobTitle: "UI/UX Designer",
    company: "Design Studio",
    location: "Los Angeles, CA",
    salary: "$90,000 - $120,000",
    status: "Active",
    datePosted: "2024-10-21",
    description: "Create beautiful and intuitive user interfaces",
  },
  "JC-006": {
    id: "6",
    jobId: "JC-006",
    jobTitle: "Data Scientist",
    company: "Analytics Pro",
    location: "Boston, MA",
    salary: "$125,000 - $155,000",
    status: "Active",
    datePosted: "2024-10-19",
    description: "Analyze data and build machine learning models",
  },
}

export default function Home() {
  const [jobCardInput, setJobCardInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [data, setData] = useState<{string:object}[]>([])
  const [columns, setColumns] = useState<string[]>([])
  const [originalData, setOriginalData] = useState([])
  const [hasGenerated, setHasGenerated] = useState(false)
  const [processedCount, setProcessedCount] = useState(0)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState("")
  const [jobCardData, setJobCardData] = useState({})
  const { toast } = useToast()
  const [productionOrder, setProductionOrder] = useState<string | null>(null)
  const [orderQty, setOrderQty] = useState<number>(1000)
  const [selectedRow, setSelectedRow] = useState<{string:object} | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [header, setHeader] = useState<Partial<{string:object}>>({})
  const [lines, setLines] = useState<Partial<{[k:string]:object|number}[]>>([])
  const [formData, setFormData] = useState<Partial<{string:string|number|{string:object}[]}>>({})
  const [editedValues, setEditedValues] = useState<Partial<{string:object}>>({})
  const [editedValues2, setEditedValues2] = useState<Partial<{[k:string]:object|number}[]>>([])

  useEffect(()=>{
    console.log(editedValues2)

  },[editedValues2])

  const generateData = async () => {
    if (!jobCardInput.trim()) {
      toast({
        title: "Input Required",
        description: "Please enter at least one job card number",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    setProgress(0)
    setData([])
    setColumns([])
    setOriginalData([])
    setProgressMessage("Starting file processing...")

    // Parse job card numbers from textarea (separated by newlines)
    const jobCardNumbers = jobCardInput
      .split("\n")
      .map((line) => line.trim().toUpperCase())
      .filter((line) => line.length > 0)

    if (jobCardNumbers.length === 0) {
      toast({
        title: "Invalid Input",
        description: "No valid job card numbers found",
        variant: "destructive",
      })
      setIsLoading(false)
      return
    }
    
    // Simulate processing delay
    // await new Promise((resolve) => setTimeout(resolve, 2000))

    // Fetch JC_Data from APIs
    try{
      const form = new FormData()
      form.append("jc_list",JSON.stringify(jobCardNumbers))
      const response = await fetch("http://127.0.0.1:5000/api/start_task",{
        method: "POST",
        // headers: {
        //   "Content-Type": "application/json"
        // },
        body: form //JSON.stringify({"jc_list":jobCardNumbers})
      })
// console.log(response)
      if (!response.ok){
        throw new Error(`HTTP error! status: ${response.statusText} - ${response.body} - ${response.url}`)
      }

      const reader = response.body?.getReader()
      const decode = new TextDecoder()
// console.log(reader)
      if(reader){
        let chunk = ''
        while(true){
          const {done, value} = await reader.read()

          if(done) break

          chunk += decode.decode(value)

          if (!chunk.includes('\n')){
            continue
          }
// console.log(chunk)
          const lines = chunk.split("\n")
          chunk=''

          for(const line of lines){
            if(line.includes("data")){
              try{
                let data = JSON.parse(line)
                data=data.data

                if(data.progress){
                  setProgress(data.progress)
                }

                if(data.message){
                  setProgressMessage(data.message)
                }

                if(data.error){
                  throw new Error(data.error)
                }

                if(data.download){
                  let download:{string:object}[] = data.download
                  console.log("download data")
                  console.log(download)
                  setHasGenerated(true)
                  setProgressMessage(data.message)
                  setJobCardData(download)
                  setData(download)
                  setColumns(download.length !==0 ? Object.keys(download[0]) : [])
                  setOriginalData(data.original)
                }

                if(data.complete){
                  setProgress(100)
                  setProgressMessage("Processing completed successfully!")
                  toast({
                    title: "Data processed successfully",
                    description: `Job Card Consumption has been generated and showing in tables.`,
                  })
                }

              }catch(err){
                toast({
                  title: "Processing Failed!",
                  description: `${err}`,
                  variant: "destructive",
                })
              }
            }
          }

        }
      }

    }catch(error){
      toast({
        title: "Processing Failed!",
        description: error instanceof Error ? error.message : "An unexpected error occurred during file processing.",
        variant: "destructive",
      })
      setProgressMessage("Processing failed")
      setProgress(0)

    } finally {
      setIsLoading(false)
    }

    // Fetch job cards from mock database
//     const fetchedData = jobCardNumbers
//       .map((jobCardId) => JOB_CARD_DATABASE[jobCardId])
//       .filter((card) => card !== undefined)
// console.log(fetchedData)
//     setData(fetchedData)
    // setProcessedCount(jobCardNumbers.length)
    // setHasGenerated(true)
    // setIsLoading(false)
  }

  const refreshTable = async () => {
    // Refresh function - can be implemented later
    
    setIsLoading(true)
    setProgress(0)
    setData([])
    setColumns([])
    setOriginalData([])
    setProgressMessage("Starting file processing...")

    try{
      const response = await fetch("http://127.0.0.1:5000/api/refresh_task",{
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(originalData)
      })

      if (!response.ok){
        throw new Error(`HTTP error! status: ${response.statusText} - ${response.body} - ${response.url}`)
      }
      
      const reader = response.body?.getReader()
      const decode = new TextDecoder()
// console.log(reader)
      if(reader){
        let chunk = ''
        while(true){
          const {done, value} = await reader.read()

          if(done) break

          chunk += decode.decode(value)

          if (!chunk.includes('\n')){
            continue
          }
// console.log(chunk)
          const lines = chunk.split("\n")
          chunk=''

          for(const line of lines){
            if(line.includes("data")){
              try{
                let data = JSON.parse(line)
                data=data.data

                if(data.progress){
                  setProgress(data.progress)
                }

                if(data.message){
                  setProgressMessage(data.message)
                }

                if(data.error){
                  throw new Error(data.error)
                }

                if(data.download){
                  let download:{string:object}[] = data.download
                  console.log("download data")
                  console.log(download)
                  setHasGenerated(true)
                  setProgressMessage(data.message)
                  setJobCardData(download)
                  setData(download)
                  setColumns(download.length !==0 ? Object.keys(download[0]) : [])
                  setOriginalData(data.original)
                }

                if(data.complete){
                  setProgress(100)
                  setProgressMessage("Processing completed successfully!")
                  toast({
                    title: "Data processed successfully",
                    description: `Job Card Consumption has been generated and showing in tables.`,
                  })
                }

              }catch(err){
                toast({
                  title: "Processing Failed!",
                  description: `${err}`,
                  variant: "destructive",
                })
              }
            }
          }

        }
      }

    }catch(error){
      toast({
        title: "Processing Failed!",
        description: error instanceof Error ? error.message : "An unexpected error occurred during file processing.",
        variant: "destructive",
      })
      setProgressMessage("Processing failed")
      setProgress(0)

    } finally {
      setIsLoading(false)
    }
  }

  const openModal = (row: {string:object}) => {
    setSelectedRow(row)
    // setEditedValues(row)
    handleEditedValues(row)
    setIsModalOpen(true)
    setProductionOrder('')
    setOrderQty(1000)
  }

  const closeModal = () => {
    setIsModalOpen(false)
    setSelectedRow(null)
    setEditedValues({})
    setProductionOrder('')
    setOrderQty(1000)
  }

  const handleEditedValues = (row: {string:object}) => {
    console.log(Object.entries(row))
    const header = Object.entries(row).filter((field)=>{
      let filename = field[0].includes('FileName')
      let sheetname = field[0].includes('SheetName')
      // let d = parseInt(String(field[1]) ?? '') > 0
      return (filename || sheetname)
    }).map((field)=>Object.fromEntries([[field[0].replace('-',''),field[1]]]))
    const lines = Object.entries(row).filter((field)=>{
      let d1 = parseInt(String(field[1]) ?? '') > 0
      let d2 = parseInt(String(field[0].split("-").at(0)) ?? '') > 0
      return (d1 && d2)
    }).map((field)=>Object.fromEntries([['opp',parseInt(String(field[0].split("-").at(0)))],['witem',field[0].split("-").at(1)],['wqty',field[1]]]))
  // }).map((field)=>Object.fromEntries([field]))
    const editedData = {...Object.assign({}, {orderQty:1000}, ...header), lines}
    // console.log(Object.entries(row))
    // console.log(...header)
    
    console.log({...editedData})
    // setEditedValues(editedData)
    setHeader(Object.assign({}, ...header))
    // setLines(lines)
    setFormData(editedData)
    setEditedValues(editedData)
    // setColumns(Object.keys(editedData))
  }

  const handleInputChange = (key: number, value: string, oldKey:string) => {
    // setEditedValues((prev) => ({
    //   ...prev,
    //   [key]: value,
    // }))
    // let editedData = editedValues2
    // console.log(key,value,oldKey,{[oldKey]:parseInt(value)})
    editedValues2[key] = {[oldKey]:parseInt(value)}
    // setEditedValues2([...editedValues2, editedData])
    // setEditedValues2([...editedValues2, {key:{[oldKey]:parseInt(value)}}])
    setEditedValues2([...editedValues2])
  }

  const handleInputChange2 = () => {
    setEditedValues2([...editedValues2])
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    // Submit function - will be implemented later
    alert(editedValues2.map((e)=>Object.keys(e??{})))
    console.log(e.currentTarget)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header Section */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg flex items-center justify-center">
              <Upload className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-4xl font-bold text-slate-900">Job Card Data Finder</h1>
          </div>
          <p className="text-lg text-slate-600 max-w-2xl">
            Paste multiple job card numbers to retrieve and analyze job data with advanced filtering capabilities
          </p>
        </div>

        {/* Input Section */}
        <Card className="bg-white border border-slate-200 shadow-lg p-8 mb-8">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-slate-900 mb-3">Job Card Numbers</label>
              <p className="text-sm text-slate-600 mb-3">
                Enter one job card number per line (e.g., 4XXXX, 9XXXX, etc.)
              </p>
              <textarea
                placeholder={"4XXXX\n40XXX\n9XXXX\n90XXX"}
                value={jobCardInput}
                onChange={(e) => setJobCardInput(e.target.value)}
                disabled={isLoading}
                className="w-full h-32 px-4 py-3 border border-slate-300 rounded-lg bg-white text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm disabled:bg-slate-100 disabled:cursor-not-allowed"/>
            </div>

            {isLoading && (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-700">Processing...</span>
                  <span className="text-sm font-semibold text-blue-600">{Math.round(progress)}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div>
                  <span className="text-xs text-muted-foreground">{progressMessage}</span>
                </div>
              </div>
            )}

            <div className="flex gap-3 pt-2">
              <Button
                onClick={generateData}
                disabled={isLoading || !jobCardInput.trim()}
                className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-2 rounded-lg font-semibold flex items-center gap-2 transition-all shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Generate
                  </>
                )}
              </Button>
            </div>
          </div>
        </Card>

        {/* Data Table */}
        {hasGenerated && (
          <div className="animate-in fade-in duration-500">
              <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-blue-600 flex-shrink-0" />              <p className="text-sm text-slate-700">
                <span className="font-semibold text-blue-900">{data.length}</span> of{" "}
                <span className="font-semibold text-blue-900">{processedCount}</span> job cards found
              </p>
            </div>
            <DataTable data={data} columns={data.length !==0 ? Object.keys(data[0]) : []} refreshCB={refreshTable} onRowView={openModal}  />
          </div>
        )}

        {/* Empty State */}
        {!hasGenerated && (
          <Card className="bg-white border border-slate-200 p-12 text-center shadow-sm">
            <div className="flex flex-col items-center gap-3">
              <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
                <Upload className="w-8 h-8 text-slate-400" />
              </div>
              <p className="text-slate-600 text-lg">Paste job card numbers above and click Generate to load data</p>
            </div>
          </Card>
        )}
      </div>
      
      
      {/* Modal */}
      {isModalOpen && selectedRow && (
        // <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="fixed inset-0 bg-gray-300/50 flex items-center justify-center z-50">
          <Card className="bg-white border border-slate-200 shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-slate-100 to-slate-50 border-b border-slate-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold text-slate-900">Job Card Details</h2>
              <button
                onClick={closeModal}
                className="text-slate-600 hover:text-slate-900 transition p-1"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <form id="production_form" onSubmit={handleSubmit}>
              <div className="flex-1 overflow-y-auto p-8">
                <div className="max-w-5xl mx-auto">
                  {/* <div className="grid grid-cols-1 md:grid-cols-1 gap-6"> */}
                  <div className="flex flex-col item-center gap-3">
                    {/* <div className="flex flex-row gap-3">
                      <label className="block text-sm text-gray-500 font-semibold px-1 py-2">Production Order</label>
                      <input 
                        type='text' 
                        value={productionOrder?.toUpperCase() ?? ''}
                        maxLength={9}
                        onChange={(e) => setProductionOrder(e.target.value)}
                        className="w-40 border border-slate-200 rounded-lg px-3 py-1" 
                        min="1"/>
                    </div> */}
                    <div className="flex flex-row gap-3">
                      <label className="block text-sm text-gray-500 font-semibold px-1 py-2">Order Quantity</label>
                      <input 
                        name="order_quantity"
                        type='number' 
                        value={orderQty} 
                        onChange={(e) => {

                          setOrderQty(parseInt(e.target.value))
                        }}
                        className="w-35 border border-slate-200 rounded-lg px-3 py-1" 
                        min="0"
                        step={1000}
                      />
                    </div>

                    {/* {Object.keys(editedValues).map((k,i) =>  {
                    let field = k
                    let fieldVal = String(editedValues[k as keyof typeof data[0]] || '')
                    // let field = Object.keys(k ?? {})[0]
                    // let fieldVal = String(k && k[field as keyof typeof data[0]])

                    // let fieldVal = String(editedValues[field as keyof typeof data[0]] || "")
                    let operations = field.split("-").at(0)
                    let w_items = field.split("-").at(1)

                    let value = parseInt(fieldVal)
                    let filename = field.includes("FileName")
                    let sheetname = field.includes("SheetName")
                    let total = field.toLowerCase().includes("total")
                    let diff = field.toLowerCase().includes("diff")
                    let actVal = String(value*orderQty/1000 || 0)
                    console.log(field, fieldVal, actVal, orderQty)

                    return (filename || sheetname) && 
                      (
                        <div key={field} className="flex flex-row gap-3">
                          <label className="block text-sm font-semibold px-1 py-2">{field.replace("-","")}</label>
                          <div className="border bg-gray-200 border-slate-200 rounded-lg px-3 py-1">{fieldVal}</div>
                        </div>
                      ) 
                      // || parseInt(String(field.at(0)||''))>=0 && value > 0 && 
                      || (!total && !diff) &&
                      (
                        <div key={field} className="space-y-2 grid grid-cols-3 gap-2">
                          <div>
                              <input
                                name={field+'operation'}
                                type="number"
                                value={field.split("-")[0]}
                                onChange={(e) => handleInputChange(i, actVal, String(e.currentTarget.value+"-"+field.split("-")[1]))}
                                // onInput={(e) => {
                                //   handleInputChange(i, actVal, String(e.currentTarget.value+"-"+field.split("-")[1]))
                                // }}
                                // onChange={(e)=>handleInputChange2()}
                                className="w-full bg-white border border-slate-300 rounded-lg px-4 py-3 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                              />
                          </div>
                          <label className="block text-sm font-semibold bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-700">{field.split("-")[1]}</label>
                          {/* <label className="block text-sm font-semibold text-slate-900">{field.split("-")[1]}</label> /}
                          {/* <label className="block text-sm font-semibold text-slate-900">{field}</label> /}
                          {/* <div className="bg-slate-50 border border-slate-200 rounded-lg px-4 py-3 text-slate-700"> /}
                          <div>
                              <input
                                name={field}
                                type="text"
                                value={actVal}
                                readOnly
                                // onChange={(e) => handleInputChange(i, e.target.value, field)}
                                // onChange={(e) => handleInputChange(i, e.currentTarget.value, field)}
                                // onChange={(e) => console.log(e.target.value)}
                                // onInput={(e) => console.log(e.currentTarget.value)}
                                // onBlur={(e) => console.log(e.currentTarget.value)}
                                // onFocus={(e) => console.log(e.currentTarget.value)}
                                // onLoad={(e) => console.log(e.currentTarget.value)}
                                className="w-full bg-white border border-slate-300 rounded-lg px-4 py-3 text-slate-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 font-medium"
                              />
                          </div>
                        </div>
                      )
                    
                    })} */}
                    
                  </div>
                </div>
              </div>
            </form>

            <div className="bg-slate-50 border-t border-slate-200 px-8 py-4 flex justify-end gap-3">
              <button
                onClick={closeModal}
                className="bg-slate-200 hover:bg-slate-300 text-slate-900 px-6 py-2 rounded-lg font-medium transition"
              >
                Cancel
              </button>
              <button
                type="submit"
                form="production_form"
                // onClick={handleSubmit}
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition"
              >
                Submit
              </button>
            </div>
          </Card>
        </div>
      )}
    </main>
  )
}
