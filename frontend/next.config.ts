import type { NextConfig } from "next";
import crypto from "crypto";

const nextConfig: NextConfig = {
  // Development settings
  allowedDevOrigins: ["http://localhost:3000", "http://localhost:8000"],

  // Image optimization
  images: {
    domains: ["localhost"],
    unoptimized: true,
  },

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  },

  // CORS and security
  async headers() {
    return [
      {
        source: "/api/:path*",
        headers: [
          { key: "Access-Control-Allow-Credentials", value: "true" },
          { key: "Access-Control-Allow-Origin", value: "*" },
          {
            key: "Access-Control-Allow-Methods",
            value: "GET,OPTIONS,PATCH,DELETE,POST,PUT",
          },
          {
            key: "Access-Control-Allow-Headers",
            value:
              "X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version",
          },
        ],
      },
    ];
  },

  // Rewrites for API proxy
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: process.env.NEXT_PUBLIC_API_URL
          ? `${process.env.NEXT_PUBLIC_API_URL}/api/:path*`
          : "http://localhost:8000/api/:path*",
      },
    ];
  },

  // Build optimizations
  // webpack: (config, { dev, isServer }) => {
  //   // Optimize for RAG application
  //   if (!dev && !isServer) {
  //     config.optimization.splitChunks = {
  //       chunks: "all",
  //       cacheGroups: {
  //         default: false,
  //         vendors: false,
  //         framework: {
  //           chunks: "all",
  //           name: "framework",
  //           test: /[\\/]node_modules[\\/](react|react-dom|scheduler|prop-types|use-subscription)[\\/]/,
  //           priority: 40,
  //           enforce: true,
  //         },
  //         lib: {
  //           test(module: any) {
  //             return (
  //               module.size() > 160000 &&
  //               /node_modules[/\\]/.test(module.identifier())
  //             );
  //           },
  //           name(module: any) {
  //             const hash = crypto.createHash("sha1");
  //             hash.update(module.identifier());
  //             return hash.digest("hex").substring(0, 8);
  //           },
  //           priority: 30,
  //           minChunks: 1,
  //           reuseExistingChunk: true,
  //         },
  //         commons: {
  //           name: "commons",
  //           chunks: "all",
  //           minChunks: 2,
  //           priority: 20,
  //         },
  //       },
  //     };
  //   }

  //   return config;
  // },

  // Experimental features
  experimental: {
    optimizeCss: true,
    optimizePackageImports: ["lucide-react", "@radix-ui/react-icons"],
  },

  // Output configuration
  output: "standalone",

  // Trailing slash
  trailingSlash: false,

  // Strict mode
  reactStrictMode: true,
};

export default nextConfig;
