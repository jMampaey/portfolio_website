// Netlify runs this automatically when a deploy fails.
import { notifyDiscord } from '../lib/discord.mjs';

export const handler = (event) => notifyDiscord(event, {
    title: '❌ Deploy failed',
    color: 'failure',
    includeError: true,
});
