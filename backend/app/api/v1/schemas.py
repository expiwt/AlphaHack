frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  container_name: alfabank-frontend
  environment:
    VITE_API_URL: /api/v1  # Относительный путь через Nginx
  ports:
    - "3000:5173"
  volumes:
    - ./frontend/src:/app/src
  depends_on:
    - backend
  networks:
    - alfabank-network
  command: npm run dev -- --host
