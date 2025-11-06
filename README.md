# CRM-Dashboard

Uma solução para construir dashboards dinâmicos usando dados extraídos de plataformas de CRM como o Kommo.  
Inclui backend para processamento de dados e frontend para visualização de métricas.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Instalação](#instalação)
- [Uso](#uso)
- [Configuração](#configuração)
- [Contribuição](#contribuição)
- [Licença](#licença)

---

## 🚀 Visão Geral

O **CRM-Dashboard** permite integrar dados de um sistema de CRM (como o Kommo), processá-los e exibir painéis interativos de desempenho.  
Ideal para equipes que precisam acompanhar métricas de vendas, funil de leads e conversões em tempo real.

---

## ⚙️ Funcionalidades

- Extração e importação de dados de CRM (Kommo, entre outros)
- API backend modular
- Frontend de dashboard com visualização de métricas
- Suporte a contêinerização com **Docker**
- Configuração simples via variáveis de ambiente

---

## 🧱 Arquitetura

```
crm-dashboard/
│
├── backend/               # API e lógica de integração com CRM
├── frontend/dashboard/     # Aplicação de visualização
├── docker-compose.yml      # Orquestração de containers
└── .gitignore              # Arquivos ignorados pelo Git
```

- **Backend:** processa dados, expõe endpoints de API  
- **Frontend:** consome APIs e exibe dashboards em tempo real  

---

## 🛠️ Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/LLawli/crm-dashboard.git
cd crm-dashboard
```

### 2. Usando Docker (recomendado)
```bash
docker-compose up --build
```

### 3. Instalação manual

**Backend**
```bash
cd backend
pip install -r requirements.txt
```

---

## 💡 Uso

- Backend disponível em: `http://localhost:<porta>/api`
- Frontend disponível em: `http://localhost:<porta>/`
- Configure o token da CRM no `.env`
- Acesse o dashboard e visualize métricas de vendas, leads e funil
- **Pode exigir configuração manual de pipeline_id, status_id e field_id nas rotas da api**

---

## ⚙️ Configuração

Crie um arquivo `.env` no diretório `backend` com variáveis como:
```bash
KOMMO_KEY=<sua_chave_api>
KOMMO_DOMAIN=<dominio_do_crm>
```

---

## 🤝 Contribuição

Contribuições são bem-vindas!  
1. Faça um fork do projeto  
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)  
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)  
4. Faça push (`git push origin feature/nova-funcionalidade`)  
5. Abra um **Pull Request**

---

## 📄 Licença

Distribuído sob a licença **The Unlicense**.  
Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🧩 Contato

Desenvolvido por **LLawli**  
GitHub: [@LLawli](https://github.com/LLawli)
