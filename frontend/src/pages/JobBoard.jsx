import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, SlidersHorizontal, Loader2 } from 'lucide-react'
import api from '../api'
import JobCard from '../components/jobs/JobCard'
import useAuthStore from '../store/useAuthStore'

const fetchJobs = async ({ queryKey }) => {
  const [_key, { page, source, skills, attention_score }] = queryKey
  const params = new URLSearchParams()
  params.append('page', page)
  params.append('per_page', 20)
  if (source) params.append('source', source)
  if (skills) params.append('skills', skills)
  if (attention_score) params.append('attention_score', attention_score)
  
  const { data } = await api.get(`/jobs?${params.toString()}`)
  return data
}

const JobBoard = () => {
  const [page, setPage] = useState(1)
  const [sourceFilter, setSourceFilter] = useState('')
  const [skillsFilter, setSkillsFilter] = useState('')
  const [scoreFilter, setScoreFilter] = useState(0)
  
  const { isAuthenticated } = useAuthStore()
  const queryClient = useQueryClient()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['jobs', { page, source: sourceFilter, skills: skillsFilter, attention_score: scoreFilter > 0 ? scoreFilter : undefined }],
    queryFn: fetchJobs,
    keepPreviousData: true,
  })

  const saveApplicationMutation = useMutation({
    mutationFn: (job_id) => api.post('/applications', { job_id }),
    onSuccess: () => {
      queryClient.invalidateQueries(['applications'])
    }
  })

  const handleSaveJob = async (jobId) => {
    if (!isAuthenticated) {
      alert("Please login to save jobs to your CRM.")
      return
    }
    try {
       await saveApplicationMutation.mutateAsync(jobId)
       // Could toast success here
    } catch (e) {
      if(e.response?.status === 400 && e.response?.data?.detail.includes('already exists')) {
          alert('Job is already in your CRM!');
      } else {
          console.error(e)
          alert('Failed to save job.')
      }
    }
  }

  return (
    <div className="flex flex-col lg:flex-row gap-8">
      {/* Sidebar Filters */}
      <aside className="w-full lg:w-64 shrink-0 space-y-6">
        <div className="glass-panel p-5 rounded-2xl sticky top-24">
          <div className="flex items-center space-x-2 mb-6 text-glow">
            <SlidersHorizontal className="w-5 h-5 text-primary" />
            <h2 className="font-semibold text-lg">Filters</h2>
          </div>
          
          <div className="space-y-6">
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Skills (comma separated)</label>
              <div className="relative">
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="e.g. react, python"
                  value={skillsFilter}
                  onChange={(e) => { setSkillsFilter(e.target.value); setPage(1); }}
                  className="flex h-10 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 pl-9 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary backdrop-blur-md transition-all placeholder:text-white/30"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Source</label>
              <select
                value={sourceFilter}
                onChange={(e) => { setSourceFilter(e.target.value); setPage(1); }}
                className="flex h-10 w-full rounded-lg border border-white/10 bg-black/20 px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary appearance-none"
              >
                <option value="" className="bg-background">All Sources</option>
                <option value="wwr" className="bg-background">We Work Remotely</option>
                <option value="working nomads" className="bg-background">Working Nomads</option>
              </select>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-medium flex justify-between text-muted-foreground">
                <span>Min. Attention Score</span>
                <span className="text-primary font-bold">{scoreFilter}</span>
              </label>
              <input
                type="range"
                min="0"
                max="100"
                step="5"
                value={scoreFilter}
                onChange={(e) => { setScoreFilter(Number(e.target.value)); setPage(1); }}
                className="w-full accent-primary"
              />
            </div>
            
            <button
               onClick={() => {
                 setSkillsFilter('');
                 setSourceFilter('');
                 setScoreFilter(0);
                 setPage(1);
               }}
               className="w-full mt-4 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </aside>

      {/* Main Feed */}
      <section className="flex-1">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold tracking-tight text-glow">Job Feed</h1>
          <div className="text-sm text-muted-foreground px-3 py-1 rounded-full bg-white/5 border border-white/10">
             {data?.total ? `${data.total} jobs found` : '---'}
          </div>
        </div>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-20 space-y-4">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
            <p className="text-muted-foreground animate-pulse">Loading matches...</p>
          </div>
        ) : isError ? (
          <div className="p-4 border border-destructive/30 bg-destructive/10 text-destructive rounded-lg flex items-center">
            <div className="w-2 h-2 rounded-full bg-destructive animate-ping mr-3"></div>
            Error loading jobs. Please check if the backend is running at http://127.0.0.1:8000.
          </div>
        ) : data?.jobs?.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center space-y-3 glass border-dashed">
             <div className="w-16 h-16 rounded-full flex items-center justify-center text-muted-foreground mb-2">
               <Search className="w-8 h-8 opacity-50" />
             </div>
             <h3 className="text-xl font-medium">No jobs found</h3>
             <p className="text-muted-foreground text-sm max-w-sm">Try adjusting your filters, selecting a different source, or lowering the attention score threshold.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 gap-6">
              {(data?.jobs || []).map(job => (
                <JobCard key={job.id} job={job} onSave={handleSaveJob} isSaved={false} />
              ))}
            </div>
            
            {/* Pagination Controls */}
            <div className="mt-10 mb-8 flex items-center justify-center space-x-4">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 disabled:opacity-50 disabled:hover:bg-white/5 transition-colors font-medium text-sm"
              >
                Previous
              </button>
              <div className="px-4 py-2 rounded-lg bg-primary/10 border border-primary/20 text-primary font-bold text-sm">
                Page {page}
              </div>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={!data?.jobs || data.jobs.length < 20}
                className="px-4 py-2 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 disabled:opacity-50 disabled:hover:bg-white/5 transition-colors font-medium text-sm"
              >
                Next
              </button>
            </div>
          </>
        )}
      </section>
    </div>
  )
}

export default JobBoard
