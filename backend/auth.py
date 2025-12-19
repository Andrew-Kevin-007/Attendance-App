"""Authentication and Authorization middleware for Face Attendance System"""
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from typing import Callable, Any, Optional


def jwt_required_optional(fn: Callable) -> Callable:
    """
    Decorator that allows optional JWT authentication.
    If token is provided, it will be verified. If not, request continues.
    
    Args:
        fn: The function to decorate
        
    Returns:
        Decorated function
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
        except Exception:
            pass
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn: Callable) -> Callable:
    """
    Decorator that requires JWT authentication and admin role.
    
    Args:
        fn: The function to decorate
        
    Returns:
        Decorated function
        
    Raises:
        401: If no valid JWT token provided
        403: If user doesn't have admin role
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            
            if not claims.get('is_admin', False):
                return jsonify({
                    'success': False,
                    'error': 'Admin access required'
                }), 403
                
            return fn(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing authentication token'
            }), 401
            
    return wrapper


def get_current_user() -> Optional[dict]:
    """
    Get current authenticated user information from JWT token.
    
    Returns:
        Dictionary with user info if authenticated, None otherwise
        
    Example:
        user = get_current_user()
        if user:
            user_id = user['user_id']
            is_admin = user['is_admin']
    """
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        claims = get_jwt()
        
        if identity:
            return {
                'user_id': identity,
                'is_admin': claims.get('is_admin', False),
                'email': claims.get('email', None)
            }
    except Exception:
        pass
        
    return None


def create_access_token_response(user_id: str, email: str, is_admin: bool = False) -> dict:
    """
    Create a standardized token response with user information.
    
    Args:
        user_id: Unique identifier for the user
        email: User's email address
        is_admin: Whether user has admin privileges
        
    Returns:
        Dictionary with token and user information
    """
    from flask_jwt_extended import create_access_token, create_refresh_token
    
    additional_claims = {
        'is_admin': is_admin,
        'email': email
    }
    
    access_token = create_access_token(
        identity=user_id,
        additional_claims=additional_claims
    )
    
    refresh_token = create_refresh_token(
        identity=user_id,
        additional_claims=additional_claims
    )
    
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'user': {
            'user_id': user_id,
            'email': email,
            'is_admin': is_admin
        }
    }


def validate_api_key(fn: Callable) -> Callable:
    """
    Decorator that validates API key for service-to-service communication.
    Checks for X-API-Key header matching configured API key.
    
    Args:
        fn: The function to decorate
        
    Returns:
        Decorated function
        
    Raises:
        401: If API key is invalid or missing
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from config import Config
        
        api_key = request.headers.get('X-API-Key')
        expected_key = Config.API_KEY if hasattr(Config, 'API_KEY') else None
        
        # If no API key is configured, skip validation
        if not expected_key:
            return fn(*args, **kwargs)
            
        if not api_key or api_key != expected_key:
            return jsonify({
                'success': False,
                'error': 'Invalid or missing API key'
            }), 401
            
        return fn(*args, **kwargs)
        
    return wrapper
