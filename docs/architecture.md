# Arquitetura do Pipeline de Webhooks

Fluxo de processamento de mensagens e erros da Meta.

## Fluxo de Dados

1. **Recepção de Erros**: O Worker recebe webhooks de erro da Meta.
2. **Registro de Erros**: Erros são persistidos na tabela `meta_erros`.
3. **Análise de Retentativa**:
   - Se o erro for passível de retentativa:
     - Busca o ID da mensagem na tabela `messages`.
     - Identifica o serviço de origem via campo `type` (`disparo` ou `followup`).
4. **Lógica por Serviço**:
   - **Follow-up**: Verifica se não há um próximo follow-up agendado (margem de segurança de 1h) para evitar inversão.
   - **Disparos**: Atualiza o ID antigo na mensagem (mantendo credenciais extras).
5. **Notificação e Blacklist**:
   - Entradas críticas são movidas para a "Lista dos Pretos" (Blacklist).
   - O grupo de suporte é notificado via WhatsApp.

## Definição de Serviços (Campo `type`)
- `disparo`: Mensagens de envio em massa/ativação.
- `followup`: Mensagens de acompanhamento automático.
- `conversation`: Diálogo padrão do assistente.
