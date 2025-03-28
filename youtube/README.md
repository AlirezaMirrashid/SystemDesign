# YouTube‑Like Application

This is a sample project demonstrating a modular YouTube‑like application with microservices built in Python using Flask. The project is split into:

- **API Gateway:** Routes requests to the appropriate service.
- **Video Upload Service:** Handles chunked video uploads and assembles them.
- **Video Streaming Service:** Streams video content.
- **Comments Service:** Allows users to post comments.
- **Metadata Service:** Stores video metadata (title, description, etc.).
- **Client:** A simple HTML/JS frontend that chunks video files and simulates an upload.

## Running the Project

1. **Start each microservice (in separate terminals):**

   ```bash
   # API Gateway
   cd api_gateway
   python app.py

   # Video Upload Service
   cd ../services/video_upload
   python app.py

   # Video Streaming Service
   cd ../video_stream
   python app.py

   # Comments Service
   cd ../comments
   python app.py

   # Metadata Service
   cd ../metadata
   python app.py
