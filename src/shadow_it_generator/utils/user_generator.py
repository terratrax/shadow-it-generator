"""
User name generator for creating realistic user identities.

Generates both US and international names in firstname.lastname@domain format.
"""

import random
from typing import List, Tuple, Dict, Set
from faker import Faker


class UserGenerator:
    """
    Generates realistic user names from various countries.
    
    Creates email addresses in the format: firstname.lastname@domain
    """
    
    def __init__(self, enterprise_domain: str, seed: int = None):
        """
        Initialize the user generator.
        
        Args:
            enterprise_domain: The domain to use for email addresses
            seed: Random seed for reproducible results
        """
        self.enterprise_domain = enterprise_domain
        self.generated_emails: Set[str] = set()
        
        if seed:
            random.seed(seed)
            Faker.seed(seed)
        
        # Initialize Faker instances for different locales
        self.locales = {
            'US': {
                'faker': Faker('en_US'),
                'weight': 0.30  # 30% US names
            },
            'UK': {
                'faker': Faker('en_GB'),
                'weight': 0.10  # 10% UK names
            },
            'India': {
                'faker': Faker('en_IN'),
                'weight': 0.15  # 15% Indian names
            },
            'Germany': {
                'faker': Faker('de_DE'),
                'weight': 0.08  # 8% German names
            },
            'France': {
                'faker': Faker('fr_FR'),
                'weight': 0.07  # 7% French names
            },
            'Spain': {
                'faker': Faker('es_ES'),
                'weight': 0.05  # 5% Spanish names
            },
            'Italy': {
                'faker': Faker('it_IT'),
                'weight': 0.05  # 5% Italian names
            },
            'Japan': {
                'faker': Faker('ja_JP'),
                'weight': 0.05  # 5% Japanese names
            },
            'China': {
                'faker': Faker('zh_CN'),
                'weight': 0.05  # 5% Chinese names
            },
            'Brazil': {
                'faker': Faker('pt_BR'),
                'weight': 0.05  # 5% Brazilian names
            },
            'Canada': {
                'faker': Faker('en_CA'),
                'weight': 0.05  # 5% Canadian names
            }
        }
        
        # Common name variations that might exist
        self.common_variations = [
            ('john', 'j'),
            ('michael', 'mike'),
            ('robert', 'rob'),
            ('robert', 'bob'),
            ('william', 'bill'),
            ('richard', 'rick'),
            ('richard', 'dick'),
            ('elizabeth', 'liz'),
            ('elizabeth', 'beth'),
            ('jennifer', 'jen'),
            ('jessica', 'jess'),
            ('christopher', 'chris'),
            ('matthew', 'matt'),
            ('anthony', 'tony'),
            ('daniel', 'dan'),
            ('joseph', 'joe'),
            ('thomas', 'tom'),
            ('charles', 'chuck'),
            ('patricia', 'pat'),
            ('margaret', 'meg'),
            ('katherine', 'kate'),
            ('katherine', 'kathy'),
        ]
    
    def _normalize_name(self, name: str) -> str:
        """
        Normalize name for email format.
        
        Removes accents, converts to lowercase, removes spaces.
        """
        # Simple ASCII normalization
        import unicodedata
        name = unicodedata.normalize('NFD', name)
        name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')
        
        # Convert to lowercase and remove spaces/special chars
        name = name.lower()
        name = ''.join(char for char in name if char.isalnum() or char in ['-', '_'])
        
        return name
    
    def _select_locale(self) -> Tuple[str, Faker]:
        """Select a locale based on weighted distribution."""
        locales = list(self.locales.keys())
        weights = [self.locales[loc]['weight'] for loc in locales]
        selected = random.choices(locales, weights=weights)[0]
        return selected, self.locales[selected]['faker']
    
    def generate_user(self) -> Dict[str, str]:
        """
        Generate a single user with name and email.
        
        Returns:
            Dictionary with user information including:
            - first_name: Original first name
            - last_name: Original last name
            - email: firstname.lastname@domain
            - locale: Country/region of origin
            - username: Just the username part (before @)
        """
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            locale, faker = self._select_locale()
            
            # Generate names
            first_name = faker.first_name()
            last_name = faker.last_name()
            
            # Normalize for email
            first_normalized = self._normalize_name(first_name)
            last_normalized = self._normalize_name(last_name)
            
            # Create email
            username = f"{first_normalized}.{last_normalized}"
            email = f"{username}@{self.enterprise_domain}"
            
            # Check for duplicates
            if email not in self.generated_emails:
                self.generated_emails.add(email)
                
                # Sometimes add middle initial
                if random.random() < 0.1:  # 10% chance
                    middle_initial = faker.random_letter().lower()
                    username = f"{first_normalized}.{middle_initial}.{last_normalized}"
                    email = f"{username}@{self.enterprise_domain}"
                
                # Sometimes add number for common names
                elif email in self.generated_emails or random.random() < 0.05:
                    number = random.randint(1, 99)
                    username = f"{first_normalized}.{last_normalized}{number}"
                    email = f"{username}@{self.enterprise_domain}"
                
                return {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'username': username,
                    'locale': locale,
                    'full_name': f"{first_name} {last_name}"
                }
            
            attempts += 1
        
        # Fallback with number
        number = random.randint(1000, 9999)
        username = f"{first_normalized}.{last_normalized}{number}"
        email = f"{username}@{self.enterprise_domain}"
        
        return {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'username': username,
            'locale': locale,
            'full_name': f"{first_name} {last_name}"
        }
    
    def generate_users(self, count: int) -> List[Dict[str, str]]:
        """
        Generate multiple unique users.
        
        Args:
            count: Number of users to generate
            
        Returns:
            List of user dictionaries
        """
        users = []
        
        # Add some common service accounts first
        service_accounts = [
            {
                'first_name': 'Admin',
                'last_name': 'User',
                'email': f'admin@{self.enterprise_domain}',
                'username': 'admin',
                'locale': 'System',
                'full_name': 'Admin User'
            },
            {
                'first_name': 'Service',
                'last_name': 'Account',
                'email': f'service.account@{self.enterprise_domain}',
                'username': 'service.account',
                'locale': 'System',
                'full_name': 'Service Account'
            },
            {
                'first_name': 'No',
                'last_name': 'Reply',
                'email': f'noreply@{self.enterprise_domain}',
                'username': 'noreply',
                'locale': 'System',
                'full_name': 'No Reply'
            }
        ]
        
        # Add service accounts if count allows
        for account in service_accounts:
            if len(users) < count:
                users.append(account)
                self.generated_emails.add(account['email'])
        
        # Generate remaining users
        while len(users) < count:
            users.append(self.generate_user())
        
        return users
    
    def generate_user_with_profile(self, profile_name: str) -> Dict[str, str]:
        """
        Generate a user and assign a specific profile.
        
        Args:
            profile_name: Name of the user profile (normal, power_user, risky)
            
        Returns:
            User dictionary with profile field added
        """
        user = self.generate_user()
        user['profile'] = profile_name
        return user