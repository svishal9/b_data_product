# Multi-stage build for SCB Data Product Frontend
# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Build argument for API base URL (can be overridden at build time)
ARG VITE_API_BASE_URL="/api"
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Copy package files
COPY src/frontend/package*.json ./
COPY src/frontend/pnpm-workspace.yaml ./

# Install dependencies
RUN npm install

# Copy source code
COPY src/frontend/src ./src
COPY src/frontend/index.html ./
COPY src/frontend/vite.config.ts ./
COPY src/frontend/tsconfig.json ./
COPY src/frontend/tailwindcss.config.js* ./
COPY src/frontend/postcss.config.mjs* ./

# Build the application with API base URL
RUN VITE_API_BASE_URL=$VITE_API_BASE_URL npm run build

# Stage 2: Serve with lightweight nginx
FROM nginx:alpine

# Copy nginx configuration
COPY docker-k8s/frontend/nginx.conf /etc/nginx/nginx.conf
COPY docker-k8s/frontend/default.conf /etc/nginx/conf.d/default.conf

# Copy custom entrypoint script
COPY docker-k8s/frontend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Copy built application from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Fix nginx cache and temp directories for K8s environments
RUN mkdir -p /var/cache/nginx/client_temp && \
    mkdir -p /var/cache/nginx/proxy_temp && \
    mkdir -p /var/cache/nginx/fastcgi_temp && \
    mkdir -p /var/run && \
    chmod -R 777 /var/cache/nginx && \
    chmod -R 777 /var/run && \
    chmod -R 777 /etc/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/index.html || exit 1

# Expose port
EXPOSE 80

# Use custom entrypoint to avoid nginx init script permission issues
ENTRYPOINT ["/entrypoint.sh"]

