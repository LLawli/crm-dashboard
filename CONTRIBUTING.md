# Guia de Contribuição

Obrigado por seu interesse em contribuir com o **CRM-Dashboard**!  
Este documento descreve o fluxo de contribuição, padrões de código e boas práticas para colaborar de forma eficiente.

---

## 📌 Sumário

- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Commits](#commits)
- [Pull Requests](#pull-requests)
- [Relato de Problemas (Issues)](#relato-de-problemas-issues)
- [Boas Práticas](#boas-práticas)
- [Contato](#contato)

---

## 🧩 Como Contribuir

1. Faça um **fork** do repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/crm-dashboard.git
   ```
2. Crie uma nova branch para sua alteração:
   ```bash
   git checkout -b feature/nome-da-funcionalidade
   ```
3. Faça suas modificações e adicione os commits necessários.
4. Teste localmente antes de enviar.
5. Faça **push** para o seu fork:
   ```bash
   git push origin feature/nome-da-funcionalidade
   ```
6. Crie um **Pull Request** no repositório principal.

---

## ⚙️ Configuração do Ambiente

Para rodar o projeto localmente:

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app
```

Ou use Docker:
```bash
docker-compose up --build
```

---

## 🧾 Padrões de Código

- **Python (Backend):**
  - Siga o padrão [PEP 8](https://peps.python.org/pep-0008/)
  - Nomeie funções e variáveis em *snake_case*
  - Utilize *type hints* quando possível
  - Mantenha docstrings curtas e objetivas

- **JavaScript/TypeScript (Frontend):**
  - Use *camelCase* para variáveis e funções
  - Siga o estilo do ESLint configurado no projeto
  - Componentes React devem ser funcionais
  - Prefira hooks a classes

- **Geral:**
  - Evite código duplicado
  - Sempre inclua comentários em trechos complexos
  - Nomeie commits e PRs de forma descritiva

---

## 🧱 Commits

Use mensagens curtas e descritivas, preferindo o formato:

```
<tipo>: <descrição>
```

Exemplos:
```
feat: adiciona filtro de data no dashboard
fix: corrige erro de autenticação no backend
docs: atualiza instruções do README
```

Tipos comuns:
- `feat` — nova funcionalidade  
- `fix` — correção de bug  
- `docs` — mudanças na documentação  
- `refactor` — refatoração de código  
- `test` — adição ou melhoria de testes  
- `chore` — tarefas diversas sem impacto direto no código  

---

## 🔁 Pull Requests

- Certifique-se de que todos os testes passam antes de enviar
- Descreva claramente **o que foi alterado** e **por que**
- Inclua prints ou GIFs se a mudança for visual
- Mantenha o escopo do PR pequeno e específico
- Evite incluir commits não relacionados

---

## 🐞 Relato de Problemas (Issues)

Para reportar um problema:
1. Verifique se já existe uma issue semelhante.
2. Se não existir, abra uma nova em [Issues](../../issues).
3. Descreva claramente:
   - O problema encontrado
   - Passos para reproduzir
   - Resultado esperado
   - Logs ou capturas de tela (se aplicável)

---

## 🧠 Boas Práticas

- Faça pequenas mudanças incrementais
- Atualize a documentação quando necessário
- Mantenha o código limpo e legível
- Priorize simplicidade e clareza

---

## 📫 Contato

Caso tenha dúvidas ou sugestões, abra uma **Issue** ou entre em contato com o mantenedor do projeto:  
[GitHub: @LLawli](https://github.com/LLawli)

---

**Obrigado por contribuir para o CRM-Dashboard!**
