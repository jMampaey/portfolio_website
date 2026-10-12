// Posts a Netlify deploy event to Discord. The webhook URL is set in the Netlify UI
// as the DISCORD_WEBHOOK_URL environment variable (never commit it).

const COLORS = {
    success: 0x2ecc71,
    failure: 0xe74c3c,
};

function truncate(text, max) {
    if (!text) return '';
    return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

export async function notifyDiscord(event, { title, color, includeError = false }) {
    const webhookUrl = process.env.DISCORD_WEBHOOK_URL;
    if (!webhookUrl) {
        console.warn('DISCORD_WEBHOOK_URL is not set, skipping Discord notification');
        return { statusCode: 200 };
    }

    const deploy = JSON.parse(event.body).payload;
    const deployLogUrl = `${deploy.admin_url}/deploys/${deploy.id}`;
    const siteUrl = deploy.context === 'production' ? deploy.ssl_url : deploy.deploy_ssl_url;

    const fields = [
        { name: 'Branch', value: deploy.branch || 'unknown', inline: true },
        { name: 'Context', value: deploy.context || 'unknown', inline: true },
    ];
    if (deploy.deploy_time) {
        fields.push({ name: 'Build time', value: `${deploy.deploy_time}s`, inline: true });
    }
    if (deploy.title) {
        const commit = deploy.commit_ref ? ` (${deploy.commit_ref.slice(0, 7)})` : '';
        fields.push({ name: 'Commit', value: truncate(`${deploy.title}${commit}`, 1024) });
    }
    if (includeError && deploy.error_message) {
        fields.push({ name: 'Error', value: truncate(deploy.error_message, 1024) });
    }
    fields.push({ name: 'Links', value: `[Site](${siteUrl}) · [Deploy log](${deployLogUrl})` });

    const response = await fetch(webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: 'Netlify',
            embeds: [{
                title,
                url: deployLogUrl,
                color: COLORS[color],
                fields,
                timestamp: new Date().toISOString(),
            }],
        }),
    });

    if (!response.ok) {
        console.error(`Discord webhook failed: ${response.status} ${await response.text()}`);
    }
    return { statusCode: 200 };
}
