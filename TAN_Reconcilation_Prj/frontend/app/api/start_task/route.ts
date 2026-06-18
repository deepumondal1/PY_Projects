import type { NextRequest } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("file") as File
    const processingLevelsStr = formData.get("processingLevels") as string
    const processingLevels = processingLevelsStr ? JSON.parse(processingLevelsStr) : {}

    if (!file) {
      return new Response("No file uploaded", { status: 400 })
    }

    // const externalApiUrl = process.env.EXTERNAL_PROCESSING_API_URL || "http://127.0.0.1:5000/start_task"
    const externalApiUrl = "/api/start_task"

    // Create FormData for external API
    const externalFormData = new FormData()
    externalFormData.append("file", file)
    externalFormData.append("processingLevels", JSON.stringify(processingLevels))

    const response = await fetch(externalApiUrl, {
        method: "POST",
        body: externalFormData,
        headers: {
            // Add any required headers for your external API
            // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
        },
    })
//   console.log(response)
    if (!response.ok) {
        throw new Error(`External API error: ${response.status} ${response.statusText}`)
    }
    const stream = response.body
// console.log(response)
    

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    })
  } catch (error) {
    console.error("API Error:", error)
    return new Response("Internal server error", { status: 500 })
  }
}
