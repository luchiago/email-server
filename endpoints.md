# Endpoints do Email Web Service

Nós temos que completar essas tarefas:

- [ ] Enviar mensagem
- [ ] Listar mensagens
- [ ] Apagar mensagens
- [ ] Abrir mensagem
- [ ] Encaminhar mensagem
- [ ] Responder Mensagem

## Enviar mensagem

- Será um POST
- Endpoint: /messages
- JSON esperado:

```json
{
  "sender": <string>,
  "receiver": <string>,
  "subject": <string>,
  "body": <string> 
}
```

## Listar mensagens

- Será um GET
- Endpoint: /messages
- JSON da resposta:

## Apagar mensagens

- Será um DELETE
- Endpoint: /messages/:id

## Abrir mensagem

- Será um GET
- Endpoint: /messages/:id

## Encaminhar mensagem

- Será um PATCH
- Endpoint: /messages/:id

## Responder mensagem

- Será um PUT
- Endpoint: /messages/:id
