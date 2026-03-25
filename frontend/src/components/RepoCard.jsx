import ContributorList from './ContributorList'
import LanguageBar from './LanguageBar'

export default function RepoCard({ data }) {
  const { repo, top_contributors, languages } = data

  return (
    <div className="space-y-6">
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex items-start justify-between mb-3">
          <h2 className="text-2xl font-bold text-blue-400">{repo.full_name}</h2>
          {repo.language && (
            <span className="bg-gray-800 text-gray-300 text-sm px-3 py-1 rounded-full">
              {repo.language}
            </span>
          )}
        </div>
        {repo.description && (
          <p className="text-gray-400 mb-5">{repo.description}</p>
        )}
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <StatBox label="Stars" value={repo.stars.toLocaleString()} emoji="⭐" />
          <StatBox label="Forks" value={repo.forks.toLocaleString()} emoji="🍴" />
          <StatBox label="Issues" value={repo.open_issues.toLocaleString()} emoji="🐛" />
          <StatBox label="Watchers" value={repo.watchers.toLocaleString()} emoji="👁️" />
        </div>
      </div>

      {Object.keys(languages).length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Languages</h3>
          <LanguageBar languages={languages} />
        </div>
      )}

      {top_contributors.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Top Contributors</h3>
          <ContributorList contributors={top_contributors} />
        </div>
      )}
    </div>
  )
}

function StatBox({ label, value, emoji }) {
  return (
    <div className="bg-gray-800 rounded-lg p-3 text-center">
      <div className="text-xl mb-1">{emoji}</div>
      <div className="text-xl font-bold">{value}</div>
      <div className="text-gray-400 text-sm">{label}</div>
    </div>
  )
}