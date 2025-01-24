import '@testing-library/jest-dom';
import { TextEncoder, TextDecoder } from 'util';
import { Response, Request, Headers } from 'node-fetch';

// Polyfill globals
global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder as any;
global.Response = Response as any;
global.Request = Request as any;
global.Headers = Headers as any;

// Import MSW after polyfills
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

// Setup MSW server
export const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
