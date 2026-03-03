/**
 * Monaco Editor configuration for Python.
 */
import * as monaco from 'monaco-editor'

export function configurePythonLanguage() {
  // Python keywords
  monaco.languages.setMonarchTokensProvider('python', {
    keywords: [
      'and', 'as', 'assert', 'break', 'class', 'continue', 'def',
      'del', 'elif', 'else', 'except', 'False', 'finally', 'for',
      'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
      'None', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
      'True', 'try', 'while', 'with', 'yield',
    ],
    builtins: [
      'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray',
      'bytes', 'callable', 'chr', 'classmethod', 'compile', 'complex',
      'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval',
      'filter', 'float', 'format', 'frozenset', 'getattr', 'globals',
      'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int',
      'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals',
      'map', 'max', 'memoryview', 'min', 'next', 'object', 'oct',
      'open', 'ord', 'pow', 'print', 'property', 'range', 'repr',
      'reversed', 'round', 'set', 'setattr', 'slice', 'sorted',
      'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
      'vars', 'zip',
    ],
    tokenizer: {
      root: [
        [/[a-zA-Z_]\w*/, {
          cases: {
            '@keywords': 'keyword',
            '@builtins': 'type.identifier',
            '@default': 'identifier',
          },
        }],
        [/"([^"\\]|\\.)*$/, 'string.invalid'],
        [/'([^'\\]|\\.)*$/, 'string.invalid'],
        [/"/, 'string', '@string_double'],
        [/'/, 'string', '@string_single'],
        [/\d+/, 'number'],
        [/#.*$/, 'comment'],
      ],
      string_double: [
        [/[^\\"]+/, 'string'],
        [/"/, 'string', '@pop'],
      ],
      string_single: [
        [/[^\\']+/, 'string'],
        [/'/, 'string', '@pop'],
      ],
    },
  })

  // Python snippets
  monaco.languages.registerCompletionItemProvider('python', {
    provideCompletionItems: () => {
      const suggestions = [
        {
          label: 'for loop',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'for ${1:item} in ${2:items}:\n\t${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'For loop',
        },
        {
          label: 'while loop',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'while ${1:condition}:\n\t${2:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'While loop',
        },
        {
          label: 'function',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'def ${1:function_name}(${2:params}):\n\t${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Function definition',
        },
        {
          label: 'class',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'class ${1:ClassName}:\n\tdef __init__(self${2:, params}):\n\t\t${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Class definition',
        },
        {
          label: 'if-else',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'if ${1:condition}:\n\t${2:pass}\nelse:\n\t${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'If-else statement',
        },
        {
          label: 'try-except',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: 'try:\n\t${1:pass}\nexcept ${2:Exception} as e:\n\t${3:pass}',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: 'Try-except block',
        },
      ]
      return { suggestions }
    },
  })
}
