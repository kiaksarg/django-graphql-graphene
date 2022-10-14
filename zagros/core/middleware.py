
from django.utils import timezone

def request_time(get_response):
    def _stamp_request(request):
        request.request_time = timezone.now()
        return get_response(request)

    return _stamp_request