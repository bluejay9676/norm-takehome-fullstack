'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Flex,
  Heading,
  Input,
  IconButton,
  VStack,
  Spinner,
  Text,
} from '@chakra-ui/react';
import { FiSend } from 'react-icons/fi';
import ChatMessage from '@/components/ChatMessage';

interface Citation {
  source: string;
  text: string;
}

interface Message {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
}

const BACKEND_URL = 'http://localhost:8080';
const HEALTH_CHECK_INTERVAL = 2000;

export default function Page() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isBackendReady, setIsBackendReady] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const checkBackendHealth = useCallback(async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/health`);
      if (response.ok) {
        setIsBackendReady(true);
        return true;
      }
    } catch {
      // Backend not ready yet
    }
    return false;
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const startHealthCheck = async () => {
      const isReady = await checkBackendHealth();
      if (!isReady) {
        intervalId = setInterval(async () => {
          const ready = await checkBackendHealth();
          if (ready) {
            clearInterval(intervalId);
          }
        }, HEALTH_CHECK_INTERVAL);
      }
    };

    startHealthCheck();

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [checkBackendHealth]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading || !isBackendReady) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: userMessage }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: data.response,
          citations: data.citations,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Flex direction="column" h="100vh" bg="gray.50">
      <Box bg="white" borderBottom="1px" borderColor="gray.200" py={4}>
        <Container maxW="container.md">
          <Flex justify="center" align="center" gap={2}>
            <Heading size="md" textAlign="center" color="gray.700">
              Laws of the Seven Kingdoms
            </Heading>
            {!isBackendReady && (
              <Flex align="center" gap={1}>
                <Spinner size="xs" color="orange.500" />
                <Text fontSize="xs" color="orange.500">
                  Connecting...
                </Text>
              </Flex>
            )}
          </Flex>
        </Container>
      </Box>

      <Flex flex={1} overflow="hidden">
        <Container
          maxW="container.md"
          py={4}
          display="flex"
          flexDirection="column"
          h="100%"
        >
          <VStack
            flex={1}
            overflowY="auto"
            spacing={4}
            align="stretch"
            px={2}
            css={{
              '&::-webkit-scrollbar': { width: '6px' },
              '&::-webkit-scrollbar-thumb': {
                background: '#CBD5E0',
                borderRadius: '3px',
              },
            }}
          >
            {messages.length === 0 && (
              <Flex flex={1} align="center" justify="center">
                <VStack spacing={2}>
                  <Text color="gray.500" fontSize="lg" textAlign="center">
                    Ask anything about the{' '}
                    <Text as="span" fontWeight="bold">
                      Laws of the Seven Kingdoms
                    </Text>
                  </Text>
                  {!isBackendReady && (
                    <Flex align="center" gap={2}>
                      <Spinner size="sm" color="orange.500" />
                      <Text color="orange.500" fontSize="sm">
                        Waiting for backend to start...
                      </Text>
                    </Flex>
                  )}
                </VStack>
              </Flex>
            )}
            {messages.map((message, idx) => (
              <ChatMessage
                key={idx}
                role={message.role}
                content={message.content}
                citations={message.citations}
              />
            ))}
            {isLoading && (
              <Flex alignSelf="flex-start" align="center" gap={2} px={4} py={3}>
                <Spinner size="sm" color="blue.500" />
                <Text color="gray.500" fontSize="sm">
                  Thinking...
                </Text>
              </Flex>
            )}
            <div ref={messagesEndRef} />
          </VStack>

          <Box as="form" onSubmit={handleSubmit} pt={4}>
            <Flex gap={2}>
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={
                  isBackendReady
                    ? 'Ask a question...'
                    : 'Waiting for backend...'
                }
                bg="white"
                borderColor="gray.300"
                _focus={{
                  borderColor: 'blue.500',
                  boxShadow: '0 0 0 1px var(--chakra-colors-blue-500)',
                }}
                disabled={isLoading || !isBackendReady}
              />
              <IconButton
                type="submit"
                aria-label="Send message"
                icon={<FiSend />}
                colorScheme="blue"
                isLoading={isLoading}
                disabled={!input.trim() || !isBackendReady}
              />
            </Flex>
          </Box>
        </Container>
      </Flex>
    </Flex>
  );
}
