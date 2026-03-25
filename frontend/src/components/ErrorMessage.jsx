export default function ErrorMessage({ message }) {
  return (
    <div className="bg-red-950 border border-red-800 rounded-xl p-4 text-red-300">
      ⚠️ {message}
    </div>
  )
}