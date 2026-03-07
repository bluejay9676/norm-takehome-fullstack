'use client';

import { Box, Text, VStack } from '@chakra-ui/react';

interface Citation {
  source: string;
  text: string;
}

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

export default function ChatMessage({
  role,
  content,
  citations,
}: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <Box
      alignSelf={isUser ? 'flex-end' : 'flex-start'}
      maxW="80%"
      bg={isUser ? 'blue.500' : 'gray.100'}
      color={isUser ? 'white' : 'gray.800'}
      px={4}
      py={3}
      borderRadius="lg"
      borderBottomRightRadius={isUser ? 'sm' : 'lg'}
      borderBottomLeftRadius={isUser ? 'lg' : 'sm'}
    >
      <Text whiteSpace="pre-wrap">{content}</Text>
      {citations && citations.length > 0 && (
        <VStack align="stretch" mt={3} spacing={2}>
          <Text fontSize="sm" fontWeight="bold" color="gray.600">
            Sources:
          </Text>
          {citations.map((citation, idx) => (
            <Box
              key={idx}
              bg="white"
              p={2}
              borderRadius="md"
              borderLeft="3px solid"
              borderLeftColor="blue.400"
            >
              <Text fontSize="xs" fontWeight="semibold" color="blue.600">
                {citation.source}
              </Text>
              <Text fontSize="xs" color="gray.600">
                {citation.text}
              </Text>
            </Box>
          ))}
        </VStack>
      )}
    </Box>
  );
}
