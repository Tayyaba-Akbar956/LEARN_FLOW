/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    swcMinify: true,
    compiler: {
        removeConsole: process.env.NODE_ENV === 'production',
    },
    experimental: {
        optimizePackageImports: [
            '@heroicons/react',
            'lucide-react',
            'date-fns',
            'lodash'
        ],
    },
    images: {
        formats: ['image/avif', 'image/webp'],
    }
};

module.exports = nextConfig;
