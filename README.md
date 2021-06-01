Para fazer os testes é necessário criar um json com strings onde os primeiros valores dizem respeito as variaveis da formula e o ultimo valor diz respeito ao valor resultante da inequação, seguidos por outra string cujos valores indicam a função objetivo como no exemplo a seguir:

```json
{
    "constraints": [
        [2, 1, 2, 8],
        [2, 2, 3, 12],
        [2, 1, 3, 10]
    ], "objective": [20, 15, 25]
}
```