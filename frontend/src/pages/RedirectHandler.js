import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Alert, CircularProgress, Box } from '@mui/material';
import { logEvent } from '../utils/logger';

function RedirectHandler() {
  const { shortcode } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`http://localhost:5000/${shortcode}`)
      .then(res => {
        logEvent('API_REQUEST', 'Redirect success', res.data);
        setTimeout(() => {
          window.location.href = res.data.original_url || res.request.responseURL;
        }, 1500);
        setLoading(false);
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Shortcode not found or expired');
        logEvent('API_REQUEST', 'Redirect failed', err.message);
        setLoading(false);
      });
  }, [shortcode, navigate]);

  if (loading) return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 6 }}>
      <CircularProgress sx={{ mb: 2 }} />
      <span style={{ fontSize: 18, color: '#1976d2' }}>Redirecting to your destination...</span>
    </Box>
  );
  if (error) return <Alert severity="error">{error}</Alert>;
  return null;
}

export default RedirectHandler;
