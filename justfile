serve dir="devdocs_public": 
    python3 -m http.server 8000 --directory ./{{dir}}
    ## mdbook serve --open submodules/index

clean:
    rm -rf ./public/*
    rm -rf ./devdocs_public/*
    rm -rf ./submodules/*
    touch ./public/.gitkeep

build config="dependencies.toml":  
    bash ./scripts/build-netlify.sh "{{config}}"
