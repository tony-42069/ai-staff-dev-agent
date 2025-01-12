import { ChakraProvider, Box, Grid } from '@chakra-ui/react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { FC } from 'react'
import { Header, Sidebar } from './components/Layout'
import QueryProvider from './providers/QueryProvider'
import AgentsPage from './pages/Agents'

const App: FC = () => {
  return (
    <QueryProvider>
      <ChakraProvider>
        <Router>
          <Box minH="100vh">
            <Grid
              templateColumns="250px 1fr"
              templateRows="60px 1fr"
              minH="100vh"
            >
              <Box gridColumn="1 / -1">
                <Header />
              </Box>
              <Box>
                <Sidebar />
              </Box>
              <Box p={4} bg="gray.50">
                <Routes>
                  <Route path="/agents" element={<AgentsPage />} />
                  {/* Add more routes here */}
                </Routes>
              </Box>
            </Grid>
          </Box>
        </Router>
      </ChakraProvider>
    </QueryProvider>
  )
}

export default App
