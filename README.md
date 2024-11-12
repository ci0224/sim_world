# AI Character - World Simulation

## Cabability Now

Generate events of a day for each character and affect the characters' relationship with one another, status, abilities, and personalities.

## Note for Next Step

### Oct 22, 2024

Need to decide a theme and a show case for it, could be combination of...

1. Real time interactions through threads/twitter as show cases.
   1. Need to grab audience to interact with. Need to think about marketing explosure and sunk cost.
   2. Real time interactions will increase the complexity of the program, and potential cost depending on how users bully this toy.
   3. Could be a bit of boring because why would audience interact with AI not real human?
2. Research topic, for example, social relationship or economics, with Pixel games as show case.
   1. I personally don't like this idea.
3. Making it a game like westworld.
   1. Need a topic and a messive background, each character has a very colorful and rich background story.
4. ...

## Dev Setup

1. Install nginx

   ```shell
   brew install nginx
   ```

2. get certificate `openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ~/ssl/local.key -out ~/ssl/local.crt`
   1. You’ll be prompted to enter information like country and organization. For local testing, defaults are fine.
   2. Set Common Name (CN) as localhost.
3. add these two servers to nginx config file `vim /opt/homebrew/etc/nginx/nginx.conf`

   ```conf
   # Redirect HTTP to HTTPS
   server {
      listen 80;
      server_name localhost;
      return 301 https://$host$request_uri;
   }

   # HTTPS server for WebSocket with SSL
   server {
      listen 443 ssl;
      server_name localhost;

      ssl_certificate /path/to/your/ssl/local.crt;
      ssl_certificate_key /path/to/your/ssl/local.key;

      # WebSocket endpoint
      location /ws/ {
         proxy_pass http://localhost:8000/ws/;
         proxy_http_version 1.1;
         proxy_set_header Upgrade $http_upgrade;
         proxy_set_header Connection "Upgrade";
         proxy_set_header Host $host;
      }

      # Other API requests
      location / {
         proxy_pass http://localhost:8000;
      }
   }
   ```

4. restart nginx `brew services restart nginx`
4. Ensure you have Python 3.12.0 installed
5. Clone this repository
6. Run the setup script:
   - On Unix-based systems: `./setup.sh`
   - On Windows: `setup.bat`
7. Activate the virtual environment:
   - On Unix-based systems: `source fastapi-env/bin/activate`
   - On Windows: `fastapi-env\Scripts\activate`
8. Create a `.env` file in the project root directory with the following content:

    ```shell
    OPENAI_API_KEY=your_openai_api_key_here
    ```

    Replace `your_openai_api_key_here` with your actual OPENAI API secret key.
9. Get it running with

     ```shell
     cd sim_world
     uvicorn main:app --reload
     ```
