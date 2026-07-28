import { createBrowserRouter } from 'react-router-dom';
import { DashboardLayout } from '../layouts/DashboardLayout';
import { Dashboard } from '../pages/Dashboard';
import { Upload } from '../pages/Upload';
import { Documents } from '../pages/Documents';
import { Chat } from '../pages/Chat';
import { Analytics } from '../pages/Analytics';
import { Blog } from '../pages/Blog';
import { Settings } from '../pages/Settings';
import { Login } from '../pages/Login';
import { Home } from '../pages/Home';
import { NotFound } from '../pages/NotFound';

export const router = createBrowserRouter([
  { path: '/', element: <Home /> },
  { path: '/login', element: <Login /> },
  {
    path: '/dashboard',
    element: <DashboardLayout><Dashboard /></DashboardLayout>,
  },
  {
    path: '/upload',
    element: <DashboardLayout><Upload /></DashboardLayout>,
  },
  {
    path: '/documents',
    element: <DashboardLayout><Documents /></DashboardLayout>,
  },
  {
    path: '/chat',
    element: <DashboardLayout><Chat /></DashboardLayout>,
  },
  {
    path: '/analytics',
    element: <DashboardLayout><Analytics /></DashboardLayout>,
  },
  {
    path: '/blog',
    element: <Blog />,
  },
  {
    path: '/settings',
    element: <DashboardLayout><Settings /></DashboardLayout>,
  },
  { path: '*', element: <NotFound /> },
]);
