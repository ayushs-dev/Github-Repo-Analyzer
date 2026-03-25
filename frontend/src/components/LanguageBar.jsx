const COLORS = [
  'bg-blue-500', 'bg-yellow-500', 'bg-green-500',
  'bg-red-500', 'bg-purple-500', 'bg-pink-500',
  'bg-orange-500', 'bg-teal-500',
]

export default function LanguageBar({ languages }) {
  const total = Object.values(languages).reduce((a, b) => a + b, 0)
  const entries = Object.entries(languages)

  return (
    <div className="space-y-3">
      <div className="flex rounded-full overflow-hidden h-3">
        {entries.map(([lang, bytes], i) => (
          <div
            key={lang}
            className={COLORS[i % COLORS.length]}
            style={{ width: `${(bytes / total) * 100}%` }}
          />
        ))}
      </div>
      <div className="flex flex-wrap gap-3">
        {entries.map(([lang, bytes], i) => (
          <div key={lang} className="flex items-center gap-1.5">
            <div className={`w-3 h-3 rounded-full ${COLORS[i % COLORS.length]}`} />
            <span className="text-sm text-gray-300">{lang}</span>
            <span className="text-sm text-gray-500">
              {((bytes / total) * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}