import Link from 'next/link';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      
      {/* HEADER & NAVIGATION */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">Nexus</span>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">NexusHR Solutions</h1>
          </div>
          
          <nav>
            <Link 
              href="/login" 
              className="bg-gray-900 text-white px-6 py-2.5 rounded-full font-medium hover:bg-gray-800 transition shadow-sm"
            >
              Portal Login
            </Link>
          </nav>
        </div>
      </header>

      {/* MAIN HERO SECTION */}
      <main className="flex-1">
        <section className="max-w-7xl mx-auto px-6 py-20 lg:py-32 flex flex-col lg:flex-row items-center gap-12">
          <div className="flex-1 space-y-8">
            <h2 className="text-5xl lg:text-6xl font-extrabold text-gray-900 leading-tight">
              Intelligent HR for the Modern Enterprise.
            </h2>
            <p className="text-xl text-gray-600 leading-relaxed max-w-2xl">
              Empower your workforce with AI-driven onboarding, seamless policy management, and instant administrative support. We build software that puts your people first.
            </p>
            <div className="flex gap-4">
              <Link 
                href="/login" 
                className="bg-blue-600 text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-blue-700 transition shadow-md"
              >
                Access Your Workspace
              </Link>
            </div>
          </div>
          <div className="flex-1 w-full">
            <img 
              src="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?q=80&w=2070&auto=format&fit=crop" 
              alt="Team collaborating in a modern office" 
              className="w-full h-auto rounded-2xl shadow-2xl object-cover border border-gray-200"
            />
          </div>
        </section>

        {/* COMING SOON / ROADMAP SECTION */}
        <section className="bg-white py-24 border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center mb-16">
              <h3 className="text-blue-600 font-bold tracking-wider uppercase text-sm mb-3">Product Roadmap</h3>
              <h2 className="text-4xl font-bold text-gray-900">Exciting Features Coming Soon</h2>
              <p className="mt-4 text-gray-600 max-w-2xl mx-auto text-lg">
                Our engineering team is actively developing the next generation of workspace tools to make your daily operations even smoother.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
              
              {/* Feature 1 */}
              <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition duration-300">
                <img 
                  src="https://images.unsplash.com/photo-1611224923853-80b023f02d71?q=80&w=2069&auto=format&fit=crop" 
                  alt="Task Tracking Interface" 
                  className="w-full h-48 object-cover rounded-xl mb-6"
                />
                <h4 className="text-xl font-bold text-gray-900 mb-2">Smart Task Tracking</h4>
                <p className="text-gray-600">
                  Assign, monitor, and complete onboarding and daily operational tasks directly from your unified dashboard. Keep your entire team aligned.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition duration-300">
                <img 
                  src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?q=80&w=2070&auto=format&fit=crop" 
                  alt="Data Analytics" 
                  className="w-full h-48 object-cover rounded-xl mb-6"
                />
                <h4 className="text-xl font-bold text-gray-900 mb-2">Advanced Analytics</h4>
                <p className="text-gray-600">
                  Gain deep insights into employee engagement, AI query trends, and onboarding efficiency with customizable data visualizations.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 hover:shadow-lg transition duration-300">
                <img 
                  src="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?q=80&w=2070&auto=format&fit=crop" 
                  alt="Payroll and Finance" 
                  className="w-full h-48 object-cover rounded-xl mb-6"
                />
                <h4 className="text-xl font-bold text-gray-900 mb-2">Automated Payroll Integration</h4>
                <p className="text-gray-600">
                  Seamlessly connect employee database records directly to standard payroll providers for frictionless end-of-month processing.
                </p>
              </div>

            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="bg-gray-900 text-gray-400 py-12 text-center">
        <p>© {new Date().getFullYear()} NexusHR Solutions. All rights reserved.</p>
      </footer>
      
    </div>
  );
}