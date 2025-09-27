import { useState, useEffect } from "react";
import { Twitter, Facebook, Linkedin, X } from "lucide-react";

type UserKolam = {
  id: number;
  title: string;
  image: string;
};

export default function Community() {
  const [userKolams, setUserKolams] = useState<UserKolam[]>([]);

  // Load kolams from localStorage on mount
  useEffect(() => {
    const savedKolams = localStorage.getItem("userKolams");
    if (savedKolams) {
      setUserKolams(JSON.parse(savedKolams));
    }
  }, []);

  const removeKolam = (id: number) => {
    const updated = userKolams.filter(k => k.id !== id);
    setUserKolams(updated);
    localStorage.setItem("userKolams", JSON.stringify(updated));
  };

  const shareLinks = (kolam: UserKolam) => {
    const url = encodeURIComponent(window.location.origin + kolam.image);
    const text = encodeURIComponent(`Check out my recreated Kolam design: ${kolam.title}`);
    return {
      twitter: `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
      whatsapp: `https://wa.me/?text=${text}%20${url}`,
    };
  };

  return (
    <div className="p-8 h-screen overflow-y-auto">
      <div className="mb-6 flex justify-between items-center">
        <h2 className="text-2xl font-bold">My Recreated Kolams</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {userKolams.map((kolam) => (
          <div
            key={kolam.id}
            className="relative p-4 bg-white rounded-lg shadow h-[400px] flex flex-col justify-between"
          >
            {/* Cross button */}
            <button
              onClick={() => removeKolam(kolam.id)}
              className="absolute top-2 right-2 text-gray-500 hover:text-red-500 transition"
            >
              <X size={20} />
            </button>

            <img
              src={kolam.image}
              alt={kolam.title}
              className="w-full h-64 object-cover rounded-md mb-2"
            />
            <h3 className="text-center font-semibold">{kolam.title}</h3>

            {/* Share Buttons */}
            <div className="flex justify-around mt-2">
              <a
                href={shareLinks(kolam).twitter}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full bg-blue-400 text-white hover:bg-blue-500 transition"
              >
                <Twitter size={16} />
              </a>
              <a
                href={shareLinks(kolam).facebook}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full bg-blue-600 text-white hover:bg-blue-700 transition"
              >
                <Facebook size={16} />
              </a>
              <a
                href={shareLinks(kolam).linkedin}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full bg-blue-500 text-white hover:bg-blue-600 transition"
              >
                <Linkedin size={16} />
              </a>
              <a
                href={shareLinks(kolam).whatsapp}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-full bg-green-500 text-white hover:bg-green-600 transition flex items-center justify-center"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path d="M20.52 3.48A11.94 11.94 0 0012 0C5.37 0 0 5.37 0 12c0 2.12.55 4.09 1.52 5.82L0 24l6.49-1.52A11.94 11.94 0 0012 24c6.63 0 12-5.37 12-12 0-3.19-1.24-6.16-3.48-8.52zM12 22c-2.06 0-3.99-.6-5.61-1.62l-.4-.26-3.85.9.91-3.76-.26-.41A10 10 0 1122 12c0 5.52-4.48 10-10 10zm5.43-7.85c-.3-.15-1.77-.87-2.05-.97-.27-.1-.47-.15-.67.15s-.77.97-.94 1.17c-.17.2-.33.22-.62.08-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.49-1.77-1.67-2.07-.17-.3-.02-.46.13-.61.13-.13.3-.33.45-.5.15-.17.2-.28.3-.47.1-.2.05-.37-.02-.52-.08-.15-.67-1.61-.92-2.2-.24-.57-.49-.5-.67-.51l-.57-.01c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.87 1.22 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.69.63.71.23 1.36.2 1.87.12.57-.1 1.77-.72 2.02-1.42.25-.7.25-1.3.17-1.42-.08-.12-.27-.2-.57-.35z"/>
                </svg>
              </a>
            </div>
          </div>
        ))}
      </div>

      {userKolams.length === 0 && (
        <p className="text-center text-gray-500 mt-8">
          Recreate a Kolam to share it here!
        </p>
      )}
    </div>
  );
}
