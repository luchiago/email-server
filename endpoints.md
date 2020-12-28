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
- JSON de entrada:

```json
{
  "sender": "nome do cara", // esse ja pega do cookie
  "receiver": "nome do recebedor",
  "subject": "assunto",
  "body": "texto",
}
```

- Sucesso: Status 201
- Erro:

```json
{
  "error": "Recebedor não existente"
}
```

## Listar mensagens

- Será um GET
- Endpoint: /messages
- JSON de resposta:

```json
{
  "sent": [] lista de mensagens que pode ser vazio ou seguir o padrão de uma mensagem,
  "received": [] lista de mensagens que pode ser vazio ou seguir o padrão de uma mensagem,

}
```

## Apagar mensagens

- Será um DELETE
- Endpoint: /messages/:id
- JSON de resposta:
  - Sucesso: Status 204

  - Erro:
  Caso a mensagem não exista:

  ```json
  {
    "error": "Não encontrado
  }
  ```

## Abrir mensagem

- Será um GET
- Endpoint: /messages/:id

- JSON de resposta:
  - Sucesso:

  ```json
  {
    "sender": "nome do sender",
    "receiver": "nome do receiver",
    "subject": "assunto",
    "body": "texto"
    "reply": [] lista com os emails de resposta, vazio se não houver, que cada um segue o padrão de email
  }
  ```

  - Erro:
  Caso a mensagem não exista:

  ```json
  {
    "error": "Não encontrado
  }
  ```

## Encaminhar mensagem

- Será um PATCH
- Endpoint: /messages/:id
- Nessa parte, quando ele for encaminhar, colocar o mesmo assunto só que com "ENC:" no inicio

```json
{
  "receiver": "nome do receiver"
}
```

- JSON de resposta:
  - Sucesso: Só vai vir o status 200

  - Erro:
  Caso o sender e o receiver sejam os mesmos

  ```json
  {
    "error": "Não pode ser o mesmo"
  }
  ```

  Caso o receiver não exista

    ```json
  {
    "error": "Recebedor de email inexistente"
  }
  ```

## Responder mensagem

- Será um PUT
- Endpoint: /messages/:id
- Nessa parte, quando ele for responder, colocar o mesmo assunto só que com "RE:" no inicio
- JSON de exemplo:

```json
{
  "body": "texto da resposta"
}
```

- JSON de resposta:
  - Sucesso: Só vai vir o status 200

  - Erro:
  Caso o sender e o receiver sejam os mesmos

  ```json
  {
    "error": "Não pode ser o mesmo"
  }
  ```

  Caso o receiver não exista

    ```json
  {
    "error": "Recebedor de email inexistente"
  }
  ```

## Login

- Será um POST
- Endpoint: /login
- JSON de exemplo:

```json
{
  "name": "lucas"
}
```

- JSON de resposta:
  - Sucesso: Só vai vir o status 200

  - Erro:

  ```json
  {
    "error": "Usuário não encontrado"
  }
  ```
