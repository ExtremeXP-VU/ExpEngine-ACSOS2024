# VS-Code Extension

The language server can be run on VS-Code as an extension reading files with `.exp` extension.

First install the packages:
```bash
cd vs-code-ext
npm install
```

Upon building, the generated files are created in `src/out`; open the extension script in visual studio code [src/out/extension.js](src/out/extension.js), and run the file (using F5), then select visual studio code extension.

Note that the [language server](/exp.engine.dsl.parent/README.md) should be run on another process.

To test the vs-code, create a file with `.exp` extension and write the experiment `DSL`.