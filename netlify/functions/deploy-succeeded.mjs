// Netlify runs this automatically when a deploy is published.
import { notifyDiscord } from '../lib/discord.mjs';

export const handler = (event) => notifyDiscord(event, {
    title: '✅ Site published',
    color: 'success',
});
