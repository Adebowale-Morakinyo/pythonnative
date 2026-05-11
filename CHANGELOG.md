# CHANGELOG


## v0.12.0 (2026-05-11)

### Features

- **components,hooks,native_views**: Add native UI primitives
  ([`186bba6`](https://github.com/pythonnative/pythonnative/commit/186bba6dcc1956cccb1433e004e4fb9b436736ce))


## v0.11.0 (2026-04-29)

### Features

- **layout**: Add pure-Python flexbox engine; rewrite native containers
  ([`4247386`](https://github.com/pythonnative/pythonnative/commit/42473866ee7c2380e6c38f4e42966c64ca3c2bb8))


## v0.10.0 (2026-04-27)

### Documentation

- Adopt Google-style docstrings; revamp MkDocs site
  ([`922ec94`](https://github.com/pythonnative/pythonnative/commit/922ec94bee841c8309b9b26a0c5085f663addb11))

### Features

- **hot_reload**: Reload Python app code without rebuilding
  ([`cddbcdc`](https://github.com/pythonnative/pythonnative/commit/cddbcdc1bfd57ea2362116f0a8e0b1f8c98ca8f9))


## v0.9.0 (2026-04-16)

### Features

- **cli,page,templates**: Stream Python logs from pn run android/ios
  ([`57179b9`](https://github.com/pythonnative/pythonnative/commit/57179b9c3946486aac6eb37a38dbdaa8755335b2))


## v0.8.0 (2026-04-08)

### Features

- **hooks,reconciler**: Defer effects; add batching and use_reducer
  ([`bf6bb57`](https://github.com/pythonnative/pythonnative/commit/bf6bb57b6f97c140820a902ea0eff6bf6a7ffdbc))

- **native_views,components**: Add flexbox-inspired layout system
  ([`094d997`](https://github.com/pythonnative/pythonnative/commit/094d99786f7153a7286eb7db9775db0bb90abf1d))

- **navigation**: Add declarative navigation system
  ([`828bbb0`](https://github.com/pythonnative/pythonnative/commit/828bbb0c83fba640a7055edf1237500f27493fd3))

- **navigation**: Add native tab bars and nested navigator forwarding
  ([`2b80032`](https://github.com/pythonnative/pythonnative/commit/2b8003218267dd39b968c630b89bd5e212ea7254))

### Refactoring

- **native_views**: Split monolithic module into platform-specific package
  ([`d0068fd`](https://github.com/pythonnative/pythonnative/commit/d0068fdbcceb4745b02d8043b03eade2b54dde66))


## v0.7.0 (2026-04-03)

### Features

- Replace class-based Page with function components, style prop, and use_navigation hook
  ([`8103710`](https://github.com/pythonnative/pythonnative/commit/8103710aed5feb564583bb161cf81771669645fe))


## v0.6.0 (2026-04-03)

### Build System

- **deps**: Drop Python 3.9 support (EOL October 2025)
  ([`552cd99`](https://github.com/pythonnative/pythonnative/commit/552cd9958c463a51af9e33f0e254dab18135130f))

### Code Style

- **cli**: Reformat pn.py for Black 2026 stable style
  ([`298f884`](https://github.com/pythonnative/pythonnative/commit/298f884ce3e1c58a17c92484c5832ebae6f1beaa))

### Continuous Integration

- **workflows**: Add package build step to verify sdist and wheel before release
  ([`7fbf9c0`](https://github.com/pythonnative/pythonnative/commit/7fbf9c07988d4c543253dec8ba28da42c38cc3a9))

- **workflows,cli**: Fix e2e workflow script chaining and GitHub API auth
  ([`01d1968`](https://github.com/pythonnative/pythonnative/commit/01d19683f41a4b00048dfbce687e510bec2e2d31))

### Documentation

- Align branch prefixes with conventional commit types
  ([`c6e0e08`](https://github.com/pythonnative/pythonnative/commit/c6e0e08cb0757dad6495c6fee36063699afba87a))

- **repo**: Align conventional commit scopes with module structure
  ([`ecc39af`](https://github.com/pythonnative/pythonnative/commit/ecc39af78708bc5a83ba81501c7b65d985890de9))

- **repo**: Remove component table from README
  ([`ab162c5`](https://github.com/pythonnative/pythonnative/commit/ab162c5b658b2367857ab998d3b3f750eca15b4a))

### Features

- Add function components, hooks, layout, styling, hot reload, native APIs, and new UI components
  ([`3bd87de`](https://github.com/pythonnative/pythonnative/commit/3bd87de4a8775e23eb4f081a31b9125f9b20861c))

- **cli,templates**: Add pythonVersion config, fix Android build, and wire pip requirements
  ([`a529834`](https://github.com/pythonnative/pythonnative/commit/a529834a7bfe817a51ef2a5846c97c2f4deee321))

### Testing

- Increase app startup wait for slow CI emulators
  ([`4ff6b94`](https://github.com/pythonnative/pythonnative/commit/4ff6b9453a7687eeaf7777bf4a2ab542b32a7e25))


## v0.5.0 (2026-03-31)

### Continuous Integration

- **workflows**: Add Maestro E2E tests for Android and iOS
  ([`cfe247e`](https://github.com/pythonnative/pythonnative/commit/cfe247edf99da8ff870e2d4118ef74b2df5521c1))

### Features

- **core**: Replace imperative widget API with declarative component model and reconciler
  ([`b6b7721`](https://github.com/pythonnative/pythonnative/commit/b6b77216305202ea0c5197b29e725e14cbe99b5e))


## v0.4.0 (2026-03-18)

### Bug Fixes

- **components,templates**: Restore hello-world on iOS and Android
  ([`d7ac93b`](https://github.com/pythonnative/pythonnative/commit/d7ac93be202161a5c8328816a5c6ff8a96dde1d5))

### Continuous Integration

- **workflows**: Add semantic-release pipeline and PR commit linting
  ([`0711683`](https://github.com/pythonnative/pythonnative/commit/0711683f5b56751027bb1a5a63ee2d9afcd4b620))

- **workflows**: Append detailed changes link to release notes
  ([`11d50a7`](https://github.com/pythonnative/pythonnative/commit/11d50a75dff850a3855a299f38f5885cf15cefc6))

- **workflows**: Fix duplicate release, and use changelog for release notes
  ([`1cd5393`](https://github.com/pythonnative/pythonnative/commit/1cd5393e7bf20d5350052cfaa81fd511dc4ca3ca))

- **workflows**: Simplify release pipeline to use python-semantic-release defaults
  ([`2766f24`](https://github.com/pythonnative/pythonnative/commit/2766f244f84d359e1ae74a4b029e0701fad4b0be))

### Documentation

- **repo**: Rewrite README with banner, structured sections, and badges
  ([`7c083f4`](https://github.com/pythonnative/pythonnative/commit/7c083f4e38367c6cd4163e0be8c78da1fdf8d3da))

- **repo**: Simplify README with badges and one-paragraph overview
  ([`3ac84b1`](https://github.com/pythonnative/pythonnative/commit/3ac84b1a3f541b47121b46a687b78826f8d348f9))

### Features

- **components**: Standardize fluent setters and align base signatures
  ([`d236d89`](https://github.com/pythonnative/pythonnative/commit/d236d899690a4033effdcab4862a556a742fa6d1))

- **components,core**: Add layout/styling APIs and fluent setters
  ([`6962d38`](https://github.com/pythonnative/pythonnative/commit/6962d3881bf091b3494fc2c964f7ea65a99ce606))

### Refactoring

- **components**: Declare abstract static wrap in ScrollViewBase
  ([`593fee4`](https://github.com/pythonnative/pythonnative/commit/593fee4fcf66678cb026de58115f959633d859b4))

- **core,components,examples**: Add annotations; tighten mypy
  ([`86e4ffc`](https://github.com/pythonnative/pythonnative/commit/86e4ffc9e51810997006055434783416784c182f))


## v0.3.0 (2025-10-22)

### Build System

- **repo**: Remove invalid PyPI classifier
  ([`c8552e1`](https://github.com/pythonnative/pythonnative/commit/c8552e137e0176c0f5c61193e786429e2e93ac7c))

### Chores

- **experiments**: Remove experiments directory
  ([`caf6993`](https://github.com/pythonnative/pythonnative/commit/caf69936e085a3f487123ebcb3a6d807fefcc66c))

- **repo,core,mkdocs**: Bump version to 0.3.0
  ([`64d7c1c`](https://github.com/pythonnative/pythonnative/commit/64d7c1cfb448797305efc7f4014e56584f92fc1a))

### Documentation

- **mkdocs**: Add Architecture page
  ([`6d61ffc`](https://github.com/pythonnative/pythonnative/commit/6d61ffc64ca5db8ae688d09a748ddda2a1bc0af6))

### Features

- **core,templates**: Add push/pop navigation and lifecycle wiring
  ([`06ea22d`](https://github.com/pythonnative/pythonnative/commit/06ea22d215a1700685a7ca8070ca2189895ed25c))

- **templates,core**: Adopt Fragment-based Android navigation
  ([`7a3a695`](https://github.com/pythonnative/pythonnative/commit/7a3a695477ece3cf76afd00f203523990f8789df))


## v0.2.0 (2025-10-14)

### Build System

- **templates,cli**: Ship template dirs with package; drop zip artifacts
  ([`7725b14`](https://github.com/pythonnative/pythonnative/commit/7725b1462c42d89f27fb4d3d733e73177c55d8ac))

### Chores

- Clean up
  ([`6c7a882`](https://github.com/pythonnative/pythonnative/commit/6c7a882895691903457a0a94d33192b6018c77fd))

- **core,components,cli**: Align lint, typing, and tests with CI
  ([`30037d1`](https://github.com/pythonnative/pythonnative/commit/30037d17ad397952a88e3dfeb8bd003ced7319d8))

- **experiments**: Remove unused experiment directories
  ([`db06fd1`](https://github.com/pythonnative/pythonnative/commit/db06fd101789392deee8c37263a61ee4d7106853))

- **repo,ci,docs**: Rename demo to examples/hello-world and update refs
  ([`6d5b78e`](https://github.com/pythonnative/pythonnative/commit/6d5b78ea7dce66b5031b952928aed8d4a713fae8))

- **repo,core,mkdocs**: Bump version to 0.2.0
  ([`d3f8d31`](https://github.com/pythonnative/pythonnative/commit/d3f8d31942c3ca5d1657024e3a5cb332787afcd8))

- **templates**: Scrub DEVELOPMENT_TEAM from iOS template
  ([`64ab266`](https://github.com/pythonnative/pythonnative/commit/64ab2666fe09f036934d3922ab55e8e599df3c35))

### Continuous Integration

- **workflows,mkdocs**: Set CNAME to docs.pythonnative.com for docs deploy
  ([`401a076`](https://github.com/pythonnative/pythonnative/commit/401a076dcb1fe0c19771f4a19141ee8da28c80e2))

### Documentation

- **mkdocs**: Add roadmap and link in nav
  ([`16ede97`](https://github.com/pythonnative/pythonnative/commit/16ede972d41b549853962c7056b65558c9ebd2f5))

- **mkdocs**: Update Getting Started, Hello World, Components, and platform guides
  ([`f3a03b0`](https://github.com/pythonnative/pythonnative/commit/f3a03b01986365063535a2f336793cc6f21836db))

- **repo**: Add CONTRIBUTING.md
  ([`f61cb85`](https://github.com/pythonnative/pythonnative/commit/f61cb85301c7bff57299b4c814319e9262f0f5ef))

### Features

- Update README
  ([`e839585`](https://github.com/pythonnative/pythonnative/commit/e8395855acf5d38a0e5987475900f4eeb1eee313))

- **cli,mkdocs,tests**: Add pn init/run/clean; use bundled templates
  ([`9c61757`](https://github.com/pythonnative/pythonnative/commit/9c61757713fe60b5e98756f552681a782f397f3a))

- **cli,templates**: Auto-select iOS sim; guard PythonKit
  ([`7b7c59c`](https://github.com/pythonnative/pythonnative/commit/7b7c59c262f2510a5fb46e455c13a2fc56086845))

- **cli,templates**: Bundle offline templates; add run --prepare-only
  ([`d9dd821`](https://github.com/pythonnative/pythonnative/commit/d9dd821bc18289f1f1a367e737cfe7d5bfaf6ee3))

- **cli,templates**: Dev-first templates; stage in-repo lib for pn run
  ([`b3dd731`](https://github.com/pythonnative/pythonnative/commit/b3dd731bd5efcca8e1a47f8f888fc6123854a40c))

- **cli,templates,core**: Bootstrap entrypoint; pn run shows Hello UI
  ([`2805e1d`](https://github.com/pythonnative/pythonnative/commit/2805e1d5c6a58eb718b94ba0ce57c1078a08d578))

- **cli,templates,core**: Fetch iOS Python runtime and bootstrap PythonKit
  ([`bcc0916`](https://github.com/pythonnative/pythonnative/commit/bcc0916a5b7427874ab7a5971a6a9941c4222c77))

- **components,utils**: Unify constructors; set Android context
  ([`4c06b67`](https://github.com/pythonnative/pythonnative/commit/4c06b67214ea7fc4530a0d39b7105cfb62d20cf5))

- **repo,mkdocs,workflows**: Migrate to src layout; add pyproject and docs scaffold
  ([`f273922`](https://github.com/pythonnative/pythonnative/commit/f273922e8a0494df7ba2cd59a3ad2ef54f918d3e))

### Refactoring

- **cli**: Make pn.py typing py3.9-compatible and wrap long lines
  ([`b38da78`](https://github.com/pythonnative/pythonnative/commit/b38da78dac52e42968efa6f4115b6b84de65b3b5))

- **components,core**: Align component names with docs
  ([`a326ceb`](https://github.com/pythonnative/pythonnative/commit/a326ceb23c2cfaba409f11451a1c0000f0afbf5e))


## v0.1.0 (2025-10-14)


## v0.0.1 (2025-10-14)
