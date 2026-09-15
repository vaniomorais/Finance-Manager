SCHEMA = '#/components/schemas/'


def ref(name):
    return {'$ref': f'{SCHEMA}{name}'}


def json_response(description, schema):
    return {'description': description, 'content': {'application/json': {'schema': schema}}}


def error(description):
    return json_response(description, ref('Error'))


def operation(tag, summary, responses, body=None):
    spec = {'tags': [tag], 'summary': summary, 'responses': responses}
    if body:
        spec['requestBody'] = {'required': True, 'content': {'application/json': {'schema': ref(body)}}}
    return spec


def path_parameter(name):
    return {'parameters': [{'name': name, 'in': 'path', 'required': True, 'schema': {'type': 'integer'}}]}


validation_error = error('Dados inválidos')
not_found = error('Recurso não encontrado')
server_error = error('Erro interno')
deleted = json_response('Recurso removido', {'type': 'object', 'properties': {'message': {'type': 'string'}}})

openapi_spec = {
    'openapi': '3.0.3',
    'info': {'title': 'Finance Manager API', 'version': '1.0.9'},
    'tags': [{'name': 'Usuários'}, {'name': 'Transações'}],
    'paths': {
        '/users': {
            'get': operation('Usuários', 'Retorna uma lista de todos os usuários', {
                '200': json_response('OK', {'type': 'array', 'items': ref('User')}), '500': server_error
            }),
            'post': operation('Usuários', 'Cria um novo usuário', {
                '201': json_response('Usuáriocadastrado', ref('User')), '400': validation_error, '500': server_error
            }, 'UserCreate')
        },
        '/transactions': {
            'get': operation('Transações', 'Retorna uma lista de todas as transações e resumo financeiro', {
                '200': json_response('OK', ref('TransactionList')), '500': server_error
            })
        },
        '/users/{user_id}/transactions': {
            **path_parameter('user_id'),
            'get': operation('Transações', 'Retorna uma lista de transações por ID de usuário', {
                '200': json_response('OK', ref('UserTransactionList')), '404': not_found, '500': server_error
            }),
            'post': operation('Transações', 'Cadastra nova transação para o usuário', {
                '201': json_response('Transação cadastrada', ref('Transaction')), '400': validation_error,
                '404': not_found, '500': server_error
            }, 'TransactionCreate')
        },
        '/users/{user_id}': {
            **path_parameter('user_id'),
            'delete': operation('Usuários', 'Remove o usuário e transações vinculadas', {
                '200': deleted, '404': not_found, '500': server_error
            })
        },
        '/transactions/{tx_id}': {
            **path_parameter('tx_id'),
            'delete': operation('Transações', 'Remove uma transação', {
                '200': deleted, '404': not_found, '500': server_error
            })
        }
    },
    'components': {
        'schemas': {
            'User': {'type': 'object', 'properties': {
                'id': {'type': 'integer'}, 'name': {'type': 'string'},
                'initials': {'type': 'string', 'maxLength': 3}, 'avatar_color': {'type': 'string', 'nullable': True},
                'balance': {'type': 'number', 'format': 'float'}, 'transaction_count': {'type': 'integer'}
            }},
            'UserCreate': {'type': 'object', 'required': ['name', 'initials', 'avatar_color'], 'properties': {
                'name': {'type': 'string'}, 'initials': {'type': 'string', 'maxLength': 3},
                'avatar_color': {'type': 'string'}
            }},
            'Transaction': {'type': 'object', 'properties': {
                'id': {'type': 'integer'}, 'title': {'type': 'string'}, 'amount': {'type': 'number', 'format': 'float'},
                'type': {'type': 'string', 'enum': ['income', 'expense']}, 'category': {'type': 'string'},
                'date': {'type': 'string', 'format': 'date'}, 'user_id': {'type': 'integer'}
            }},
            'TransactionCreate': {'type': 'object', 'required': ['title', 'amount', 'type', 'category', 'date'], 'properties': {
                'title': {'type': 'string'}, 'amount': {'type': 'number', 'format': 'float'},
                'type': {'type': 'string', 'enum': ['income', 'expense']}, 'category': {'type': 'string'},
                'date': {'type': 'string', 'format': 'date'}
            }},
            'Summary': {'type': 'object', 'properties': {
                'income': {'type': 'number', 'format': 'float'}, 'expenses': {'type': 'number', 'format': 'float'},
                'balance': {'type': 'number', 'format': 'float'}
            }},
            'Error': {'type': 'object', 'properties': {'error': {'type': 'string'}, 'details': {'type': 'array'}}},
            'TransactionList': {'type': 'object', 'properties': {
                'summary': ref('Summary'), 'transactions': {'type': 'array', 'items': ref('Transaction')},
                'transaction_count': {'type': 'integer'}
            }},
            'UserTransactionList': {'type': 'object', 'properties': {
                'user': {'type': 'string'}, 'summary': ref('Summary'),
                'transactions': {'type': 'array', 'items': ref('Transaction')}
            }}
        }
    }
}
