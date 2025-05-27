# Shadow IT Log Generator

A Python tool that generates realistic web gateway logs simulating enterprise users accessing cloud services, including both sanctioned and shadow IT applications.

## Features

- **Realistic Log Generation**: Creates McAfee Web Gateway logs in LEEF and CEF formats
- **499 Pre-configured Cloud Services**: Each with realistic traffic patterns and access controls
- **User Behavior Simulation**: Multiple user profiles with different usage patterns  
- **Junk Traffic Generation**: Adds realistic noise from general internet browsing (30% of total traffic)
- **Time-based Patterns**: Business hours, lunch breaks, weekends
- **International User Names**: Realistic names from multiple countries (US, UK, India, Germany, etc.)

## Architecture

### Configuration Structure

```
config/
├── enterprise.yaml           # Main enterprise configuration
└── cloud-services/          # Individual service configurations (499 services)
    ├── slack.yaml          # Sanctioned collaboration tool
    ├── dropbox.yaml        # Unsanctioned storage service  
    ├── discord.yaml        # Blocked communication service
    └── ... (496 more services)
```

### Cloud Service Configuration

Each cloud service is self-contained in its own YAML file:

```yaml
service:
  name: "Dropbox"
  category: "cloud_storage"
  status: "unsanctioned"  # Controls access (sanctioned/unsanctioned/blocked)
  risk_level: "medium"    # Risk assessment (low/medium/high)

network:
  domains:
    - "dropbox.com"
    - "*.dropbox.com"
  ip_ranges:
    - "162.125.0.0/16"

traffic_patterns:
  # API endpoints, paths, user agents
  
activity:
  user_adoption_rate: 0.15  # 15% of users use this service
  
security_events:
  block_rate: 0.3  # 30% of attempts blocked
```

### Service Status Types

- **Sanctioned**: Officially approved services (low block rate, high adoption)
- **Unsanctioned**: Shadow IT services (medium block rate, medium adoption)  
- **Blocked**: Prohibited services (100% block rate, low adoption from persistent users)

### Junk Traffic

The system generates realistic background noise by including traffic to popular internet sites:
- News sites (CNN, BBC, etc.) - 25%
- Reference sites (Wikipedia, etc.) - 20%
- Shopping sites - 15%
- Blogs - 15%
- Forums - 10%
- Misc (weather, sports) - 15%

## Installation

```bash
# Clone the repository
git clone https://github.com/skyhighsecurity/shadow-it-generator.git
cd shadow-it-generator

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

## Usage

### Basic Usage

```bash
# Generate logs using default configuration
python main.py --enterprise-config config/enterprise.yaml

# Specify date range
python main.py --enterprise-config config/enterprise.yaml \
  --start-date "2024-01-01" --end-date "2024-01-31"

# Generate both LEEF and CEF formats
python main.py --enterprise-config config/enterprise.yaml \
  --format both
```

### Docker Usage

```bash
# Build the image
docker build -t shadow-it-generator .

# Run with mounted volumes
docker run -v $(pwd)/config:/app/config \
  -v $(pwd)/output:/app/output \
  shadow-it-generator \
  --enterprise-config /app/config/enterprise.yaml
```

## Configuration

### Enterprise Configuration

The `enterprise.yaml` file controls company-wide settings:

```yaml
enterprise:
  name: "Acme Corporation"
  domain: "acme.com"
  
users:
  total_count: 5000
  
user_profiles:
  - name: "normal"
    percentage: 0.70
    shadow_it_likelihood: 0.2
  - name: "power_user"
    percentage: 0.20
    shadow_it_likelihood: 0.4
  - name: "risky"
    percentage: 0.10
    shadow_it_likelihood: 0.8
    
junk_traffic:
  enabled: true
  percentage_of_total: 0.30
  allowed_rate: 0.85
```

## Output

Logs are generated in the specified format and saved to dated files:

```
output/
├── leef/
│   ├── leef_20240101.log
│   ├── leef_20240102.log
│   └── ...
└── cef/
    ├── cef_20240101.log
    ├── cef_20240102.log
    └── ...
```

## Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/

# Type checking
mypy src/
```

## License

Copyright (c) Skyhigh Security