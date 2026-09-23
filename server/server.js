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

require('dotenv').config(); 

function fetchSentinelAlerts() {
    return new Promise((resolve, reject) => {
        const scriptPath = path.join(__dirname, '..', 'python backend', 'main.py');
        
        
        const pythonCommand = process.env.PYTHON_BIN || (process.platform === 'win32' ? 'python' : 'python3');

        const pyProcess = spawn(pythonCommand, ['-u', scriptPath]);

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
                const jsonStart = stdoutData.indexOf('[');
                const jsonEnd = stdoutData.lastIndexOf(']');

                if (jsonStart === -1 || jsonEnd === -1) {
                    if (stdoutData.includes('[]')) return resolve([]);
                    return reject(new Error(`No valid JSON found in stdout | Logs: ${stderrData}`));
                }

                const cleanedJson = stdoutData.substring(jsonStart, jsonEnd + 1);
                resolve(JSON.parse(cleanedJson));
            } catch (err) {
                reject(new Error(`JSON Parse Error: ${err.message}`));
            }
        });

        pyProcess.on('error', (err) => {
            reject(new Error(`Failed to start subprocess: ${err.message}`));
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


setInterval(updateAlerts, 1000 * 60 * 10);