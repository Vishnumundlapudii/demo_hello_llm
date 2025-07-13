# E2E Networks LLM Chatbot

A simple and elegant chatbot application built with Streamlit and LangChain, designed to work with E2E Networks hosted LLM endpoints.

## Features

- 🤖 **Interactive Chat Interface**: Clean, user-friendly Streamlit interface
- 🔧 **Configurable Parameters**: Adjust temperature, max tokens, and other model parameters
- 📊 **Chat Statistics**: Track conversation metrics in real-time
- 🔒 **Secure Configuration**: Environment-based API key management
- ⚡ **Real-time Responses**: Fast communication with E2E Networks LLM endpoints
- 📝 **Chat History**: Persistent conversation history with timestamps
- 🛡️ **Error Handling**: Robust error handling and user feedback

## Prerequisites

- Python 3.8 or higher
- E2E Networks LLM endpoint URL and API key
- Git (for cloning the repository)

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd hello_llm
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit the `.env` file with your E2E Networks credentials:
```bash
# Edit .env file
E2E_ENDPOINT_URL=https://your-llm-endpoint.e2enetworks.com/api/v1/chat/completions
E2E_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Deployment on Server

### Option 1: Direct Deployment

1. **Clone on server:**
```bash
git clone <your-repository-url>
cd hello_llm
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.template .env
# Edit .env with your credentials
```

4. **Run with custom port:**
```bash
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### Option 2: Using Docker (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```bash
docker build -t e2e-chatbot .
docker run -p 8501:8501 --env-file .env e2e-chatbot
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `E2E_ENDPOINT_URL` | Your E2E Networks LLM endpoint URL | Yes |
| `E2E_API_KEY` | API key for authentication | Yes |
| `E2E_MODEL_NAME` | Model name (if endpoint supports multiple) | No |
| `DEFAULT_TEMPERATURE` | Default temperature setting | No |
| `DEFAULT_MAX_TOKENS` | Default max tokens setting | No |

### Runtime Configuration

You can also configure the chatbot through the Streamlit sidebar:
- **Endpoint URL**: Change the LLM endpoint
- **API Key**: Update authentication credentials
- **Temperature**: Control response creativity (0.0 = deterministic, 2.0 = very creative)
- **Max Tokens**: Limit response length

## Project Structure

```
hello_llm/
├── app.py              # Main Streamlit application
├── llm_wrapper.py      # LangChain wrapper for E2E Networks LLM
├── requirements.txt    # Python dependencies
├── .env.template      # Environment variables template
├── .env              # Your actual environment variables (create from template)
└── README.md         # This file
```

## API Integration

The application uses a custom LangChain wrapper (`E2ENetworksLLM`) that:
- Handles HTTP requests to your E2E Networks endpoint
- Manages authentication and headers
- Provides error handling and retry logic
- Supports various response formats
- Integrates seamlessly with LangChain ecosystem

### Supported Response Formats

The wrapper automatically handles different API response formats:
- OpenAI-style responses (`choices[0].message.content`)
- Direct text responses (`response`, `text`, `generated_text`)
- Custom response structures

## Usage Tips

1. **API Key Security**: Never commit your `.env` file to version control
2. **Performance**: Adjust `max_tokens` based on your needs to optimize response time
3. **Error Handling**: Check the sidebar for connection status and error messages
4. **Chat History**: Use "Clear Chat History" to start fresh conversations

## Troubleshooting

### Common Issues

1. **Connection Error**: Verify your endpoint URL and API key
2. **Timeout Error**: Check network connectivity or increase timeout in code
3. **Authentication Error**: Ensure your API key is valid and active
4. **Import Errors**: Make sure all dependencies are installed correctly

### Debug Mode

To enable debug logging, modify `llm_wrapper.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Support

For issues related to:
- **E2E Networks**: Contact E2E Networks support
- **This Application**: Create an issue in this repository
- **LangChain**: Check LangChain documentation

---

**Happy Chatting! 🤖**