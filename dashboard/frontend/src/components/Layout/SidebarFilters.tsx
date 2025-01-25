import { 
  Box, 
  VStack, 
  Text, 
  Input,
  Checkbox,
  CheckboxGroup,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  InputGroup,
  InputLeftElement
} from '@chakra-ui/react'
import { FiSearch } from 'react-icons/fi'
import { FC, useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { Agent, Project } from '../../services/api'

interface FilterProps {
  onFilterChange: (filters: any) => void;
}

const SidebarFilters: FC<FilterProps> = ({ onFilterChange }) => {
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatuses, setSelectedStatuses] = useState<string[]>([]);
  const [selectedCapabilities, setSelectedCapabilities] = useState<string[]>([]);
  
  // Reset filters when route changes
  useEffect(() => {
    setSearchTerm('');
    setSelectedStatuses([]);
    setSelectedCapabilities([]);
  }, [location.pathname]);

  // Update parent component with filter changes
  useEffect(() => {
    onFilterChange({
      search: searchTerm,
      statuses: selectedStatuses,
      capabilities: selectedCapabilities
    });
  }, [searchTerm, selectedStatuses, selectedCapabilities, onFilterChange]);

  const renderAgentFilters = () => (
    <>
      <AccordionItem>
        <h2>
          <AccordionButton>
            <Box flex="1" textAlign="left">
              Status
            </Box>
            <AccordionIcon />
          </AccordionButton>
        </h2>
        <AccordionPanel>
          <CheckboxGroup value={selectedStatuses} onChange={(values) => setSelectedStatuses(values as string[])}>
            <VStack align="start">
              <Checkbox value="idle">Idle</Checkbox>
              <Checkbox value="busy">Busy</Checkbox>
              <Checkbox value="error">Error</Checkbox>
            </VStack>
          </CheckboxGroup>
        </AccordionPanel>
      </AccordionItem>
      <AccordionItem>
        <h2>
          <AccordionButton>
            <Box flex="1" textAlign="left">
              Capabilities
            </Box>
            <AccordionIcon />
          </AccordionButton>
        </h2>
        <AccordionPanel>
          <CheckboxGroup value={selectedCapabilities} onChange={(values) => setSelectedCapabilities(values as string[])}>
            <VStack align="start">
              {/* We'll populate this dynamically based on available capabilities */}
              <Checkbox value="code">Code</Checkbox>
              <Checkbox value="test">Test</Checkbox>
              <Checkbox value="deploy">Deploy</Checkbox>
            </VStack>
          </CheckboxGroup>
        </AccordionPanel>
      </AccordionItem>
    </>
  );

  const renderProjectFilters = () => (
    <AccordionItem>
      <h2>
        <AccordionButton>
          <Box flex="1" textAlign="left">
            Status
          </Box>
          <AccordionIcon />
        </AccordionButton>
      </h2>
      <AccordionPanel>
        <CheckboxGroup value={selectedStatuses} onChange={(values) => setSelectedStatuses(values as string[])}>
          <VStack align="start">
            <Checkbox value="active">Active</Checkbox>
            <Checkbox value="completed">Completed</Checkbox>
            <Checkbox value="archived">Archived</Checkbox>
          </VStack>
        </CheckboxGroup>
      </AccordionPanel>
    </AccordionItem>
  );

  return (
    <Box mt={6} px={3}>
      <Text mb={2} fontWeight="medium" color="gray.600">
        Filters
      </Text>
      
      <InputGroup mb={4}>
        <InputLeftElement pointerEvents="none">
          <FiSearch color="gray.300" />
        </InputLeftElement>
        <Input
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </InputGroup>

      <Accordion allowMultiple>
        {location.pathname === '/agents' && renderAgentFilters()}
        {location.pathname === '/projects' && renderProjectFilters()}
      </Accordion>
    </Box>
  );
};

export default SidebarFilters;
