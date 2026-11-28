
import { Suspense } from 'react'
import { createBrowserRouter } from 'react-router'
import {
  HomePage,
  GuestPage,
  PanelPage,
  AdminPage,
  Loading,
} from './routeComponents'

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <Suspense fallback={<Loading />}>
        <HomePage />
      </Suspense>
    ),
  },
  {
    path: '/t/:qrToken',
    element: (
      <Suspense fallback={<Loading />}>
        <GuestPage />
      </Suspense>
    ),
  },
  {
    path: '/panel/*',
    element: (
      <Suspense fallback={<Loading />}>
        <PanelPage />
      </Suspense>
    ),
  },
  {
    path: '/admin/*',
    element: (
      <Suspense fallback={<Loading />}>
        <AdminPage />
      </Suspense>
    ),
  },
])

export default router
