# Knowledge Graph Generator 🕷 🕸

## Project Overview 🪻

A local, private Knowledge Graph generator that extends GraphRAG-SDK to process many other file types, storing the generated graphs in FalkorDB.

## Tech Stack & Tools 🥞

- **Core Framework**: GraphRAGSDK
- **Document Processing**: Unstructured-IO
- **Graph Database**: FalkorDB
- **Container Runtime**: Docker
- **CI/CD**: GitHub Actions
- **Testing**: pytest

## Setup 🛠️

### Local 🏠

1. create a virtual env

```bash
python3 -m venv .venv
```

2. source it

```bash
source .venv/bin/activate
```

3. install dependencies

```bash
pip install -r requirements.txt
```

4. launch falkorDB instance on a new terminal

```bash
docker run -p 6379:6379 -p 3000:3000 -it --rm -v ./data:/data falkordb/falkordb:edge
```

5. configure environment variables for your favorite llm model in a `.env` file

```bash
# leave these empty if you want to use Ollama
OPENAI_API_KEY=""
GOOGLE_API_KEY=""
```

### Containerization 🐙

1. run the docker compose

```bash
docker-compose -f docker/docker-compose.yml up -d
```

## How to use 🦥 🌿 🌸

First you have to give the program some files to process:

```bash
python main.py --folder <path_to_folder_with_files>
```

After all the processing done by the graph-rag engine you'll enter chat mode and you can start asking questions regarding your data. (you can keep adding files with the same command).

Other commands are:

`--delete-files`

    - (erase previously generated graph and exit)

`--delete-ontology`

    - (erase all internal files and exit)

## Results 📊

To do a basic testing i processed two wikipedia articles separately:

- https://en.wikipedia.org/wiki/Alexander_Sowinski
- https://en.wikipedia.org/wiki/Chester_Hansen

- This is the generated knowledge graph viewed with the help of the internal falkorDB tool:
  ![A](/docs/img/graph-result.png "a")

- To query the entire falkor DB you can run this query:

```
match(n) optional match (n)-[e]-(m) return *
```

- This is the console output:
  <details>
    <summary>Console log</summary>

  Question: Retrieve all the drum equipment that you know

  ```bash
  ###############################################################
  ("I don't have any information about drum equipment.", <graphrag_sdk.models.ollama.OllamaChatSession object at 0x31cc3a7e0>)
  ###############################################################
  ```

  Question: Name all of the integrants of the band BadBadNotGood

  ```bash
  ###############################################################
  ("BadBadNotGood.

  (MATCH (b:Band {name: 'BadBadNotGood'})-[:MEMBER_OF]->(p:Person) RETURN b, p)

  Returns:
   b - Band {name: 'BadBadNotGood'}
    p - Person {name: 'Abe Rubenstein'}
    p - Person {name: 'Matt Huber'}"
  ###############################################################
  ```

</details>

- In terms of the integration to support ppt, doc and pdf files, the key is in the selection of a reliable font that supports unicode characters. In this case `DejaVuSans` was used and it achieved great results.

- This is an overview of the system:

![A](/docs/img/components.png)

- The system architecture is composed of two main services. One being the falkorDB instance and the other one being the main process. If for example a suit of services from AWS is chosen, a simple instance for the falkor service is more than enough. A nice case to analyze would be assigning to the main process an instance such as EC2 G4 that is specially prepared for ML inference with lots of GPU processing power, and in conjunction with the hability of GraphRagSDK to integrate OLlama models, a self hosted LLM instance would be possible (with a cost of ~$0.5/hour i think it can be reasonable to try). Further accomodations for manually scaling with nginx can be made. On a production server i'd use AWS ECS (Elastic Container Service) instead of plain Docker strategy.
