
import { lazy } from 'react'

export const HomePage = lazy(() => import('../routes/landing/HomePage'))
export const GuestPage = lazy(() => import('../routes/guest/GuestPage'))
export const PanelPage = lazy(() => import('../routes/panel/PanelPage'))
export const AdminPage = lazy(() => import('../routes/admin/AdminPage'))

export function Loading() {
  return <p>در حال بارگذاری...</p>
}
