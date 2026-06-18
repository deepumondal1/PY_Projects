"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"
import { Upload, Download, FileSpreadsheet, CheckCircle } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { downloadBase64File } from '../utils/fileDownload';
import { Checkbox } from "@/components/ui/checkbox"

export default function ExcelUploadPage() {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [isProcessing, setIsProcessing] = useState(false)
  const [isDragOver, setIsDragOver] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { toast } = useToast()

  interface IProcessLevel {
    level1: string | Boolean;
    level2: string | Boolean;
    level3: string | Boolean;
    level4: string | Boolean;
    level5: string | Boolean;
    level6: string | Boolean;
    level7: string | Boolean;
  }
  
  const [processingLevels, setProcessingLevels] = useState<IProcessLevel>({
    level1: true,
    level2: true,
    level3: true,
    level4: true,
    level5: true,
    level6: true,
    level7: true,
  })
  const [processingLevelsName, setProcessingLevelsName] = useState<IProcessLevel>({
    level1: "Tan Fully Match Diff <=100",
    level2: "Own Sheet TAN Matched",
    level3: "Single Entry Amount Match Diff <=1",
    level4: "Single Entry Amount Match Diff <=1 (Different Section Wise)",
    level5: "Group Amount Match Diff [<=1]",
    level6: "Group Amount Match Diff [<=50]",
    level7: "Multiple Entry Amount Match Diff [<=1] and [<=5] and [<=50]",
  })

  const validateAndSetFile = (file: File) => {
    const validTypes = ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel"]

    if (validTypes.includes(file.type)) {
      setUploadedFile(file)
      toast({
        title: "File uploaded successfully",
        description: `${file.name} is ready for processing.`,
      })
    } else {
      toast({
        title: "Invalid file type",
        description: "Please upload an Excel file (.xlsx or .xls)",
        variant: "destructive",
      })
      if (fileInputRef.current) {
        fileInputRef.current.value = ""
      }
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      validateAndSetFile(file)
    }
  }

  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragOver(true)
  }

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragOver(false)
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setIsDragOver(false)

    const files = event.dataTransfer.files
    if (files.length > 0) {
      validateAndSetFile(files[0])
    }
  }

  const handleClickUpload = () => {
    fileInputRef.current?.click()
  }

  const handleDownloadSample = async () => {
    try{
      const sampleFileUrl = "/api/download_file" // Replace with your actual sample file URL
      const response = await fetch(sampleFileUrl)
      if(!response.ok){
        throw new Error("Error on downloading sample file. Try again latter...")
      }
// console.log(response.body?.getReader())
      const download = await response.json()
      downloadBase64File(download.file_content,download.filename,download.mimetype)

      toast({
        title: "Sample file downloaded",
        description: download?.message ? download.message : "Use this template to format your data correctly.",
      })

    } catch (error) {
      console.error("Processing error:", error)
      toast({
        title: "Downloaded file failed",
        description: error instanceof Error ? error.message : "An unexpected error occurred during file processing.",
        variant: "destructive",
      })
    }

  }

  const toggleProcessingLevel = (level: keyof typeof processingLevels) => {
    setProcessingLevels((prev) => ({
      ...prev,
      [level]: !prev[level],
    }))
  }

  const handleSubmit = async () => {
    if (!uploadedFile) return

    setIsProcessing(true)
    setProgress(0)
    setProgressMessage("Starting file processing...")

    try {
      const formData = new FormData()
      formData.append("processingLevels", JSON.stringify(processingLevels))
      formData.append("file", uploadedFile)
// console.log(formData)
      const response = await fetch("/api/start_task", {
        method: "POST",
        body: formData,
      })
// console.log(response)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.statusText} - ${response.body} - ${response.url}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
// console.log(reader)
      if (reader) {
        let chunk= ''
        while (true) {
          const { done, value } = await reader.read()
// console.log( done, value)
          if (done) break

          chunk = chunk+decoder.decode(value)
          if(!chunk.includes("\n")) {
              continue
          }
          const lines = chunk.split("\n")
          chunk = ''
// console.log(chunk, lines)
          for (const line of lines) {
            if (line.includes("data")) {
              try {
                let data = JSON.parse(line)
                data=data.data
// console.log(data,data.progress)                
                if (data.progress) {
                  setProgress(data.progress)
                }

                if (data.message) {
                  setProgressMessage(data.message)
                }

                if (data.error) {
                  throw new Error(data.error)
                }

                if (data.download) {
                  const download = data.download
// console.log(download.file_content.length)
// console.log(download)
                  setProgressMessage(download.message)
                  downloadBase64File(download.file_content,download.filename,download.mimetype)
                }

                if (data.complete) {
                  setProgress(100)
                  setProgressMessage("Processing completed successfully!")

                  toast({
                    title: "File processed successfully",
                    description: `${uploadedFile.name} has been processed and data imported.`,
                  })

                  setTimeout(() => {
                    setUploadedFile(null)
                    setProgress(0)
                    setProgressMessage("")
                    if (fileInputRef.current) {
                      fileInputRef.current.value = ""
                    }
                  }, 1000)

                  break
                }
              } catch (parseError) {
                console.error("Error parsing SSE data:", parseError)
                  toast({
                    title: "File processed Failed",
                    description: `${parseError}`,
                    // variant: "destructive",
                  })
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Processing error:", error)

      toast({
        title: "Processing failed",
        description: error instanceof Error ? error.message : "An unexpected error occurred during file processing.",
        variant: "destructive",
      })

      setProgressMessage("Processing failed")
      setProgress(0)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleRemoveFile = () => {
    setUploadedFile(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
    toast({
      title: "File removed",
      description: "You can now download the sample template again.",
    })
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold text-foreground">Reconcilation TAN File</h1>
          <p className="text-muted-foreground">
            Download the sample template, fill it with your data, and upload it for processing
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileSpreadsheet className="h-5 w-5" />
              File Management
            </CardTitle>
            <CardDescription>Follow the steps below to process your Excel data</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-3">
              <Label className="text-sm font-medium">Step 1: Download Sample Template</Label>
              <Button
                onClick={handleDownloadSample}
                disabled={uploadedFile !== null}
                className="w-full"
                variant={uploadedFile ? "secondary" : "default"}
              >
                <Download className="h-4 w-4 mr-2" />
                {uploadedFile ? "Sample Downloaded" : "Download Sample Excel Template"}
              </Button>
              {uploadedFile && (
                <p className="text-xs text-muted-foreground">Sample template download is disabled after file upload</p>
              )}
            </div>

            <div className="space-y-3">
              <Label className="text-sm font-medium">Step 2: Upload Your Excel File</Label>
              <div className="space-y-2">
                <div
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={handleClickUpload}
                  className={`
                    relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                    ${
                      isDragOver
                        ? "border-primary bg-primary/5"
                        : "border-muted-foreground/25 hover:border-primary/50 hover:bg-muted/50"
                    }
                  `}
                >
                  <Input
                    ref={fileInputRef}
                    type="file"
                    accept=".xlsx,.xls"
                    onChange={handleFileUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div className="flex flex-col items-center gap-3">
                    <Upload className={`h-8 w-8 ${isDragOver ? "text-primary" : "text-muted-foreground"}`} />
                    <div className="space-y-1">
                      <p className="text-sm font-medium">
                        {isDragOver ? "Drop your Excel file here" : "Drag and drop your Excel file here"}
                      </p>
                      <p className="text-xs text-muted-foreground">or click to browse (.xlsx, .xls files only)</p>
                    </div>
                  </div>
                </div>

                {uploadedFile && (
                  <div className="flex items-center justify-between p-3 bg-muted rounded-md">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4 text-green-600" />
                      <span className="text-sm font-medium">{uploadedFile.name}</span>
                      <span className="text-xs text-muted-foreground">
                        ({(uploadedFile.size / 1024).toFixed(1)} KB)
                      </span>
                    </div>
                    <Button
                      onClick={handleRemoveFile}
                      variant="ghost"
                      size="sm"
                      className="text-destructive hover:text-destructive"
                    >
                      Remove
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {uploadedFile && (
              <div className="space-y-3">
                <Label className="text-sm font-medium">Step 3: Configure Processing Levels</Label>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(processingLevels).map(([level, enabled]) => (
                    <div
                      key={level}
                      className="flex items-center gap-3 p-3 border rounded-md hover:bg-muted/50 transition-colors"
                    >
                      <Checkbox
                        id={level}
                        checked={enabled}
                        onCheckedChange={() => toggleProcessingLevel(level as keyof typeof processingLevels)}
                      />
                      <Label htmlFor={level} className="flex-1 cursor-pointer font-medium">
                        <b>{`${level.charAt(0).toUpperCase() + level.slice(1)} `}</b>
                        {`${processingLevelsName[level as keyof IProcessLevel]}`}
                      </Label>
                      
                    </div>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                Check or uncheck to enable/disable processing levels. Disabled levels will be skipped during processing.
                </p>
              </div>
            )}

            <div className="space-y-3">
              <Label className="text-sm font-medium">
                {uploadedFile ? "Step 4: Process Data" : "Step 3: Process Data"}
              </Label>
              {isProcessing && (
                <div className="space-y-3 p-4 bg-muted/50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary border-t-transparent" />
                    <span className="text-sm font-medium">Processing file...</span>
                  </div>
                  <Progress value={progress} className="w-full" />
                  <p className="text-xs text-muted-foreground">{progressMessage}</p>
                </div>
              )}
              <Button onClick={handleSubmit} disabled={!uploadedFile || isProcessing} className="w-full" size="lg">
                <Upload className="h-4 w-4 mr-2" />
                {isProcessing ? "Processing..." : "Submit & Process File"}
              </Button>
              {!uploadedFile && (
                <p className="text-xs text-muted-foreground">Submit button is disabled until you upload a file</p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Instructions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            <p>• Download the sample template to see the expected format</p>
            <p>• Fill in your data following the same structure</p>
            <p>• Drag and drop your Excel file or click to browse (.xlsx or .xls)</p>
            <p>• Configure which processing levels to enable or disable</p>
            <p>• Click submit to process your data</p>
            <p>• The download button will be disabled after uploading a file</p>
            <p>• The submit button is only enabled when a file is uploaded</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
