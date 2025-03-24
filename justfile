update-submodules: 
    bash ./scripts/update-submodules.sh

serve: 
    python3 -m http.server 8000 --directory ./public
