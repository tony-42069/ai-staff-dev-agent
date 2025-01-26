import { ChakraProvider, Box, Grid, Container, extendTheme } from '@chakra-ui/react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { FC } from 'react'
import { Header, Sidebar } from '@components/Layout'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import AgentsPage from '@pages/Agents'
import ProjectsPage from '@pages/Projects'
import ChatPage from '@pages/Chat'
import MonitoringPage from '@pages/Monitoring'

const queryClient = new QueryClient()

// Custom theme
const theme = extendTheme({
  styles: {
    global: {
      'html, body': {
        margin: 0,
        padding: 0,
        height: '100%',
        width: '100%',
        backgroundColor: 'gray.50'
      }
    }
  },
  components: {
    Card: {
      baseStyle: {
        container: {
          backgroundColor: 'white',
          borderRadius: 'lg',
          boxShadow: 'sm',
          border: '1px solid',
          borderColor: 'gray.200'
        }
      }
    },
    Button: {
      defaultProps: {
        colorScheme: 'blue'
      }
    }
  },
  colors: {
    brand: {
      50: '#e3f2fd',
      100: '#bbdefb',
      200: '#90caf9',
      300: '#64b5f6',
      400: '#42a5f5',
      500: '#2196f3',
      600: '#1e88e5',
      700: '#1976d2',
      800: '#1565c0',
      900: '#0d47a1'
    }
  }
})

const App: FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ChakraProvider theme={theme}>
        <Router>
          <Box minHeight="100vh" width="100vw" overflow="hidden">
            <Grid
              templateColumns={{ base: '1fr', md: '250px 1fr' }}
              templateRows="60px 1fr"
              minHeight="100vh"
              gap={0}
            >
              {/* Header */}
              <Box 
                gridColumn="1 / -1" 
                bg="white" 
                borderBottom="1px" 
                borderColor="gray.200"
                zIndex={2}
                position="fixed"
                width="100%"
                height="60px"
              >
                <Header />
              </Box>

              {/* Sidebar */}
              <Box
                display={{ base: 'none', md: 'block' }}
                bg="white"
                borderRight="1px"
                borderColor="gray.200"
                position="fixed"
                top="60px"
                bottom={0}
                width="250px"
                overflowY="auto"
                zIndex={1}
              >
                <Sidebar />
              </Box>

              {/* Main Content */}
              <Box
                gridColumn={{ base: '1', md: '2' }}
                mt="60px"
                bg="gray.50"
                p={6}
                overflowY="auto"
                minHeight="calc(100vh - 60px)"
              >
                <Container maxW="1200px">
                  <Routes>
                    <Route path="/" element={<Navigate to="/agents" replace />} />
                    <Route path="/agents" element={<AgentsPage />} />
                    <Route path="/projects" element={<ProjectsPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                    <Route path="/monitoring" element={<MonitoringPage />} />
                  </Routes>
                </Container>
              </Box>
            </Grid>
          </Box>
        </Router>
      </ChakraProvider>
    </QueryClientProvider>
  )
}

export default App
