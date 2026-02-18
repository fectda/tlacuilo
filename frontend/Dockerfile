FROM node:20-alpine

WORKDIR /app

COPY package*.json ./

# Install dependencies if node_modules doesn't exist (e.g. initial build)
RUN npm install

# Copy source (not used in dev due to volume mount, but good for build completeness)
COPY . .

# Expose Vite default port
EXPOSE 5173

# Run dev server with host flag for container access
CMD ["npm", "run", "dev", "--", "--host"]
