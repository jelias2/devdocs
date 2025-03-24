serve: 
    python3 -m http.server 8000 --directory ./public
    ## mdbook serve --open submodules/index

clean:
    rm -rf ./public/*
    rm -rf ./submodules/*
    touch ./public/.gitkeep

build config="dependencies.toml":
    bash ./scripts/build-netlify.sh "{{config}}"
