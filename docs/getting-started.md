# Getting Started

```bash
pip install pythonnative
pn --help
```

- Install: `pip install pythonnative`
- Create a project: `pn init my_app`
  - Scaffolds `app/`, `pythonnative.json`, `requirements.txt`, `.gitignore`
- Run: `pn run android` or `pn run ios`
  - Uses bundled templates; copies your `app/` into the platform project
- Clean: `pn clean`
  - Removes the `build/` directory safely
