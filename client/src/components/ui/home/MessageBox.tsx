
export default function MessageBox({ width, children, text }: { width: string, children?: React.ReactNode, text?: string }) {
  return (
    <div className={`bg-white p-4 rounded-lg shadow flex gap-2 justify-start items-start`} style={{ maxWidth: width }}>
      <div className="min-w-10 min-h-10 bg-gray-200 rounded-full flex items-center justify-center overflow-hidden">
        <img src="/logo.webp" alt="logo" className="object-cover w-10 h-10" />
      </div>
      <div className="mt-1 flex flex-col gap-6 mr-4">
        {text && <div className="text-gray-800 whitespace-pre-wrap">{text}</div>}
        {
          children ? children : <p className="text-gray-800">Hello, how can I help you?</p>
        }
      </div>
    </div>
  )
}