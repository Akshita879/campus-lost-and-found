import { Routes, Route } from 'react-router-dom'
import Layout from './layouts/Layout'
import Landing from './pages/Landing'
import Explore from './pages/Explore'
import Report from './pages/Report'
import Matches from './pages/Matches'
import Verify from './pages/Verify'
import NotFound from './pages/NotFound'
export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Landing />} />
        <Route path="/explore" element={<Explore />} />
        <Route path="/report" element={<Report />} />
        <Route path="/matches" element={<Matches />} />
        <Route path="/verify/:id" element={<Verify />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}
