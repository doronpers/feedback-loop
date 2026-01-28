import { ThemeProvider, CssBaseline } from '@mui/material';
import { theme } from './theme';
import { Dashboard } from './components/Dashboard';

function App() {
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Dashboard />
        </ThemeProvider>
    );
}

export default App;
