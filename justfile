serve dir="devdocs_public": 
    python3 -m http.server 8000 --directory ./{{dir}}
    ## mdbook serve --open submodules/index

clean:
    rm -rf ./devdocs_public/*
    rm -rf ./devdocs_private/*
    rm -rf ./submodules/*

build config="dependencies.toml":  
    bash ./scripts/build-netlify.sh "{{config}}"
