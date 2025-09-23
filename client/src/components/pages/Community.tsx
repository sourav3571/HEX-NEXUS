import { TrendingUp } from "lucide-react";

export default function Community() {
  return (
    <div className="p-8 h-screen overflow-y-auto">
      <div className="flex gap-2">
        <div className="p-2 bg-secondary text-primary rounded-full px-6 flex gap-2">
          Rangoli
          <TrendingUp size={16} className="text-primary" />
        </div>
        <div className="p-2 bg-secondary text-primary rounded-full px-6 flex gap-2">
          Kolam
          <TrendingUp size={16} className="text-primary" />
        </div>
        <div className="p-2 bg-secondary text-primary rounded-full px-6 flex gap-2">
          Diwali
          <TrendingUp size={16} className="text-primary" />
        </div>
        <div className="p-2 bg-secondary text-primary rounded-full px-6 flex gap-2">
          Digital
          <TrendingUp size={16} className="text-primary" />
        </div>
        <div className="p-2 bg-secondary text-primary rounded-full px-6 flex gap-2">
          Holi
          <TrendingUp size={16} className="text-primary" />
        </div>
      </div>
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/1.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/2.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/3.png" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/6.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/7.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/8.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/9.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/10.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/1.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/2.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/3.png" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/6.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
        <div className="p-4 bg-white rounded-lg shadow h-[300px]">
          <img src="/kolam/7.jpg" alt="Rangoli 1" className="w-full h-full object-cover rounded-md mb-4" />
        </div>
      </div>
    </div>
  )
}