const express = require('express');
const cors = require('cors');
const path = require('path');
const { spawn } = require('child_process');

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '..', 'public', 'homepage.html'));
});
let alerts = [];

function fetchSentinelAlerts() {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(__dirname, '..', 'python backend', 'main.py');
        const pythonCommand = process.platform === 'win32' ? 'python' : 'python3';

        const pyProcess = spawn(pythonCommand, [scriptPath]);

        let stdoutData = '';
        let stderrData = '';

        pyProcess.stdout.on('data', (data) => {
            stdoutData += data.toString();
        });

        pyProcess.stderr.on('data', (data) => {
            stderrData += data.toString();
        });

        pyProcess.on('close', (code) => {
            if (code !== 0) {
                return reject(new Error(`Python script exited with code ${code}: ${stderrData}`));
            }
            try {
                const parsed = JSON.parse(stdoutData.trim());
                resolve(parsed);
            } catch (err) {
                reject(new Error(`JSON Parse Error: ${err.message} | Raw: ${stdoutData}`));
            }
        });
    });
}

async function updateAlerts() {
    try {
        const freshAlerts = await fetchSentinelAlerts();
        alerts = freshAlerts;
        console.log(`[Sentinel] Synced ${alerts.length} high-impact catalysts at ${new Date().toISOString()}`);
    } catch (err) {
        console.error(`[Sentinel Error] ${err.message}`);
    }
}

app.get('/api/signal/info/data', (req, res) => {
    res.json({
        status: "success",
        timestamp: new Date().toISOString(),
        count: alerts.length,
        data: alerts
    });
});

app.listen(port, () => {
    console.log(`Macro Surveillance Server listening on port ${port}`);
    updateAlerts();
});


setInterval(updateAlerts, 1000 * 60 * 5);