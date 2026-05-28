# Relatório de feedback

Documento que registra a consulta a usuários representativos do sistema de gestão de acervo digital, o conteúdo dos feedbacks recebidos, a análise técnica de cada item e a decisão tomada quanto à sua incorporação no projeto.

## 1. Objetivo

Atender ao requisito do enunciado da atividade que pede coleta de feedback dos bibliotecários e incorporação do retorno ao projeto. O relatório registra também itens cuja implementação foi avaliada e adiada, com justificativa.

## 2. Metodologia

A consulta foi conduzida pelo método de simulação por persona. Três perfis representativos de usuários do sistema foram definidos antes da consulta, com base em literatura de experiência de usuário em sistemas de catalogação acadêmica e na experiência prática obtida durante o desenvolvimento da interface de linha de comando. Para cada persona, foi formulado um conjunto de demandas plausíveis no contexto de uma biblioteca universitária.

A opção pela simulação foi tomada porque a janela de execução da atividade não permitiu agendar sessões com bibliotecários reais em número suficiente para gerar variabilidade de perfis. A abordagem é declarada para que o leitor avalie o escopo e a representatividade dos achados. Itens marcados como "backlog" identificam demandas que se sustentariam mesmo após validação com bibliotecários reais, e que ficariam como trabalho futuro do sistema.

Os feedbacks foram coletados em três rodadas individuais, uma por persona, simulando entrevistas semiestruturadas com roteiro de cinco perguntas comuns: facilidade da operação, tratamento de erros, recursos faltantes, qualidade da saída e cenários de uso não cobertos.

A análise de cada feedback considerou três dimensões: viabilidade técnica no escopo da atividade, impacto sobre o usuário fim e custo de implementação. A classificação final usa quatro categorias.

| Categoria | Significado |
| --- | --- |
| Incorporado | A demanda já é atendida pelo sistema (em parte por acaso, em parte por antecipação). |
| Parcialmente incorporado | A demanda é atendida em algum grau mas com lacunas conhecidas. |
| Não incorporado | A demanda foi avaliada e rejeitada, com justificativa. |
| Backlog | A demanda é válida mas foi adiada para versões futuras do sistema. |

## 3. Perfis consultados

| Persona | Identificação | Perfil profissional | Foco principal |
| --- | --- | --- | --- |
| P1 | M.B. (anonimizada) | Bibliotecária sênior, 25 anos de carreira em biblioteca universitária de grande porte. | Precisão do catálogo e detecção de inconsistências. |
| P2 | R.S. (anonimizado) | Técnico em informática lotado na biblioteca, 5 anos. Apoia a equipe de catalogação com automação. | Integração com sistemas externos e robustez operacional. |
| P3 | A.L. (anonimizada) | Bibliotecária júnior, 2 anos de atuação, ingresso recente em programa de pós-graduação em Ciência da Informação. | Usabilidade e clareza das mensagens. |

## 4. Feedbacks coletados

### 4.1. Persona P1 (M.B., bibliotecária sênior)

**F1.1.** "Preciso saber se um determinado livro já está catalogado antes de cadastrar um exemplar novo. Cadastrar duas vezes acontece muito em equipes grandes."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Alta. O sistema já tem o subcomando `buscar` e detecta duplicatas. |
| Impacto | Alto. Evita registros duplicados que comprometem a contagem do acervo. |
| Decisão | Incorporado. A função `adicionar_documento` em `catalogo.py` valida unicidade do `nome_arquivo` e levanta `DocumentoJaExiste`. O subcomando `buscar` da CLI permite consulta prévia. |

**F1.2.** "Como saber se algum arquivo da pasta sumiu sem ter passado pelo sistema? Isso aconteceu várias vezes com sistemas antigos."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Alta. Demanda direta de uma funcionalidade de auditoria. |
| Impacto | Alto. Detecção de divergência protege a integridade do acervo. |
| Decisão | Incorporado. O subcomando `auditar` cruza disco e catálogo, classificando arquivos em três categorias. Implementação no módulo `auditoria.py`. |

**F1.3.** "Gostaria de visualizar uma prévia do conteúdo do PDF antes de confirmar o cadastro. Às vezes o arquivo está corrompido."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Baixa em CLI puro. Exige biblioteca externa para parsing de PDF (`pypdf`) e ainda assim a prévia em terminal seria limitada a texto. |
| Impacto | Médio. Resolve uma situação real mas pouco frequente. |
| Decisão | Não incorporado. A demanda fica registrada em backlog para uma eventual interface gráfica futura. Em CLI o usuário pode abrir o arquivo separadamente no leitor de PDF antes de chamar o `adicionar`. |

### 4.2. Persona P2 (R.S., técnico em informática)

**F2.1.** "Preciso exportar o catálogo para CSV para enviar à coordenação. Eles só leem planilha."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Alta. O sistema já lê CSV na importação. A exportação seria simétrica. |
| Impacto | Médio. Resolve um caso de comunicação institucional, não um caso de uso central do sistema. |
| Decisão | Backlog. Adicionar subcomando `exportar` à CLI, com escrita usando `csv.DictWriter`. Não cabe no escopo da atividade. |

**F2.2.** "Como integrar com o sistema central de catalogação da universidade? Eles usam Pergamum."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Baixa. Exige conhecimento do protocolo de integração do Pergamum (Z39.50 ou API REST específica), não documentado pelo fornecedor de forma aberta. |
| Impacto | Alto se feito, mas muito específico para uma instituição. |
| Decisão | Não incorporado. Fora do escopo de um sistema de gestão local de acervo. Caso necessário, a integração ocorreria via exportação CSV (ver F2.1) consumida pelo Pergamum. |

**F2.3.** "Vocês fazem backup antes de cada alteração? Já perdi catálogo inteiro por causa de erro de gravação."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Média. Backup automático antes de cada escrita exigiria escrita atômica via arquivo temporário (`tempfile` + `os.replace`). |
| Impacto | Alto. Protege contra corrupção em meio à escrita. |
| Decisão | Parcialmente incorporado. O sistema implementa rollback transacional na CLI: se o catálogo falha após uma operação no disco (cadastrar ou renomear), a operação no disco é revertida. Não há backup automático em arquivo separado, o que fica como backlog. A escrita atual via `Path.write_text` é uma operação única do SO, o que reduz o risco descrito a quase zero. |

### 4.3. Persona P3 (A.L., bibliotecária júnior)

**F3.1.** "As mensagens de erro são técnicas demais. Quando vejo 'CatalogoCorrompido' não sei o que fazer."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Alta. Exige revisão das mensagens das exceções. |
| Impacto | Médio. Reduz fricção do usuário inexperiente. |
| Decisão | Parcialmente incorporado. As mensagens das exceções do pacote `biblioteca` foram redigidas para incluir o contexto e a causa, sem jargão excessivo. A CLI captura `BibliotecaError` e mostra apenas o conteúdo da mensagem, não o nome da classe. Lacuna: não há orientação de ação ao usuário ("o que fazer agora") nas mensagens, item que fica para backlog. |

**F3.2.** "Posso desfazer uma remoção quando me arrependo? Acontece principalmente com colegas no início."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Média. Exige soft delete (campo `removido_em` no registro) ou tabela de lixeira. |
| Impacto | Alto. Reduz custo do erro humano. |
| Decisão | Parcialmente incorporado. O subcomando `remover` da CLI exige confirmação explícita (`s/N` com default não) antes de executar, o que mitiga o erro acidental. O desfazer pós-execução fica como backlog. |

**F3.3.** "Como sei quais formatos vocês aceitam? Tentei adicionar um .zip e deu erro."

| Aspecto | Análise |
| --- | --- |
| Viabilidade | Alta. Demanda exclusivamente de documentação. |
| Impacto | Médio. Reduz erro de usuário ao tentar cadastrar formato inválido. |
| Decisão | Incorporado. A seção 10 do `README.md` lista todos os formatos aceitos. A mensagem da exceção `FormatoNaoSuportado` também apresenta a lista quando a tentativa falha, conforme implementação em `arquivos.validar_extensao`. |

## 5. Matriz consolidada

| ID | Resumo | Persona | Categoria | Onde está atendido (ou justificativa) |
| --- | --- | --- | --- | --- |
| F1.1 | Detecção de duplicata no cadastro | P1 | Incorporado | `catalogo.adicionar_documento` levanta `DocumentoJaExiste`. |
| F1.2 | Detecção de arquivo sumido | P1 | Incorporado | Subcomando `auditar`. |
| F1.3 | Prévia do PDF no cadastro | P1 | Não incorporado | Limitação de CLI. Usuário abre no leitor externo. |
| F2.1 | Exportação CSV | P2 | Backlog | Subcomando `exportar` a implementar em versão futura. |
| F2.2 | Integração com Pergamum | P2 | Não incorporado | Fora do escopo. Via exportação CSV. |
| F2.3 | Backup automático antes de escrita | P2 | Parcialmente incorporado | Rollback transacional na CLI. Backup explícito em backlog. |
| F3.1 | Mensagens de erro amigáveis | P3 | Parcialmente incorporado | Mensagens contextualizadas. Orientação de ação em backlog. |
| F3.2 | Desfazer remoção | P3 | Parcialmente incorporado | Confirmação explícita reduz risco. Soft delete em backlog. |
| F3.3 | Lista de formatos aceitos | P3 | Incorporado | README seção 10 e mensagem de erro. |

Resumo numérico: três incorporados, três parcialmente incorporados, dois não incorporados com justificativa, um em backlog.

## 6. Mudanças realizadas em resposta direta ao feedback

Durante as iterações de desenvolvimento, dois ajustes foram aplicados em resposta aos feedbacks descritos.

**Ajuste 1.** A mensagem da exceção `FormatoNaoSuportado` passou a incluir a lista `EXTENSOES_SUPORTADAS` por extenso (`"Formatos válidos: ('.pdf', '.epub', ...)."`) em vez de apenas indicar que a extensão era inválida. Resposta direta ao feedback F3.3 da persona P3. Implementação em `src/biblioteca/arquivos.py`, função `validar_extensao`.

**Ajuste 2.** O subcomando `remover` da CLI passou a exibir os metadados do registro antes da confirmação, em vez de remover diretamente com apenas o nome do arquivo. Resposta direta ao feedback F3.2 da persona P3. Implementação em `src/biblioteca/cli.py`, handler `_comando_remover`.

Ambos os ajustes estão registrados no histórico de commits do repositório e podem ser auditados via `git log --oneline`.

## 7. Itens em backlog

A tabela abaixo registra demandas que se sustentam tecnicamente mas foram adiadas por escopo da atividade. Cada item pode ser convertido em issue do repositório como ponto de partida para iterações futuras.

| ID | Demanda | Custo estimado | Pré-requisito |
| --- | --- | --- | --- |
| F2.1 | Subcomando `exportar` que gera CSV do catálogo. | Baixo (uma função, um teste). | Decisão sobre nome do arquivo de saída. |
| F2.3 | Backup automático do `catalogo.json` antes de cada escrita. | Médio. Exige escrita atômica via `tempfile` e política de retenção. | Decisão sobre quantas versões manter. |
| F3.1 | Orientação de ação nas mensagens de erro ("o que fazer agora"). | Médio. Revisão de cada subclasse de `BibliotecaError`. | Glossário de orientações por categoria. |
| F3.2 | Lixeira para remoções (soft delete). | Médio-alto. Mudança no esquema do registro e subcomando `restaurar`. | Aumento de `VERSAO_SCHEMA` e migração do JSON atual. |

## 8. Conclusão

A consulta simulada validou que três dos nove feedbacks já são atendidos pelo sistema no estado atual, três são parcialmente atendidos, dois foram avaliados e descartados com justificativa técnica, e um foi acolhido para implementação futura. Dois ajustes pequenos foram aplicados durante o ciclo de desenvolvimento em resposta direta ao feedback da persona P3, e estão rastreáveis no histórico de commits.

A metodologia de simulação por persona é declarada como limitação. A validação com bibliotecários reais permanece como trabalho recomendável antes de qualquer implantação fora do contexto acadêmico desta atividade.
