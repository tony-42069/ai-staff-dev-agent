import '@testing-library/jest-dom';
import { beforeAll, afterEach, afterAll, vi } from 'vitest';
import { TextEncoder, TextDecoder } from 'util';
import { fetch, Headers, Request, Response } from 'whatwg-fetch';

// Polyfill globals
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;
global.fetch = fetch;
global.Headers = Headers;
global.Request = Request;
global.Response = Response;

// Add missing Web API types
const webAPIs = {
  ReadableStream: class {
    constructor() {}
    getReader() {
      return {
        read: () => Promise.resolve({ done: true, value: undefined }),
        releaseLock: () => {},
      };
    }
  },
  TransformStream: class {
    constructor() {}
    readable = new webAPIs.ReadableStream();
    writable = new webAPIs.WritableStream();
  },
  WritableStream: class {
    constructor() {}
    getWriter() {
      return {
        write: () => Promise.resolve(),
        close: () => Promise.resolve(),
        abort: () => Promise.resolve(),
        releaseLock: () => {},
      };
    }
  },
};

Object.assign(global, webAPIs);

// Import MSW after polyfills
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

// Setup MSW server with error handling
export const server = setupServer(...handlers);

beforeAll(() => {
  // Start MSW server
  server.listen({ onUnhandledRequest: 'warn' });
});

afterEach(() => {
  // Reset handlers between tests
  server.resetHandlers();
  // Clear any mocked timers
  vi.clearAllTimers();
  // Clear any mocked functions
  vi.clearAllMocks();
});

afterAll(() => {
  // Clean up MSW server
  server.close();
});
