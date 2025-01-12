import '@testing-library/jest-dom';
import { server } from './mocks/server';

beforeAll(() => {
  // Enable API mocking before tests
  server.listen();
});

afterEach(() => {
  // Reset any runtime request handlers we may add during the tests
  server.resetHandlers();
});

afterAll(() => {
  // Clean up after the tests are finished
  server.close();
}); 