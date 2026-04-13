import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Trash2, ExternalLink, Loader2, Search, Briefcase } from 'lucide-react'
import api from '../api'

const fetchApplications = async () => {
  const { data } = await api.get('/applications')
  return data
}

const CRM = () => {
  const queryClient = useQueryClient()

  const { data: applications, isLoading, isError } = useQuery({
    queryKey: ['applications'],
    queryFn: fetchApplications,
  })

  const deleteMutation = useMutation({
    mutationFn: (appId) => api.delete(`/applications/${appId}`),
    onSuccess: () => {
      queryClient.invalidateQueries(['applications'])
    }
  })

  const handleDelete = (appId) => {
    if(confirm('Are you sure you want to remove this job from your CRM?')) {
        deleteMutation.mutate(appId)
    }
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 slide-in-from-bottom-4">
       <div className="flex items-center justify-between border-b border-white/5 pb-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-glow mb-2 flex items-center">
              <Briefcase className="mr-3 text-primary w-8 h-8" />
              My Applications
            </h1>
            <p className="text-muted-foreground text-sm">Track and manage the jobs you've saved for future reference.</p>
          </div>
          <div className="text-sm font-medium px-4 py-2 bg-primary/10 text-primary border border-primary/20 rounded-lg">
             {applications?.length || 0} Saved
          </div>
       </div>

       {isLoading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
          </div>
       ) : isError ? (
          <div className="p-4 border border-destructive/30 bg-destructive/10 text-destructive rounded-lg flex items-center">
            Error loading your applications.
          </div>
       ) : !applications || applications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-32 text-center space-y-4 glass border-dashed rounded-2xl">
             <div className="w-20 h-20 rounded-full bg-white/5 flex items-center justify-center text-muted-foreground mb-2 shadow-inner">
               <Search className="w-10 h-10 opacity-40" />
             </div>
             <h3 className="text-2xl font-semibold text-glow">No saved applications</h3>
             <p className="text-muted-foreground text-sm max-w-sm">Save a job from the job board by clicking the heart icon to start tracking your applications here.</p>
          </div>
       ) : (
          <div className="glass rounded-xl overflow-hidden border border-white/10 shadow-2xl">
             <div className="overflow-x-auto">
               <table className="w-full text-sm text-left">
                  <thead className="text-xs text-muted-foreground uppercase bg-white/5 border-b border-white/10">
                     <tr>
                        <th className="px-6 py-5 font-semibold tracking-wider">Job Details</th>
                        <th className="px-6 py-5 font-semibold tracking-wider">Status</th>
                        <th className="px-6 py-5 font-semibold text-center tracking-wider">AI Score</th>
                        <th className="px-6 py-5 font-semibold text-right tracking-wider">Actions</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                     {applications.map((app) => (
                        <tr key={app.id} className="hover:bg-white/5 transition-colors group">
                           <td className="px-6 py-4">
                              <div className="font-semibold text-base mb-1 group-hover:text-primary transition-colors line-clamp-1">{app.job.title}</div>
                              <div className="text-muted-foreground text-xs flex items-center space-x-2">
                                <span className="uppercase tracking-wider font-medium text-[10px] bg-white/10 px-1.5 py-0.5 rounded text-white">{app.job.source}</span>
                                <span>{app.job.company}</span>
                              </div>
                           </td>
                           <td className="px-6 py-4">
                              <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-500/10 text-blue-400 border border-blue-500/20">
                                 {app.status || 'Saved'}
                              </span>
                           </td>
                           <td className="px-6 py-4">
                              <div className="flex justify-center">
                                <div className={`px-2 py-1 rounded font-bold text-xs ${app.job.attention_score > 80 ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'}`}>
                                  {app.job.attention_score || '-'}
                                </div>
                              </div>
                           </td>
                           <td className="px-6 py-4 text-right space-x-4">
                              <a 
                                href={app.job.apply_link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center text-muted-foreground hover:text-primary transition-colors"
                                title="Apply External"
                              >
                                 <span className="text-xs mr-1 opacity-0 group-hover:opacity-100 transition-opacity">Apply</span>
                                 <ExternalLink className="w-4 h-4" />
                              </a>
                              <button 
                                onClick={() => handleDelete(app.id)}
                                disabled={deleteMutation.isLoading}
                                className="inline-flex items-center text-muted-foreground hover:text-destructive transition-colors opacity-50 group-hover:opacity-100"
                                title="Remove Application"
                              >
                                 <Trash2 className="w-4 h-4" />
                              </button>
                           </td>
                        </tr>
                     ))}
                  </tbody>
               </table>
             </div>
          </div>
       )}
    </div>
  )
}

export default CRM
