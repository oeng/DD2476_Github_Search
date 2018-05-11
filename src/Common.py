class IndexSettings:
    settings = {}
    settings_separate = {}
    analyzer = {
        'analysis': {
            'analyzer': {
                'camel': {
                    'type': 'pattern',
                    'pattern': '([^\\p{L}\\d]+)|(?<=\\D)(?=\\d)|(?<=\\d)(?=\\D)|(?<=[\\p{L}&&[^\\p{Lu}]])(?=\\p{Lu})|(?<=\\p{Lu})(?=\\p{Lu}[\\p{L}&&[^\\p{Lu}]])'
                }
            }
        }
    }
    mappings = {'mappings': {
        'java': {
                'properties': {
                    # 'type': 'nested', # Tror denna måste bort för att
                    # dokumenten ska bli nested.
                    'filename': {'type': 'text', 'analyzer': 'camel'},
                    'filepath': {'type': 'keyword'},
                    'package': {'type': 'text', 'analyzer': 'simple'},
                    'functions': {
                        'type': 'nested',
                        'properties': {
                            'name': {'type': 'text', 'analyzer': 'camel'},
                            'start_row': {'type': 'integer'},
                            'end_row': {'type': 'integer'},
                            'return_type': {'type': 'text'},
                        },
                    },
                    'classes': {
                        'type': 'nested',
                        'properties': {
                            'name': {'type': 'text', 'analyzer': 'camel'},
                            'start_row': {'type': 'integer'},
                            'end_row': {'type': 'integer'},
                        },
                    }
                }
                }
    }
    }
    mappings_separate = {
        'java': {
            'properties': {
                'category': {'type': 'keyword'},
                'filepath': {'type': 'keyword'},
                'package': {'type': 'text', "analyzer": "camel"},
                'name': {'type': 'text', 'analyzer': 'camel'},
                'start_row': {'type': 'integer'},
                'end_row': {'type': 'integer'},
                'return_type': {'type': 'text'},
            },
        }
    }
    settings['settings'] = analyzer
    settings['mapping'] = mappings
    settings_separate['settings'] = analyzer
    settings_separate['mappings'] = mappings_separate
