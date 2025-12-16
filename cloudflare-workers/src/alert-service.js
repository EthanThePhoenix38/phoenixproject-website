export class AlertService {
  constructor(env) {
    this.env = env;
    this.sentAlerts = new Set();
  }

  async sendLimitAlert(apiKey, usage) {
    const alertKey = `${apiKey}:${new Date().toISOString().split('T')[0]}`;

    // Only send once per day per API key
    if (this.sentAlerts.has(alertKey)) {
      return;
    }

    try {
      const response = await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.env.RESEND_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from: 'alerts@phoenixproject.dev',
          to: 'admin@phoenixproject.dev',
          subject: 'Usage Limit Reached',
          html: `
            <h2>Usage Limit Alert</h2>
            <p>API Key: <code>${apiKey}</code></p>
            <p>Daily Count: <strong>${usage.dailyCount}</strong></p>
            <p>Tier: <strong>${usage.tier}</strong></p>
            <p>Timestamp: ${new Date().toISOString()}</p>
            <hr>
            <p>Consider upgrading or scaling infrastructure.</p>
          `
        })
      });

      if (response.ok) {
        this.sentAlerts.add(alertKey);
      }
    } catch (err) {
      console.error('Alert send error:', err);
    }
  }

  async sendScaleAlert(metric, threshold) {
    try {
      await fetch('https://api.resend.com/emails', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.env.RESEND_API_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          from: 'alerts@phoenixproject.dev',
          to: 'admin@phoenixproject.dev',
          subject: 'Scale Alert - Action Required',
          html: `
            <h2>Infrastructure Scaling Required</h2>
            <p>Metric: <strong>${metric}</strong></p>
            <p>Threshold: <strong>${threshold}</strong></p>
            <p>Timestamp: ${new Date().toISOString()}</p>
            <hr>
            <p>Consider scaling up infrastructure to handle increased load.</p>
          `
        })
      });
    } catch (err) {
      console.error('Scale alert error:', err);
    }
  }
}
