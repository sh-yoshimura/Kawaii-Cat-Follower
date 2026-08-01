# Build & Production Stage using Node.js Alpine
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package.json and install production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy application files
COPY server.js ./
COPY public/ ./public/

# Environment configuration
ENV NODE_ENV=production
ENV PORT=3000

# Expose app port
EXPOSE 3000

# Run non-root user for security best practice
USER node

# Healthcheck for container health monitoring
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Start server
CMD ["node", "server.js"]
