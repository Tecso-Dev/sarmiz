
import { createBrowserRouter } from 'react-router'
import HomePage from '../routes/landing/HomePage'

const router = createBrowserRouter([
  {
    path: '/',
    element: <HomePage />,
  },
])

export default router
