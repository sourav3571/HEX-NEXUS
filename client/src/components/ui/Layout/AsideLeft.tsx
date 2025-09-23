import { Link2 } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { routes } from "../../../routes";

export default function AsideLeft() {
  const location = useLocation();

  return (
    <aside className="bg-white w-full h-screen overflow-x-hidden overflow-y-auto border-r border-gray-200">
      <div className="flex items-center gap-2 p-5 mb-2">
        <img src="/logo.webp" className="h-10 w-10 rounded-lg" />
        <h1 className="text-xl font-semibold text-primary">KOLAM.AI</h1>
      </div>
      <div className="flex flex-col p-2">
        {
          routes.map((route) => {
            if (!route.menu) return null;

            const isActive = getIsActive(route.path, location.pathname);

            return (
              <Link
                key={route.path}
                to={route.path}
                className={isActive ? activeStyle : defaultStyle}
              >
                <span className="flex items-center justify-center w-6 h-6">
                  {route.icon || <Link2 className="w-4 h-4" />}
                </span>
                <span className="truncate">
                  {route.name || route.path.replace('/', '')}
                </span>
                {isActive && (
                  <span className="absolute right-0 w-1 h-6 bg-primary rounded-l-md"></span>
                )}
              </Link>
            );
          })
        }
      </div>
    </aside>
  );
}

const defaultStyle = 'relative flex items-center gap-3 text-gray-600 p-3 rounded-lg hover:bg-gray-50 transition-all duration-200 text-sm font-medium';
const activeStyle = 'relative flex items-center gap-3 text-primary bg-primary/10 p-3 rounded-lg transition-all duration-200 text-sm font-semibold';

function getIsActive(routePath: string, currentPath: string): boolean {
  // Exact match
  if (routePath === currentPath) return true;

  const route = routes.find(r => r.path === routePath);
  if (!route) return false;

  // Check if currentPath starts with routePath (e.g., /tasks and /project/tasks)
  if (currentPath.startsWith(routePath)) return true;

  // Check activeFor paths
  return (route.activeFor || []).some(path => currentPath.startsWith(path));
}