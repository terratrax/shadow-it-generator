# Shadow IT Log Generator - Product Specification

## Overview
The Shadow IT Log Generator is a Python-based tool that creates synthetic web access logs simulating enterprise users accessing various cloud services. These logs are formatted for ingestion into Skyhigh Security's Shadow IT analysis system.

## Core Requirements

### 1. Log Format Support
The system will generate logs in McAfee/Skyhigh Secure Web Gateway format, supporting:
- **LEEF Format** (primary): `LEEF:1.0|McAfee|Web Gateway|8.2.9|<event_id>|<key=value pairs>`
- **CEF Format** (secondary): `CEF:0|McAfee|Web Gateway|7.8.2.8.0|<event_id>|<name>|<severity>|<key=value pairs>`

#### Required Log Fields
- `devTime`: Timestamp (epoch milliseconds)
- `src`: Source IP address
- `dst`: Destination IP address
- `dhost`: Destination hostname
- `usrName`: Username (email format)
- `httpStatus`: HTTP response code
- `requestMethod`: HTTP method (GET, POST, PUT, DELETE, etc.)
- `url`: Full URL requested
- `urlCategories`: URL category (provided by cloud service config)
- `blockReason`: Reason for blocking (if denied)
- `out`: Response size in bytes
- `in`: Request size in bytes
- `requestClientApplication`: User agent string
- `app`: Protocol (HTTP/HTTPS)
- `cs3`: HTTP version (HTTP/1.1, HTTP/2.0)
- `fileType`: File type if applicable
- `cn1`: Numeric block reason code
- `cs5`: Policy name

### 2. Cloud Service Configuration
Each cloud service stored as individual YAML file in `/cloud-services/` directory:

```yaml
service:
  name: "Microsoft Office 365"
  hostname: "outlook.office365.com"
  category: "Business"
  
traffic:
  avg_bytes_per_session: 1048576  # 1MB
  bytes_std_deviation: 524288     # 512KB
  avg_requests_per_session: 50
  requests_std_deviation: 20
  
access:
  allowed: true  # or false for blocked services
  block_reason: ""  # e.g., "Unsanctioned Application"
  
endpoints:
  - path: "/api/v2/messages"
    method: "GET"
    weight: 0.4  # 40% of requests
    is_api: true
  - path: "/owa/"
    method: "GET"
    weight: 0.3
    is_api: false
  - path: "/api/v2/attachments"
    method: "POST"
    weight: 0.2
    is_api: true
  - path: "/api/v2/calendar"
    method: "GET"
    weight: 0.1
    is_api: true
```

### 3. Enterprise Configuration
Single YAML file for enterprise-wide settings:

```yaml
enterprise:
  name: "Acme Corporation"
  total_users: 5000
  domain: "acme.com"
  
network:
  source_ips:
    - "10.10.0.0/16"
    - "192.168.0.0/16"
  proxy_ip: "10.10.1.100"  # Optional: if using proxy
  
user_behavior:
  working_hours:
    start: "08:00"
    end: "18:00"
    timezone: "America/New_York"
  
  user_profiles:
    normal_users:
      percentage: 70
      avg_services_per_day: 10
      service_variance: 3
    
    power_users:
      percentage: 20
      avg_services_per_day: 25
      service_variance: 5
    
    risky_users:
      percentage: 10
      avg_services_per_day: 30
      service_variance: 10
      risky_app_preference: 0.4  # 40% chance to use risky apps
  
  activity_patterns:
    peak_hours: [9, 10, 11, 14, 15, 16]
    lunch_dip: true
    weekend_activity: 0.1  # 10% of weekday activity
  
browsers:
  - user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
    weight: 0.5
  - user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.59"
    weight: 0.3
  - user_agent: "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/14.1.1"
    weight: 0.2

output:
  format: "logs/{year}/{month}/{day}/webgateway_{timestamp}.log"
  rotation: "hourly"  # hourly, daily
  compression: true
  
policies:
  - name: "Default Policy"
    id: "POL001"
```

### 4. User Generation & Behavior

#### User Types
1. **Normal Users (70%)**
   - Access 5-15 sanctioned services daily
   - Minimal risky app usage
   - Standard working hours activity

2. **Power Users (20%)**
   - Access 20-30 services daily
   - Mix of sanctioned and unsanctioned apps
   - Extended hours activity

3. **Risky Users (10%)**
   - Access 25-35 services daily
   - High percentage of unsanctioned/risky apps
   - Irregular activity patterns
   - More likely to trigger blocks

#### Activity Patterns
- **Temporal Distribution**: Bell curve centered on business hours
- **Lunch Dip**: 30% reduction in activity 12:00-13:00
- **Session Duration**: Normal distribution (mean: 30 min, std: 10 min)
- **Inter-request Timing**: Exponential distribution within sessions
- **Junk Traffic**: 30% of total traffic to popular internet sites (news, shopping, reference, etc.)
  - Adds realistic noise to log streams
  - 85% allowed, 15% blocked (inappropriate content)
  - Distributed across categories: news (25%), reference (20%), shopping (15%), blogs (15%), forums (10%), misc (15%)

### 5. Traffic Generation Algorithm

```python
# Pseudocode for traffic generation
for each_hour in simulation_period:
    active_users = calculate_active_users(hour, user_profiles)
    
    for user in active_users:
        services = select_services(user.profile, available_services)
        
        for service in services:
            session = generate_session(service, user)
            
            for request in session.requests:
                log_entry = create_log_entry(
                    timestamp=request.time,
                    user=user,
                    service=service,
                    endpoint=request.endpoint,
                    response=generate_response(service.access)
                )
                write_log(log_entry)
```

### 6. Docker Implementation

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]
```

#### CLI Interface
```bash
# Generate 30 days of logs starting from specific date
docker run -it -v $(pwd)/output:/app/output \
  -v $(pwd)/config:/app/config \
  ghcr.io/skyhighsecurity/solution-stage/shadow-it-generator:latest \
  generate --days 30 --start "2024-01-01 00:00:00"

# Additional options
  --config /app/config/enterprise.yaml
  --services /app/config/cloud-services/
  --output /app/output/
  --format leef|cef
  --compress
  --real-time  # Generate in real-time vs batch
```

### 7. Implementation Phases

#### Phase 1: Core Infrastructure
- YAML configuration parsing
- User and session generation
- Basic log formatting (LEEF)
- File output with rotation

#### Phase 2: Cloud Services & Patterns
- Implement 500+ cloud service definitions
- Realistic traffic patterns
- User behavior profiles
- Time-based activity

#### Phase 3: Advanced Features
- CEF format support
- Blocked/denied traffic simulation
- API vs web traffic differentiation
- Performance optimization for large-scale generation

### 8. Cloud Service Categories (Top 500)
Services should include but not be limited to:
- **Sanctioned**: Office 365, Salesforce, ServiceNow, Workday
- **Collaboration**: Slack, Teams, Zoom, Webex
- **Storage**: Box, Dropbox, Google Drive, OneDrive
- **Development**: GitHub, GitLab, Jira, Jenkins
- **Unsanctioned**: Personal email, social media, file sharing
- **Risky**: Torrent sites, anonymous proxies, crypto mining

### 9. Performance Requirements
- Generate 1 million log entries per hour
- Support simulation of 10,000+ users
- Configurable output rate limiting
- Memory-efficient streaming output

### 10. Validation & Testing
- Log format validation against Skyhigh parser
- Statistical validation of traffic patterns
- User behavior distribution verification
- Performance benchmarking

## Success Criteria
1. Logs successfully parse in Skyhigh Security platform
2. Shadow IT discovery identifies all configured services
3. Risk scoring aligns with configured service categories
4. Traffic patterns appear realistic in analytics dashboards
5. Performance meets or exceeds requirements