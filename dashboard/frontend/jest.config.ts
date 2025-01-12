export default {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      useESM: true,
    }],
  },
  moduleDirectories: ['node_modules', '<rootDir>/src'],
  extensionsToTreatAsEsm: ['.ts', '.tsx'],
  testEnvironmentOptions: {
    customExportConditions: ['node', 'node-addons'],
  }
}; 