# First stage: Build project
FROM node as build

ARG NPM_BUILD_COMMAND=build

# Copy files and install dependencies
COPY ./ /
RUN npm install

# Build project
RUN npm run $NPM_BUILD_COMMAND


# Second stage: Server to deliver files
FROM nginx:1.15-alpine

# Copy files from first stage
COPY --from=build /index.html /var/www/
COPY --from=build /dist /var/www/dist

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
