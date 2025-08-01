import React from 'react';
import { List, ListItem, ListItemText, Paper, Typography } from '@mui/material';
import { useNavigate } from 'react-router-dom';

function ShortenedList({ items }) {
  const navigate = useNavigate();
  if (!items || items.length === 0) return null;
  return (
    <Paper sx={{ mt: 2, p: 2 }}>
      <Typography variant="h6">Shortened URLs</Typography>
      <List>
        {items.map((item, i) => {
          // Extract the shortcode from the URL for navigation
          const url = new URL(item.shortened_url);
          const shortcode = url.pathname.replace(/^\//, '');
          return (
            <ListItem key={i} divider>
              <ListItemText
                primary={
                  <a
                    href={item.shortened_url}
                    onClick={e => {
                      e.preventDefault();
                      navigate(`/${shortcode}`);
                    }}
                    style={{ cursor: 'pointer', color: '#1976d2', textDecoration: 'underline' }}
                  >
                    {item.shortened_url}
                  </a>
                }
                secondary={`Expires at: ${item.expiry || 'N/A'}`}
              />
            </ListItem>
          );
        })}
      </List>
    </Paper>
  );
}

export default ShortenedList;
