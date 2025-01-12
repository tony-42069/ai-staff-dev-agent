import { ChakraProvider, Box, Grid } from '@chakra-ui/react'
import { BrowserRouter as Router } from 'react-router-dom'
import Header from './components/Layout/Header'
import Sidebar from './components/Layout/Sidebar'

function App() {
  return (
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
              {/* Main content will go here */}
            </Box>
          </Grid>
        </Box>
      </Router>
    </ChakraProvider>
  )
}

export default App
