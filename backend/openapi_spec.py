openapi_spec = {
  'openapi': '3.0.3',
  'info': {
    'title': 'Finance Manager API',
    'description': 'Gerenciador de finanças pessoais e familiares',
    'version': '1.0.9'
  },
  'tags': [
    {'name': 'Usuários', 'description': 'Operações relacionadas aos usuários'},
    {'name': 'Transações', 'description': 'Operações relacionadas às transações'}
  ],
  'paths': {
    '/users': {
      'get': {
        'tags': ['Usuários'],
        'summary': 'Lista todos os usuários',
        'responses': {
          '200': {
            'description': 'Usuários carregados com sucesso',
            'content': {'application/json': {
              'schema': {'type': 'array', 'items': {'$ref': '#/components/schemas/User'}}
            }}
          },
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      },
      'post': {
        'tags': ['Usuários'],
        'summary': 'Cria um usuário',
        'requestBody': {'$ref': '#/components/requestBodies/UserCreate'},
        'responses': {
          '201': {
            'description': 'Usuário criado com sucesso',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/User'}}}
          },
          '400': {'$ref': '#/components/responses/ValidationError'},
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      }
    },
    '/transactions': {
      'get': {
        'tags': ['Transações'],
        'summary': 'Lista todas as transações e o resumo consolidado',
        'responses': {
          '200': {
            'description': 'Transações carregadas com sucesso',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/TransactionList'}}}
          },
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      }
    },
    '/users/{user_id}/transactions': {
      'parameters': [{'name': 'user_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}],
      'get': {
        'tags': ['Transações'],
        'summary': 'Lista as transações de um usuário',
        'responses': {
          '200': {
            'description': 'Transações e resumo do usuário',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/UserTransactionList'}}}
          },
          '404': {'$ref': '#/components/responses/NotFound'},
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      },
      'post': {
        'tags': ['Transações'],
        'summary': 'Cria uma transação para um usuário',
        'requestBody': {'$ref': '#/components/requestBodies/TransactionCreate'},
        'responses': {
          '201': {
            'description': 'Transação criada com sucesso',
            'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Transaction'}}}
          },
          '400': {'$ref': '#/components/responses/ValidationError'},
          '404': {'$ref': '#/components/responses/NotFound'},
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      }
    },
    '/users/{user_id}': {
      'parameters': [{'name': 'user_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}],
      'delete': {
        'tags': ['Usuários'],
        'summary': 'Deleta um usuário e suas transações',
        'responses': {
          '200': {'$ref': '#/components/responses/Deleted'},
          '404': {'$ref': '#/components/responses/NotFound'},
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      }
    },
    '/transactions/{tx_id}': {
      'parameters': [{'name': 'tx_id', 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}],
      'delete': {
        'tags': ['Transações'],
        'summary': 'Deleta uma transação',
        'responses': {
          '200': {'$ref': '#/components/responses/Deleted'},
          '404': {'$ref': '#/components/responses/NotFound'},
          '500': {'$ref': '#/components/responses/ServerError'}
        }
      }
    }
  },
  'components': {
    'schemas': {
      'User': {
        'type': 'object',
        'properties': {
          'id': {'type': 'integer'},
          'name': {'type': 'string'},
          'initials': {'type': 'string', 'maxLength': 3},
          'avatar_color': {'type': 'string', 'nullable': True},
          'balance': {'type': 'number', 'format': 'float'},
          'transaction_count': {'type': 'integer'}
        }
      },
      'UserCreate': {
        'type': 'object',
        'required': ['name', 'initials', 'avatar_color'],
        'properties': {
          'name': {'type': 'string'},
          'initials': {'type': 'string', 'maxLength': 3},
          'avatar_color': {'type': 'string'}
        }
      },
      'Transaction': {
        'type': 'object',
        'properties': {
          'id': {'type': 'integer'},
          'title': {'type': 'string'},
          'amount': {'type': 'number', 'format': 'float'},
          'type': {'type': 'string', 'enum': ['income', 'expense']},
          'category': {'type': 'string'},
          'date': {'type': 'string', 'format': 'date'},
          'user_id': {'type': 'integer'}
        }
      },
      'TransactionCreate': {
        'type': 'object',
        'required': ['title', 'amount', 'type', 'category', 'date'],
        'properties': {
          'title': {'type': 'string'},
          'amount': {'type': 'number', 'format': 'float'},
          'type': {'type': 'string', 'enum': ['income', 'expense']},
          'category': {'type': 'string'},
          'date': {'type': 'string', 'format': 'date'}
        }
      },
      'Summary': {
        'type': 'object',
        'properties': {
          'income': {'type': 'number', 'format': 'float'},
          'expenses': {'type': 'number', 'format': 'float'},
          'balance': {'type': 'number', 'format': 'float'}
        }
      },
      'Error': {
        'type': 'object',
        'properties': {
          'error': {'type': 'string'},
          'details': {'type': 'array', 'items': {'type': 'object'}}
        }
      },
      'TransactionList': {
        'type': 'object',
        'properties': {
          'summary': {'$ref': '#/components/schemas/Summary'},
          'transactions': {'type': 'array', 'items': {'$ref': '#/components/schemas/Transaction'}},
          'transaction_count': {'type': 'integer'}
        }
      },
      'UserTransactionList': {
        'type': 'object',
        'properties': {
          'user': {'type': 'string'},
          'summary': {'$ref': '#/components/schemas/Summary'},
          'transactions': {'type': 'array', 'items': {'$ref': '#/components/schemas/Transaction'}}
        }
      }
    },
    'requestBodies': {
      'UserCreate': {
        'required': True,
        'content': {'application/json': {'schema': {'$ref': '#/components/schemas/UserCreate'}}}
      },
      'TransactionCreate': {
        'required': True,
        'content': {'application/json': {'schema': {'$ref': '#/components/schemas/TransactionCreate'}}}
      }
    },
    'responses': {
      'ValidationError': {
        'description': 'Erro na validação dos dados',
        'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Error'}}}
      },
      'NotFound': {
        'description': 'Recurso não encontrado',
        'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Error'}}}
      },
      'ServerError': {
        'description': 'Erro no servidor',
        'content': {'application/json': {'schema': {'$ref': '#/components/schemas/Error'}}}
      },
      'Deleted': {
        'description': 'Recurso deletado com sucesso',
        'content': {'application/json': {'schema': {'type': 'object', 'properties': {'message': {'type': 'string'}}}}}
      }
    }
  }
}