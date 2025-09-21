from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken
from .models import CompanyToken


class TokenRevocationChecker:
    """Verifica se um token JWT foi revogado no banco de dados."""
    
    @staticmethod
    def is_token_revoked(token):
        """
        Verifica se um token foi revogado.
        
        Args:
            token: String do JWT token ou objeto AccessToken
            
        Returns:
            bool: True se o token foi revogado, False caso contrário
        """
        try:
            if isinstance(token, str):
                access_token = AccessToken(token)
            else:
                access_token = token
            
            # Extrai o JTI (JWT ID) do access token
            jti = access_token.get('jti')
            if not jti:
                return False
            
            # Verifica se existe um CompanyToken com este JTI que foi revogado
            # O JTI do access token deve corresponder ao refresh_jti no banco
            company_token = CompanyToken.objects.filter(refresh_jti=jti).first()
            
            # Se não existe no banco, considera como válido (token antigo ou de outro sistema)
            if not company_token:
                return False
                
            # Se existe no banco e foi revogado, retorna True
            if company_token.revoked_at:
                return True
                
            return False
            
        except (InvalidToken, TokenError, Exception):
            # Se houver erro ao processar o token, considera como inválido
            return True
    
    @staticmethod
    def get_company_id_from_token(token):
        """
        Extrai o company_id do token JWT.
        
        Args:
            token: String do JWT token ou objeto AccessToken
            
        Returns:
            int: ID da empresa ou None se não encontrado
        """
        try:
            if isinstance(token, str):
                access_token = AccessToken(token)
            else:
                access_token = token
            
            return access_token.get('company_id')
            
        except (InvalidToken, TokenError, Exception):
            return None
