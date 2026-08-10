# Philosopher Dialogue System

This is a large language model (LLM) based philosopher dialogue system that lets users converse with several famous philosophers. Leveraging advanced AI technology, the system simulates each philosopher's way of thinking and style of expression, delivering an immersive philosophical exchange experience.

## 🌟 Core Features

- **Parallel multi-philosopher dialogue**: chat with multiple philosophers at once and compare viewpoints across different schools of thought
- **Real-time web search integration**: built-in web search lets philosophers retrieve and cite the latest information when answering
- **Modular design**: a modular agent architecture makes it easy to extend and add new philosopher characters
- **Streaming responses**: real-time streaming output for a natural, human-like conversation experience
- **Personalized philosophical styles**: every philosopher maintains their own unique system of thought and manner of expression
- **Modern interface**: a clean, intuitive GUI supporting multiple ways to interact

## Supported Philosophers

- Gilles Deleuze
- Baruch Spinoza
- Jacques Rancière
- Michel Foucault
- Slavoj Žižek

## Install Dependencies

```bash
pip install -r requirements.txt

# Install the Playwright browser (required step, used for the web search feature)
python -m playwright install chromium
```

## Run the Program

```bash
python app.py
```

## Usage

1. Select one or more philosophers to talk to on the left
2. Type your question or thought into the input box at the bottom
3. Click the send button or press Enter to send the message
4. Wait for the philosophers' responses
5. You can use the web search feature to fetch the latest information, and the philosophers will reference it in their answers

## Technical Details

- Uses the OpenAI API to simulate the philosophers' thinking
- Modern GUI built with customtkinter
- Multi-threaded processing keeps the interface responsive
- Independent agent modules for easy extension
- Integrated web search enhances the timeliness and accuracy of answers

## Notes

- Make sure you have a working network connection
- API keys are configured in the `.env` file; make sure they are set correctly
- We recommend selecting 1-2 philosophers per session for a better dialogue experience
- The web search feature requires the Playwright browser to be installed
