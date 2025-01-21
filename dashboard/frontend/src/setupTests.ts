import '@testing-library/jest-dom';
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

// Polyfill Response if not available
if (typeof Response === 'undefined') {
  global.Response = class Response {
    constructor() {
      throw new Error('Response is not supported in this environment');
    }
  } as any;
}

// Setup requests interception using the given handlers
export const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
