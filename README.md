# Optimism Devdocs

This repo aggregates `mdbook` docs from multiple repositories, and deploys them as a website on Netlify. It
works like this:

1. Repositories are added as Git submodules,
2. A Python tool walks the directory structure and finds `mdbook` configs in the source.
3. The Python tool builds the books and copies them into subfolders of the `public` directory.

Netlify performs steps two and three during the website build process.

Books are deployed to https://devdocs.optimism.io, and <TODO:private-devdocs>

## Adding a new repository

Find the toml configuration file you would like to add the repository to. See the files
such as dependencies.toml or infra.dependencies.toml

Add a new dependencies object within the config

```toml
[dependencies]
...
[dependencies.new]
url = "<repository-url>
path = "submodules/<repo-name>"
branch = "<branch to build from>"
```

## Adding new books to Remote Repository

Once your repository has been added as a submodule, you can create a new book by initializing an `mdbook` in any
subdirectory. In your `book.toml` make sure to specify the following fields:

```toml
[book]
title = "My Book" # used to generate the index page
description = "A book about my project" # used to generate the index page

[output.html]
build-dir = "some-subdirectory" # defines which subdirectory the book will be deployed to
```

Optionally, you can use `mdbook-mermaid` to render Mermaid diagrams in your book. Otherwise, don't install
additional renderers/plugins to your book without installing them in `scripts/build-netlify.sh` first.

## CI

Books are rebuilt every four hours via triggering a build with circle ci.
There's no need to manually update the submodules unless you need to build the books
locally. The Netlify builder will automatically update the submodules with every build.

