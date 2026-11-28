
import { Suspense } from 'react'
import { createBrowserRouter } from 'react-router'
import {
  HomePage,
  PricingPage,
  GuestPage,
  MenuPage,
  OrderPage,
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
  {
  path: '/pricing',
  element: (
    <Suspense fallback={<Loading />}>
      <PricingPage />
    </Suspense>
  ),
},
{
  path: '/m/:slug',
  element: (
    <Suspense fallback={<Loading />}>
      <MenuPage />
    </Suspense>
  ),
},
{
  path: '/o/:orderId',
  element: (
    <Suspense fallback={<Loading />}>
      <OrderPage />
    </Suspense>
  ),
},
])

export default router
