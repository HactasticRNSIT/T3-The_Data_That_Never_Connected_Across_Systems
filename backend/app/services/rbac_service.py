from typing import List

def get_allowed_sectors_for_user(user_sector: str, user_role: str) -> List[str]:
    """
    Returns the list of sectors a user is allowed to see data from.
    Admins see everything. Department users see their own and community.
    """
    if user_role == 'admin':
        return ['police', 'healthcare', 'transport', 'community']
    
    # Department users always see community reports along with their own
    allowed = [user_sector]
    if user_sector != 'community':
        allowed.append('community')
        
    return allowed
