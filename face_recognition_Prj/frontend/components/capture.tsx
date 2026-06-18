"use client"

import { useState, useRef, useEffect } from "react"
import { Play, Square } from "lucide-react"
import { useCamera } from "@/context/camera-context"

export default function Capture() {
  const [submitting, setSubmitting] = useState(false)

  const {
    isActive,
    hasPermission,
    nCamera,
    imgSrc,
    imgRef,
    startCamera,
    stopCamera,
  } = useCamera()

  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  const handleStartCamera = async () => {
    try {
      setSubmitting(true)
      await startCamera()
    } catch (error) {
      console.error("Camera error:", error)
      alert("Unable to access camera. Please check permissions.")
    } finally{
      setSubmitting(false)
    }
  }

  const handleStopCamera = async () => {
    await stopCamera()
  }

  return (
    <div className="p-8">
      <h2 className="text-3xl font-bold text-slate-800 mb-8">Live Camera Feed</h2>

      <div className="max-w-2xl mx-auto">
        <div className="bg-slate-900 rounded-lg shadow-lg overflow-hidden">
          {/* <video ref={videoRef} autoPlay playsInline className="w-full bg-slate-900" style={{ minHeight: "500px" }} /> */}
          <img src={imgSrc} alt="Capture"/>
        </div>

        <div className="mt-8 flex justify-center">
          {!isActive ? (
            <button
              onClick={handleStartCamera}
              disabled={submitting}
              className="bg-green-500 text-white px-8 py-4 rounded-lg hover:bg-green-600 transition-colors flex items-center gap-3 font-semibold text-lg"
            >
              <Play size={24} /> Start Camera
            </button>
          ) : (
            <button
              onClick={handleStopCamera}
              className="bg-red-500 text-white px-8 py-4 rounded-lg hover:bg-red-600 transition-colors flex items-center gap-3 font-semibold text-lg"
            >
              <Square size={24} /> Stop Camera
            </button>
          )}
        </div>

        {hasPermission === false && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            <p className="font-semibold">Camera Access Denied</p>
            <p className="text-sm mt-1">
              Please enable camera permissions in your browser settings to use this feature.
            </p>
          </div>
        )}

        <div className="mt-8 p-6 bg-slate-100 rounded-lg">
          <h3 className="font-semibold text-slate-800 mb-4">Instructions</h3>
          <ul className="space-y-2 text-slate-700 text-sm">
            <li className="flex gap-2">
              <span className="font-bold">1.</span> Click "Start Camera" to begin the live feed
            </li>
            <li className="flex gap-2">
              <span className="font-bold">2.</span> The camera will display your live video stream
            </li>
            <li className="flex gap-2">
              <span className="font-bold">3.</span> Click "Stop Camera" to end the feed
            </li>
            <li className="flex gap-2">
              <span className="font-bold">4.</span> Use this for attendance verification and monitoring
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}
