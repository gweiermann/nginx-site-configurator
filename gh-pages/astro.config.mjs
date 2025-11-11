import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
	integrations: [tailwind()],
	output: 'static',
	build: {
		format: 'directory'
	},
	vite: {
		server: {
			port: 4321,
			strictPort: true
		}
	},
	site: 'https://gweiermann.github.io/nginx-site-configurator/'
});
