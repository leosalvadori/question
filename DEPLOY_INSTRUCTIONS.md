# Instruções para Deploy da Exportação CSV

## Problema Identificado
A exportação CSV não está funcionando em produção porque:
1. Você precisa estar logado no sistema
2. O código da exportação CSV precisa ser deployado

## Soluções

### 1. Fazer Login no Sistema de Produção
1. Acesse: https://leosalvadori.pythonanywhere.com/login/
2. Faça login com suas credenciais
3. Depois acesse: https://leosalvadori.pythonanywhere.com/answers/5/dashboard/
4. Clique em "Exportar CSV"

### 2. Deploy do Código (se necessário)
Se o código da exportação CSV não estiver em produção, você precisa:

1. **Fazer upload dos arquivos modificados:**
   - `answers/views.py` (linhas 234-267 contêm a lógica de exportação CSV)
   - `answers/urls.py` (se houver mudanças)

2. **Reiniciar o servidor PythonAnywhere:**
   - Acesse o painel do PythonAnywhere
   - Vá em "Web" → "Reload" para reiniciar o servidor

### 3. Verificar se a Exportação está Funcionando
Após o login, teste:
- URL: https://leosalvadori.pythonanywhere.com/answers/5/dashboard/?format=csv
- Deve baixar um arquivo CSV com os dados

## Código da Exportação CSV
A exportação CSV está implementada na view `survey_dashboard` (linhas 234-267) e inclui:
- Dados básicos da submissão (ID, data, IP, localização)
- Todas as respostas das perguntas
- Filtros por estado/cidade aplicados

## Teste Local
Para testar localmente:
1. `python manage.py runserver`
2. Acesse: http://127.0.0.1:8000/answers/5/dashboard/
3. Faça login se necessário
4. Clique em "Exportar CSV"
