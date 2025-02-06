import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  Grid,
  Typography,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  CircularProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tooltip,
  SvgIcon,
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Refresh as RefreshIcon,
  Build as BuildIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useTheme } from '@mui/material/styles';
import { format, formatDistanceToNow } from 'date-fns';

import { api } from '../../services/api';
import { useWebSocket } from '../../services/websocket';

interface Agent {
  id: string;
  name: string;
  status: string;
  is_active: boolean;
  is_available: boolean;
  capabilities: string[];
  last_heartbeat: string;
  version: string;
  metadata: Record<string, any>;
}

interface AgentMetrics {
  operations_completed: number;
  operations_failed: number;
  average_response_time: number;
  error_rate: number;
  resource_utilization: Record<string, number>;
}

interface WebSocketMessage {
  type: string;
  agent?: Agent;
  agent_id?: string;
  metrics?: AgentMetrics;
}

const AgentList: React.FC = () => {
  const theme = useTheme();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [metrics, setMetrics] = useState<Record<string, AgentMetrics>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [maintenanceDialog, setMaintenanceDialog] = useState(false);

  const ws = useWebSocket();

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (ws) {
      ws.subscribe('system');
      ws.onMessage((data: WebSocketMessage) => {
        if (data.type === 'agent_update' && data.agent) {
          updateAgent(data.agent);
        } else if (data.type === 'agent_metrics' && data.agent_id && data.metrics) {
          updateMetrics(data.agent_id, data.metrics);
        }
      });
    }
  }, [ws]);

  const fetchAgents = async () => {
    try {
      const response = await api.get('/agents');
      setAgents(response.data);
      setError(null);

      // Fetch metrics for each agent
      response.data.forEach(async (agent: Agent) => {
        try {
          const metricsResponse = await api.get(`/agents/${agent.id}/metrics`);
          updateMetrics(agent.id, metricsResponse.data);
        } catch (e) {
          console.error(`Failed to fetch metrics for agent ${agent.id}:`, e);
        }
      });
    } catch (e) {
      setError('Failed to fetch agents');
      console.error('Error fetching agents:', e);
    } finally {
      setLoading(false);
    }
  };

  const updateAgent = (agent: Agent) => {
    setAgents(prev => prev.map(a => a.id === agent.id ? agent : a));
  };

  const updateMetrics = (agentId: string, agentMetrics: AgentMetrics) => {
    setMetrics(prev => ({
      ...prev,
      [agentId]: agentMetrics
    }));
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, agent: Agent) => {
    setMenuAnchor(event.currentTarget);
    setSelectedAgent(agent);
  };

  const handleMenuClose = () => {
    setMenuAnchor(null);
    setSelectedAgent(null);
  };

  const handleMaintenanceClick = () => {
    handleMenuClose();
    setMaintenanceDialog(true);
  };

  const handleMaintenanceSubmit = async () => {
    if (!selectedAgent) return;

    try {
      await api.post(`/agents/${selectedAgent.id}/maintenance`, {
        type: 'scheduled',
        start_time: new Date().toISOString(),
        end_time: new Date(Date.now() + 3600000).toISOString(),
      });
      setMaintenanceDialog(false);
    } catch (e) {
      console.error('Failed to schedule maintenance:', e);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return theme.palette.success.main;
      case 'unavailable':
        return theme.palette.error.main;
      case 'busy':
        return theme.palette.warning.main;
      default:
        return theme.palette.grey[500];
    }
  };

  const getStatusIcon = (status: string): typeof SvgIcon => {
    switch (status) {
      case 'active':
        return CheckCircleIcon;
      case 'unavailable':
        return ErrorIcon;
      case 'busy':
        return WarningIcon;
      default:
        return CheckCircleIcon;
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Agents</Typography>
        <IconButton onClick={fetchAgents} size="large">
          <RefreshIcon />
        </IconButton>
      </Box>

      <Grid container spacing={3}>
        {agents.map((agent) => (
          <Grid item xs={12} md={6} lg={4} key={agent.id}>
            <Card sx={{ p: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                <Box>
                  <Typography variant="h6">{agent.name || agent.id}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Version {agent.version}
                  </Typography>
                </Box>
                <IconButton onClick={(e) => handleMenuOpen(e, agent)}>
                  <MoreVertIcon />
                </IconButton>
              </Box>

              <Box mt={2}>
                <Chip
                  icon={React.createElement(getStatusIcon(agent.status))}
                  label={agent.status}
                  sx={{
                    bgcolor: `${getStatusColor(agent.status)}20`,
                    color: getStatusColor(agent.status),
                    mr: 1,
                  }}
                />
                {agent.last_heartbeat && (
                  <Tooltip title={format(new Date(agent.last_heartbeat), 'PPpp')}>
                    <Typography variant="body2" color="text.secondary" display="inline">
                      Last seen {formatDistanceToNow(new Date(agent.last_heartbeat))} ago
                    </Typography>
                  </Tooltip>
                )}
              </Box>

              <Box mt={2}>
                <Typography variant="subtitle2">Capabilities:</Typography>
                <Box display="flex" flexWrap="wrap" gap={1} mt={1}>
                  {agent.capabilities.map((cap) => (
                    <Chip
                      key={cap}
                      label={cap}
                      size="small"
                      sx={{ bgcolor: theme.palette.grey[100] }}
                    />
                  ))}
                </Box>
              </Box>

              {metrics[agent.id] && (
                <Box mt={2}>
                  <Typography variant="subtitle2">Metrics:</Typography>
                  <Grid container spacing={2} mt={0.5}>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Operations:
                      </Typography>
                      <Typography>
                        {metrics[agent.id].operations_completed} completed
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="body2" color="text.secondary">
                        Error Rate:
                      </Typography>
                      <Typography>
                        {(metrics[agent.id].error_rate * 100).toFixed(1)}%
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              )}
            </Card>
          </Grid>
        ))}
      </Grid>

      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMaintenanceClick}>
          <BuildIcon sx={{ mr: 1 }} /> Schedule Maintenance
        </MenuItem>
      </Menu>

      <Dialog
        open={maintenanceDialog}
        onClose={() => setMaintenanceDialog(false)}
      >
        <DialogTitle>Schedule Maintenance</DialogTitle>
        <DialogContent>
          <Typography>
            Schedule maintenance for agent {selectedAgent?.name || selectedAgent?.id}?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMaintenanceDialog(false)}>Cancel</Button>
          <Button onClick={handleMaintenanceSubmit} variant="contained">
            Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AgentList;
