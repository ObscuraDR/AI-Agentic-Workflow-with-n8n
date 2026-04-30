# Deployment Guide
# Hướng dẫn triển khai

## Production Deployment Options

### 1. Docker Compose (Recommended for Small-Medium Scale)

#### Prerequisites
- Docker and Docker Compose installed
- Server with minimum 4GB RAM
- SSL certificate (optional but recommended)
- Backup strategy

#### Production Docker Compose

```yaml
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    container_name: n8n_prod
    restart: always
    ports:
      - "127.0.0.1:5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - N8N_HOST=${N8N_HOST}
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=${WEBHOOK_URL}
      - GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
      - N8N_SECURE_COOKIE=true
      - N8N_LOG_LEVEL=info
      - NODE_ENV=production
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/workflows:/home/node/.n8n/workflows
      - ./logs:/home/node/.n8n/logs
    networks:
      - n8n_network
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    container_name: n8n_postgres_prod
    restart: always
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - n8n_network
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c pg_stat_statements.track=all
      -c max_connections=200
      -c shared_buffers=256MB
      -c effective_cache_size=1GB

  redis:
    image: redis:7-alpine
    container_name: n8n_redis_prod
    restart: always
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - n8n_network

  nginx:
    image: nginx:alpine
    container_name: n8n_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    networks:
      - n8n_network
    depends_on:
      - n8n

volumes:
  n8n_data:
  postgres_data:
  redis_data:

networks:
  n8n_network:
    driver: bridge
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://n8n:5678;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### 2. Kubernetes Deployment

#### Namespace and ConfigMap

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: n8n-workflow
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: n8n-config
  namespace: n8n-workflow
data:
  N8N_BASIC_AUTH_ACTIVE: "true"
  N8N_HOST: "your-domain.com"
  N8N_PORT: "5678"
  N8N_PROTOCOL: "https"
  GENERIC_TIMEZONE: "Asia/Ho_Chi_Minh"
  N8N_SECURE_COOKIE: "true"
  N8N_LOG_LEVEL: "info"
  NODE_ENV: "production"
```

#### Secret Configuration

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: n8n-secrets
  namespace: n8n-workflow
type: Opaque
data:
  N8N_BASIC_AUTH_USER: <base64-encoded-username>
  N8N_BASIC_AUTH_PASSWORD: <base64-encoded-password>
  POSTGRES_DB: <base64-encoded-db-name>
  POSTGRES_USER: <base64-encoded-db-user>
  POSTGRES_PASSWORD: <base64-encoded-db-password>
  OPENAI_API_KEY: <base64-encoded-openai-key>
  GMAIL_CLIENT_ID: <base64-encoded-gmail-client-id>
  GMAIL_CLIENT_SECRET: <base64-encoded-gmail-secret>
```

#### PostgreSQL Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: n8n-workflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_DB
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: POSTGRES_DB
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: POSTGRES_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: n8n-secrets
              key: POSTGRES_PASSWORD
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
```

### 3. Cloud Deployment Options

#### AWS ECS

1. **Create ECS Cluster**
   ```bash
   aws ecs create-cluster --cluster-name n8n-workflow
   ```

2. **Create Task Definition**
   ```json
   {
     "family": "n8n-task",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "n8n",
         "image": "docker.n8n.io/n8nio/n8n",
         "portMappings": [
           {
             "containerPort": 5678,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "N8N_BASIC_AUTH_ACTIVE",
             "value": "true"
           }
         ],
         "secrets": [
           {
             "name": "N8N_BASIC_AUTH_PASSWORD",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:n8n/password"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/n8n",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

#### Google Cloud Run

1. **Build and Push Image**
   ```bash
   gcloud builds submit --tag gcr.io/project-id/n8n-workflow
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy n8n-workflow \
     --image gcr.io/project-id/n8n-workflow \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars N8N_BASIC_AUTH_ACTIVE=true \
     --set-secrets N8N_BASIC_AUTH_PASSWORD=n8n-password:latest
   ```

## Security Configuration

### 1. Environment Variables Security

```bash
# Use Docker secrets or Kubernetes secrets
# Never commit sensitive data to version control

# Example: Using Docker secrets
echo "your-secret-value" | docker secret create n8n_password -

# Example: Using Kubernetes secrets
kubectl create secret generic n8n-secrets \
  --from-literal=OPENAI_API_KEY="your-openai-key" \
  --from-literal=GMAIL_CLIENT_SECRET="your-gmail-secret"
```

### 2. Network Security

```yaml
# Docker Compose with isolated network
networks:
  n8n_internal:
    driver: bridge
    internal: true
  n8n_external:
    driver: bridge

services:
  n8n:
    networks:
      - n8n_internal
      - n8n_external
  
  postgres:
    networks:
      - n8n_internal  # Only accessible internally
```

### 3. SSL/TLS Configuration

```bash
# Generate self-signed certificate (for development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem

# Use Let's Encrypt (for production)
certbot certonly --standalone -d your-domain.com
```

## Monitoring and Logging

### 1. Application Monitoring

```yaml
# Prometheus configuration
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'n8n'
    static_configs:
      - targets: ['n8n:5678']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
```

### 2. Log Aggregation

```yaml
# ELK Stack for logging
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

### 3. Health Checks

```yaml
# Docker Compose health checks
services:
  n8n:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5678/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  postgres:
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
```

## Backup and Recovery

### 1. Database Backup

```bash
#!/bin/bash
# backup-postgres.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_CONTAINER="n8n_postgres_prod"

# Create backup
docker exec $POSTGRES_CONTAINER pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > $BACKUP_DIR/backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Remove old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

### 2. n8n Data Backup

```bash
#!/bin/bash
# backup-n8n.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
N8N_DATA_DIR="/var/lib/docker/volumes/ai-agentic-workflow_n8n_data/_data"

# Create tar backup
tar -czf $BACKUP_DIR/n8n_data_$DATE.tar.gz -C $N8N_DATA_DIR .

echo "n8n data backup completed: n8n_data_$DATE.tar.gz"
```

### 3. Automated Backup with Cron

```bash
# Add to crontab
# 0 2 * * * /path/to/backup-postgres.sh
# 0 3 * * 0 /path/to/backup-n8n.sh  # Weekly n8n backup
```

## Performance Optimization

### 1. Database Optimization

```sql
-- PostgreSQL performance tuning
-- Add to postgresql.conf

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 200
shared_preload_libraries = 'pg_stat_statements'

# Logging settings
log_statement = 'all'
log_duration = on
log_min_duration_statement = 1000
```

### 2. n8n Performance

```yaml
# Environment variables for performance
environment:
  - N8N_EXECUTORS_WORKERS=4
  - N8N_PAYLOAD_SIZE_MAX=16
  - N8N_METRICS=true
  - N8N_QUEUE_BULL_REDIS_OPTIONS_CONCURRENCY=10
```

### 3. Caching Strategy

```yaml
# Redis configuration for caching
services:
  redis:
    image: redis:7-alpine
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --appendonly yes
      --save 900 1
      --save 300 10
      --save 60 10000
```

## Scaling Strategies

### 1. Horizontal Scaling

```yaml
# Multiple n8n instances with load balancer
services:
  n8n-1:
    image: docker.n8n.io/n8nio/n8n
    environment:
      - N8N_QUEUE_BULL_REDIS_OPTIONS_CONCURRENCY=5
    
  n8n-2:
    image: docker.n8n.io/n8nio/n8n
    environment:
      - N8N_QUEUE_BULL_REDIS_OPTIONS_CONCURRENCY=5
    
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/load-balancer.conf:/etc/nginx/conf.d/default.conf
```

### 2. Database Scaling

```yaml
# Read replica for PostgreSQL
services:
  postgres-master:
    image: postgres:15
    environment:
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=replicator_password
    
  postgres-replica:
    image: postgres:15
    environment:
      - PGUSER=replicator
      - POSTGRES_MASTER_SERVICE=postgres-master
      - POSTGRES_REPLICATION_USER=replicator
      - POSTGRES_REPLICATION_PASSWORD=replicator_password
```

## Troubleshooting Production Issues

### 1. Common Issues and Solutions

#### Memory Issues
```bash
# Check memory usage
docker stats

# Increase memory limits
docker-compose up -d --scale n8n=2
```

#### Database Connection Issues
```bash
# Check database connections
docker exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT count(*) FROM pg_stat_activity;"

# Kill idle connections
docker exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle';"
```

#### Workflow Execution Issues
```bash
# Check n8n logs
docker logs n8n_prod --tail 100

# Restart specific workflow
curl -X POST "http://localhost:5678/api/v1/workflows/{workflow_id}/activate"
```

### 2. Performance Monitoring

```bash
# Monitor system resources
htop
iotop
docker stats --no-stream

# Monitor database performance
docker exec postgres psql -U $POSTGRES_USER -d $POSTGRES_DB -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"
```

## Maintenance Procedures

### 1. Regular Maintenance Tasks

```bash
#!/bin/bash
# maintenance.sh

echo "Starting maintenance tasks..."

# Clean up Docker images
docker system prune -f

# Restart services
docker-compose restart

# Check health status
docker-compose ps

# Update workflow definitions
curl -X POST "http://localhost:5678/api/v1/workflows" -d @workflows/backup.json

echo "Maintenance completed"
```

### 2. Security Updates

```bash
#!/bin/bash
# security-update.sh

# Update Docker images
docker-compose pull

# Restart with new images
docker-compose up -d

# Verify services are running
docker-compose ps

echo "Security updates completed"
```

This deployment guide provides comprehensive instructions for deploying the AI Agentic Workflow with n8n in production environments, including security configurations, monitoring, backup strategies, and troubleshooting procedures.
