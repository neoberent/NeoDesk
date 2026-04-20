# NeoDesk

A secure, role-based desktop workspace built with Python and CustomTkinter, featuring an AI chat assistant, encrypted note management, and user administration.

---

## About

NeoDesk started as a personal project to explore how a self-contained desktop application could bring together authentication, AI, and data management in one clean interface. Everything runs locally, no cloud, no external accounts required beyond an API key for the AI chat.

The codebase is structured around distinct modules (Auth, Chat, Notes, Dashboard) that communicate through a shared design system and data layer, making it straightforward to extend or swap out individual parts.

## Features

- Login and registration with bcrypt password hashing
- Role-based access control, Admin and User roles with enforced permissions
- AI chat powered by an external API client, with persistent conversation history
- Note manager with search, autosave indicator, and word count
- Admin panel for user management (add, remove, change roles)
- Dark theme throughout, built on CustomTkinter

## Tech Stack

- Python 3.13
- CustomTkinter
- bcrypt
- SQLite (chat history)
- JSON-based user and notes storage

## Getting Started

1. Clone the repository
2. Install dependencies

```
pip install -r requirements.txt
```

3. Add your API key to the `.env` file
4. Run the application

```
python main.py
```

The default admin account is created automatically on first launch with the username `admin` and password `admin`. Change this immediately.

## Project Structure

```
Auth/               Login, registration, user management
Chatpage_Gui/       AI chat window, design system, database
Dashboard/          Dashboard, admin panel
NoteManager_Gui/    Note editor and storage
data/               Local database and JSON files
```

## License

MIT License. See LICENSE for details.
