The purpose of this project is to generate internet access logs representative of what users in an enteprise would use. The logs will be imported into Skyhigh Security's shadow it analysis system and should be in the McAfee / Skyhigh Secure Web Gateway (on premesis, not cloud) log format.

We'll need to "prime the system" with a representative list of at least the top 500 cloud services that enterprise cloud users access. This should include sanctioned as well as unsanctioned and potentially dangerous apps.

Each service needs to be stored with some configuration:

- Service Name
- Average traffic per session
- Variance metric for average traffic (what's the best thing to call this?)
- Average connections per session
- Variance metric for average connections per session

Also there should be an enterprise configuration:
- Total number of users
- Domain suffix for users' email addresses
- IP address CIDR list for source IP addresses
- User agent list for browsers
- Anything else you would recommend
- Output filename format (including month/day/timestamp etc)

I was thinking that the enterprise configuration could be in one YAML file and then each cloud service would have its own YAML file located in a /cloud-services folder.

We should dockerize the application and provide for some command line arguments like so

docker run -it ghcr.io/skyhighsecurity/solution-stage/shadow-it-generator:latest generate 30 days | beginning <beginning date/time> 