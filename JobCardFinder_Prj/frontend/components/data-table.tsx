"use client"

import { useState, useMemo } from "react"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { ChevronDown, X, Download, RefreshCw, Eye } from "lucide-react"

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

type FilterType = "equals" | "startsWith" | "contains" | "endsWith" | "isEmpty" | "isNotEmpty"

interface ColumnFilter {
  value: string
  type: FilterType
}

interface Filters {
  [key: string]: ColumnFilter
}

const FILTER_TYPES: { value: FilterType; label: string }[] = [
  { value: "equals", label: "Equals" },
  { value: "startsWith", label: "Starts With" },
  { value: "contains", label: "Contains" },
  { value: "endsWith", label: "Ends With" },
  { value: "isEmpty", label: "Is Empty" },
  { value: "isNotEmpty", label: "Is Not Empty" },
]

const COLUMNS1 = [
  { key: "jobId", label: "Job ID" },
  { key: "jobTitle", label: "Job Title" },
  { key: "company", label: "Company" },
  { key: "location", label: "Location" },
  { key: "salary", label: "Salary" },
  { key: "status", label: "Status" },
  { key: "datePosted", label: "Date Posted" },
]

export default function DataTable({ data, columns, refreshCB, onRowView }: { data: {string:object}[], columns: string[], refreshCB: () => void, onRowView: (row: {string:object}) => void }) {
  const [filters, setFilters] = useState<Filters>({})
  const [expandedFilters, setExpandedFilters] = useState<Set<string>>(new Set())

  const toggleFilterExpand = (column: string) => {
    const newExpanded = new Set(expandedFilters)
    if (newExpanded.has(column)) {
      newExpanded.delete(column)
    } else {
      newExpanded.add(column)
    }
    setExpandedFilters(newExpanded)
  }

  const applyFilter = (value: string, filterType: FilterType): boolean => {
    if (!value) return true

    switch (filterType) {
      case "equals":
        return value.toLowerCase() === value.toLowerCase()
      case "startsWith":
        return value.toLowerCase().startsWith(value.toLowerCase())
      case "contains":
        return value.toLowerCase().includes(value.toLowerCase())
      case "endsWith":
        return value.toLowerCase().endsWith(value.toLowerCase())
      case "isEmpty":
        return value.trim() === ""
      case "isNotEmpty":
        return value.trim() !== ""
      default:
        return true
    }
  }

  const filteredData = useMemo(() => {
    return data.filter((row) => {
      return Object.entries(filters).every(([columnKey, filter]) => {
        if (!filter.value && filter.type !== "isEmpty") return true

        const cellValue = String(row[columnKey as keyof typeof data[0]] || "")

        switch (filter.type) {
          case "equals":
            return cellValue.toLowerCase() === filter.value.toLowerCase()
          case "startsWith":
            return cellValue.toLowerCase().startsWith(filter.value.toLowerCase())
          case "contains":
            return cellValue.toLowerCase().includes(filter.value.toLowerCase())
          case "endsWith":
            return cellValue.toLowerCase().endsWith(filter.value.toLowerCase())
          case "isEmpty":
            return cellValue.trim() === ""
          case "isNotEmpty":
            return cellValue.trim() !== ""
          default:
            return true
        }
      })
    })
  }, [data, filters])

  const updateFilter = (column: string, value: string, type: FilterType) => {
    setFilters((prev) => ({
      ...prev,
      [column]: { value, type },
    }))
  }

  const clearFilters = () => {
    setFilters({})
  }

  const removeFilter = (column: string) => {
    setFilters((prev) => {
      const newFilters = { ...prev }
      delete newFilters[column]
      return newFilters
    })
  }

  const refreshTable = () => {
    // Refresh function - can be implemented later
    refreshCB()
  }

  const exportToExcel = () => {
    if (filteredData.length === 0) {
      alert("No data to export")
      return
    }

    // Create CSV content
    const headers = columns.map((col) => col).join(",")
    const rows = filteredData.map((row) =>
      columns.map((col) => {
        const value = String(row[col as keyof typeof data[0]] || "")
        // Escape quotes and wrap in quotes if contains comma
        return value.includes(",") ? `"${value.replace(/"/g, '""')}"` : value
      }).join(","),
    )

    const csvContent = [headers, ...rows].join("\n")

    // Create blob and download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
    const link = document.createElement("a")
    const url = URL.createObjectURL(blob)

    link.setAttribute("href", url)
    link.setAttribute("download", `job-cards-${new Date().toISOString().split("T")[0]}.csv`)
    link.style.visibility = "hidden"

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="space-y-6">
      {/* Filter Controls */}
      <Card className="bg-white border border-slate-200 p-6 shadow-md">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-slate-900">Filters</h3>
          {Object.keys(filters).length > 0 && (
            <button onClick={clearFilters} className="text-sm font-medium text-blue-600 hover:text-blue-700 transition">
              Clear All
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {columns.map((column) => (
            <div key={column} className="space-y-2">
              <button
                onClick={() => toggleFilterExpand(column)}
                className="w-full flex items-center justify-between bg-slate-100 hover:bg-slate-200 text-slate-900 px-3 py-2 rounded-lg transition text-sm font-medium"
              >
                <span>{column}</span>
                <ChevronDown
                  className={`w-4 h-4 transition-transform text-slate-600 ${
                    expandedFilters.has(column) ? "rotate-180" : ""
                  }`}
                />
              </button>

              {expandedFilters.has(column) && (
                <div className="space-y-2 bg-slate-50 p-3 rounded-lg border border-slate-200">
                  <select
                    value={filters[column]?.type || "contains"}
                    onChange={(e) =>
                      updateFilter(column, filters[column]?.value || "", e.target.value as FilterType)
                    }
                    className="w-full bg-white text-slate-900 text-sm px-3 py-2 rounded border border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {FILTER_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>

                  {filters[column]?.type !== "isEmpty" && (
                    <Input
                      type="text"
                      placeholder={`Filter by ${column.toLowerCase()}...`}
                      value={filters[column]?.value || ""}
                      onChange={(e) =>
                        updateFilter(column, e.target.value, filters[column]?.type || "contains")
                      }
                      className="bg-white border-slate-300 text-slate-900 placeholder:text-slate-400 text-sm focus:ring-blue-500"
                    />
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Active Filters Display */}
      {Object.keys(filters).length > 0 && (
        <div className="flex flex-wrap gap-2">
          {Object.entries(filters).map(([columnKey, filter]) => {
            const column = columns.find((c) => c === columnKey)
            return (
              <div
                key={columnKey}
                className="inline-flex items-center gap-2 bg-blue-100 text-blue-900 px-3 py-1 rounded-full text-sm font-medium"
              >
                <span>
                  {column}: {filter.type} {filter.value && `"${filter.value}"`}
                </span>
                <button onClick={() => removeFilter(columnKey)} className="hover:text-blue-700 transition">
                  <X className="w-4 h-4" />
                </button>
              </div>
            )
          })}
        </div>
      )}

      {/* Results Count and Action Buttons */}
      <div className="flex items-center justify-between">
        <div className="text-sm font-medium text-slate-700">
          Showing <span className="text-blue-600 font-semibold">{filteredData.length}</span> of{" "}
          <span className="text-blue-600 font-semibold">{data.length}</span> results
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={refreshTable}
            className="flex items-center gap-2 bg-slate-600 hover:bg-slate-700 text-white px-4 py-2 rounded-lg font-medium transition text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
          <button
            onClick={exportToExcel}
            disabled={filteredData.length === 0}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg font-medium transition text-sm"
          >
            <Download className="w-4 h-4" />
            Export to CSV
          </button>
        </div>
      </div>

      {/* Data Table */}
      <Card className="bg-white border border-slate-200 overflow-hidden shadow-md">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-slate-100 to-slate-50 border-b border-slate-200">
                <th className="px-6 py-4 text-left text-sm font-semibold text-slate-900">
                  Actions
                </th>
                {columns.map((column) => (
                  <th key={column} className="px-6 py-4 text-left text-sm font-semibold text-slate-900">
                    {column}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredData.length > 0 ? (
                filteredData.map((row, idx) => (
                  <tr
                    key={idx}
                    className={`border-b border-slate-200 hover:bg-blue-50 transition ${
                      idx % 2 === 0 ? "bg-white" : "bg-slate-50"
                    }`}
                  >
                    {/* view button */}
                    <td className="px-6 py-4 text-sm">
                      <button
                        onClick={() => onRowView(row)}
                        className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg font-medium transition text-sm"
                      >
                        <Eye className="w-4 h-4" />
                        View
                      </button>
                    </td>
                    {/* datatable in td */}
                    {columns.map((column) => (
                      <td key={`${row}-${column}`} className="px-6 py-4 text-sm text-slate-700">
                        <div className="flex items-center gap-2">
                          {/* {column === "status" && (
                            <span
                              className={`inline-block w-2 h-2 rounded-full ${
                                row.status === "Active" ? "bg-green-500" : "bg-red-500"
                              }`}
                            />
                          )} */}
                          <span className={column === "jobId" ? "font-medium text-slate-900" : ""}>
                            {String(row[column as keyof typeof data[0]])}
                          </span>
                        </div>
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={columns.length} className="px-6 py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-2">
                      <p className="font-medium">No results found</p>
                      <p className="text-sm">Try adjusting your filters</p>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
      
    </div>
  )
}
