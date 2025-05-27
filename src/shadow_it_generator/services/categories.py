"""Cloud service category definitions.

This module defines the various categories of cloud services and their
risk levels for Shadow IT analysis.
"""

from enum import Enum
from typing import Dict, List


class ServiceCategory(Enum):
    """Cloud service categories."""
    
    # Sanctioned business applications
    BUSINESS = "Business"
    PRODUCTIVITY = "Productivity"
    COLLABORATION = "Collaboration"
    CRM = "CRM"
    ERP = "ERP"
    HR = "Human Resources"
    FINANCE = "Finance"
    
    # Communication
    EMAIL = "Email"
    MESSAGING = "Messaging"
    VIDEO_CONFERENCING = "Video Conferencing"
    
    # Storage and file sharing
    CLOUD_STORAGE = "Cloud Storage"
    FILE_SHARING = "File Sharing"
    PERSONAL_STORAGE = "Personal Storage"
    
    # Development and IT
    DEVELOPMENT = "Development"
    CODE_REPOSITORY = "Code Repository"
    CI_CD = "CI/CD"
    CLOUD_INFRASTRUCTURE = "Cloud Infrastructure"
    IT_MANAGEMENT = "IT Management"
    
    # Security and networking
    SECURITY = "Security"
    VPN = "VPN"
    PROXY = "Proxy"
    
    # Personal and social
    SOCIAL_MEDIA = "Social Media"
    PERSONAL_EMAIL = "Personal Email"
    ENTERTAINMENT = "Entertainment"
    
    # High risk
    TORRENT = "Torrent"
    CRYPTO = "Cryptocurrency"
    GAMBLING = "Gambling"
    ADULT = "Adult Content"
    
    # Other
    UNKNOWN = "Unknown"
    MISCELLANEOUS = "Miscellaneous"


class CategoryRiskLevel:
    """Risk level definitions for service categories."""
    
    # Risk levels
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    # Category to risk level mapping
    RISK_MAP: Dict[ServiceCategory, int] = {
        # Low risk - sanctioned business apps
        ServiceCategory.BUSINESS: LOW,
        ServiceCategory.PRODUCTIVITY: LOW,
        ServiceCategory.CRM: LOW,
        ServiceCategory.ERP: LOW,
        ServiceCategory.HR: LOW,
        ServiceCategory.FINANCE: LOW,
        ServiceCategory.EMAIL: LOW,
        ServiceCategory.IT_MANAGEMENT: LOW,
        
        # Medium risk - collaboration and development
        ServiceCategory.COLLABORATION: MEDIUM,
        ServiceCategory.MESSAGING: MEDIUM,
        ServiceCategory.VIDEO_CONFERENCING: MEDIUM,
        ServiceCategory.CLOUD_STORAGE: MEDIUM,
        ServiceCategory.DEVELOPMENT: MEDIUM,
        ServiceCategory.CODE_REPOSITORY: MEDIUM,
        ServiceCategory.CI_CD: MEDIUM,
        ServiceCategory.CLOUD_INFRASTRUCTURE: MEDIUM,
        ServiceCategory.SECURITY: MEDIUM,
        
        # High risk - personal and unmanaged
        ServiceCategory.FILE_SHARING: HIGH,
        ServiceCategory.PERSONAL_STORAGE: HIGH,
        ServiceCategory.SOCIAL_MEDIA: HIGH,
        ServiceCategory.PERSONAL_EMAIL: HIGH,
        ServiceCategory.ENTERTAINMENT: HIGH,
        ServiceCategory.VPN: HIGH,
        ServiceCategory.PROXY: HIGH,
        ServiceCategory.UNKNOWN: HIGH,
        
        # Critical risk - prohibited
        ServiceCategory.TORRENT: CRITICAL,
        ServiceCategory.CRYPTO: CRITICAL,
        ServiceCategory.GAMBLING: CRITICAL,
        ServiceCategory.ADULT: CRITICAL,
    }
    
    @classmethod
    def get_risk_level(cls, category: ServiceCategory) -> int:
        """Get risk level for a category.
        
        Args:
            category: Service category
            
        Returns:
            Risk level (1-4)
        """
        return cls.RISK_MAP.get(category, cls.HIGH)
    
    @classmethod
    def get_risk_name(cls, level: int) -> str:
        """Get risk level name.
        
        Args:
            level: Risk level number
            
        Returns:
            Risk level name
        """
        names = {
            cls.LOW: "Low",
            cls.MEDIUM: "Medium",
            cls.HIGH: "High",
            cls.CRITICAL: "Critical"
        }
        return names.get(level, "Unknown")


class ServiceDatabase:
    """Database of well-known cloud services and their categories."""
    
    # Well-known services by category
    SERVICES: Dict[ServiceCategory, List[Dict[str, str]]] = {
        ServiceCategory.BUSINESS: [
            {"name": "Microsoft Office 365", "hostname": "outlook.office365.com"},
            {"name": "Google Workspace", "hostname": "workspace.google.com"},
            {"name": "Salesforce", "hostname": "salesforce.com"},
            {"name": "ServiceNow", "hostname": "servicenow.com"},
            {"name": "Workday", "hostname": "workday.com"},
        ],
        
        ServiceCategory.COLLABORATION: [
            {"name": "Slack", "hostname": "slack.com"},
            {"name": "Microsoft Teams", "hostname": "teams.microsoft.com"},
            {"name": "Asana", "hostname": "asana.com"},
            {"name": "Monday.com", "hostname": "monday.com"},
            {"name": "Trello", "hostname": "trello.com"},
        ],
        
        ServiceCategory.CLOUD_STORAGE: [
            {"name": "Box", "hostname": "box.com"},
            {"name": "Dropbox Business", "hostname": "dropbox.com"},
            {"name": "OneDrive", "hostname": "onedrive.live.com"},
            {"name": "Google Drive", "hostname": "drive.google.com"},
            {"name": "SharePoint", "hostname": "sharepoint.com"},
        ],
        
        ServiceCategory.PERSONAL_STORAGE: [
            {"name": "Dropbox Personal", "hostname": "dropbox.com"},
            {"name": "Google Drive Personal", "hostname": "drive.google.com"},
            {"name": "iCloud", "hostname": "icloud.com"},
            {"name": "MEGA", "hostname": "mega.nz"},
            {"name": "pCloud", "hostname": "pcloud.com"},
        ],
        
        ServiceCategory.DEVELOPMENT: [
            {"name": "GitHub", "hostname": "github.com"},
            {"name": "GitLab", "hostname": "gitlab.com"},
            {"name": "Bitbucket", "hostname": "bitbucket.org"},
            {"name": "Jira", "hostname": "atlassian.net"},
            {"name": "Jenkins", "hostname": "jenkins.io"},
        ],
        
        ServiceCategory.VIDEO_CONFERENCING: [
            {"name": "Zoom", "hostname": "zoom.us"},
            {"name": "Webex", "hostname": "webex.com"},
            {"name": "GoToMeeting", "hostname": "gotomeeting.com"},
            {"name": "Google Meet", "hostname": "meet.google.com"},
            {"name": "Skype", "hostname": "skype.com"},
        ],
        
        ServiceCategory.SOCIAL_MEDIA: [
            {"name": "Facebook", "hostname": "facebook.com"},
            {"name": "Twitter", "hostname": "twitter.com"},
            {"name": "LinkedIn", "hostname": "linkedin.com"},
            {"name": "Instagram", "hostname": "instagram.com"},
            {"name": "Reddit", "hostname": "reddit.com"},
        ],
        
        ServiceCategory.PERSONAL_EMAIL: [
            {"name": "Gmail Personal", "hostname": "mail.google.com"},
            {"name": "Yahoo Mail", "hostname": "mail.yahoo.com"},
            {"name": "Outlook Personal", "hostname": "outlook.live.com"},
            {"name": "ProtonMail", "hostname": "protonmail.com"},
            {"name": "AOL Mail", "hostname": "mail.aol.com"},
        ],
        
        ServiceCategory.FILE_SHARING: [
            {"name": "WeTransfer", "hostname": "wetransfer.com"},
            {"name": "SendSpace", "hostname": "sendspace.com"},
            {"name": "MediaFire", "hostname": "mediafire.com"},
            {"name": "4shared", "hostname": "4shared.com"},
            {"name": "RapidShare", "hostname": "rapidshare.com"},
        ],
        
        ServiceCategory.VPN: [
            {"name": "NordVPN", "hostname": "nordvpn.com"},
            {"name": "ExpressVPN", "hostname": "expressvpn.com"},
            {"name": "CyberGhost", "hostname": "cyberghost.com"},
            {"name": "Surfshark", "hostname": "surfshark.com"},
            {"name": "ProtonVPN", "hostname": "protonvpn.com"},
        ],
        
        ServiceCategory.TORRENT: [
            {"name": "The Pirate Bay", "hostname": "thepiratebay.org"},
            {"name": "1337x", "hostname": "1337x.to"},
            {"name": "RARBG", "hostname": "rarbg.to"},
            {"name": "YTS", "hostname": "yts.mx"},
            {"name": "Torrentz2", "hostname": "torrentz2.eu"},
        ],
    }
    
    @classmethod
    def get_services_by_category(cls, category: ServiceCategory) -> List[Dict[str, str]]:
        """Get services for a specific category.
        
        Args:
            category: Service category
            
        Returns:
            List of service definitions
        """
        return cls.SERVICES.get(category, [])