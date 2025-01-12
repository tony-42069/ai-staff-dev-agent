import { Box, Badge, Text } from '@chakra-ui/react'

interface AgentCardProps {
  name: string;
  status: string;
  type: string;
}

export const AgentCard = ({ name, status, type }: AgentCardProps) => {
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
    </Box>
  )
}