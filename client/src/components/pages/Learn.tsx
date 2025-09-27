import { useState, useEffect } from "react";
import { TrendingUp } from "lucide-react";

type KolamDesign = {
  id: number;
  title: string;
  image: string;
};

export default function StateKolam() {
  const [selectedState, setSelectedState] = useState<string>("Tamil Nadu");
  const [designs, setDesigns] = useState<KolamDesign[]>([]);

  useEffect(() => {
    async function fetchDesigns() {
      const mockDB: Record<string, KolamDesign[]> = {
        "Tamil Nadu": [
          { id: 1, title: "Traditional Kolam", image: "/kolam/tn1.jpg" },
          { id: 2, title: "Festival Kolam", image: "/kolam/tn2.jpg" },
        ],
        Karnataka: [
          { id: 3, title: "Mysore Rangoli", image: "/kolam/kar1.jpg" },
          { id: 4, title: "Floral Pattern", image: "/kolam/kar2.jpg" },
        ],
        Andhra: [
          { id: 5, title: "Pongal Kolam", image: "/kolam/ap1.jpg" },
          { id: 6, title: "Geometric Style", image: "/kolam/ap2.jpg" },
        ],
      };

      setDesigns(mockDB[selectedState] || []);
    }

    fetchDesigns();
  }, [selectedState]);

  const states = ["Tamil Nadu", "Karnataka", "Andhra"];

  return (
    <div className="p-8 h-screen overflow-y-auto">
      {/* State Buttons */}
      <div className="flex flex-wrap gap-2">
        {states.map((state) => (
          <button
            key={state}
            onClick={() => setSelectedState(state)}
            className={`p-2 px-6 rounded-full flex gap-2 items-center ${
              selectedState === state
                ? "bg-primary text-white"
                : "bg-secondary text-primary"
            }`}
          >
            {state}
            <TrendingUp size={16} />
          </button>
        ))}
      </div>

      {/* Selected State Heading */}
      <h2 className="text-2xl font-bold mt-6">
        Kolam Designs from {selectedState}
      </h2>

      {/* Kolam Grid */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {designs.map((design) => (
          <div
            key={design.id}
            className="p-4 bg-white rounded-lg shadow hover:scale-105 transition-transform duration-200"
          >
            <img
              src={design.image}
              alt={design.title}
              className="w-full h-[250px] object-cover rounded-md mb-2"
            />
            {/* Title below image */}
            <h3 className="text-center font-semibold text-gray-700">
              {design.title}
            </h3>
          </div>
        ))}
      </div>
    </div>
  );
}
