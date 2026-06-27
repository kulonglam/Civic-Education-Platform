from rest_framework.throttling import UserRateThrottle


class TutorRateThrottle(UserRateThrottle):
    scope = 'ai_tutor'
