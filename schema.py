CREATE_USER = {
    'type': 'object',
    'properties': {
        'name': {
            'type': 'string',
            'maxLength': 256,
        },
        'advertisements':{
            'type': "null",
        }
    },
    'required': ['name']
}

CREATE_ADVERTISEMENT = {
    'type': 'object',
    'properties': {
        'title': {
            'type': 'string',
            'maxLength': 64,
        },
        'description': {
            'type': 'string',
            'maxLength': 256,
        },
        'owner': {
            'type': 'integer',
            'minimum': 0,
        },
        'created_at':{
            'type': 'null',
        }
    },
    'required': ['title', 'owner']
}

UPDATE_ADVERTISEMENT = {
    'type': 'object',
    'properties': {
        'title': {
            'type': 'string',
            'maxLength': 64,
        },
        'description': {
            'type': 'string',
            'maxLength': 256,
        },
        'owner': {
            'type': 'integer',
            'minimum': 0,
        }
    }
}