import { ChakraProvider, Box, Grid } from '@chakra-ui/react'
import { BrowserRouter as Router } from 'react-router-dom'
import { FC } from 'react'
import { Header, Sidebar } from './components/Layout'

const App: FC = () => {
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
