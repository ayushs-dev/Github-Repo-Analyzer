export default function ContributorList({ contributors }) {
  return (
    <div className="space-y-3">
      {contributors.map((c) => (
        <a
          key={c.login}
          href={c.html_url}
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-3 p-3 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors"
        >
          <img
            src={c.avatar_url}
            alt={c.login}
            className="w-10 h-10 rounded-full"
          />
          <div className="flex-1">
            <div className="font-medium">{c.login}</div>
            <div className="text-gray-400 text-sm">
              {c.contributions.toLocaleString()} contributions
            </div>
          </div>
          <div className="text-gray-500 text-sm">↗</div>
        </a>
      ))}
    </div>
  )
}