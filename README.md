# WhistleDrop
## Created by Hackintosh 102x
A secure whistleblower system that enables encrypted communication between whistleblowers and journalists through the Tor network with end-to-end encryption using asymmetric RSA encryption.

## System Requirements

- Docker and Docker Compose
- Python 3.9+
- Tor Browser (for easy access to .onion addresses)

## Installation and Setup

### Configure Environment Variables

1. Create a `.env` file in the main directory with the following values:

```
DATABASE_URL_NORMAL=postgresql://normal_db_user:normal_password@db:5432/whistledrop_db
DATABASE_URL_ADMIN=postgresql://admin:admin_password@db:5432/whistledrop_db

POSTGRES_USER=normal_db_user
POSTGRES_PASSWORD=normal_password
POSTGRES_ADMIN_USER=admin
POSTGRES_ADMIN_PASSWORD=admin_password
POSTGRES_DB=whistledrop_db

AUTH_SECRET=your_secure_jwt_secret_here
```

2. Generate a secure AUTH_SECRET with the journalist interface:

```bash
cd journalist_area
python whistle_interface.py config --gensecret
```

### Initialize Database

1. Start only the database first:

```bash
docker-compose run db
```

2. Initialize DB and create admin account in a new terminal:

```bash
docker-compose run backend python main.py --init
docker-compose run backend python main.py --createadmin your_secure_passphrase
```

be catious with the --init command, it will reinitialise your database, so only run it if you are sure.

### Start the Application

Start all containers:

```bash
docker-compose up -d
```

### Configure Tor Hidden Service

After startup, a Tor Hidden Service is automatically created. 
To find and configure the onion address:

1. Navigate to the journalist area:

```bash
cd journalist_area
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the onion address:

Get your onion address from the Tor hidden service configuration:

```bash
cat ../tor-data/hidden_service/hostname
```

Configure the journalist interface with the onion address:


```bash
python whistle_interface.py config --onion your_onion_address.onion
```

## Using the System

### For Journalists

#### Upload RSA Keys:

```bash
python whistle_interface.py upload --count 10
```

You'll be prompted for the passphrase you set during admin creation.

#### Download and Decrypt Documents:

```bash
python whistle_interface.py download
```

Files will be downloaded and automatically decrypted.

#### Clean Up All Local Data:

```bash
python whistle_interface.py cleanup
```
This will remove all local data, including the database, so be cautious.
### For Whistleblowers

Whistleblowers can access the onion address through the Tor Browser and upload encrypted files without revealing their identity.

## Security Notes

- The Auth Secret should never be shared publicly
- All passwords in the .env file should be strong and unique
- The tor-data folder contains sensitive data and should be protected
- The journalist interface should be operated on a secure machine

## Troubleshooting

- **NGINX not accessible via localhost**: Ensure ports are correctly mapped in the Docker Compose file
- **Large file uploads fail**: Adjust NGINX configuration with `client_max_body_size`
- **Tor connection problems**: Check proxy settings in the journalist interface configuration

And now, let 's get started with secure whistleblowing!
```
