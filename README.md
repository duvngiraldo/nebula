# Nebula - Data Lake Architecture

## 📂 Contents

* **[Part 1: Technical Challenge](#🎯-part-1-technical-challenge)**
* **[Part 2: Data Lake Architecture](#🏗️-part-2-data-lake-architecture)**
  * [1. Infraestructura (IaC)](#1-infraestructura-iac)
  * [2. Ingesta (CDC)](#2-ingesta-cdc)
  * [3. Multi-fuente](#3-multi-fuente)
  * [4. Gobierno y confianza](#4-gobierno-y-confianza)

---

## 🎯 Part 1: Technical Challenge

* **[`challenge/`](challenge/)**
  * Proyecto en Python utilizando la librería **Polars** para calcular las agregaciones:
    - Leads por día
    - Tasa de conversión
    - Llamadas efectivas por día
    - Llamadas efectivas por agente
---

## 🏗️ Part 2: Data Lake Architecture

### 🗺️ Diagrama de Arquitectura
![Infrastructure diagram](documentation/architecture-diagram.png)

### 1. Infraestructura (IaC)

Esta sección detalla los componentes de AWS necesarios para desplegar esta arquitectura mediante **Infraestructura como Código (IaC)**, utilizando herramientas como Terraform, AWS CloudFormation o AWS CDK. Se han incluido los servicios de red, seguridad, orquestación y monitoreo que no aparecen explícitamente en el diagrama de arquitectura pero que son indispensables para un entorno productivo.

| Categoría | Servicio de AWS | Función en la Arquitectura | Enfoque de IaC / Eficiencia |
| :--- | :--- | :--- | :--- |
| **Almacenamiento** | **Amazon S3** | Foundation del Data Lake. Almacenamiento desacoplado en capas: *Raw* (JSON), *Clean* (Iceberg) y *Marts* (Iceberg). | Bajo coste (~$0.023/GB). Se definen políticas de ciclo de vida (Lifecycle Rules) vía IaC para mover datos antiguos a Glacier. |
| **Ingesta** | **AWS DMS** | Réplica de datos desde PostgreSQL (carga inicial + CDC continuo). | Se definen `ReplicationInstances`, `SourceEndpoints`, `TargetEndpoints` y `ReplicationTasks` en código. Lee logs transaccionales asíncronamente. |
| | **Amazon API Gateway** | Expone endpoints públicos HTTPS para webhooks externos. | Integración directa de servicio (*Service Integration*) hacia Firehose definida en VTL vía IaC, sin Lambda intermedia. |
| | **Amazon Kinesis Firehose** | Entrega continua y agrupada (*buffering*) de eventos hacia S3 Raw. | Evita el *"Small Files Problem"* agrupando por tiempo (60s) o tamaño (5MB). |
| **Computo** | **Amazon Athena** | Motor de consultas SQL Serverless para ELT y MERGE sobre Iceberg. | Sustituye a AWS Glue Spark Jobs. Se definen `Workgroups` vía IaC para controlar costes y aislar cargas de trabajo. Se paga por TB escaneado. |
| | **AWS Lambda** | Orquestación ligera de transformaciones Athena (programada en Rust). | Cómputo serverless con coste por milisegundo de ejecución. Se despliega el paquete de código y variables de entorno vía IaC. |
| **Gobierno y Metadatos** | **AWS Glue Data Catalog** | Catálogo centralizado de metadatos, esquemas e histórico de Iceberg. | Gobierno Serverless. Se definen `Databases` y `Tables` (DDL Iceberg) iniciales vía IaC. |
| | **AWS Lake Formation** | Control de acceso granular (fila/columna) unificado sobre el Glue Catalog. | Se definen permisos de IAM y políticas de Lake Formation en código para seguridad unificada. |
| **Red (Network)** | **Amazon VPC** | Aislamiento de red para DMS y orígenes de datos privados. | IaC define Subnets, Route Tables, Internet Gateways y NAT Gateways. |
| | **VPC Endpoints (Gateway/Interface)** | Permite que DMS y Lambda se comuniquen de forma privada con S3, Athena y Glue sin salir a la internet pública. | IaC configura `vpce` para S3, Glue y Athena, mejorando seguridad y costes de tráfico. |
| **Seguridad y Cifrado** | **AWS IAM** | Gestión de identidades y roles para permisos entre servicios. | IaC define roles mínimos necesarios (p.ej., rol para que Firehose escriba en S3). |
| | **AWS KMS** | Gestión de claves de cifrado en reposo para S3, Kinesis y Athena. | Se define una *Customer Managed Key (CMK)* vía IaC para cifrado homogeneizado. |
| **Orquestación y Eventos** | **Amazon EventBridge** | Planificador serverless (*Cron job*) que dispara la Lambda cada 5 minutos. | Se define una `Rule` y un `Target` (la Lambda) en el código IaC. |
| **Monitoreo y Logs** | **Amazon CloudWatch** | Centraliza métricas (latencia, fallos) y logs de DMS, Firehose, Lambda y Athena. | IaC configura `LogGroups` y `Alarms` (p.ej., alerta si DMS tiene alto lag). |
| **Visualización** | **Amazon QuickSight** | Herramienta de BI para consumo de la Capa Marts. | Se paga por autor/usuario sesión. La conexión a Athena se puede configurar vía IaC (CDK). |

### 2. Ingesta (CDC)

### 2.1. Metodología de Ingesta

**Fuentes de datos - PostgreSQL**
Se utiliza AWS DMS configurado con una tarea de tipo CDC (Change Data Capture) combinada con el parámetro BufferInSeconds=60 y BufferSize=5.
*   **Fase Initial:** Copia masiva inicial de datos históricos.
*   **Fase CDC:** Escucha continua del WAL (wal_level = logical) de PostgreSQL para capturar mutaciones en tiempo real.

**Fuentes de Terceros - APIS**
Para integrar las APIs externas sin incurrir en costes de servidores 24/7, se configura una integración nativa en API Gateway. Las peticiones HTTP POST entrantes en el webhook se validan y se envían a Kinesis Firehose usando plantillas de mapeo VTL, sin usar Lambda intermedia para reducir latencia y coste.

### 2.2. Capa Raw (Bronce) - Ingesta Multifuente Inmutable
Almacena una copia exacta, cruda, inmutable y *append-only* de todos los orígenes de datos sin transformaciones. Aísla el impacto en los sistemas de origen y permite la reejecución completa de pipelines analíticos en caso de fallo.

* **Formato de archivo:** **JSON** (para eventos de base de datos y APIs).
* **Almacenamiento Físico:** Ficheros de texto plano organizados por ráfagas de tiempo generados por Firehose.

> ⚠️ **Decisión crítica de diseño (Evitando el "Small Files Problem"):** Se descarta almacenar en Parquet directo desde DMS o Firehose en esta capa. Como el CDC e inyectan eventos continuamente, escribir Parquet directamente generaría miles de archivos de pocos Kilobytes (debido a su estructura interna de bloques). Esto degradaría el rendimiento de Athena. JSON tolera cambios dinámicos de esquemas y permite que Firehose realice un *buffering* óptimo (5MB / 60s).

### 🚫 Descarte de Apache Kafka / AWS MSK
Se evaluó y descartó la inclusión de Apache Kafka en favor de **Kinesis Firehose + Athena** debido a tres factores críticos:
* **Eficiencia en Costes (Filosofía Serverless):** Kafka requiere clústeres aprovisionados con coste fijo 24/7. La arquitectura actual es 100% serverless: si no hay tráfico, el coste es casi cero.
* **Carga de Mantenimiento:** Delegar la administración de la ingesta en Kinesis Firehose elimina la carga operativa de gestionar brokers, particiones y zookeeper.
* **Alineación con el Caso de Uso (Data Lake Analítico):** Kafka brilla en reactividad en milisegundos. Para un Data Lake de BI, una latencia de consolidación de 5 minutos (*near real-time*) es óptima. Introducir Kafka habría supuesto una sobreingeniería injustificada.

**Organización del particionado estilo Hive en S3 (`capa raw`):**
```text
raw/
├── postgres/              # Fuente Transaccional Estructurada (via AWS DMS CDC)
│   ├── lead/
│   ├── llamada/
│   └── usuario/
│       └── year=2026/month=07/day=18/hour=19/
│           └── dms-cdc-file-102.json
├── api_externa_1/         # Fuente Semiestructurada en Streaming (via API Gateway)
│   └── eventos/
│       └── year=2026/month=07/day=18/hour=19/
│           └── firehose-api-stream-1-2026-07-18...json
└── api_externa_1/       # Extensibilidad: Nueva fuente batch aislada de forma nativa
    └── eventos/
        └── year=2026/month=07/day=19/hour=09/
            └── batch-ingest-01.json
```

### 2.3. Capa Clean (Silver) - Consolidación ACID
Mantiene una única versión consistente, tipada, limpia y reconciliada de cada entidad de negocio, independientemente de su origen.

* **Formato de tabla:** **Apache Iceberg**.
* **Almacenamiento Físico:** Archivos columnares en **Parquet** comprimidos con **Snappy** (`.parquet.snappy`).

**Orquestación y Computo (¿Cómo funciona la Lambda?):**
Se descartan los AWS Glue Spark Jobs continuos por su alto coste fijo. Se utiliza un enfoque **ELT Serverless** optimizado:

1.  **Orquestación:** Amazon EventBridge despierta una función **Lambda (programada en Rust** para máximo rendimiento) cada 5 minutos.
2.  **Ejecución:** La Lambda no procesa los datos; simplemente invoca la API asíncrona de Amazon Athena para ejecutar comandos SQL `MERGE` e `INSERT`.
3.  **¿Cómo sabe qué carpeta consultar?**
    *   **Definición de Tabla:** Durante la fase IaC de DDL (`CREATE EXTERNAL TABLE`), se define explícitamente el parámetro `LOCATION` apuntando al prefijo de S3 Raw correspondiente. Athena consulta el Glue Catalog para saber dónde leer.
    *   **SQL MERGE:** El script SQL orquestado por la Lambda define el flujo: `MERGE INTO capa_clean.usuario TARGET USING capa_raw.usuario_updates SOURCE ...`. Athena traduce estos nombres de tabla a rutas físicas de S3 (Raw para leer, Clean para escribir via Iceberg) consultando el catálogo.

**Organización del particionado Iceberg en S3 (`capa-clean-bucket`):**
```text
clean/
├── usuario/                      # Entidad unificada (Postgres + APIs)
│   ├── metadata/                 # Archivos de control de transacciones ACID
│   └── data/                     # Ficheros físicos en Parquet Columnar + Snappy
│       └── year=2026/month=07/day=18/
│           ├── 4a8b2c1d-data.parquet.snappy
├── lead/
├── llamada/
```

### 2.4. Capa Marts (Gold) - Modelado Analítico
Contiene modelos de datos de alto rendimiento optimizados para consumo directo por herramientas de BI como **Amazon QuickSight**.

#### 🛠️ Especificaciones Técnicas
* **Formato de tabla:** **Apache Iceberg** (respaldado por archivos Parquet comprimidos con Snappy).
* **Enfoque de Diseño:** Modelado Dimensional en **Estrella / Copo de Nieve** para garantizar consultas SQL sencillas, intuitivas y ultra rápidas.

#### ⚙️ Orquestación y Estrategia de Cómputo
Al igual que en la capa Clean, se implementa un enfoque **ELT Serverless** para mantener el control estricto de costes:

* **Disparador:** La función **AWS Lambda** (orquestada por EventBridge cada 5 minutos junto al pipeline principal) gestiona la ejecución.
* **Procesamiento:** La Lambda invoca de manera asíncrona a **Amazon Athena** para ejecutar sentencias `INSERT INTO` masivas.
* **Transformación:** En esta etapa se realizan los *Joins* definitivos entre las tablas de la capa *Clean*, se aplica la lógica de negocio, el cálculo de métricas, la generación de claves subrogadas y las reglas de dimensionalidad (como SCD Tipo 2).

#### 📂 Estructura de Almacenamiento en S3 (`capa-marts-bucket`)
Los datos se organizan físicamente en subcarpetas separadas según su propósito dimensional para coincidir con el diagrama de arquitectura:

```text
marts/
├── dimensions/                 # Dimensiones: Tablas de contexto (Entidades)
│   ├── dim_persona/
│   │   ├── metadata/
│   │   └── data/
│   └── dim_usuario/
│       ├── metadata/
│       └── data/
└── facts/                      # Hechos: Tablas de métricas y eventos cuantitativos
    ├── facts_leads/
    ├── facts_llamadas/
    └── facts_cloud_events/     # Extensibilidad: Nuevas métricas de negocio
```

### 3. Multi-fuente
El Data Lake está diseñado unificando la ingesta de bases de datos relacionales y webhooks de terceros.

**Si mañana llega una nueva fuente distinta (p. ej. eventos de proveedor cloud o ficheros batch), ¿cómo la integrarías?**
Gracias al desacoplamiento de componentes y formatos abiertos, la inclusión se resuelve de manera nativa en 3 pasos:

1.  **Capa Raw (Bronce): Ingesta:**
    *   **Si son ficheros en S3 (Batch):** Se configura réplica de bucket o regla de eventos S3 -> Lambda -> Nuevo prefijo (ej: `raw/api_externa_1/`).
    *   **Si son eventos Cloud (Streaming):** Se expone nuevo endpoint en **API Gateway** existente. Usando VTL, se redirige a un nuevo stream de **Firehose**.
2.  **Capa Clean (Silver): Unificación:**
    Se crea la definición de tabla en el **Glue Catalog** apuntando al nuevo prefijo Raw. Se extiende la lógica de la función Lambda orquestadora (programada en Rust) para incluir la nueva transformación SQL en Athena que popula una tabla Iceberg Silver.
3.  **Capa Marts (Gold): Modelado:**
    Al ser todas tablas Iceberg consultables desde Athena, Herramientas de BI como **QuickSight** pueden cruzar los datos de ambas fuentes de manera transparente a través de relaciones `JOIN` en consultas SQL, abstrayendo la complejidad al usuario final.

### 4. Gobierno y confianza

#### 🔍 1. Descuadres de Cifras: Causas Potenciales
Si las métricas del Data Lake no coinciden con producción, el origen suele ser:
* **Latencia de Consolidación:** CDC es inmediato a Raw, pero Silver se actualiza cada 5 minutos.
* **Duplicidad de Eventos:** Kinesis Firehose garantiza entrega *At-Least-Once*. Ante reintentos de red, puede duplicar registros en Raw. La lógica `MERGE` en Silver debe deduplicar usando marcas de tiempo (`metadata.timestamp`).
* **Borrados Físicos:** Si la aplicación hace `DELETE` físico y la tarea DMS o el SQL `MERGE` en Athena ignora ese evento, el Data Lake mantendrá registros "fantasma".

#### 🧪 2. Estrategia de Reconciliación Automática
![Reconciliation strategy](documentation/reconciliation-strategy.png)


#### 📜 3. Trazabilidad Histórica
Para responder a auditorías (ej: "¿En qué estado estaba este Lead el 1 de marzo?") hay dos opciones:
1.  **SCD Tipo 2 (Modelado Dimensional):** Transformaciones SQL gestionan columnas de validez temporal (`fecha_inicio`, `fecha_fin`, `is_active`) en Marts.
2.  **Iceberg Time Travel (Nativo en Silver):** Apache Iceberg conserva snapshots. Es posible interrogar al Data Lake usando SQL nativo en Athena especificando un momento del pasado:

```sql
-- Ejemplo de consulta el estado de una tabla y como estaba el 1 de Marzo
SELECT * 
FROM capa_clean.usuario 
FOR SYSTEM_TIME AS OF TIMESTAMP '2026-03-01 00:00:00 UTC';
```