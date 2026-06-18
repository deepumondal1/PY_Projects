import { downloadBase64File } from "@/utils/fileDownload"

export async function GET() {
  try {
    // Replace this URL with your actual sample file URL
    // const sampleFileUrl = "http://127.0.0.1:5000/api/download_file"
    const sampleFileUrl = "/api/download_file"

    const response = await fetch(sampleFileUrl, { cache: 'no-store' })

    if (!response.ok) {
      throw new Error("Failed to fetch sample file")
    }
// console.log(await response.arrayBuffer())
    // const headers = response.headers
    // const fileBuffer = await response.arrayBuffer()
    // const blob = (await response.blob()).arrayBuffer();
    // const url = URL.createObjectURL(blob)
// console.log(blob) 
    // return new Response(fileBuffer, {
    //   headers: headers
    // //   headers: {
    // //     "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    // //     "Content-Disposition": `attachment; filename=${response.download_name ?? "sample_file.xlsx"}`,
    // //   },
    // })
    return response
    // const download = await response.json()
    // console.log(download)
    // downloadBase64File(download.file_content,download.filename,download.mimetype)
  } catch (error) {
    console.error("Sample file error:", error)
    return new Response("Sample file not available", { status: 500 })
  }
}
