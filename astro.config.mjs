// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import starlightThemeRapide from 'starlight-theme-rapide';
import vercel from '@astrojs/vercel';

// https://astro.build/config
export default defineConfig({
    site: 'https://docs-gilt-eta.vercel.app/', // TODO: switch to hegel.dev
	integrations: [
		starlight({
			title: 'Hegel',
			social: [{ icon: 'github', label: 'GitHub', href: 'https://github.com/hegeldev' }],
			sidebar: [
				{
					label: 'Introduction',
					autogenerate: { directory: 'intro' },
				},
				{
					label: 'Libraries',
					items: [
						{ label: 'hegel-rust', link: 'https://github.com/hegeldev/hegel-rust', attrs: { target: '_blank', class: 'external-link' } },
						{ label: 'hegel-go', link: 'https://github.com/hegeldev/hegel-go', attrs: { target: '_blank', class: 'external-link' } },
					],
				},
				{
					label: 'How-to guides',
					autogenerate: { directory: 'how-to' },
				},
				{
					label: 'Explanation',
					autogenerate: { directory: 'explanation' },
				},
				{
					label: 'Reference',
					items: [
						{ slug: 'reference/installation' },
						{ slug: 'reference/protocol' },
					],
				},
				{
					slug: 'reference/stability',
				},
			],
            customCss: ['./src/styles/style.css'],
            plugins: [ starlightThemeRapide() ],
		}),
	],
    adapter: vercel({
        webAnalytics: { enabled: true },
    }),
});
