import type { JSX } from "react";
import Home from "./components/pages/Home";
import { Brain, Compass, HomeIcon, ImageDown, MessageCircle, Navigation } from "lucide-react";
import AppLayout from "./components/ui/Layout/AppLayout";
import Community from "./components/pages/Community";

type Route = {
  path: string;
  element: JSX.Element;
  menu?: boolean;
  name?: string;
  icon?: JSX.Element;
  activeFor?: string[];
}[]

export const routes: Route = [
  {
    path: '*',
    element: <div>Sorry not found</div>
  },
  {
    path: "/",
    element: (
      <div>Landing page <a href="/home">go home</a></div>
    )
  },
  {
    path: "/home",
    element: (
      <AppLayout>
        <Home />
      </AppLayout>
    ),
    menu: true,
    name: "Playground",
    icon: <HomeIcon size={16} />,
  },
  {
    path: "/community",
    element: (
      <AppLayout>
        <Community />
      </AppLayout>
    ),
    menu: true,
    name: "Community",
    icon: <Compass size={16} />,
  },
  {
    path: "/learn",
    element: (
      <AppLayout>
        <Community />
      </AppLayout>
    ),
    menu: true,
    name: "Learn Kolam",
    icon: <Brain size={16} />,
  },
  {
    path: "/my-kolams",
    element: (
      <AppLayout>
        <Community />
      </AppLayout>
    ),
    menu: true,
    name: "My Kolams",
    icon: <ImageDown size={16} />,
  },
    {
    path: "/support",
    element: (
      <AppLayout>
        <Community />
      </AppLayout>
    ),
    menu: true,
    name: "Support",
    icon: <MessageCircle size={16} />,
  }
]