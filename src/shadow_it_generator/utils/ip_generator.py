"""
IP address generator for creating realistic network traffic patterns.
"""

import random
import ipaddress
from typing import List, Optional, Union


class IPGenerator:
    """
    Generates IP addresses for simulating network traffic.
    
    Handles both internal and external IP addresses with realistic patterns.
    """
    
    def __init__(
        self,
        internal_subnets: List[str],
        egress_ips: List[str],
        proxy_ips: Optional[List[str]] = None,
        vpn_subnets: Optional[List[str]] = None
    ):
        """
        Initialize IP generator.
        
        Args:
            internal_subnets: List of internal network subnets (CIDR notation)
            egress_ips: List of external egress IP addresses
            proxy_ips: Optional list of proxy server IPs
            vpn_subnets: Optional list of VPN subnets
        """
        self.internal_networks = [ipaddress.ip_network(subnet) for subnet in internal_subnets]
        self.egress_ips = [ipaddress.ip_address(ip) for ip in egress_ips]
        self.proxy_ips = [ipaddress.ip_address(ip) for ip in (proxy_ips or [])]
        self.vpn_networks = [ipaddress.ip_network(subnet) for subnet in (vpn_subnets or [])]
        
        # Common CDN and cloud provider IP ranges (simplified)
        self.cdn_ranges = [
            ipaddress.ip_network("104.16.0.0/12"),    # Cloudflare
            ipaddress.ip_network("172.64.0.0/13"),    # Cloudflare
            ipaddress.ip_network("52.84.0.0/15"),     # CloudFront
            ipaddress.ip_network("13.224.0.0/14"),    # CloudFront
            ipaddress.ip_network("151.101.0.0/16"),   # Fastly
            ipaddress.ip_network("172.217.0.0/16"),   # Google
            ipaddress.ip_network("142.250.0.0/15"),   # Google
        ]
    
    def generate_internal_ip(self, exclude_servers: bool = True) -> str:
        """
        Generate a random internal IP address.
        
        Args:
            exclude_servers: If True, avoid .1-.10 addresses (typically servers)
            
        Returns:
            Internal IP address as string
        """
        network = random.choice(self.internal_networks)
        
        # Generate random host within the network
        if network.num_addresses > 2:
            if exclude_servers:
                # Skip first 10 and last address
                host_offset = random.randint(11, network.num_addresses - 2)
            else:
                # Skip network and broadcast addresses
                host_offset = random.randint(1, network.num_addresses - 2)
            
            ip = network.network_address + host_offset
            return str(ip)
        else:
            # Small network, just return first usable
            return str(list(network.hosts())[0])
    
    def generate_vpn_ip(self) -> Optional[str]:
        """
        Generate a VPN IP address if VPN subnets are configured.
        
        Returns:
            VPN IP address or None if no VPN configured
        """
        if not self.vpn_networks:
            return None
            
        network = random.choice(self.vpn_networks)
        if network.num_addresses > 2:
            host_offset = random.randint(1, network.num_addresses - 2)
            ip = network.network_address + host_offset
            return str(ip)
        else:
            return str(list(network.hosts())[0])
    
    def get_egress_ip(self, use_proxy: bool = False) -> str:
        """
        Get an egress IP address.
        
        Args:
            use_proxy: If True and proxies configured, return proxy IP
            
        Returns:
            Egress IP address as string
        """
        if use_proxy and self.proxy_ips:
            return str(random.choice(self.proxy_ips))
        else:
            return str(random.choice(self.egress_ips))
    
    def generate_destination_ip(self, service_ip_ranges: Optional[List[str]] = None) -> str:
        """
        Generate a destination IP address for a cloud service.
        
        Args:
            service_ip_ranges: Optional specific IP ranges for the service
            
        Returns:
            Destination IP address as string
        """
        if service_ip_ranges:
            # Use service-specific ranges
            ip_range = random.choice(service_ip_ranges)
            network = ipaddress.ip_network(ip_range)
            
            if network.num_addresses > 2:
                host_offset = random.randint(1, network.num_addresses - 2)
                ip = network.network_address + host_offset
                return str(ip)
            else:
                return str(network.network_address)
        else:
            # Use CDN ranges
            network = random.choice(self.cdn_ranges)
            host_offset = random.randint(1, min(1000, network.num_addresses - 2))
            ip = network.network_address + host_offset
            return str(ip)
    
    def generate_source_port(self, privileged: bool = False) -> int:
        """
        Generate a source port number.
        
        Args:
            privileged: If True, can return privileged ports (< 1024)
            
        Returns:
            Port number
        """
        if privileged and random.random() < 0.05:  # 5% chance of privileged
            return random.randint(1, 1023)
        else:
            # Ephemeral port range
            return random.randint(32768, 65535)
    
    def get_destination_port(self, protocol: str = "https") -> int:
        """
        Get destination port based on protocol.
        
        Args:
            protocol: Protocol name
            
        Returns:
            Port number
        """
        port_map = {
            "http": 80,
            "https": 443,
            "ftp": 21,
            "ssh": 22,
            "telnet": 23,
            "smtp": 25,
            "dns": 53,
            "http-alt": 8080,
            "https-alt": 8443,
        }
        
        return port_map.get(protocol.lower(), 443)  # Default to HTTPS