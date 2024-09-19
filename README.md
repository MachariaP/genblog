# genblog
# GenBlog

GenBlog is a dynamic blogging platform where users can share their thoughts, connect through messaging, and follow each other to stay updated on new posts. Built using Flask for the backend and Bootstrap for the frontend, with custom CSS for styling, GenBlog offers an interactive and user-friendly blogging experience.

## Features

- **User Registration and Authentication**: Users can create accounts, log in, and manage their profiles.
- **Blog Posting**: Users can write and publish blog posts to share their thoughts and ideas.
- **Messaging System**: Users can send messages to each other directly within the platform.
- **Follow Feature**: Users can follow other bloggers and receive updates on their new posts.
- **Responsive Design**: The application is designed using Bootstrap, ensuring it works well on both desktop and mobile devices.

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Bootstrap, HTML5
- **Styling**: Custom CSS
- **Database**: SQLite (can be switched to any other database like MySQL, PostgreSQL)
- **Authentication**: Flask-Login

## Installation

### Prerequisites
- Python 3.6+
- pip (Python package manager)

### Steps

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/genblog.git
    cd genblog
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Linux/macOS:
      ```bash
      source venv/bin/activate
      ```
    - On Windows:
      ```bash
      venv\Scripts\activate
      ```

4. **Install the dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Run the application**:
    ```bash
    flask run
    ```

6. Open your browser and go to `http://127.0.0.1:5000` to view the app.

## Project Structure


