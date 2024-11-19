---
part: modular-community
title: Getting Started
description: The modular community conda channel
---

# Modular Community

Welcome to the modular community conda channel.
This is a place to contribute or consume packages within the Mojo or MAX ecosystem.

## Contributing

All packages are built from [rattler-build] recipes
and are managed on the [modular-community] GitHub repository.
Contributions are done via opening pull requests against the aforementioned repository.

### Adding a New Package

In order to create a new package, follow the following steps:

- Fork [modular-community]
- Add a folder for your new packages under `recipe`
- Create a new `recipe.yaml` in that folder, feel free to take inspiration from the other recipes
- Make sure that the build number is set to `0` and that the license file is packaged
- Open a pull request

### Update an Existing Package

- Fork [modular-community]
- Adapt the `recipe.yaml` of the package you want to update
- If you updated the version, reset the build number to 0
- If the version didn't change, increase the build number by 1
- Open a pull request


[modular-community]: https://github.com/modular/modular-community
[rattler-build]: https://prefix-dev.github.io/rattler-build/latest/
