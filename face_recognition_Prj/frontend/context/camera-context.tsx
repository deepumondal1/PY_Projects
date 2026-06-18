"use client"

import type React from "react"

import { createContext, useContext, useState, useRef, useEffect, type ReactNode } from "react"
import { useToast } from "@/hooks/use-toast"
import { Label } from "@/components/ui/label"

const HOST = "http://127.0.0.1:8080"

interface CameraContextType {
  isActive: boolean
  hasPermission: boolean | null
  nCamera: number | null
  //   videoRef: React.RefObject<HTMLVideoElement>
  //   imgRef: React.RefObject<HTMLImageElement | null>
  imgSrc: string | undefined
  imgRef: React.RefObject<string | undefined>
  startCamera: () => Promise<void>
  stopCamera: () => Promise<void>
}

const CameraContext = createContext<CameraContextType | undefined>(undefined)

export function CameraProvider({ children }: { children: ReactNode }) {
//   const videoRef = useRef<HTMLVideoElement | null>(null)
  const [isActive, setIsActive] = useState(false)
  const [hasPermission, setHasPermission] = useState<boolean | null>(null)
  //   const streamRef = useRef<MediaStream | null>(null)
  const { toast } = useToast()
  const reader = useRef<ReadableStreamDefaultReader<Uint8Array<ArrayBuffer>> | undefined>(undefined)
  
  const [imgSrc, setImgSrc] = useState<string | undefined>(undefined)
  const [nCamera, setNCamera] = useState<number | null>(null)
  const imgRef = useRef<string | undefined>(undefined)

  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  const startCamera = async () => {
    try {
      if (isActive) return

      let url = `${HOST}/api/live_camera_feed`
      const resp = await fetch(url)
      if(!resp.ok){
        throw Error("Invalid Response Generated")
      }
      reader.current = await resp.body?.getReader()
      const textDecoder = new TextDecoder()
      let chunk = ''
      let img_array = []
      try{
        if(reader.current){
            
            setIsActive(true)
            setHasPermission(true)
            while(true){
                const {done, value} = await reader.current.read()
                if(done){
                console.log('job done')
                setIsActive(false)
                setHasPermission(false)
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
                        //   setTestPhotoData(data.base64img)
                        // console.log(data.base64img)
                        if (data.isMatched){
                            // console.log(data.base64img)
                            toast({
                                title: "Testing Capture Image",
                                description: <>
                                <br/>
                                <div>
                                  <Label>MATCH FOUND!</Label>
                                  <Label>{`EMPLOYEE: [${data.emp_id}] ${data.emp_name}`}</Label>
                                  <img src={data.base64img_face} alt="Found Image"/>
                                </div>
                                </>,
                                variant:'success'
                            }) 
                        }else{
                          // imgRef.current = data.base64img
                          img_array.push(data.base64img)
                          setImgSrc(data.base64img)
                        }
                      } catch (parseError) {
                      // console.error("Error parsing SSE data:", parseError)
                      }
                      
                  }
                }
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

    //   const stream = await navigator.mediaDevices.getUserMedia({
    //     video: { facingMode: "user" },
    //   })
    //   if (videoRef.current) {
    //     videoRef.current.srcObject = stream
    //     streamRef.current = stream
    //     setIsActive(true)
    //     setHasPermission(true)
    //   }
    } catch (error) {
      console.error("Camera error:", error)
      setHasPermission(false)
      alert("Unable to access camera. Please check permissions.")
    
    }finally{
      reader.current = undefined
    }

  }

  const stopCamera = async () => {
    try{
      if(reader.current){
          await reader.current.cancel()
      }
    }catch(e){
      console.log(e)
    }finally{
      reader.current = undefined
    }
    // if (streamRef.current) {
    //   streamRef.current.getTracks().forEach((track) => track.stop())
    //   streamRef.current = null
    //   setIsActive(false)
    // }
  }

  return (
    // <CameraContext.Provider value={{ isActive, hasPermission, videoRef, startCamera, stopCamera }}>
    <CameraContext.Provider value={{ isActive, hasPermission, nCamera, imgSrc, imgRef, startCamera, stopCamera }}>
      {children}
    </CameraContext.Provider>
  )
}

export function useCamera() {
  const context = useContext(CameraContext)
  if (!context) {
    throw new Error("useCamera must be used within CameraProvider")
  }
  return context
}
