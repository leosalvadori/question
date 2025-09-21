from django.core.management.base import BaseCommand
from companies.models import CompanyToken
from companies.token_utils import TokenRevocationChecker


class Command(BaseCommand):
    help = 'Verifica se um token JWT foi revogado'

    def add_arguments(self, parser):
        parser.add_argument('jti', type=str, help='JTI do token a ser verificado')

    def handle(self, *args, **options):
        jti = options['jti']
        
        # Busca o token no banco
        token = CompanyToken.objects.filter(refresh_jti=jti).first()
        
        if token:
            self.stdout.write(f'Token encontrado: {token}')
            self.stdout.write(f'Criado em: {token.created_at}')
            self.stdout.write(f'Revogado em: {token.revoked_at}')
            self.stdout.write(f'Status: {"Revogado" if token.revoked_at else "Ativo"}')
        else:
            self.stdout.write('Token não encontrado no banco de dados')
        
        # Lista todos os tokens da empresa 3
        self.stdout.write('\n--- Todos os tokens da empresa 3 ---')
        tokens = CompanyToken.objects.filter(company_id=3).order_by('-created_at')
        for t in tokens:
            self.stdout.write(f'JTI: {t.refresh_jti} | Revogado: {t.revoked_at} | Label: {t.label}')
