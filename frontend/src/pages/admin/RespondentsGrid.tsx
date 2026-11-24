import React, { useState, useMemo } from "react"
import {
  Search,
  Download,
  Filter,
  Eye,
  FileSpreadsheet,
  X,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/Card"
import { Badge } from "@/components/ui/Badge"
import { Button } from "@/components/ui/Button"
import { Modal } from "@/components/ui/Modal"
import { EmptyState } from "@/components/ui/EmptyState"
import { mockRespondents, RespondentDemo } from "@/mock/demoData"

export const AdminRespondentsGrid: React.FC = () => {
  const [search, setSearch] = useState("")
  const [cityFilter, setCityFilter] = useState("ALL")
  const [sourceFilter, setSourceFilter] = useState("ALL")
  const [selectedRespondent, setSelectedRespondent] = useState<RespondentDemo | null>(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)

  // Filtered dataset
  const filteredData = useMemo(() => {
    return mockRespondents.filter((r) => {
      const matchSearch =
        search.trim() === "" ||
        r.name.toLowerCase().includes(search.toLowerCase()) ||
        r.member_id.toLowerCase().includes(search.toLowerCase()) ||
        r.city.toLowerCase().includes(search.toLowerCase()) ||
        r.phone.includes(search)

      const matchCity = cityFilter === "ALL" || r.city === cityFilter
      const matchSource = sourceFilter === "ALL" || r.source === sourceFilter

      return matchSearch && matchCity && matchSource
    })
  }, [search, cityFilter, sourceFilter])

  // Contextual CSV Export of the currently filtered dataset
  const handleExportCSV = () => {
    const headers = [
      "Member ID",
      "Full Name",
      "Phone",
      "Email",
      "Gender",
      "DOB",
      "City",
      "Income Range",
      "Interests",
      "Source",
      "Joined On",
    ]
    const rows = filteredData.map((r) => [
      r.member_id,
      r.name,
      r.phone,
      r.email,
      r.gender,
      r.date_of_birth,
      r.city,
      r.income_range,
      r.interests.join(";"),
      r.source,
      r.joined_on,
    ])

    const csvContent =
      "data:text/csv;charset=utf-8," +
      [headers.join(","), ...rows.map((e) => e.map((val) => `"${val}"`).join(","))].join("\n")

    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `viewbox_respondents_filtered_${new Date().toISOString().slice(0, 10)}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleOpenDetail = (r: RespondentDemo) => {
    setSelectedRespondent(r)
    setDetailModalOpen(true)
  }

  const cities = Array.from(new Set(mockRespondents.map((r) => r.city)))
  const sources = Array.from(new Set(mockRespondents.map((r) => r.source)))

  return (
    <div className="space-y-6">
      {/* Title & Export Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            Respondent Directory
          </h2>
          <p className="text-xs text-slate-500">
            Searchable, filterable registry of registered consumer panelists with dynamic demographic metadata.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={handleExportCSV}>
            <Download className="mr-1.5 h-3.5 w-3.5" />
            Export CSV ({filteredData.length})
          </Button>
          <Button size="sm" variant="brand" onClick={handleExportCSV}>
            <FileSpreadsheet className="mr-1.5 h-3.5 w-3.5" />
            Export Excel (.xlsx)
          </Button>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <Card className="border-slate-200 shadow-2xs">
        <CardContent className="p-4 flex flex-wrap items-center justify-between gap-3">
          {/* Debounced Instant Search */}
          <div className="relative flex-1 min-w-[240px] max-w-md">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by name, member ID (e.g. VB10073), city, or phone..."
              className="w-full pl-9 pr-8 py-1.5 text-xs rounded-md border border-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500 bg-white"
            />
            {search && (
              <button
                onClick={() => setSearch("")}
                className="absolute right-2.5 top-2 text-slate-400 hover:text-slate-600"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          {/* Filter Selectors */}
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-1.5 text-xs text-slate-500">
              <Filter className="h-3.5 w-3.5" />
              <span>Filters:</span>
            </div>

            <select
              value={cityFilter}
              onChange={(e) => setCityFilter(e.target.value)}
              className="text-xs border border-slate-200 rounded-md py-1.5 px-2 bg-white text-slate-700 focus:ring-1 focus:ring-brand-500"
            >
              <option value="ALL">All Cities ({cities.length})</option>
              {cities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="text-xs border border-slate-200 rounded-md py-1.5 px-2 bg-white text-slate-700 focus:ring-1 focus:ring-brand-500"
            >
              <option value="ALL">All Sources ({sources.length})</option>
              {sources.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>

            {(search || cityFilter !== "ALL" || sourceFilter !== "ALL") && (
              <button
                onClick={() => {
                  setSearch("")
                  setCityFilter("ALL")
                  setSourceFilter("ALL")
                }}
                className="text-xs text-brand-600 hover:underline font-semibold"
              >
                Reset
              </button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Data Table or Empty State */}
      {filteredData.length === 0 ? (
        <EmptyState
          title="No respondents match filters"
          description="Try broadening your search term or clearing the city and acquisition source filters."
          actionLabel="Clear Filters"
          onAction={() => {
            setSearch("")
            setCityFilter("ALL")
            setSourceFilter("ALL")
          }}
        />
      ) : (
        <Card className="border-slate-200 shadow-xs overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-500 uppercase tracking-wider text-[10px] font-bold">
                <tr>
                  <th className="py-3 px-4">Member ID</th>
                  <th className="py-3 px-4">Full Name</th>
                  <th className="py-3 px-4">Phone & City</th>
                  <th className="py-3 px-4">Gender & DOB</th>
                  <th className="py-3 px-4">Income Bracket</th>
                  <th className="py-3 px-4">Acquisition Source</th>
                  <th className="py-3 px-4">Joined Date</th>
                  <th className="py-3 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white">
                {filteredData.map((row) => (
                  <tr
                    key={row.id}
                    onClick={() => handleOpenDetail(row)}
                    className="hover:bg-slate-50/70 transition-colors cursor-pointer"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-brand-700">
                      {row.member_id}
                    </td>
                    <td className="py-3 px-4">
                      <p className="font-semibold text-slate-900">{row.name}</p>
                      <p className="text-[10px] text-slate-400">{row.email}</p>
                    </td>
                    <td className="py-3 px-4">
                      <p className="text-slate-800 font-medium">+91 {row.phone}</p>
                      <p className="text-[10px] text-slate-500">{row.city}</p>
                    </td>
                    <td className="py-3 px-4 text-slate-600">
                      <p>{row.gender}</p>
                      <p className="text-[10px] text-slate-400">{row.date_of_birth}</p>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-medium text-slate-700">
                        {row.income_range}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-[11px] bg-slate-100 text-slate-700 px-2 py-0.5 rounded-full font-medium">
                        {row.source}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">{row.joined_on}</td>
                    <td className="py-3 px-4 text-right">
                      <button className="text-brand-600 hover:text-brand-800 p-1 rounded hover:bg-brand-50">
                        <Eye className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-3 bg-slate-50/50 border-t border-slate-100 text-xs text-slate-500 flex items-center justify-between">
            <span>
              Showing <strong>{filteredData.length}</strong> of{" "}
              <strong>{mockRespondents.length}</strong> respondents
            </span>
            <span className="text-[11px] text-slate-400">Page 1 of 1</span>
          </div>
        </Card>
      )}

      {/* Respondent Detail Modal */}
      {selectedRespondent && (
        <Modal
          isOpen={detailModalOpen}
          onClose={() => setDetailModalOpen(false)}
          title={`Respondent Profile: ${selectedRespondent.name}`}
          description={`Member ID: ${selectedRespondent.member_id}`}
          footer={
            <Button size="sm" variant="outline" onClick={() => setDetailModalOpen(false)}>
              Close Drawer
            </Button>
          }
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
              <div>
                <span className="text-slate-400 text-[10px]">Phone Number:</span>
                <p className="font-semibold text-slate-900">+91 {selectedRespondent.phone}</p>
              </div>
              <div>
                <span className="text-slate-400 text-[10px]">Email Address:</span>
                <p className="font-semibold text-slate-900">{selectedRespondent.email}</p>
              </div>
              <div>
                <span className="text-slate-400 text-[10px]">City:</span>
                <p className="font-semibold text-slate-900">{selectedRespondent.city}</p>
              </div>
              <div>
                <span className="text-slate-400 text-[10px]">Date of Birth:</span>
                <p className="font-semibold text-slate-900">{selectedRespondent.date_of_birth}</p>
              </div>
            </div>

            <div>
              <span className="text-slate-500 text-[11px] font-semibold block mb-1.5">
                Stated Category Interests:
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedRespondent.interests.map((int) => (
                  <Badge key={int} variant="secondary" className="text-[10px]">
                    {int}
                  </Badge>
                ))}
              </div>
            </div>

            <div className="border-t border-slate-100 pt-3">
              <span className="text-slate-500 text-[11px] font-semibold block mb-1">
                Acquisition Attribution:
              </span>
              <p className="text-slate-700">
                Channel: <strong>{selectedRespondent.source}</strong>
                {selectedRespondent.referred_by && (
                  <span className="ml-2 text-brand-600 font-mono">
                    (Referred by {selectedRespondent.referred_by})
                  </span>
                )}
              </p>
            </div>
          </div>
        </Modal>
      )}
    </div>
  )
}
