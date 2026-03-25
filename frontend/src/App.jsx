import { useState } from 'react'
import SearchBar from './components/SearchBar'
import RepoCard from './components/RepoCard'
import LoadingSpinner from './components/LoadingSpinner'
import ErrorMessage from './components/ErrorMessage'

export default function App() {
  const [repoData, setRepoData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSearch(owner, repo) {
    setLoading(true)
    setError(null)
    setRepoData(null)

    try {
      const res = await fetch(`/api/repos/${owner}/${repo}`)
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Something went wrong')
      }
      const data = await res.json()
      setRepoData(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-3xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">
            GitHub Repo Analyzer
          </h1>
          <p className="text-gray-400">
            Enter any GitHub repository to see its stats
          </p>
        </div>
        <SearchBar onSearch={handleSearch} loading={loading} />
        <div className="mt-10">
          {loading && <LoadingSpinner />}
          {error && <ErrorMessage message={error} />}
          {repoData && <RepoCard data={repoData} />}
        </div>
      </div>
    </div>
  )
}