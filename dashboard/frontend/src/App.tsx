import { ChakraProvider, Box, Grid } from '@chakra-ui/react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { FC } from 'react'
import { Header, Sidebar } from '@/components/Layout'
import QueryProvider from '@/providers/QueryProvider'
import AgentsPage from '@/pages/Agents'
import ProjectsPage from '@/pages/Projects'
import ChatPage from '@/pages/Chat'

const App: FC = () => {
  console.log('App component rendering')
  return (
    <QueryProvider>
      <ChakraProvider theme={{
        styles: {
          global: {
            'html, body': {
              margin: 0,
              padding: 0,
              height: '100%',
              width: '100%'
            }
          }
        }
      }}>
        <Router>
          <Box height="100vh" width="100vw" overflow="hidden" bg="gray.100">
            <Grid
              templateColumns="250px 1fr"
              templateRows="60px 1fr"
              height="100%"
              gap={0}
            >
              <Box gridColumn="1 / -1">
                <Header />
              </Box>
              <Box>
                <Sidebar />
              </Box>
              <Box p={4} bg="gray.50">
                <Routes>
                  <Route path="/" element={<Navigate to="/agents" replace />} />
                  <Route path="/agents" element={<AgentsPage />} />
                  <Route path="/projects" element={<ProjectsPage />} />
                  <Route path="/chat" element={<ChatPage />} />
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
