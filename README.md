[![build](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-build.yaml/badge.svg?branch=main)](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-build.yaml)
[![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/mgcth/2d8de651f24d184f5ebe101ffc3c9527/raw/ifk-smhi-coverage-badge.json)](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-build.yaml)
[![docs](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-docs.yaml/badge.svg?branch=main)](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-docs.yaml)
[![lint](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml/badge.svg?branch=main)](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml)
[![mypy](https://img.shields.io/badge/mypy-checked-blue)](https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-type.yaml)
![code style](https://img.shields.io/badge/Code%20style-black-black)

# smhi

Web scraper for SMHI climate data.

The 1-versions of the code are intended to generalize the concept, include functional tests and build functionality such as listing of data sources with relevant information, searchability w r t nearest gps position etc. The work will be a joint effort, but the idea is that it will primarily be led by Mladen Gibanica (mgcth).

The 0-versions of this code (starting at 0.2 to acknowledge that the first version, 0.1, was a part of an ongoing ad-hoc initiative to model solar panels - still under development) are written by Anders Nord (docNord) for the swedish non-profit environmental community "Ingenjörsarbete För Klimatet" <https://ingenjorsarbeteforklimatet.se>. They sport a series of hard-coded solutions to reach relevant data in the Gothenburg area, which was the initial target of the code.
