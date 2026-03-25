import { useState } from 'react'

export default function SearchBar({ onSearch, loading }) {
  const [input, setInput] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const parts = input.trim().split('/')
    if (parts.length !== 2 || !parts[0] || !parts[1]) {
      alert('Please enter in format: owner/repo (e.g. facebook/react)')
      return
    }
    onSearch(parts[0], parts[1])
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="e.g. facebook/react"
        className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-4 py-3
                   text-white placeholder-gray-500 focus:outline-none
                   focus:border-blue-500 transition-colors"
      />
      <button
        type="submit"
        disabled={loading}
        className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-900
                   disabled:cursor-not-allowed px-6 py-3 rounded-lg font-medium
                   transition-colors"
      >
        {loading ? 'Loading...' : 'Analyze'}
      </button>
    </form>
  )
}