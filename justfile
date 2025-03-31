serve dir="devdocs_public": 
    python3 -m http.server 8000 --directory ./{{dir}}
    ## mdbook serve --open submodules/index

clean-repos:
    rm -rf ./submodules/*

clean-all: clean-repos
    rm -rf ./devdocs_public/*
    rm -rf ./devdocs_private/*

build config="dependencies.toml":  
    bash ./scripts/build-netlify.sh "{{config}}"
