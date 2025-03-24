serve: 
    python3 -m http.server 8000 --directory ./public

clean:
    rm -rf ./public

build:
    bash ./scripts/build-netlify.sh