import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  typography: {
    fontFamily: 'Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },
  palette: {
    mode: 'light',
    primary: {
      main: '#2454d6',
    },
    secondary: {
      main: '#0f8f7a',
    },
    background: {
      default: '#f7f8fa',
    },
  },
  shape: {
    borderRadius: 8,
  },
});
