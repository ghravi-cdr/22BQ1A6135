import React, { useState } from 'react';
import { TextField, Button, Grid, Alert, Box, Typography } from '@mui/material';
import axios from 'axios';
import { logEvent } from '../utils/logger';

const initialForm = { url: '', expiry_minutes: 30, shortcode: '' };

function ShortenerForm({ onShortened }) {
  const [forms, setForms] = useState([ { ...initialForm } ]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (idx, field, value) => {
    const updated = forms.map((f, i) => i === idx ? { ...f, [field]: value } : f);
    setForms(updated);
  };

  const addForm = () => {
    if (forms.length < 5) setForms([...forms, { ...initialForm }]);
  };

  const removeForm = idx => {
    if (forms.length > 1) setForms(forms.filter((_, i) => i !== idx));
  };

  const validate = () => {
    const errs = forms.map((f, i) => {
      if (!/^https?:\/\//.test(f.url)) return `Form ${i+1}: URL must start with http/https.`;
      if (f.expiry_minutes && (!Number.isInteger(Number(f.expiry_minutes)) || Number(f.expiry_minutes) <= 0)) return `Form ${i+1}: Validity must be a positive integer.`;
      if (f.shortcode && !/^[a-zA-Z0-9]+$/.test(f.shortcode)) return `Form ${i+1}: Shortcode must be alphanumeric.`;
      return null;
    }).filter(Boolean);
    return errs;
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setErrors([]);
    const errs = validate();
    if (errs.length) {
      setErrors(errs);
      logEvent('VALIDATION_ERROR', 'Validation failed', errs);
      return;
    }
    setLoading(true);
    try {
      const results = [];
      const now = new Date();
      for (const f of forms) {
        const res = await axios.post('http://localhost:5000/shorturls', {
          url: f.url,
          expiry_minutes: f.expiry_minutes,
          shortcode: f.shortcode || undefined
        });
        // Calculate expiry time in frontend for display
        const expiryDate = new Date(now.getTime() + (Number(f.expiry_minutes) || 30) * 60000);
        results.push({ ...res.data, expiry: expiryDate.toLocaleString() });
        logEvent('API_REQUEST', 'Shorten URL', res.data);
      }
      onShortened(results);
      setForms([ { ...initialForm } ]);
    } catch (err) {
      const msg = err.response?.data?.error || 'API error';
      setErrors([msg]);
      logEvent('API_REQUEST', 'Shorten URL failed', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 3 }}>
      {errors.length > 0 && errors.map((e, i) => <Alert severity="error" key={i}>{e}</Alert>)}
      {forms.map((f, idx) => (
        <Grid container spacing={2} alignItems="center" key={idx} sx={{ mb: 1 }}>
          <Grid item xs={12} sm={5}>
            <TextField label="Original URL" value={f.url} onChange={e => handleChange(idx, 'url', e.target.value)} required fullWidth />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField label="Validity (min)" type="number" value={f.expiry_minutes} onChange={e => handleChange(idx, 'expiry_minutes', e.target.value)} fullWidth />
          </Grid>
          <Grid item xs={12} sm={3}>
            <TextField label="Custom Shortcode" value={f.shortcode} onChange={e => handleChange(idx, 'shortcode', e.target.value)} fullWidth />
          </Grid>
          <Grid item xs={12} sm={1}>
            {forms.length > 1 && <Button color="error" onClick={() => removeForm(idx)}>-</Button>}
          </Grid>
        </Grid>
      ))}
      <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
        <Button variant="contained" onClick={addForm} disabled={forms.length >= 5}>Add</Button>
        <Button variant="contained" type="submit" disabled={loading}>Shorten</Button>
      </Box>
      <Typography variant="caption" color="text.secondary">You can shorten up to 5 URLs at once.</Typography>
    </Box>
  );
}

export default ShortenerForm;
