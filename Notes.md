docker build -t build-script:debian . -f .\Dockerfile.debian
docker run -v $PWD/debian:/app/linux build-script:latest