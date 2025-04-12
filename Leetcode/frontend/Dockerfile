# Use an official Node.js runtime as a parent image
FROM node:16-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package files to install dependencies
COPY package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the rest of your application code
COPY . .

# Expose the port the app runs on (e.g., 3000)
EXPOSE 3000

# Start the frontend application
CMD ["npm", "start"]
