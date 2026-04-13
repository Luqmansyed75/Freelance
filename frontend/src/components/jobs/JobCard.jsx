import { Heart, ExternalLink, Building, DollarSign } from 'lucide-react'
import { useState } from 'react'

const JobCard = ({ job, onSave, isSaved }) => {
  const [isSaving, setIsSaving] = useState(false)
  
  // attention_score is generally 0-100.
  const score = job.attention_score || 0
  const scoreColor = score > 80 ? 'text-green-400' : score > 50 ? 'text-yellow-400' : 'text-red-400'
  
  const handleSave = async () => {
    if (isSaving || isSaved) return;
    setIsSaving(true);
    await onSave(job.id);
    setIsSaving(false);
  }

  // Handle skills which might be a string or array depending on the backend response
  const skillsArray = Array.isArray(job.skills) 
    ? job.skills 
    : (typeof job.skills === 'string' ? JSON.parse(job.skills.replace(/'/g, '"') || "[]") : []);

  return (
    <div className="glass rounded-xl p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_8px_30px_rgba(80,40,250,0.2)] hover:border-primary/40 group flex flex-col justify-between h-full">
      
      <div>
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1 pr-4">
            <h3 className="font-semibold text-lg leading-tight mb-2 group-hover:text-glow transition-all line-clamp-2">{job.title}</h3>
            <div className="flex items-center text-sm text-muted-foreground space-x-2">
              <Building className="w-3.5 h-3.5" />
              <span className="truncate">{job.company}</span>
            </div>
          </div>
          
          <div className="flex flex-col items-center justify-center relative w-12 h-12 shrink-0">
             <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-white/10"
                stroke="currentColor"
                strokeWidth="3.8"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className={`${scoreColor} transition-all duration-1000 ease-out`}
                stroke="currentColor"
                strokeWidth="3.8"
                strokeDasharray={`${score}, 100`}
                strokeLinecap="round"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center text-[11px] font-bold leading-none">
              {score}
            </div>
          </div>
        </div>

        {/* Badges */}
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary border border-primary/20 uppercase tracking-wider">
            {job.source}
          </span>
          {(job.salary_min || job.salary_max) && (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-500/20 text-green-400 border border-green-500/20">
              <DollarSign className="w-3 h-3 mr-0.5" />
              {job.salary_min || 'N/A'} {job.salary_max ? `- ${job.salary_max}` : ''}
            </span>
          )}
        </div>

        {/* Skills */}
        {skillsArray && skillsArray.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {skillsArray.slice(0, 4).map((skill, idx) => (
              <span key={idx} className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-white/5 text-muted-foreground border border-white/10">
                {skill}
              </span>
            ))}
            {skillsArray.length > 4 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium bg-white/5 text-muted-foreground border border-white/10">
                +{skillsArray.length - 4}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center justify-between pt-4 border-t border-white/5 mt-auto">
        <a 
          href={job.apply_link} 
          target="_blank" 
          rel="noopener noreferrer"
          className="inline-flex items-center text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
        >
          <span>Apply External</span>
          <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
        </a>
        
        <button
          onClick={handleSave}
          disabled={isSaved || isSaving}
          title={isSaved ? "Saved to CRM" : "Save to CRM"}
          className={`p-2 rounded-full transition-all flex items-center justify-center ${isSaved ? 'text-rose-500 bg-rose-500/10' : 'text-muted-foreground hover:text-rose-400 hover:bg-rose-400/10'} disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          <Heart className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
        </button>
      </div>
    </div>
  )
}

export default JobCard
