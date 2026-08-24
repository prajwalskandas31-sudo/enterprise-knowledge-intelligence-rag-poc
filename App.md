Build an independent, open-source Enterprise Knowledge Intelligence POC from scratch that implements a simplified end-to-end RAG architecture without depending on Snowflake or Cortex AI. The purpose is educational: every major component must be explicit and understandable so that it can later be mapped one-to-one against Snowflake Cortex capabilities.

Implement document ingestion, text extraction, chunking, metadata management, embedding generation, vector/semantic retrieval, context assembly, LLM generation, source attribution, configuration management, API endpoints, and a minimal user interface.

Keep the architecture modular and provider-agnostic. LLM, embedding, and retrieval providers must be replaceable through configuration rather than hard-coded throughout the application.

Provide a complete runnable repository with clean Python structure, requirements, environment configuration, Docker support where useful, sample data, tests, error handling, logging, and a comprehensive README.

The README must explain the architecture, request lifecycle, RAG pipeline, each major component, why it exists, alternatives, limitations, and how to run the application locally.

Create a dedicated docs/snowflake-cortex-mapping.md explaining how each independently implemented component corresponds conceptually to capabilities available in Snowflake and Cortex AI. Clearly distinguish between components that Cortex can replace, components that Snowflake provides natively, and components that remain application responsibilities.

Do not falsely claim feature equivalence. Where Snowflake/Cortex provides a managed capability rather than an identical implementation, explicitly explain the difference.

Optimize for educational clarity and reproducibility rather than enterprise-scale complexity. Avoid unnecessary frameworks, microservices, orchestration platforms, authentication systems, or infrastructure.

The final repository must be understandable by a developer attending an FDP workshop, clonable from GitHub, configurable with environment variables, and runnable using clear documented commands.

Integrate Snowflake Cortex Analyst as a second intelligence engine alongside the existing enterprise-document RAG pipeline, with automated query routing distinguishing structured analytics questions from unstructured document knowledge queries.

Before implementation, inspect the repository requirements and produce a concise architecture plan. Then implement incrementally and verify that the application actually runs. Do not merely generate placeholder files.