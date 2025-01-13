# RAG Voice Assistant Project

This project implements a Retrieval-Augmented Generation (RAG) Voice Assistant composed of three main services. Each service plays a distinct role in the overall functionality of the assistant. Below, you will find a brief overview of these services, followed by detailed setup and usage instructions.

![Screenshot of the frontend application.](/.github/assets/rag.png)

## Overview of Services

1. **Livekit Service (Agent)**:
   - A Python-based WebRTC agent that connects to the Livekit cloud.
   - Handles real-time voice communication and retrieves document-related embeddings from Pinecone to answer user questions.
   - Integrates Speech-to-Text (STT), Text-to-Speech (TTS), and Language Learning Models (LLM).

2. **FastAPI Service (Embeddings API)**:
   - A backend server that processes uploaded files, converts text to embeddings using OpenAI, and stores them in Pinecone.
   - Summarizes the document for use in the voice assistant's system prompt.
   - Stores namespaces of embeddings in a database for easy document retrieval.

3. **Next.js Frontend**:
   - A web interface based on the LiveKit Next.js template, enhanced with ShadCN components.
   - Allows users to upload files, select a document namespace, and interact with the assistant in real-time.

## Documentation and Resources
- **Livekit**:
  - Documentation: [Livekit Docs](https://docs.livekit.io/home/)
  - To set up a project and get environment variables: [Livekit Cloud](https://cloud.livekit.io/)
- **Deepgram**:
  - For Speech-to-Text (STT) and Text-to-Speech (TTS): [Deepgram](https://deepgram.com/)
- **Pinecone**:
  - For vector database management: [Pinecone](https://www.pinecone.io/)

---

## Livekit Service - (Agent)

### Overview
The Livekit Service serves as the WebRTC agent connected to the Livekit cloud. This service is implemented in Python and is responsible for facilitating voice interactions and retrieving embeddings to answer user questions about uploaded documents. 

### Requirements
The service dependencies can be installed using either `poetry` or `requirements.txt`.

#### Using Poetry
1. Install Poetry if not already installed:
   ```bash
   pip install poetry
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

#### Using `requirements.txt`
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables
The `.env` file must be configured with the following variables:
- **LIVEKIT_URL**: The URL of the Livekit server.
- **LIVEKIT_API_KEY**: The API key for authenticating with Livekit.
- **LIVEKIT_API_SECRET**: The secret key for authenticating with Livekit.
- **DEEPGRAM_API_KEY**: The API key for Deepgram (if used as the STT/TTS provider).
- **CARTESIA_API_KEY**: The API key for Cartesia (if used as the TTS provider).
- **ELEVENLABS_API_KEY**: The API key for ElevenLabs (if used as the TTS provider).
- **OPENAI_API_KEY**: The API key for OpenAI (used to process embeddings and generate responses).
- **PINECONE_API_KEY**: The API key for Pinecone.
- **PINECONE_INDEX_NAME**: The name of the Pinecone index used to store embeddings.

### Running the Service
To start the Livekit Service, run the following command:
```bash
python main.py dev
```

## FastAPI Service - (Embeddings API)

### Overview
The Embeddings API is a FastAPI server that processes uploaded files, generates embeddings using OpenAI, and stores them in Pinecone. It also generates a document summary for use in the assistant's system prompt.

### Features
- Accepts file uploads in PDF, DOCX, and HTML formats.
- Converts text to embeddings using OpenAI and stores them in Pinecone.
- Generates a unique namespace for each file and stores namespace references in a PostgreSQL database.
- Summarizes the document's first chunk for context.

### Requirements
The service requires a PostgreSQL database to store namespaces and document metadata. A `docker-compose.yml` file is provided to set up the database.

#### Using Poetry
1. Install Poetry if not already installed:
   ```bash
   pip install poetry
   ```
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

#### Using `requirements.txt`
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Variables
The `.env` file for this service must include the following variables:
- **OPENAI_API_KEY**: The API key for OpenAI (used to generate embeddings and summaries).
- **PINECONE_API_KEY**: The API key for Pinecone.
- **PINECONE_INDEX_NAME**: The name of the Pinecone index used to store embeddings.
- **POSTGRES_USER**: The username for the PostgreSQL database.
- **POSTGRES_PASSWORD**: The password for the PostgreSQL database.
- **POSTGRES_DB**: The name of the PostgreSQL database.
- **POSTGRES_HOST**: The host where the PostgreSQL database is running.
- **POSTGRES_PORT**: The port for connecting to the PostgreSQL database.

### Running the Service
1. Set up the PostgreSQL database using Docker Compose:
   ```bash
   docker-compose up -d
   ```

2. Start the FastAPI server:
   ```bash
   python main.py
   ```

### Endpoints
The Embeddings API provides the following endpoints:
- **POST /textfiles**: Upload a file and process its embeddings.
- **GET /textfiles**: List all uploaded files and their namespaces.

d
## Next.js Frontend

### Overview
The Next.js frontend is based on the LiveKit Next.js base template, enhanced with ShadCN components. It serves as the user interface for interacting with the Voice Assistant and Embeddings API.

### Requirements
The frontend uses `pnpm` for package management. Ensure `pnpm` is installed before proceeding.

### Environment Variables
The `.env` file for the frontend must include the following variables:
- **LIVEKIT_URL**: The WebSocket URL for connecting to the Livekit server.
- **LIVEKIT_API_KEY**: The API key for Livekit authentication.
- **LIVEKIT_API_SECRET**: The secret key for Livekit authentication.
- **API_URL**: The base URL for the Embeddings API.

### Running the Service
1. Install dependencies:
   ```bash
   pnpm install
   ```

2. Start the development server:
   ```bash
   pnpm dev
   ```

3. Open your browser and navigate to `http://localhost:3000` to view the application.
