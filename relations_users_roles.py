from typing import Optional, List
from app.schemes.users import SUserGet
from app.schemes.roles import SRoleGet
from app.schemes.registrations import SRegistrationWithEvent
from app.schemes.certificates import SCertificateGet


class SUserGetWithRels(SUserGet):
    role: SRoleGet
    registrations: Optional[List[SRegistrationWithEvent]] = None
    certificates: Optional[List[SCertificateGet]] = None

    class Config:
        from_attributes = True

