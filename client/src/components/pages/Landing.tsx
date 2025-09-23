import { useNavigate } from "react-router-dom";

export default function Landing() {

  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-orange-100 flex flex-col">
      {/* Navigation */}
      <nav className="w-full py-6 px-12 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <div className="w-10 h-10 bg-orange-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-xl">K</span>
          </div>
          <span className="text-2xl font-bold text-orange-800">Kolam.ai</span>
        </div>

        <div className="hidden md:flex space-x-8">
          <a href="#" className="text-orange-700 hover:text-orange-500 font-medium">About</a>
          <a href="#" className="text-orange-700 hover:text-orange-500 font-medium">Features</a>
          <a href="#" className="text-orange-700 hover:text-orange-500 font-medium">Gallery</a>
          <a href="#" className="text-orange-700 hover:text-orange-500 font-medium">Contact</a>
        </div>

        <button className="bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-full font-medium transition duration-300"
          onClick={() => navigate('/home')}
        >
          Get Started
        </button>
      </nav>

      {/* Hero Section */}
      <div className="flex-1 flex flex-col md:flex-row items-center justify-center px-8 py-12 md:py-24 gap-[200px]">
        {/* Left Content */}
        <div className="flex flex-col items-center md:items-start text-center md:text-left mb-12 md:mb-0">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-orange-900 mb-6">
            Where <span className="text-orange-500">Culture</span>, <span className="text-orange-500">Math</span> & <span className="text-orange-500">AI</span> Unite
          </h1>

          <p className="text-lg text-orange-800 mb-8 max-w-lg">
            Discover, analyze, and share the beauty of traditional kolams with our AI-powered platform.
            Explore the intricate patterns, mathematical foundations, and cultural significance of this ancient art form.
          </p>

          <div className="flex flex-col sm:flex-row gap-4">
            <button className="bg-orange-500 hover:bg-orange-600 text-white px-8 py-4 rounded-full font-medium text-lg transition duration-300 shadow-lg"
              onClick={() => navigate('/home')}>
              Create Your Kolam
            </button>
            <button className="border-2 border-orange-500 text-orange-500 hover:bg-orange-50 px-8 py-4 rounded-full font-medium text-lg transition duration-300"
              onClick={() => navigate('/home')}>
              Explore Gallery
            </button>
          </div>
        </div>

        {/* Right Content - Kolam Pattern Visualization */}
        <div className="flex justify-center">
          <div className="relative w-80 h-80 lg:w-96 lg:h-96">
            {/* Kolam pattern representation */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-full h-full bg-orange-200 rounded-full opacity-30"></div>
            </div>

            <div className="absolute inset-0 flex items-center justify-center">
              <svg viewBox="0 0 100 100" className="w-full h-full">
                {/* Base circles */}
                <circle cx="50" cy="50" r="45" stroke="#ea580c" strokeWidth="0.5" fill="none" />
                <circle cx="50" cy="50" r="35" stroke="#ea580c" strokeWidth="0.5" fill="none" />
                <circle cx="50" cy="50" r="25" stroke="#ea580c" strokeWidth="0.5" fill="none" />

                {/* Pattern elements */}
                <path d="M30,50 Q50,30 70,50 Q50,70 30,50" stroke="#ea580c" strokeWidth="0.8" fill="none" />
                <path d="M35,50 Q50,35 65,50 Q50,65 35,50" stroke="#ea580c" strokeWidth="0.8" fill="none" />

                {/* Decorative dots */}
                <circle cx="50" cy="30" r="1.5" fill="#ea580c" />
                <circle cx="50" cy="70" r="1.5" fill="#ea580c" />
                <circle cx="30" cy="50" r="1.5" fill="#ea580c" />
                <circle cx="70" cy="50" r="1.5" fill="#ea580c" />
                <circle cx="40" cy="40" r="1.5" fill="#ea580c" />
                <circle cx="60" cy="40" r="1.5" fill="#ea580c" />
                <circle cx="40" cy="60" r="1.5" fill="#ea580c" />
                <circle cx="60" cy="60" r="1.5" fill="#ea580c" />
              </svg>
            </div>

            {/* Floating elements */}
            <div className="absolute top-10 left-10 w-6 h-6 bg-orange-400 rounded-full opacity-70"></div>
            <div className="absolute bottom-12 right-8 w-5 h-5 bg-orange-300 rounded-full opacity-70"></div>
            <div className="absolute top-16 right-16 w-4 h-4 bg-orange-500 rounded-full opacity-70"></div>
          </div>
        </div>
      </div>

      {/* Feature Highlights */}
      <div className="w-full px-8 py-12 bg-orange-50 bg-opacity-50">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="flex flex-col items-center text-center p-6 rounded-lg bg-white bg-opacity-70 shadow-sm">
            <div className="w-14 h-14 bg-orange-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </div>
            <h3 className="font-semibold text-orange-900 mb-2">AI Analysis</h3>
            <p className="text-orange-700">Understand the patterns and mathematical structures behind traditional kolams</p>
          </div>

          <div className="flex flex-col items-center text-center p-6 rounded-lg bg-white bg-opacity-70 shadow-sm">
            <div className="w-14 h-14 bg-orange-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
            </div>
            <h3 className="font-semibold text-orange-900 mb-2">Create & Share</h3>
            <p className="text-orange-700">Design your own digital kolams and share them with a global community</p>
          </div>

          <div className="flex flex-col items-center text-center p-6 rounded-lg bg-white bg-opacity-70 shadow-sm">
            <div className="w-14 h-14 bg-orange-100 rounded-full flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8h2a2 2 0 012 2v6a2 2 0 01-2 2h-2v4l-4-4H9a1.994 1.994 0 01-1.414-.586m0 0L11 14h4a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2v4l.586-.586z"></path>
              </svg>
            </div>
            <h3 className="font-semibold text-orange-900 mb-2">Cultural Stories</h3>
            <p className="text-orange-700">Discover the meanings and traditions behind different kolam designs</p>
          </div>
        </div>
      </div>
    </div>
  );
}