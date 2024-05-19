/** @type {import('next').NextConfig} */
const nextConfig = {
    output: "standalone",
    reactStrictMode: false, /* @note: To prevent duplicated call of useEffect */
    swcMinify: true,
    images: {
        domains: ['iris2.gettimely.com'],
    },

    async rewrites() {
        return [{
            source: "/api/:path*",
            // Change to your backend URL in production
            // change 
            destination: "https://capybara-backend-Capybara.app.secoder.net/:path*",
            // destination: "http://localhost:9099/:path*",
        }];
    }
};

// eslint-disable-next-line no-undef
module.exports = nextConfig;
