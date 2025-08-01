import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Alert, Grid, Box, Chip, Link } from '@mui/material';
import { logEvent } from '../utils/logger';

function StatisticsPage() {
  const [stats, setStats] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    axios.get('http://localhost:5000/stats')
      .then(res => {
        setStats(res.data);
        logEvent('API_REQUEST', 'Fetched stats', res.data);
      })
      .catch(err => {
        setError('Failed to fetch statistics');
        logEvent('API_REQUEST', 'Fetch stats failed', err.message);
      });
  }, []);

  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600, color: 'primary.main' }}>URL Shortener Analytics</Typography>
      {stats.length === 0 ? (
        <Typography>No stats available.</Typography>
      ) : (
        <Grid container spacing={3}>
          {stats.map((item, i) => (
            <Grid item xs={12} md={6} key={i}>
              <Card elevation={3} sx={{ borderRadius: 3 }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Chip label={item.shortcode} color="primary" size="small" sx={{ mr: 1 }} />
                    <Link href={item.short_url} target="_blank" rel="noopener" underline="hover">
                      {item.short_url}
                    </Link>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    <b>Original:</b> <Link href={item.original_url} target="_blank" rel="noopener" underline="hover">{item.original_url}</Link>
                  </Typography>
                  <Grid container spacing={1} sx={{ mb: 1 }}>
                    <Grid item xs={4}><b>Created:</b><br />{item.created_at}</Grid>
                    <Grid item xs={4}><b>Expiry:</b><br />{item.expiry}</Grid>
                    <Grid item xs={4}><b>Clicks:</b><br /><Chip label={item.clicks} color={item.clicks > 0 ? 'success' : 'default'} size="small" /></Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
}

export default StatisticsPage;
