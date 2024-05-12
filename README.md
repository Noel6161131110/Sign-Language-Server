# Sign Language Detector Server

This repository contains the code for a Sign Language Detector Server built using Django and WebSocket Channels. The server receives frames from the frontend in real-time, processes them, and detects signs, whether they are individual letters or complete words.

## Features

- Real-time sign language detection using WebSocket Channels.
- Support for detecting both individual letters and complete words.
- Built-in Django admin interface for managing users, sessions, and other backend data.
- Scalable architecture for handling multiple clients simultaneously.

## Installation

1. Clone the repository to your local machine:

```

git clone https://github.com/your-username/sign-language-detector-server.git

```

2. Install the required dependencies using pip:

```

pip install -r requirements.txt

```

3. Migrate the database:

```

python manage.py migrate

```

4. Run the Django development server:

```

python manage.py runserver

```

5. Run the Docker container in production using :

```

docker-compose -f docker-compose.yml up -d --build

```

## Usage

1. Access the server's WebSocket endpoint from your frontend application.
2. Send frames from the frontend to the WebSocket endpoint.
3. The server will process the frames and detect signs, returning the detected signs back to the frontend in real-time.

## Configuration

- You can configure the server settings, such as the WebSocket endpoint URL and other parameters, in the `settings.py` file.
- Make sure to set appropriate permissions and security measures, especially if deploying the server in a production environment.

## Contributing

Contributions are welcome! If you'd like to contribute to this project, please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature/your-feature`).
6. Create a new Pull Request.

