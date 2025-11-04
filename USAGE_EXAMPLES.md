# 📖 Exemplos de Uso - Asaas Manager

## 🎯 Casos de Uso Práticos

### Caso 1: Academia de Musculação 🏋️

#### Contexto
Academia "Força Total" quer gerenciar mensalidades dos alunos.

#### Passo a Passo

**1. Cadastrar Aluno como Cliente**
```
Nome: João Carlos Silva
CPF: 123.456.789-01
Email: joao.carlos@email.com
Celular: (11) 98765-4321
Endereço: Rua das Palmeiras, 456
Bairro: Centro
CEP: 01234-567
```

**2. Criar Mensalidade como Recorrência**
```
Cliente: João Carlos Silva
Descrição: Mensalidade Academia - Plano Premium
Valor: R$ 150,00
Ciclo: Mensal
Forma de Pagamento: Boleto
Próximo Vencimento: 01/12/2025
```

**Resultado:** ✅ João receberá boleto todo dia 1 de cada mês!

---

### Caso 2: Escola de Idiomas 🎓

#### Contexto
Escola "English Fast" tem cursos com pagamento trimestral.

#### Passo a Passo

**1. Cadastrar Estudante**
```
Nome: Maria Eduarda Santos
CPF: 987.654.321-00
Email: maria.eduarda@email.com
Celular: (11) 91234-5678
```

**2. Criar Assinatura Trimestral**
```
Cliente: Maria Eduarda Santos
Descrição: Curso de Inglês Intermediário
Valor: R$ 450,00
Ciclo: Trimestral
Forma de Pagamento: PIX
Próximo Vencimento: 15/12/2025
Número Máximo de Cobranças: 4 (1 ano = 4 trimestres)
Data de Término: 15/12/2026
```

**Resultado:** ✅ Maria pagará 4 parcelas trimestrais via PIX!

---

### Caso 3: SaaS / Software 💻

#### Contexto
Software "CloudManager" com assinatura anual.

#### Passo a Passo

**1. Cadastrar Empresa Cliente**
```
Nome: Tech Solutions LTDA
CNPJ: 12.345.678/0001-90
Email: contato@techsolutions.com.br
Telefone: (11) 4040-1234
Endereço: Av. Paulista, 1000
Complemento: Sala 1501
Bairro: Bela Vista
CEP: 01310-100
```

**2. Criar Assinatura Anual**
```
Cliente: Tech Solutions LTDA
Descrição: Plano Enterprise - CloudManager
Valor: R$ 2.400,00
Ciclo: Anual
Forma de Pagamento: Cartão de Crédito
Próximo Vencimento: 01/01/2026
```

**Resultado:** ✅ Cobrança anual automática no cartão!

---

### Caso 4: Condomínio 🏘️

#### Contexto
Condomínio "Residencial Solar" quer gerenciar taxas condominiais.

#### Passo a Passo

**1. Cadastrar Morador**
```
Nome: Carlos Alberto Oliveira
CPF: 456.789.123-45
Email: carlos.oliveira@email.com
Celular: (11) 96543-2109
Endereço: Rua das Acácias, 789
Complemento: Apto 302 - Bloco B
Bairro: Jardim das Flores
CEP: 04567-890
```

**2. Criar Taxa Condominial**
```
Cliente: Carlos Alberto Oliveira
Descrição: Taxa Condominial - Apto 302B
Valor: R$ 850,00
Ciclo: Mensal
Forma de Pagamento: Boleto
Próximo Vencimento: 10/12/2025
```

**Resultado:** ✅ Boleto gerado automaticamente todo dia 10!

---

### Caso 5: Clínica Odontológica 🦷

#### Contexto
Clínica "Sorriso Perfeito" oferece planos de manutenção.

#### Passo a Passo

**1. Cadastrar Paciente**
```
Nome: Ana Paula Ferreira
CPF: 321.654.987-12
Email: ana.ferreira@email.com
Celular: (11) 94567-8901
```

**2. Criar Plano Semestral**
```
Cliente: Ana Paula Ferreira
Descrição: Plano Manutenção Odontológica
Valor: R$ 300,00
Ciclo: Semestral
Forma de Pagamento: PIX
Próximo Vencimento: 20/01/2026
Número Máximo de Cobranças: 4 (2 anos)
```

**Resultado:** ✅ Cobrança a cada 6 meses por 2 anos!

---

### Caso 6: Streaming de Conteúdo 📺

#### Contexto
Plataforma "VideoFlix" com assinatura mensal.

#### Passo a Passo

**1. Cadastrar Assinante**
```
Nome: Pedro Henrique Costa
CPF: 159.753.486-20
Email: pedro.costa@email.com
Celular: (11) 99876-5432
```

**2. Criar Assinatura Mensal**
```
Cliente: Pedro Henrique Costa
Descrição: Plano Premium VideoFlix
Valor: R$ 34,90
Ciclo: Mensal
Forma de Pagamento: Cartão de Crédito
Próximo Vencimento: 05/12/2025
```

**Resultado:** ✅ Renovação automática mensal no cartão!

---

### Caso 7: Clube de Assinatura 📦

#### Contexto
"Box Gourmet" entrega caixa mensal de produtos.

#### Passo a Passo

**1. Cadastrar Cliente**
```
Nome: Juliana Martins Rodrigues
CPF: 753.159.486-33
Email: ju.martins@email.com
Celular: (11) 93214-5678
Endereço: Rua dos Girassóis, 234
Complemento: Casa 2
Bairro: Vila Nova
CEP: 05678-901
```

**2. Criar Assinatura com Limite**
```
Cliente: Juliana Martins Rodrigues
Descrição: Box Gourmet Premium
Valor: R$ 89,90
Ciclo: Mensal
Forma de Pagamento: Cartão de Crédito
Próximo Vencimento: 01/12/2025
Número Máximo de Cobranças: 6 (teste de 6 meses)
Data de Término: 01/06/2026
```

**Resultado:** ✅ 6 cobranças mensais, depois cancela automaticamente!

---

## 🔄 Operações Comuns

### Editar Valor da Recorrência

**Cenário:** Academia aumentou o preço

1. Acesse "Recorrências"
2. Encontre a recorrência do cliente
3. Clique em "Editar"
4. Altere o valor: R$ 150,00 → R$ 165,00
5. Clique em "Salvar"
6. ✅ Próximas cobranças serão no novo valor!

### Cancelar Assinatura

**Cenário:** Cliente pediu cancelamento

1. Acesse "Recorrências"
2. Encontre a recorrência
3. Clique em "Excluir"
4. Confirme a exclusão
5. ✅ Recorrência cancelada no Asaas!

### Sincronizar Cliente Manualmente

**Cenário:** Erro na sincronização anterior

1. Acesse "Clientes"
2. Encontre o cliente
3. Clique no menu (⋮)
4. Selecione "Sincronizar"
5. ✅ Dados atualizados no Asaas!

### Alterar Dados do Cliente

**Cenário:** Cliente mudou de endereço

1. Acesse "Clientes"
2. Clique em "Editar"
3. Atualize o endereço
4. Clique em "Salvar"
5. ✅ Dados sincronizados automaticamente!

---

## 📊 Interpretando o Dashboard

### Card: Total de Clientes
```
Total de Clientes: 150
```
**Significa:** 150 clientes cadastrados no sistema

### Card: Total de Recorrências
```
Total de Recorrências: 120
```
**Significa:** 120 assinaturas criadas (ativas ou não)

### Card: Recorrências Ativas
```
Recorrências Ativas: 95
```
**Significa:** 95 assinaturas cobrando atualmente

### Card: Clientes Sincronizados
```
Clientes Sincronizados: 145
```
**Significa:** 145 de 150 clientes estão no Asaas (5 precisam sincronizar)

---

## ⚠️ Cenários de Erro e Solução

### Erro: "Cliente precisa estar sincronizado"

**Situação:** Tentou criar recorrência para cliente não sincronizado

**Solução:**
1. Vá em "Clientes"
2. Encontre o cliente
3. Clique em "Sincronizar"
4. Aguarde mensagem de sucesso
5. Volte e crie a recorrência

### Erro: "CPF/CNPJ já existe"

**Situação:** Tentou cadastrar cliente com CPF já no Asaas

**Solução:**
1. Verifique se o cliente já existe
2. Use o cliente existente
3. Ou use CPF/CNPJ diferente

### Erro: "API Key inválida"

**Situação:** Problema na configuração

**Solução:**
1. Abra o arquivo `.env`
2. Verifique a API Key
3. Confirme se está correta
4. Reinicie o servidor

---

## 💡 Dicas de Uso

### ✅ Organize por Descrição
Use descrições claras:
- ❌ Ruim: "Plano 1"
- ✅ Bom: "Mensalidade Academia - Plano Premium"

### ✅ Configure Datas Corretas
- **Primeira cobrança:** Use data futura
- **Data de término:** Opcional, use apenas se necessário
- **Máximo de cobranças:** Útil para contratos temporários

### ✅ Escolha a Forma de Pagamento Adequada
- **Boleto:** Valor mais alto, prazo maior
- **Cartão:** Pagamentos automáticos
- **PIX:** Pagamentos rápidos

### ✅ Use Sandbox para Testes
Antes de usar em produção:
1. Configure ambiente sandbox
2. Teste todos os fluxos
3. Verifique no painel Asaas
4. Depois migre para produção

### ✅ Mantenha Dados Atualizados
- Sincronize sempre que alterar
- Verifique status no dashboard
- Confirme no painel Asaas

---

## 🎓 Fluxo Ideal

```
1. Configurar API Key
   ↓
2. Testar no Sandbox
   ↓
3. Cadastrar primeiro cliente
   ↓
4. Verificar sincronização
   ↓
5. Criar primeira recorrência
   ↓
6. Confirmar no Asaas
   ↓
7. Monitorar dashboard
   ↓
8. Gerenciar conforme necessário
```

---

**Pronto! Agora você sabe usar o sistema em qualquer cenário!** 🚀

