# 📥 Guia de Importação de Dados do Asaas

## Visão Geral

O sistema agora permite importar clientes e recorrências já cadastrados no Asaas para o sistema local. Isso é útil quando:

- Você já tem dados no Asaas antes de começar a usar este sistema
- Quer sincronizar dados existentes
- Precisa recuperar informações do Asaas

---

## 🎯 Como Importar Clientes

### Passo a Passo:

1. **Acesse a lista de clientes:**
   - No menu principal, clique em "Clientes"

2. **Clique no botão "Importar do Asaas":**
   - Localizado no canto superior direito da página
   - Ícone de nuvem com seta para baixo

3. **Confirme a importação:**
   - Leia as informações sobre o processo
   - Clique em "Iniciar Importação"

4. **Aguarde o processamento:**
   - A importação busca até 100 clientes por vez
   - Pode levar alguns segundos

5. **Verifique os resultados:**
   - Sistema mostra quantos clientes foram importados
   - Quantos foram atualizados (se já existiam)
   - Quantos erros ocorreram (se houver)

### ⚙️ Como Funciona:

- **Clientes Novos:** Serão criados no sistema local
- **Clientes Existentes:** Serão atualizados com dados mais recentes do Asaas
- **Identificação:** Sistema usa o `asaas_id` para evitar duplicatas
- **Status:** Todos marcados como "Sincronizado com Asaas"

### 📊 Dados Importados:

```
✅ Nome completo
✅ CPF/CNPJ
✅ E-mail
✅ Telefone
✅ Celular
✅ Endereço completo
✅ ID do Asaas
```

---

## 🔄 Como Importar Recorrências

### Passo a Passo:

1. **Acesse a lista de recorrências:**
   - No menu principal, clique em "Recorrências"

2. **Clique no botão "Importar do Asaas":**
   - Localizado no canto superior direito da página
   - Botão verde com ícone de download

3. **Confirme a importação:**
   - Leia as informações sobre o processo
   - Clique em "Iniciar Importação"

4. **Aguarde o processamento:**
   - A importação busca até 100 recorrências por vez
   - Sistema também importa clientes associados automaticamente

5. **Verifique os resultados:**
   - Sistema mostra quantas recorrências foram importadas
   - Quantas foram atualizadas
   - Quantas não puderam ser importadas (por falta de cliente)
   - Quantos erros ocorreram

### ⚙️ Como Funciona:

- **Recorrências Novas:** Serão criadas no sistema local
- **Recorrências Existentes:** Serão atualizadas com dados mais recentes
- **Clientes Associados:** Se o cliente não existir localmente, será importado automaticamente
- **Identificação:** Sistema usa o `asaas_id` para evitar duplicatas

### 📊 Dados Importados:

```
✅ Descrição
✅ Valor
✅ Ciclo (Mensal, Anual, etc.)
✅ Forma de pagamento
✅ Data do próximo vencimento
✅ Data de término (se houver)
✅ Número máximo de cobranças
✅ Status (Ativa, Inativa, Expirada)
✅ Cliente associado
✅ ID do Asaas
```

---

## 🔐 Segurança

### Proteção de Dados:

✅ **Sem Duplicatas:** Sistema verifica se o registro já existe pelo `asaas_id`
✅ **Atualização Segura:** Dados existentes são atualizados, não sobrescritos
✅ **Logs de Erro:** Todos os erros são registrados para análise
✅ **Transações:** Cada registro é processado individualmente

---

## 📈 Limitações

### Importação de Clientes:

- **Máximo por vez:** 100 clientes
- **Paginação:** Se você tem mais de 100 clientes, execute a importação novamente
- **Taxa de API:** Respeita limites da API do Asaas

### Importação de Recorrências:

- **Máximo por vez:** 100 recorrências
- **Dependência:** Clientes são importados automaticamente se necessário
- **Status:** Preserva o status original do Asaas

---

## ⚠️ Cenários Comuns

### 1. "Nenhum cliente importado"

**Possíveis causas:**
- Não há clientes cadastrados no Asaas
- API Key incorreta
- Problemas de conexão

**Solução:**
- Verifique se tem clientes no painel do Asaas
- Confirme sua API Key no arquivo `.env`
- Teste a conexão com o Asaas

### 2. "Alguns clientes não foram importados"

**Possíveis causas:**
- CPF/CNPJ inválido
- Dados obrigatórios faltando
- Conflito de e-mail

**Solução:**
- Verifique os logs no terminal
- Corrija os dados no Asaas
- Execute a importação novamente

### 3. "Recorrência importada sem cliente"

**Isso não deve acontecer!**
- O sistema importa o cliente automaticamente
- Se acontecer, é um erro que será reportado

**Solução:**
- Importe os clientes primeiro
- Depois importe as recorrências

---

## 🔄 Sincronização Contínua

### Recomendações:

**Importação Inicial:**
```
1. Importe TODOS os clientes primeiro
2. Depois importe as recorrências
3. Verifique os resultados
```

**Atualizações Periódicas:**
```
1. Execute a importação semanalmente
2. Ou sempre que adicionar dados direto no Asaas
3. Sistema atualiza dados existentes automaticamente
```

**Manutenção:**
```
1. Sempre sincronize novos clientes antes de criar recorrências
2. Use o botão "Sincronizar" individual para atualizações pontuais
3. Importação não deleta dados locais
```

---

## 📝 Exemplos de Uso

### Cenário 1: Novo Sistema

```
Situação: Você já usa o Asaas e quer começar a usar este sistema

Passos:
1. Configure a API Key no .env
2. Vá em "Clientes" > "Importar do Asaas"
3. Aguarde a importação completa
4. Vá em "Recorrências" > "Importar do Asaas"
5. Pronto! Todos os dados estão sincronizados
```

### Cenário 2: Atualização de Dados

```
Situação: Você atualizou alguns clientes diretamente no Asaas

Passos:
1. Vá em "Clientes" > "Importar do Asaas"
2. Sistema atualiza automaticamente os dados modificados
3. Dados não modificados permanecem iguais
```

### Cenário 3: Recuperação de Dados

```
Situação: Você deletou algo no sistema local por engano

Passos:
1. Execute a importação correspondente
2. Dados serão reimportados do Asaas
3. Sistema usa o asaas_id para localizar registros
```

---

## 🛠️ Troubleshooting

### Erro: "Erro ao buscar clientes do Asaas"

**Verificações:**
1. API Key está correta no `.env`?
2. URL da API está correta (produção vs sandbox)?
3. Sua conta Asaas está ativa?
4. Há conexão com a internet?

### Erro: "Timeout"

**Causa:** Muitos dados para processar

**Solução:**
- A API do Asaas tem limites de tempo
- Execute a importação em horários de menor uso
- Se persistir, contate o suporte do Asaas

### Erro: "Cliente não encontrado"

**Causa:** Recorrência sem cliente associado no Asaas

**Solução:**
- Verifique a recorrência no painel do Asaas
- Associe um cliente válido
- Execute a importação novamente

---

## 📞 Suporte

### Logs de Erro:

Todos os erros são registrados no terminal onde o servidor está rodando.

Para ver detalhes:
```bash
# No terminal do servidor, procure por linhas começando com "ERROR"
```

### Documentação Adicional:

- **API do Asaas:** https://docs.asaas.com
- **Suporte Asaas:** suporte@asaas.com

---

## ✅ Checklist de Importação

Antes de importar:
- [ ] API Key configurada corretamente
- [ ] Servidor Django rodando
- [ ] Conexão com internet ativa
- [ ] Dados no Asaas conferidos

Durante a importação:
- [ ] Não fechar a página
- [ ] Aguardar mensagem de conclusão
- [ ] Verificar mensagens de erro

Após importação:
- [ ] Conferir quantidade de registros
- [ ] Verificar se dados estão corretos
- [ ] Testar sincronização individual se necessário

---

**Pronto!** Agora você pode importar seus dados do Asaas facilmente! 🎉

Para mais informações, consulte o [README.md](README.md) ou o [API_GUIDE.md](API_GUIDE.md).

