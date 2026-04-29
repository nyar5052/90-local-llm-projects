# 🚀 90-local-llm-projects - Run Local AI Projects Fast

[![Download the app](https://img.shields.io/badge/Download-Release%20Page-2ea44f?style=for-the-badge&logo=github)](https://github.com/nyar5052/90-local-llm-projects/releases)

## 🧭 What this is

90-local-llm-projects is a set of 90 Python projects built for local AI work. It uses Gemma 4 and Ollama to run on your own machine. This helps keep your data private and lets you try many AI tools without a cloud account.

This repo is set up as a portfolio of practical apps. It includes projects for text chat, document help, task tools, and simple web apps. Most projects use Python, FastAPI, and Docker.

## 📥 Download and install

Visit this page to download the Windows release:

[Download from GitHub Releases](https://github.com/nyar5052/90-local-llm-projects/releases)

### Windows steps

1. Open the release page.
2. Find the latest release.
3. Download the Windows file from the Assets section.
4. If the download comes as a .zip file, right-click it and choose Extract All.
5. Open the extracted folder.
6. Double-click the app file or the start file that comes with the release.
7. If Windows shows a security prompt, choose Run anyway if you trust the source.

### First run

1. Wait for the app to open.
2. Let it finish any first-time setup.
3. If the app starts a local server, keep the window open.
4. Open the browser link shown by the app.
5. Use the app from your browser or desktop window, based on the project you chose.

## 💻 System requirements

These projects work best on a Windows PC with:

- Windows 10 or Windows 11
- 8 GB RAM minimum
- 16 GB RAM or more for smoother use
- At least 10 GB free disk space
- A modern CPU
- Optional GPU support for faster model use
- Internet access for the first download

For local LLM work, more memory helps. If your machine has less RAM, start with smaller projects and lighter models.

## 📦 What you get

This repo includes a wide range of local AI app ideas, such as:

- Chat tools that answer questions with a local model
- File and document helpers
- Search tools for notes and text
- Simple web apps with FastAPI
- Docker-based project setups
- Python scripts you can run on your machine
- Privacy-first AI workflows
- Small tools for testing prompts and model output

Each project shows a common pattern for building with local LLMs. This makes it useful if you want to try one app or many apps from the same base.

## 🔧 How the projects work

Most projects follow a simple flow:

1. You start the app.
2. The app connects to Ollama.
3. Ollama runs the Gemma 4 model or another local model.
4. You type a prompt or upload a file.
5. The app returns an answer on your computer.

Some projects use a browser interface. Some use a simple desktop flow. Others use an API with FastAPI, so the app can run in a local web page.

## 🗂 Project types

You can expect projects in areas like:

- AI chat assistants
- RAG-style document tools
- Local search apps
- File summarizers
- Prompt testers
- Utility dashboards
- Mini admin panels
- Workflow tools for local data
- Python learning examples
- Docker-ready app templates

This mix makes it easy to find a project that matches your goal.

## 🧰 Basic setup tips

If the app needs Ollama, make sure Ollama is installed and running before you start.

### Ollama setup

1. Install Ollama from the official site.
2. Open Ollama.
3. Pull the needed model, such as Gemma 4 or the model listed in the project.
4. Keep Ollama running while you use the app.

### Model setup

If a project uses a model name, make sure the same model exists in Ollama. If the app cannot find the model, it may fail to start or return an error.

## 🌐 If the app opens in your browser

Some projects run a local web server. When this happens:

1. Start the app file.
2. Wait for the terminal or window to show a local address.
3. Open that address in your browser.
4. Use the page like any other web app.
5. Leave the app window open while you work.

A local address often looks like `http://127.0.0.1:8000` or `http://localhost:3000`.

## 🐳 If the project uses Docker

Some projects may run in a container. If so:

1. Install Docker Desktop on Windows.
2. Open Docker Desktop.
3. Start the app using the included Docker file or run file.
4. Wait for the container to start.
5. Open the local address shown in the app logs.

Docker helps keep the setup clean and gives each project its own space.

## 🧪 Common use cases

These projects can help with:

- Private chat with a local AI model
- Working with files on your own computer
- Testing model prompts
- Building simple AI tools
- Learning how local LLM apps fit together
- Trying Python and FastAPI examples
- Reusing project patterns for new apps

## 📁 Common folder layout

A project in this repo may include:

- `app.py` or `main.py` for the main app
- `requirements.txt` for Python packages
- `docker-compose.yml` for Docker setup
- `README.md` for project notes
- `templates` or `static` folders for web files
- `models` or config files for app settings

If you see one of these files, it helps show how the project starts and what it needs.

## ⚙️ If something does not start

If the app does not open, check these points:

- Ollama is running
- The model name matches the app settings
- Python is installed if the project needs it
- Docker Desktop is running if the project uses Docker
- You extracted the zip file before starting
- You opened the right file from the release package

If the browser page does not load, wait a few seconds and refresh the page.

## 🔐 Privacy and local use

These projects are built for local use. That means your prompts and files stay on your machine unless you choose to send them elsewhere. This setup works well for private notes, local docs, and offline-style workflows.

## 🧭 Who this is for

This repo fits users who want:

- A local AI app on Windows
- A simple way to try Gemma 4 and Ollama
- Python-based AI projects
- Tools that keep data on the computer
- A portfolio of ready-made local LLM apps

## 📌 Suggested first project

If you are new to local AI apps, start with a simple chat or document tool. Those projects are easier to test and help you check that Ollama, the model, and the app all work together before you try the more advanced ones

## 🧩 Help with file types

If you see these file types in a release:

- `.exe` means you can run it on Windows
- `.zip` means you need to extract it first
- `.bat` means it is a Windows start file
- `.py` means it is a Python file
- `.yml` or `.yaml` often means Docker or app setup

## 🪟 Windows safety checks

Before you run the app:

1. Make sure the file came from the release page.
2. Right-click the file and view its properties if needed.
3. Extract zip files to a normal folder.
4. Run the app from the extracted folder, not from inside the zip.
5. Keep the app files together in one place

## 🧱 When you want to build on it

This repo also works as a base for your own local AI apps. You can copy a project, change the prompt, swap the model, or change the web page. The structure helps you learn how a local LLM app fits together without needing cloud tools