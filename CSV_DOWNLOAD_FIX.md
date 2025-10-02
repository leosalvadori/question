# Solução para Problema de Download CSV no Chrome

## Problema Identificado
O Chrome pode estar bloqueando o download do CSV devido a:
1. Políticas de segurança do navegador
2. Headers de resposta inadequados
3. Problemas com Content-Disposition

## Soluções Implementadas

### 1. Headers Melhorados
- Adicionado `charset=utf-8` ao Content-Type
- Adicionados headers de cache para evitar problemas
- Melhorado o Content-Disposition

### 2. JavaScript com Fetch API
- Implementada função `downloadCSV()` que usa fetch
- Fallback para método de link direto
- Logs de debug para identificar problemas

### 3. Botão Melhorado
- Mudado de link `<a>` para botão `<button>`
- Adicionado onclick para controlar o download
- Melhorados os estilos CSS

## Como Testar

### 1. Teste Local
1. Acesse: http://127.0.0.1:8000/answers/5/dashboard/
2. Faça login se necessário
3. Clique em "Exportar CSV"
4. Verifique o console do navegador (F12) para logs

### 2. Teste em Produção
1. Faça upload dos arquivos modificados:
   - `answers/views.py`
   - `answers/templates/answers/survey_dashboard.html`
2. Reinicie o servidor PythonAnywhere
3. Acesse: https://leosalvadori.pythonanywhere.com/answers/5/dashboard/
4. Clique em "Exportar CSV"

### 3. Verificações no Chrome
1. Abra o Console (F12 → Console)
2. Clique em "Exportar CSV"
3. Verifique se aparecem os logs:
   - "Iniciando download CSV..."
   - "URL do CSV: ?format=csv"
   - "Download iniciado via fetch!" ou "Tentativa de download via link direto"

### 4. Verificar Downloads
1. Vá em Configurações do Chrome → Downloads
2. Verifique se há downloads bloqueados
3. Se houver, clique em "Permitir" ou "Permitir sempre"

## Soluções Alternativas

### Se o download ainda não funcionar:

1. **Teste em modo incógnito** do Chrome
2. **Desabilite temporariamente** o bloqueador de pop-ups
3. **Teste em outro navegador** (Firefox, Safari, Edge)
4. **Verifique as configurações** de segurança do Chrome

### Para forçar o download:
1. Clique com botão direito no botão "Exportar CSV"
2. Selecione "Salvar link como..."
3. Ou acesse diretamente: `?format=csv` na URL

## Arquivos Modificados
- `answers/views.py` - Headers melhorados
- `answers/templates/answers/survey_dashboard.html` - JavaScript e botão
