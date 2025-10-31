# /home/ubuntu/lenskart_backend/app/middleware.py

import logging
import json

payload_logger = logging.getLogger('payload_logger')

class PayloadLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                body = request.body
                content_type = request.headers.get('Content-Type', '')

                # Log regular form/JSON data
                if 'application/json' in content_type:
                    try:
                        payload = json.loads(body.decode('utf-8'))
                        payload_logger.info(f"Incoming JSON Payload for {request.path}: {payload}")
                    except json.JSONDecodeError:
                        payload_logger.warning(f"Incoming Request for {request.path} has JSON content-type but invalid JSON body: {body.decode('utf-8')}")
                elif 'multipart/form-data' in content_type or 'application/x-www-form-urlencoded' in content_type:
                    # Log POST data
                    post_data = request.POST.dict()
                    payload_logger.info(f"Incoming Form/Multipart Payload (POST data) for {request.path}: {post_data}")

                    # Log FILES data separately
                    if request.FILES:
                        files_info = {}
                        for filename, uploaded_file in request.FILES.items():
                            files_info[filename] = {
                                'name': uploaded_file.name,
                                'size': uploaded_file.size,
                                'content_type': uploaded_file.content_type,
                                # You can add more attributes if needed, e.g., 'charset'
                            }
                        payload_logger.info(f"Incoming Form/Multipart Payload (FILES data) for {request.path}: {files_info}")
                    else:
                        payload_logger.info(f"Incoming Form/Multipart Payload for {request.path} has no files.")
                else:
                    payload_logger.info(f"Incoming Raw Payload for {request.path} (Content-Type: {content_type}): {body.decode('utf-8')}")
                
                # Check for empty body for methods that might have one
                if not body and request.method not in ['GET', 'HEAD']: # Only log "no body" for methods that typically have one
                    payload_logger.info(f"Incoming Request to {request.path} has no body (Method: {request.method}).")

            except Exception as e:
                # This is where the DATA_UPLOAD_MAX_MEMORY_SIZE error would be caught.
                # It's important to still report this.
                payload_logger.error(f"Error logging request payload for {request.path}: {e}")

        response = self.get_response(request)
        return response
