import React from 'react';
import { Box, Badge, Text, Flex, List, ListItem } from '@chakra-ui/react';

interface AgentCardProps {
  name: string;
  status: 'active' | 'inactive';  // More specific type
  type: string;
  capabilities: string[];
}

const AgentCard: React.FC<AgentCardProps> = ({ name, status, type, capabilities }) => {
  return (
    <Box p={5} shadow="md" borderWidth="1px" borderRadius="lg">
      <Flex align="baseline">
        <Badge colorScheme={status === 'active' ? 'green' : 'gray'}>
          {status}
        </Badge>
        <Text
          ml={2}
          textTransform="uppercase"
          fontSize="sm"
          fontWeight="bold"
          color="gray.500"
        >
          {type}
        </Text>
      </Flex>
      <Text mt={2} fontSize="xl" fontWeight="semibold">
        {name}
      </Text>
      <List mt={2} spacing={1}>
        {capabilities.map((capability, index) => (
          <ListItem key={index} fontSize="sm" color="gray.600">
            {capability}
          </ListItem>
        ))}
      </List>
    </Box>
  );
};

export default AgentCard;
