from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from .token_utils import TokenRevocationChecker


def require_token_not_revoked(view_func):
    """
    Decorator que verifica se o token JWT não foi revogado.
    
    Aplica-se a views que usam autenticação JWT e verifica se o token
    presente no header Authorization foi revogado no banco de dados.
    
    Retorna 401 Unauthorized se o token foi revogado.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verifica se há um token Bearer no header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if TokenRevocationChecker.is_token_revoked(token):
                return Response(
                    {'detail': 'Token has been revoked.'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # Se não há token ou token não foi revogado, continua normalmente
        return view_func(request, *args, **kwargs)
    
    return wrapper
