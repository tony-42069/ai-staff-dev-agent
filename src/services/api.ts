// src/services/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api'
})

export const getAgents = async () => {
  const { data } = await api.get('/agents')
  return data
}

export const createAgent = async (agentData: any) => {
  const { data } = await api.post('/agents', agentData)
  return data
}