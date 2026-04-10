# Test Sheet Generator
A project to store test questions and generate test sheet contents, deployed in Linux environment.

## Docker Setup
### Installation
```bash
# Update and install dependencies
sudo apt update
sudo apt install -y ca-certificates curl gnupg

# Add Docker’s official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow your user to run docker without sudo
sudo usermod -aG docker $USER
```

### docker-compose.yaml
```yaml
services:
  postgres:
    image: postgres:16
    container_name: ${DB_CONTAINER}
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASS}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "${DB_PORT}:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

volumes:
  pg_data:
```

### Build
```bash
docker compose up -d
```

## Python Setup
### Installation
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

### Virtual Environment and Pip Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate

pip install "psycopg[binary]" python-dotenv pandas
```