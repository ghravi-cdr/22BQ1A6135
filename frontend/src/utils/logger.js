// utils/logger.js
// Logs events to localStorage
export function logEvent(type, message, data = null) {
  const logs = JSON.parse(localStorage.getItem('logs') || '[]');
  logs.push({
    timestamp: new Date().toISOString(),
    type,
    message,
    data
  });
  localStorage.setItem('logs', JSON.stringify(logs));
}

export function getLogs() {
  return JSON.parse(localStorage.getItem('logs') || '[]');
}

export function clearLogs() {
  localStorage.removeItem('logs');
}
