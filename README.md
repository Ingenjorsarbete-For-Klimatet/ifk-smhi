# smhi

<p align="center">
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-build.yaml">
        <img src="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-build.yaml/badge.svg?branch=main" alt="build" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-build.yaml">
        <img src="https://img.shields.io/endpoint?logo=github&labelColor=%23333a41&logoColor=%23959da5&url=https://gist.githubusercontent.com/mgcth/2d8de651f24d184f5ebe101ffc3c9527/raw/ifk-smhi-coverage-badge.json" alt="coverage" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-docs.yaml">
        <img src="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-docs.yaml/badge.svg?branch=main" alt="docs" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml">
        <img src="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml/badge.svg?branch=main" alt="lint" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-type.yaml">
        <img src="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-type.yaml/badge.svg?branch=main" alt="type" style="max-width: 100%;">
    </a>
</p>

<p align="center">
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml">
        <img src="https://img.shields.io/badge/Linter-flake8-red" alt="linter: flake8" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml">
        <img src="https://img.shields.io/badge/Security-bandit-yellow.svg" alt="security: bandit" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-lint.yaml">
        <img src="https://img.shields.io/badge/Code_style-black-black" alt="code style: black" style="max-width: 100%;">
    </a>
    <a href="https://github.com/Ingenjorsarbete-For-Klimatet/ifk-smhi/actions/workflows/github-action-type.yaml">
        <img src="https://img.shields.io/badge/Type_checker-mypy-blue" alt="type checker: mypy" style="max-width: 100%;">
    </a>
</p>

Web scraper for SMHI climate data.

The 1-versions of the code are intended to generalize the concept, include functional tests and build functionality such as listing of data sources with relevant information, searchability w r t nearest gps position etc. The work will be a joint effort, but the idea is that it will primarily be led by Mladen Gibanica (mgcth).

The 0-versions of this code (starting at 0.2 to acknowledge that the first version, 0.1, was a part of an ongoing ad-hoc initiative to model solar panels - still under development) are written by Anders Nord (docNord) for the swedish non-profit environmental community "Ingenjörsarbete För Klimatet" <https://ingenjorsarbeteforklimatet.se>. They sport a series of hard-coded solutions to reach relevant data in the Gothenburg area, which was the initial target of the code.
