# Troubleshooting Guide
# Hướng dẫn xử lý sự cố

## Common Issues and Solutions

### 1. Docker và Container Issues

#### Container không khởi động
**Symptoms:**
- `docker-compose up` failed
- Services không available
- Port conflicts

**Solutions:**
```bash
# Check port usage
netstat -tulpn | grep :5678

# Kill processes using ports
sudo kill -9 <PID>

# Clean up containers
docker-compose down -v
docker system prune -f

# Restart with clean state
docker-compose up -d --force-recreate
```

#### Out of memory errors
**Symptoms:**
- Container crashes randomly
- n8n becomes unresponsive
- Database connection fails

**Solutions:**
```bash
# Check memory usage
docker stats

# Increase Docker memory limits
# In Docker Desktop: Settings > Resources > Memory

# Add memory limits to docker-compose.yml
services:
  n8n:
    mem_limit: 2g
```

### 2. n8n Issues

#### Cannot access n8n interface
**Symptoms:**
- Browser shows connection refused
- 502 Bad Gateway error
- Authentication fails

**Solutions:**
```bash
# Check n8n container status
docker-compose logs n8n

# Restart n8n service
docker-compose restart n8n

# Check port mapping
docker-compose ps
```

#### Workflow execution fails
**Symptoms:**
- Workflow stops midway
- Nodes show error status
- No output generated

**Solutions:**
1. **Check node configuration:**
   - Verify all required fields are filled
   - Check API credentials
   - Validate data flow between nodes

2. **Debug with test data:**
   - Use "Execute Workflow" with sample data
   - Check individual node outputs
   - Enable debug mode

3. **Review execution logs:**
   - Go to "Executions" in n8n
   - Click failed execution
   - Review error messages

### 3. API Integration Issues

#### Gmail API Problems
**Symptoms:**
- OAuth authentication fails
- No emails retrieved
- Permission denied errors

**Solutions:**
```bash
# Test OAuth flow manually
curl -X POST "https://oauth2.googleapis.com/token" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "grant_type=refresh_token"

# Verify API access
curl -X GET "https://www.googleapis.com/gmail/v1/users/me/profile" \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

**Common fixes:**
- Re-generate refresh token
- Check OAuth scopes
- Verify client ID/secret
- Enable Gmail API in Google Cloud Console

#### OpenAI API Issues
**Symptoms:**
- API key invalid
- Rate limit exceeded
- Model not available

**Solutions:**
```bash
# Test API key
curl -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hello"}]}'
```

**Common fixes:**
- Verify API key validity
- Check usage limits
- Use correct model name
- Implement retry logic

#### Slack API Problems
**Symptoms:**
- Webhook URL not working
- Bot permissions denied
- Channel not found

**Solutions:**
```bash
# Test webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test message"}' \
  YOUR_SLACK_WEBHOOK_URL

# Test bot token
curl -X POST -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"channel":"#general","text":"Test"}' \
  https://slack.com/api/chat.postMessage
```

**Common fixes:**
- Regenerate webhook URL
- Check bot permissions
- Verify channel ID
- Ensure bot is in workspace

### 4. Database Issues

#### Connection refused
**Symptoms:**
- Cannot connect to PostgreSQL
- Authentication failed
- Database not found

**Solutions:**
```bash
# Check database container
docker-compose logs postgres

# Test connection manually
docker-compose exec postgres psql -U n8n_user -d n8n_workflow -c "SELECT version();"

# Reset database
docker-compose down -v
docker-compose up -d postgres
```

#### Table not found
**Symptoms:**
- SQL errors for missing tables
- Workflow fails at database nodes

**Solutions:**
```sql
-- Check if tables exist
\dt

-- Create tables manually
\i /docker-entrypoint-initdb.d/database-setup.sql
```

### 5. Performance Issues

#### Slow workflow execution
**Symptoms:**
- Workflows take minutes to complete
- High CPU/memory usage
- Timeouts on API calls

**Solutions:**
1. **Optimize API calls:**
   - Reduce OpenAI token usage
   - Cache repeated requests
   - Use appropriate models

2. **Database optimization:**
   - Add indexes
   - Optimize queries
   - Use connection pooling

3. **Workflow optimization:**
   - Remove unnecessary nodes
   - Use parallel execution
   - Implement early exits

#### Memory leaks
**Symptoms:**
- Container memory increases over time
- n8n becomes slow
- Random crashes

**Solutions:**
```bash
# Monitor memory usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Restart services periodically
docker-compose restart

# Set memory limits in docker-compose.yml
```

### 6. Debugging Techniques

#### Enable debug logging
```yaml
# In docker-compose.yml
services:
  n8n:
    environment:
      - N8N_LOG_LEVEL=debug
      - NODE_ENV=development
```

#### Test individual components
```bash
# Test database connection
docker-compose exec postgres psql -U n8n_user -d n8n_workflow

# Test n8n health
curl http://localhost:5678/healthz

# Test API endpoints
curl -X GET "http://localhost:5678/api/v1/workflows"
```

#### Monitor workflow execution
1. Use n8n's built-in execution history
2. Check individual node outputs
3. Review error messages
4. Test with sample data

### 7. Recovery Procedures

#### Complete system reset
```bash
# Stop all services
docker-compose down -v

# Remove all data (WARNING: This deletes all data)
docker system prune -a --volumes

# Rebuild from scratch
docker-compose up -d --build
```

#### Database recovery
```bash
# Backup current data
docker-compose exec postgres pg_dump -U n8n_user n8n_workflow > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U n8n_user n8n_workflow < backup.sql
```

#### Workflow recovery
1. Export workflows from n8n UI
2. Save to version control
3. Import to fresh n8n instance

### 8. Monitoring and Alerts

#### Health checks
```bash
# Create health check script
#!/bin/bash
echo "Checking n8n health..."
curl -f http://localhost:5678/healthz || echo "n8n is down"

echo "Checking database..."
docker-compose exec postgres pg_isready -U n8n_user || echo "Database is down"

echo "Checking disk space..."
df -h | grep -E "/$|/docker"
```

#### Log monitoring
```bash
# Monitor all services
docker-compose logs -f

# Monitor specific service
docker-compose logs -f n8n

# Filter errors
docker-compose logs | grep ERROR
```

### 9. Best Practices

#### Prevention
1. Regular backups
2. Monitor resource usage
3. Keep dependencies updated
4. Use version control for workflows
5. Document all configurations

#### Maintenance
1. Weekly system health checks
2. Monthly security updates
3. Quarterly performance reviews
4. Annual disaster recovery testing

#### Documentation
1. Keep troubleshooting guide updated
2. Document all custom configurations
3. Maintain change logs
4. Create runbooks for common issues

### 10. Emergency Contacts

#### Internal resources
- System administrator
- Database administrator
- Network team
- Security team

#### External resources
- n8n community: https://community.n8n.io/
- n8n documentation: https://docs.n8n.io/
- Docker support: https://docs.docker.com/
- PostgreSQL support: https://www.postgresql.org/support/
