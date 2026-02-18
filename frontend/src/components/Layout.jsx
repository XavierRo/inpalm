import { NavLink, Outlet } from 'react-router-dom';
import {
  Leaf,
  Upload,
  Map,
  Settings,
  FlaskConical,
  BarChart3,
  Home,
} from 'lucide-react';

const NAV_ITEMS = [
  { to: '/', icon: Home, label: 'Dashboard' },
  { to: '/import', icon: Upload, label: 'Import données' },
  { to: '/fields', icon: Map, label: 'Parcelles' },
  { to: '/parameters', icon: Settings, label: 'Paramètres' },
  { to: '/simulations', icon: FlaskConical, label: 'Simulations' },
  { to: '/results', icon: BarChart3, label: 'Résultats' },
];

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-palm-800 text-white flex flex-col flex-shrink-0">
        {/* Logo */}
        <div className="px-6 py-6 border-b border-palm-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-palm-400 rounded-xl flex items-center justify-center">
              <Leaf className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="font-display text-xl tracking-tight">NBalance</h1>
              <p className="text-palm-300 text-xs mt-0.5">Bilan Azoté</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-palm-600 text-white shadow-md'
                    : 'text-palm-200 hover:bg-palm-700 hover:text-white'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-palm-700">
          <p className="text-palm-400 text-xs">
            NBalance v0.1.0
            <br />
            Agroécologie — Palmier à huile
          </p>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-8 py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
