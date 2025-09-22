import AsideLeft from "./AsideLeft";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <main className="grid md:grid-cols-5 2xl:grid-cols-6 w-screen h-screen">
      <div className="col-span-1">
        <AsideLeft />
      </div>
      <div className="md:col-span-4 2xl:col-span-5 bg-white">
        {children}
      </div>
    </main>
  )
}