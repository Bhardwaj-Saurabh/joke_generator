FROM nginx:alpine

# Copy static assets to Nginx serve directory
COPY static /usr/share/nginx/html

# Copy custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
